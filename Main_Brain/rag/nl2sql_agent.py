"""
Dynamic NL → SQL Agent (Schema-aware, Self-Correcting)
Generates SQL from natural language and returns ONLY raw data to orchestrator.
"""

import logging
import json
import re
from typing import Dict, Any, List
import httpx

from database.connection import db_manager
from config import settings

logger = logging.getLogger(__name__)


class NL2SQLAgent:
    """Natural language → SQL → Execute → return raw data (no insights here)."""

    def __init__(self):
        self._schema_cache = None  # cache schema to avoid repeated DB calls

    async def _load_schema(self) -> Dict[str, Any]:
        """Dynamically fetch DB schema (works for any schema, any number of tables)."""


        async with db_manager.get_connection() as conn:
            rows = await conn.fetch("""
                SELECT 
                    table_name, 
                    column_name, 
                    data_type
                FROM information_schema.columns
                WHERE table_schema = 'public'
                AND table_name NOT IN ('csv_documents', 'document_metadata', 'file_registry', 'knowledge_base', 'users','data_sync_state')
                ORDER BY table_name, ordinal_position;
            """)

        schema = {}
        for r in rows:
            schema.setdefault(r["table_name"], []).append({
                "column": r["column_name"],
                "type": r["data_type"]
            })

        self._schema_cache = schema
        logger.info(f"[NL2SQL] Loaded schema for {len(schema)} tables: {list(schema.keys())}")
        return schema

    async def _call_llm_for_sql(self, natural_query: str, schema: Dict[str, Any], previous_error: str = None) -> str:
        """Generate SQL from natural language using schema-aware prompt."""
        print(schema, "schema")

        schema_json = json.dumps(schema, indent=2)

        prompt = f"""
You are a senior data engineer generating optimal PostgreSQL queries from natural language.


YOUR OBJECTIVE:
- Produce the most efficient SQL based on user intent
- Decide automatically whether to aggregate or return detailed rows
- Optimize for minimal result size without losing meaning

CONTEXT:
- You know ONLY this database schema (in JSON form below).
- You do NOT know the business domain.

DATABASE SCHEMA (JSON):
{schema_json}


PRINCIPLES:
- Infer if user wants aggregation (summary, comparison, deviation, trend, total, avg)
- If query implies analytics → aggregate + group BY relevant fields automatically
- If query implies listing entities → return detailed rows
- Only SELECT statements. No DML (INSERT/UPDATE/DELETE).
- Output ONLY SQL. No markdown, no explanation, no comments.

BEHAVIOR RULES:
- Prefer fewer rows over many rows
- If dataset would be very large eg: 1000+ rows, return summarized results (aggregation)
- NEVER guess column names. Use only schema-provided names.
- If your first attempt fails, you will get the error and rewrite.

User question:
"{natural_query}"
"""

        if previous_error:
            prompt += f"\nThe earlier SQL failed with error: {previous_error}\nRewrite corrected SQL."

        headers = {
            "Authorization": f"Bearer {settings.llm.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": settings.llm.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 500,
        }

        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(
                f"{settings.llm.base_url}/chat/completions",
                headers=headers,
                json=payload
            )

        if resp.status_code != 200:
            raise Exception(f"LLM API Error: {resp.status_code} - {resp.text}")

        print(resp.json(), "NL2SQL response")
        sql = resp.json()["choices"][0]["message"]["content"]
        print(sql, "NL2SQL sql response")
        return self._cleanup_sql(sql)

    @staticmethod
    def _cleanup_sql(sql: str) -> str:
        """Cleanup SQL if LLM returns it wrapped inside ```sql blocks."""
        return re.sub(r"```(sql)?|```", "", sql).strip().rstrip(";") + ";"

    @staticmethod
    def _is_safe_query(sql: str) -> bool:
        """Allow only SELECT queries. Block dangerous commands."""
        sql_lower = sql.lower()
        return sql_lower.startswith("select") and not any(
            keyword in sql_lower for keyword in
            ["delete", "update", "insert", "drop", "alter", "truncate"]
        )

    async def _execute_sql(self, sql: str) -> List[Dict[str, Any]]:
        """Execute SQL safely and return results."""
        if not self._is_safe_query(sql):
            raise Exception(f"Unsafe query rejected: {sql}")

        async with db_manager.get_connection() as conn:
            rows = await conn.fetch(sql)

        return [dict(r) for r in rows]

    def _reduce_for_llm(self, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Reduce large SQL result into statistical summary for hallucination-proof insights."""
        if not rows:
            return {}

        from statistics import mean

        sample = rows[0]
        numeric_cols = [k for k, v in sample.items() if isinstance(v, (int, float))]

        summary = {
            "total_rows": len(rows),
            "columns": list(sample.keys()),
            "numeric_summary": {
                col: {
                    "min": min(r[col] for r in rows),
                    "max": max(r[col] for r in rows),
                    "avg": mean(r[col] for r in rows)
                }
                for col in numeric_cols
            }
        }

        return summary

    async def process_natural_query(self, natural_query: str) -> Dict[str, Any]:
        """Full pipeline: NL → SQL → Execute → return result to orchestrator."""

        schema = await self._load_schema()

        # SQL attempt #1
        try:
            sql = await self._call_llm_for_sql(natural_query, schema)
            logger.info(f"[NL2SQL] Generated SQL: {sql}")
            results = await self._execute_sql(sql)

        except Exception as first_error:
            logger.warning(f"[NL2SQL] First SQL failed: {first_error}")

            # SQL attempt #2 - retry with error feedback
            sql = await self._call_llm_for_sql(
                natural_query, schema, previous_error=str(first_error)
            )
            logger.info(f"[NL2SQL] Retried SQL: {sql}")
            results = await self._execute_sql(sql)

    
        if len(results) > 200:
            logger.warning(f"[NL2SQL] Returned {len(results)} asking LLM to optimize (dynamic, zero template)"
            )


            optimization_prompt =f"""
Rewrite the following SQL to return fewer rows, while maintaining the SAME filters and intent.

RULES:
- KEEP the original WHERE clause EXACTLY as-is.
- Decide aggregation based on the data:
    * If there is a numeric measure (capacity, amount, mw, deviation, etc.):
        → use SUM() and COUNT() by the most meaningful dimension (e.g., customer_name or project).
    * Use AVG() **only if the user explicitly asked for "average"**.
- DO NOT remove necessary grouping dimensions.
- Output ONLY SELECT SQL. No explanation.

ORIGINAL SQL:
{sql}
"""
            

            sql = await self._call_llm_for_sql(
                optimization_prompt,
                schema
            )
            logger.info(f"[NL2SQL] Optimized SQL: {sql}")

            results = await self._execute_sql(sql)

        # ✅ return ONLY raw data. Insights agent will handle formatting.
        return {
            "success": True,
            "sql_query": sql,
            "row_count": len(results),  # give orchestrator a small preview
            "data_full": results,        # full data sent to insights agent
            "confidence": 0.95,
        }


# Required by orchestrator
nl2sql_agent = NL2SQLAgent()
