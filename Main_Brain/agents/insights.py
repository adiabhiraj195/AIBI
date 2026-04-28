"""
Generic Insights Agent for Multi-Agent Chatbot Copilot
Transforms raw data from NL2SQL into executive-level business insights using LLM
"""

import logging
import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from agents.base import BaseAgent, AgentResponse, QueryContext
from models import CFOResponse, KeyMetric

logger = logging.getLogger(__name__)

class InsightsAgent(BaseAgent):
    """
    Generic Insights Agent that uses LLM to transform raw data into executive-level insights
    Works with any data retrieved from NL2SQL agent and generates contextual business analysis around 4-5 lines
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("insights", config)
        
    async def _initialize_impl(self) -> None:
        """Initialize insights agent resources"""
        logger.info("Insights Agent initialized successfully")
    
    async def _process_impl(self, context: QueryContext) -> AgentResponse:
        """
        Process query and generate executive-level insights using LLM
        Transforms raw data from NL2SQL into business intelligence
        """
        try:
            # Extract data from context metadata (provided by orchestrator)
            data = context.metadata.get('processed_data', [])
            handler_type = context.metadata.get('handler', 'unknown')
            sql_query = context.metadata.get('sql_query', '')
            row_count = context.metadata.get('row_count', 0)
            
            logger.info(f"Processing insights for {len(data) if isinstance(data, list) else 'N/A'} data items")
            
            # Check for no data or empty data arrays
            if not data or (isinstance(data, list) and len(data) == 0) or row_count == 0:
                content = await self._generate_no_data_insights(context)
                return AgentResponse(
                    agent_name=self.name,
                    content=content,
                    confidence=0.7,
                    metadata={
                        "handler": "no_data_guidance",
                        "requires_clarification": True
                    }
                )
            
            # Generate insights using LLM for actual data
            content = await self._generate_llm_insights(data, context)
            
            return AgentResponse(
                agent_name=self.name,
                content=content,
                confidence=0.95,
                metadata={
                    "data_source": handler_type,
                    "data_rows": len(data) if isinstance(data, list) else 1,
                    "sql_query": sql_query[:100] if sql_query else None
                }
            )
            
        except Exception as e:
            logger.error(f"Insights agent processing failed: {str(e)}")
            return AgentResponse(
                agent_name=self.name,
                content=f"Unable to generate business insights: {str(e)}",
                confidence=0.0,
                metadata={"error": str(e)}
            )
    
    async def _generate_llm_insights(self, data: Union[List[Dict], Dict, Any], context: QueryContext) -> str:
        """
        Use LLM to generate executive-level insights from raw data
        This is the core method that transforms any data into business intelligence
        """
        try:
            data_summary = self._prepare_data_summary(data)

            prompt = self._create_insights_prompt(
                user_query=context.query,
                data_summary=data_summary,
                sql_query=context.metadata.get('sql_query', ''),
                data_type=type(data).__name__
            )

            llm_response = await self._call_llm_for_insights(prompt)
            formatted_content = self._format_executive_content(llm_response)
            return formatted_content

        except Exception as e:
            logger.error(f"LLM insights generation failed: {e}")
            return self._generate_fallback_insights(data, context.query)


    def _prepare_data_summary(self, data: Union[List[Dict], Dict, Any]) -> str:
        """
        Prepare a concise summary of the data for LLM processing.
        Detects if an aggregated metric exists (e.g., SUM(), total_x, avg_y, count_z)
        and marks it as the primary metric for insights.
        """
        try:
            if isinstance(data, list):
                if not data:
                    return "No data records found"

                total_records = len(data)
                sample_record = data[0] if data else {}

                columns = list(sample_record.keys()) if isinstance(sample_record, dict) else []

                summary = f"Dataset contains {total_records} records.\n"
                summary += f"Columns: {', '.join(columns)}"

                agg_columns = [
                    c for c in columns
                    if c.lower().startswith(("sum", "total", "avg", "count", "max", "min"))
                ]

                if agg_columns:
                    summary += f"\nPrimary Aggregated Metric Detected: {agg_columns[0]}"

                if total_records <= 5:
                    summary += f"\n\nData:\n{json.dumps(data, indent=2, default=str)}"
                else:
                    summary += f"\n\nFULL DATA (GROUND TRUTH):\n{json.dumps(data, indent=2, default=str)}"
                return summary

            elif isinstance(data, dict):
                return f"Single record result:\n{json.dumps(data, indent=2, default=str)}"

            else:
                return f"Raw data: {str(data)}"

        except Exception as e:
            logger.warning(f"Data summary preparation failed: {e}")
            return f"Data available but summary generation failed: {str(data)[:500]}"


    def _create_insights_prompt(self, user_query: str, data_summary: str, sql_query: str = "", data_type: str = "") -> str:
        """
            Global, schema-agnostic insight generation prompt
            (used by AWS Q, Databricks IQ, Snowflake Arctic style)
        """

        prompt = f"""
You are a senior business analyst and executive advisor. Your task is to transform raw data into executive-level business insights summary around 4-5 lines.
────────────────────────────────────────
USER QUESTION:
{user_query}

DATA (AUTHORITATIVE — DO NOT CHANGE VALUES):
{data_summary}

SQL USED:
{sql_query if sql_query else "N/A"}
────────────────────────────────────────

RULES (VERY IMPORTANT):
1. Use ONLY the numbers that appear in the dataset. NEVER guess or estimate values.
2. Do not summarize or infer values that are not explicit in rows.
3. If the dataset contains aggregated values (e.g., total_capacity, sum_x), those take precedence over individual row values.
4. If no meaningful insight can be derived, say: "Dataset insufficient to identify meaningful trend."
5. Do not hallucinate insights.
6. If a number is not shown in FULL DATA, you MUST NOT mention it.

OUTPUT FORMAT:

Executive Summary:
- 1–2 sentences strictly describing what the dataset shows.

Key Insights:
- Bullet points showing comparisons, ranking, highest/lowest, trends.

Business Actions:
- 2 short recommendations based only on the dataset.

Risk/Notes:
- Mention constraints or missing context, if applicable.

Remember: **no invented numbers, no assumptions. Only interpret what exists.**
"""
        return prompt
    

    async def _call_llm_for_insights(self, prompt: str) -> str:
        try:
            import httpx
            from config import settings
            
            headers = {
                "Authorization": f"Bearer {settings.llm.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": settings.llm.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 800,
                "temperature": 0.0
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{settings.llm.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"].strip()
                else:
                    logger.error(f"LLM API error: {response.status_code} - {response.text}")
                    raise Exception(f"LLM API returned status {response.status_code}")
                    
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise e
    

    def _format_executive_content(self, llm_response: str) -> str:
        formatted_content = "💼 **Executive Business Intelligence**\n\n"
        cleaned_response = llm_response.strip()

        if not cleaned_response.startswith("**"):
            formatted_content += cleaned_response
        else:
            formatted_content += cleaned_response
        
        return formatted_content
    

    async def _generate_no_data_insights(self, context: QueryContext) -> str:
        try:
            prompt = f"""You are a business intelligence advisor. A user asked: "{context.query}"

The query was processed but returned no data. This could be due to:
- Incorrect parameters or filters
- Data not available for the specified criteria
- Query needs refinement

Provide professional guidance that:
1. Acknowledges the user's request
2. Explains why data might not be available
3. Suggests specific ways to refine the query
4. Maintains a helpful, professional tone

Keep response concise (2-3 sentences) and actionable."""

            llm_response = await self._call_llm_for_insights(prompt)
            return f"💼 **Business Intelligence Analysis**\n\n{llm_response}"
            
        except Exception as e:
            logger.warning(f"LLM no-data insights failed: {e}")
            return f"""💼 **Business Intelligence Analysis**

Your query "{context.query}" was processed successfully but returned no matching data.
"""


    def _generate_fallback_insights(self, data: Any, query: str) -> str:
        try:
            data_info = ""
            if isinstance(data, list):
                data_info = f"Retrieved {len(data)} records"
                if data and isinstance(data[0], dict):
                    columns = list(data[0].keys())
                    data_info += f" with fields: {', '.join(columns[:5])}"
            elif isinstance(data, dict):
                data_info = f"Retrieved data with {len(data)} fields: {', '.join(list(data.keys())[:5])}"
            else:
                data_info = f"Retrieved data of type {type(data).__name__}"
            
            return f"""⚠️ **LLM Service Unavailable**

**Status:** Your query "{query}" was processed and data was successfully retrieved. {data_info}.
"""

        except Exception as e:
            logger.error(f"Fallback insights generation failed: {e}")
            return f"""⚠️ **Service Error**

Query "{query}" processed but insights generation failed.
"""


    def _calculate_confidence(self, query: str, context: QueryContext = None) -> float:
        if context and context.metadata.get('processed_data'):
            return 0.95
        return 0.7


# Global insights agent instance
insights_agent = InsightsAgent()
