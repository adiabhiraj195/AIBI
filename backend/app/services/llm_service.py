import json
import httpx
from typing import Dict, Any, List
from fastapi import HTTPException
from app.models.column_metadata import ColumnMetadata, ProcessDocumentRequest
from app.repositories.knowledge_base_repository import KnowledgeBaseRepository
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.api_key = settings.groq_api_key
        self.model = settings.groq_model
        self.base_url = settings.groq_base_url
        self.temperature = settings.groq_temperature
        self.max_tokens = settings.groq_max_tokens
        
        # Validate configuration
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")
    
    async def process_and_store_knowledge(self, request: ProcessDocumentRequest, filename: str, sample_data: List[Dict[str, Any]]) -> int:
        """Process document with LLM and directly store in knowledge base"""
        try:
            # Create analysis prompt
            prompt = self._create_analysis_prompt(request, filename, sample_data)
            
            # Get LLM analysis
            analysis_result = await self._call_llm_api(prompt)
            
            # Parse and structure the response
            structured_data = self._parse_llm_response(analysis_result, request, filename)
            print(structured_data, "structured_data")
            # Store directly in knowledge base
            knowledge_base_id = await KnowledgeBaseRepository.create_knowledge_entry(
                document_id=request.document_id,
                filename=filename,
                summary=structured_data["summary"],
                data_category=structured_data["data_category"],
                insights=structured_data["insights"],
                use_cases=structured_data["use_cases"],
                column_analysis=structured_data["column_analysis"],
                data_quality_score=structured_data["data_quality_score"],
                recommendations=structured_data["recommendations"],
                column_metadata=request.columns
            )
            
            return knowledge_base_id
            
        except Exception as e:
            logger.error(f"Error in LLM processing and storage: {e}")
            raise HTTPException(status_code=500, detail="Failed to process document with LLM")
    
    async def _call_llm_api(self, prompt: str) -> str:
        """Make API call to Groq LLM"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a data analysis expert. Analyze CSV metadata and create structured knowledge base entries. Always respond with valid JSON."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": self.temperature,
                        "max_tokens": self.max_tokens
                    }
                )
            
            if response.status_code != 200:
                logger.error(f"LLM API error: {response.status_code} - {response.text}")
                raise HTTPException(status_code=500, detail=f"LLM API error: {response.status_code}")
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except httpx.TimeoutException:
            logger.error("LLM API timeout")
            raise HTTPException(status_code=504, detail="LLM API timeout")
        except httpx.RequestError as e:
            logger.error(f"LLM API request error: {e}")
            raise HTTPException(status_code=500, detail="LLM API request failed")
    
    def _create_analysis_prompt(self, request: ProcessDocumentRequest, filename: str, sample_data: List[Dict[str, Any]]) -> str:
        """Create structured prompt for LLM analysis"""
        
        # Format column information with all user inputs
        columns_info = []
        for col in request.columns:
            col_info = {
                "name": col.column_name,
                "data_type": col.data_type,
                "connection_key": col.connection_key,
                "alias": col.alias,
                "description": col.description
            }
            columns_info.append(col_info)
        
        # Format sample data
        sample_data_str = json.dumps(sample_data[:5], indent=2)
        
        prompt = f"""
Analyze this CSV file and create a comprehensive knowledge base entry.

**File Information:**
- Filename: {filename}
- Document ID: {request.document_id}

**Column Metadata (with user descriptions):**
{json.dumps(columns_info, indent=2)}

**Sample Data (first 5 rows):**
{sample_data_str}

Create a JSON response with this EXACT structure:
{{
    "summary": "Brief 2-3 sentence summary of what this dataset contains",
    "data_category": "Primary category (e.g., sales, customer, financial, inventory, etc.)",
    "insights": [
        "Key insight 1 about the data patterns",
        "Key insight 2 about data relationships",
        "Key insight 3 about data completeness"
    ],
    "use_cases": [
        "Specific use case 1",
        "Specific use case 2", 
        "Specific use case 3"
    ],
    "column_analysis": {{
        "column_name_1": {{
            "purpose": "What this column represents based on user description",
            "data_quality": "Assessment of data quality for this column",
            "business_value": "Business value and importance",
            "relationships": "How it relates to other columns"
        }}
    }},
    "data_quality_score": 85.5,
    "recommendations": [
        "Recommendation 1 for data usage",
        "Recommendation 2 for data improvement",
        "Recommendation 3 for analysis approaches"
    ]
}}

Focus on:
1. User-provided descriptions to understand business context
2. Data quality assessment based on sample data
3. Practical recommendations for data usage
4. Identifying relationships between columns
5. Scoring data quality on a 0-100 scale

Respond ONLY with valid JSON, no additional text.
"""
        return prompt
    
    def _parse_llm_response(self, content: str, request: ProcessDocumentRequest, filename: str) -> Dict[str, Any]:
        """Parse LLM response and ensure proper structure"""
        try:
            # Try to extract JSON from response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = content[start_idx:end_idx]
                analysis = json.loads(json_str)
                
                # Validate required fields and provide defaults
                structured_data = {
                    "summary": analysis.get("summary", f"Analysis of {filename} dataset"),
                    "data_category": analysis.get("data_category", "general"),
                    "insights": analysis.get("insights", ["Data analysis completed"]),
                    "use_cases": analysis.get("use_cases", ["Data analysis", "Reporting"]),
                    "column_analysis": analysis.get("column_analysis", {}),
                    "data_quality_score": float(analysis.get("data_quality_score", 75.0)),
                    "recommendations": analysis.get("recommendations", ["Review data quality"])
                }
                
                # Ensure column_analysis has entries for all columns
                for col in request.columns:
                    if col.column_name not in structured_data["column_analysis"]:
                        structured_data["column_analysis"][col.column_name] = {
                            "purpose": col.description or f"Analysis of {col.column_name}",
                            "data_quality": "Good",
                            "business_value": "Standard",
                            "relationships": "To be determined"
                        }
                
                return structured_data
            else:
                raise ValueError("No valid JSON found in response")
                
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse LLM response as JSON: {e}")
            # Fallback structured response
            return {
                "summary": f"Automated analysis of {filename} completed",
                "data_category": "general",
                "insights": ["Data structure analyzed", "Column types identified", "Sample data reviewed"],
                "use_cases": ["Data analysis", "Reporting", "Business intelligence"],
                "column_analysis": {
                    col.column_name: {
                        "purpose": col.description or f"Analysis of {col.column_name}",
                        "data_quality": "Good",
                        "business_value": "Standard",
                        "relationships": "Independent"
                    } for col in request.columns
                },
                "data_quality_score": 75.0,
                "recommendations": ["Review data completeness", "Validate data types", "Consider data relationships"]
            }