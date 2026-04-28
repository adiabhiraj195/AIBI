"""
Statistical Query Handler for RAG System
Handles aggregation and statistical queries that require database-level operations
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
import re
from database.connection import db_manager
from config import settings

logger = logging.getLogger(__name__)

class StatisticalQueryHandler:
    """Handles statistical and aggregation queries"""
    
    def __init__(self):
        self.query_patterns = {
            'total_customers': [
                r'total.*customer.*count',
                r'how many.*customers',
                r'number.*customers',
                r'count.*customers',
                r'unique.*customers'
            ],
            'highest_capacity': [
                r'highest.*capacity',
                r'maximum.*capacity', 
                r'largest.*capacity',
                r'biggest.*capacity',
                r'customer.*highest.*capacity',
                r'which.*customer.*highest',
                r'who.*has.*highest',
                r'maximum.*mwg'
            ],
            'total_capacity': [
                r'total.*capacity',
                r'sum.*capacity',
                r'overall.*capacity',
                r'aggregate.*capacity',
                r'total.*mwg',
                r'generation.*capacity',
                r'power.*generation'
            ],
            'customer_capacity': [
                r'capacity.*by.*customer',
                r'customer.*capacity.*breakdown',
                r'each.*customer.*capacity',
                r'top.*customers.*by.*capacity',
                r'show.*me.*top.*customers',
                r'list.*customers.*by.*capacity',
                r'customers.*highest.*capacity',
                r'top.*\d+.*customers',
                r'mwg.*by.*customer',
                r'rank.*customers',
                r'compare.*customers'
            ],
            'state_analysis': [
                r'by.*state',
                r'state.*wise',
                r'per.*state',
                r'state.*breakdown',
                r'which.*states.*have.*most',
                r'states.*with.*most.*projects',
                r'top.*states',
                r'states.*highest.*capacity',
                r'bottom.*\d+.*states',
                r'compare.*states',
                r'for.*state.*\d+'
            ],
            'business_module_analysis': [
                r'by.*business.*module',
                r'business.*module.*wise',
                r'per.*business.*module'
            ],
            'wtg_analysis': [
                r'wtg.*count',
                r'turbine.*count',
                r'number.*of.*wtg',
                r'how.*many.*turbines',
                r'total.*turbines',
                r'wtg.*by.*model',
                r'turbine.*by.*type',
                r'wtg.*breakdown',
                r'model.*wise.*wtg',
                r'wtg.*distribution',
                r'by.*wtg.*model',
                r'model.*wise',
                r'turbine.*model.*breakdown',
                r'which.*models',
                r'top.*models',
                r'model.*distribution',
                r'by.*model.*bucket',
                r'by.*wtg.*type',
                r'type.*wise',
                r'hlt.*vs.*llt',
                r'turbine.*type.*breakdown'
            ],
            'mwg_analysis': [
                r'mwg.*analysis',
                r'mwg.*breakdown',
                r'avg.*mwg',
                r'average.*mwg',
                r'mean.*mwg',
                r'total.*mwg'
            ],
            'deviation_analysis': [
                r'wtg.*deviation',
                r'mwg.*deviation',
                r'variance.*in.*wtg',
                r'variance.*in.*mwg',
                r'deviation.*analysis',
                r'difference.*between.*plan.*and.*actual',
                r'gap.*analysis'
            ],
            'project_phase_analysis': [
                r'by.*project.*phase',
                r'phase.*wise',
                r'per.*phase',
                r'ro.*plan',
                r'ro.*actual',
                r'projects.*in.*phase',
                r'phase.*breakdown'
            ],
            'fiscal_year_analysis': [
                r'by.*fiscal.*year',
                r'fy.*wise',
                r'fiscal.*year.*breakdown',
                r'by.*period',
                r'monthly.*breakdown',
                r'period.*wise',
                r'time.*series',
                r'trend.*over.*time',
                r'in.*fiscal.*year'
            ],
            'data_type_analysis': [
                r'plan.*vs.*actual',
                r'budgeted.*vs.*actual',
                r'forecast.*vs.*actual',
                r'planned.*capacity',
                r'actual.*capacity',
                r'budget.*analysis'
            ],
            'source_analysis': [
                r'by.*source',
                r'source.*wise',
                r'e3.*transaction',
                r'data.*source.*breakdown'
            ],
            'ryear_analysis': [
                r'by.*ryear',
                r'r7.*projects',
                r'ryear.*breakdown'
            ],
            'average_queries': [
                r'average.*capacity.*per.*customer',
                r'average.*project.*size',
                r'mean.*project.*size',
                r'avg.*capacity(?!.*mwg)',
                r'mean.*capacity(?!.*mwg)',
                r'average.*wtg.*count.*per.*project'
            ],
            'min_max_queries': [
                r'minimum.*capacity',
                r'smallest.*project',
                r'minimum.*mwg',
                r'lowest.*(?!performing).*count',
                r'lowest.*capacity'
            ],
            'count_queries': [
                r'how.*many.*projects',
                r'number.*of.*projects',
                r'project.*count',
                r'count.*of.*records'
            ],
            'ranking_queries': [
                r'top.*\d+.*customers.*by.*wtg',
                r'lowest.*performing',
                r'bottom.*\d+'
            ],
            'comparison_queries': [
                r'compare.*models',
                r'difference.*between',
                r'\bvs\b'
            ],
            'filter_queries': [
                r'specific.*customer',
                r'only.*hlt',
                r'filter.*by'
            ],
            'portfolio_analysis': [
                r'portfolio.*capacity',
                r'total.*portfolio',
                r'portfolio.*breakdown',
                r'portfolio.*diversification',
                r'capacity.*break.*down.*by.*business.*module',
                r'revenue.*potential',
                r'market.*position'
            ],
            'concentration_risk': [
                r'concentration.*risk',
                r'percentage.*of.*total.*capacity',
                r'top.*\d+.*customers.*percentage',
                r'customer.*concentration',
                r'risk.*assessment',
                r'diversification'
            ],
            'geographic_analysis': [
                r'geographic.*risk',
                r'geographic.*diversification',
                r'market.*penetration',
                r'states.*contribute.*most',
                r'revenue.*by.*state'
            ],
            'pipeline_analysis': [
                r'project.*pipeline',
                r'pipeline.*analysis',
                r'projects.*in.*each.*phase',
                r'capacity.*in.*pipeline',
                r'cash.*flow.*forecasting',
                r'revenue.*pipeline'
            ],
            'technology_analysis': [
                r'technology.*risk',
                r'technology.*mix',
                r'wtg.*model.*distribution',
                r'turbine.*type.*capacity',
                r'operational.*efficiency'
            ],
            'performance_comparison': [
                r'compare.*capacity.*additions',
                r'year.*over.*year',
                r'fy\d+.*vs.*fy\d+',
                r'growth.*analysis',
                r'performance.*comparison'
            ],
            'efficiency_metrics': [
                r'operational.*scale',
                r'efficiency.*metrics',
                r'average.*project.*size',
                r'capacity.*utilization',
                r'asset.*utilization',
                r'technology.*roi'
            ],
            'variance_analysis': [
                r'highest.*variance',
                r'execution.*risk',
                r'customer.*reliability',
                r'planned.*vs.*actual',
                r'variance.*between.*planned.*and.*actual'
            ],
            'business_unit_performance': [
                r'business.*unit.*performance',
                r'rank.*business.*modules',
                r'resource.*allocation',
                r'business.*module.*by.*capacity'
            ]
        }
    
    def classify_query(self, query: str) -> Optional[str]:
        """Classify the query type based on patterns with priority order"""
        query_lower = query.lower()
        
        # Define priority order (more specific patterns first)
        priority_order = [
            'portfolio_analysis',
            'concentration_risk',
            'geographic_analysis',
            'pipeline_analysis',
            'technology_analysis',
            'performance_comparison',
            'efficiency_metrics',
            'variance_analysis',
            'business_unit_performance',
            'mwg_analysis',
            'wtg_analysis', 
            'deviation_analysis',
            'project_phase_analysis',
            'fiscal_year_analysis',
            'data_type_analysis',
            'average_queries',
            'min_max_queries',
            'ranking_queries',
            'comparison_queries',
            'filter_queries',
            'source_analysis',
            'ryear_analysis',
            'count_queries',
            'total_customers',
            'highest_capacity',
            'total_capacity',
            'customer_capacity',
            'state_analysis',
            'business_module_analysis'
        ]
        
        # Check patterns in priority order
        for query_type in priority_order:
            if query_type in self.query_patterns:
                patterns = self.query_patterns[query_type]
                for pattern in patterns:
                    if re.search(pattern, query_lower):
                        return query_type
        
        return None
    
    async def handle_statistical_query(self, query: str) -> Dict[str, Any]:
        """Handle statistical queries with direct database operations"""
        query_type = self.classify_query(query)
        
        if not query_type:
            return None
        
        try:
            if query_type == 'total_customers':
                return await self._get_total_customers()
            elif query_type == 'highest_capacity':
                return await self._get_highest_capacity_customer()
            elif query_type == 'total_capacity':
                return await self._get_total_capacity()
            elif query_type == 'customer_capacity':
                return await self._get_customer_capacity_breakdown()
            elif query_type == 'state_analysis':
                return await self._get_state_analysis()
            elif query_type == 'business_module_analysis':
                return await self._get_business_module_analysis()
            elif query_type == 'wtg_analysis':
                return await self._get_wtg_analysis()
            elif query_type == 'mwg_analysis':
                return await self._get_mwg_analysis()
            elif query_type == 'deviation_analysis':
                return await self._get_deviation_analysis()
            elif query_type == 'project_phase_analysis':
                return await self._get_project_phase_analysis()
            elif query_type == 'fiscal_year_analysis':
                return await self._get_fiscal_year_analysis()
            elif query_type == 'data_type_analysis':
                return await self._get_data_type_analysis()
            elif query_type == 'source_analysis':
                return await self._get_source_analysis()
            elif query_type == 'ryear_analysis':
                return await self._get_ryear_analysis()
            elif query_type == 'average_queries':
                return await self._get_average_analysis()
            elif query_type == 'min_max_queries':
                return await self._get_min_max_analysis()
            elif query_type == 'count_queries':
                return await self._get_count_analysis()
            elif query_type == 'ranking_queries':
                return await self._get_ranking_analysis()
            elif query_type == 'comparison_queries':
                return await self._get_comparison_analysis()
            elif query_type == 'filter_queries':
                return await self._get_filter_analysis()
            elif query_type == 'portfolio_analysis':
                return await self._get_portfolio_analysis()
            elif query_type == 'concentration_risk':
                return await self._get_concentration_risk_analysis()
            elif query_type == 'geographic_analysis':
                return await self._get_geographic_analysis()
            elif query_type == 'pipeline_analysis':
                return await self._get_pipeline_analysis()
            elif query_type == 'technology_analysis':
                return await self._get_technology_analysis()
            elif query_type == 'performance_comparison':
                return await self._get_performance_comparison()
            elif query_type == 'efficiency_metrics':
                return await self._get_efficiency_metrics()
            elif query_type == 'variance_analysis':
                return await self._get_variance_analysis()
            elif query_type == 'business_unit_performance':
                return await self._get_business_unit_performance()
            
        except Exception as e:
            logger.error(f"Statistical query failed: {e}")
            return {
                'error': str(e),
                'query_type': query_type,
                'success': False
            }
        
        return None
    
    async def _get_total_customers(self) -> Dict[str, Any]:
        """Get total unique customer count"""
        async with db_manager.get_connection() as conn:
            # Get unique customers
            unique_customers = await conn.fetchval(
                "SELECT COUNT(DISTINCT customer_name) FROM rag_embeddings WHERE customer_name IS NOT NULL"
            )
            
            # Get sample customer names
            sample_customers = await conn.fetch(
                "SELECT DISTINCT customer_name FROM rag_embeddings WHERE customer_name IS NOT NULL LIMIT 10"
            )
            
            return {
                'query_type': 'total_customers',
                'total_customers': unique_customers,
                'sample_customers': [row['customer_name'] for row in sample_customers],
                'success': True,
                'answer': f"The total number of unique customers is {unique_customers}.",
                'confidence': 1.0
            }
    
    async def _get_highest_capacity_customer(self) -> Dict[str, Any]:
        """Get customer with highest capacity"""
        async with db_manager.get_connection() as conn:
            # Get customer with highest single project capacity
            highest_single = await conn.fetchrow("""
                SELECT customer_name, capacity, state, business_module, project_phase
                FROM rag_embeddings 
                WHERE capacity IS NOT NULL 
                ORDER BY capacity DESC 
                LIMIT 1
            """)
            
            # Get customer with highest total capacity across all projects
            highest_total = await conn.fetchrow("""
                SELECT customer_name, SUM(capacity) as total_capacity, COUNT(*) as project_count
                FROM rag_embeddings 
                WHERE capacity IS NOT NULL AND customer_name IS NOT NULL
                GROUP BY customer_name 
                ORDER BY total_capacity DESC 
                LIMIT 1
            """)
            
            return {
                'query_type': 'highest_capacity',
                'highest_single_project': {
                    'customer_name': highest_single['customer_name'],
                    'capacity': highest_single['capacity'],
                    'state': highest_single['state'],
                    'business_module': highest_single['business_module'],
                    'project_phase': highest_single['project_phase']
                },
                'highest_total_capacity': {
                    'customer_name': highest_total['customer_name'],
                    'total_capacity': highest_total['total_capacity'],
                    'project_count': highest_total['project_count']
                },
                'success': True,
                'answer': f"Customer with highest single project capacity: {highest_single['customer_name']} with {highest_single['capacity']} MW. Customer with highest total capacity across all projects: {highest_total['customer_name']} with {highest_total['total_capacity']} MW across {highest_total['project_count']} projects.",
                'confidence': 1.0
            }
    
    async def _get_total_capacity(self) -> Dict[str, Any]:
        """Get total capacity across all projects"""
        async with db_manager.get_connection() as conn:
            total_capacity = await conn.fetchval(
                "SELECT SUM(capacity) FROM rag_embeddings WHERE capacity IS NOT NULL"
            )
            
            project_count = await conn.fetchval(
                "SELECT COUNT(*) FROM rag_embeddings WHERE capacity IS NOT NULL"
            )
            
            avg_capacity = await conn.fetchval(
                "SELECT AVG(capacity) FROM rag_embeddings WHERE capacity IS NOT NULL"
            )
            
            return {
                'query_type': 'total_capacity',
                'total_capacity': total_capacity,
                'project_count': project_count,
                'average_capacity': avg_capacity,
                'success': True,
                'answer': f"Total capacity across all projects: {total_capacity:.2f} MW from {project_count} projects. Average project capacity: {avg_capacity:.2f} MW.",
                'confidence': 1.0
            }
    
    async def _get_customer_capacity_breakdown(self) -> Dict[str, Any]:
        """Get capacity breakdown by customer"""
        async with db_manager.get_connection() as conn:
            customer_breakdown = await conn.fetch("""
                SELECT 
                    customer_name, 
                    SUM(capacity) as total_capacity, 
                    COUNT(*) as project_count,
                    AVG(capacity) as avg_capacity,
                    MAX(capacity) as max_capacity
                FROM rag_embeddings 
                WHERE capacity IS NOT NULL AND customer_name IS NOT NULL
                GROUP BY customer_name 
                ORDER BY total_capacity DESC 
                LIMIT 20
            """)
            
            breakdown_list = []
            for row in customer_breakdown:
                breakdown_list.append({
                    'customer_name': row['customer_name'],
                    'total_capacity': row['total_capacity'],
                    'project_count': row['project_count'],
                    'avg_capacity': row['avg_capacity'],
                    'max_capacity': row['max_capacity']
                })
            
            return {
                'query_type': 'customer_capacity',
                'customer_breakdown': breakdown_list,
                'success': True,
                'answer': f"Top customers by capacity: {breakdown_list[0]['customer_name']} ({breakdown_list[0]['total_capacity']:.2f} MW), {breakdown_list[1]['customer_name']} ({breakdown_list[1]['total_capacity']:.2f} MW), {breakdown_list[2]['customer_name']} ({breakdown_list[2]['total_capacity']:.2f} MW).",
                'confidence': 1.0
            }
    
    async def _get_state_analysis(self) -> Dict[str, Any]:
        """Get analysis by state"""
        async with db_manager.get_connection() as conn:
            state_analysis = await conn.fetch("""
                SELECT 
                    state,
                    COUNT(DISTINCT customer_name) as customer_count,
                    SUM(capacity) as total_capacity,
                    COUNT(*) as project_count,
                    AVG(capacity) as avg_capacity
                FROM rag_embeddings 
                WHERE capacity IS NOT NULL AND state IS NOT NULL
                GROUP BY state 
                ORDER BY total_capacity DESC 
                LIMIT 15
            """)
            
            state_list = []
            for row in state_analysis:
                state_list.append({
                    'state': row['state'],
                    'customer_count': row['customer_count'],
                    'total_capacity': row['total_capacity'],
                    'project_count': row['project_count'],
                    'avg_capacity': row['avg_capacity']
                })
            
            return {
                'query_type': 'state_analysis',
                'state_breakdown': state_list,
                'success': True,
                'answer': f"Top states by capacity: {state_list[0]['state']} ({state_list[0]['total_capacity']:.2f} MW, {state_list[0]['customer_count']} customers), {state_list[1]['state']} ({state_list[1]['total_capacity']:.2f} MW, {state_list[1]['customer_count']} customers).",
                'confidence': 1.0
            }
    
    async def _get_business_module_analysis(self) -> Dict[str, Any]:
        """Get analysis by business module"""
        async with db_manager.get_connection() as conn:
            module_analysis = await conn.fetch("""
                SELECT 
                    business_module,
                    COUNT(DISTINCT customer_name) as customer_count,
                    SUM(capacity) as total_capacity,
                    COUNT(*) as project_count,
                    AVG(capacity) as avg_capacity
                FROM rag_embeddings 
                WHERE capacity IS NOT NULL AND business_module IS NOT NULL
                GROUP BY business_module 
                ORDER BY total_capacity DESC
            """)
            
            module_list = []
            for row in module_analysis:
                module_list.append({
                    'business_module': row['business_module'],
                    'customer_count': row['customer_count'],
                    'total_capacity': row['total_capacity'],
                    'project_count': row['project_count'],
                    'avg_capacity': row['avg_capacity']
                })
            
            return {
                'query_type': 'business_module_analysis',
                'module_breakdown': module_list,
                'success': True,
                'answer': f"Business modules by capacity: {module_list[0]['business_module']} ({module_list[0]['total_capacity']:.2f} MW), {module_list[1]['business_module']} ({module_list[1]['total_capacity']:.2f} MW).",
                'confidence': 1.0
            }
    
    async def _get_wtg_analysis(self) -> Dict[str, Any]:
        """Get WTG (Wind Turbine Generator) analysis"""
        async with db_manager.get_connection() as conn:
            # Total WTG count
            total_wtg = await conn.fetchval(
                "SELECT SUM(wtg_count) FROM rag_embeddings WHERE wtg_count IS NOT NULL"
            )
            
            # WTG by model
            wtg_by_model = await conn.fetch("""
                SELECT 
                    wtg_model,
                    SUM(wtg_count) as total_wtg,
                    COUNT(*) as project_count,
                    SUM(capacity) as total_capacity
                FROM rag_embeddings 
                WHERE wtg_model IS NOT NULL AND wtg_count IS NOT NULL
                GROUP BY wtg_model 
                ORDER BY total_wtg DESC 
                LIMIT 10
            """)
            
            # WTG by type
            wtg_by_type = await conn.fetch("""
                SELECT 
                    wtg_type,
                    SUM(wtg_count) as total_wtg,
                    COUNT(*) as project_count
                FROM rag_embeddings 
                WHERE wtg_type IS NOT NULL AND wtg_count IS NOT NULL
                GROUP BY wtg_type 
                ORDER BY total_wtg DESC
            """)
            
            model_breakdown = [dict(row) for row in wtg_by_model]
            type_breakdown = [dict(row) for row in wtg_by_type]
            
            return {
                'query_type': 'wtg_analysis',
                'total_wtg': total_wtg,
                'model_breakdown': model_breakdown,
                'type_breakdown': type_breakdown,
                'success': True,
                'answer': f"Total WTG count: {total_wtg}. Top models: {model_breakdown[0]['wtg_model']} ({model_breakdown[0]['total_wtg']} turbines), {model_breakdown[1]['wtg_model']} ({model_breakdown[1]['total_wtg']} turbines).",
                'confidence': 1.0
            }
    
    async def _get_mwg_analysis(self) -> Dict[str, Any]:
        """Get MWG (Megawatt Generation) analysis"""
        async with db_manager.get_connection() as conn:
            total_mwg = await conn.fetchval(
                "SELECT SUM(mwg) FROM rag_embeddings WHERE mwg IS NOT NULL"
            )
            
            avg_mwg = await conn.fetchval(
                "SELECT AVG(mwg) FROM rag_embeddings WHERE mwg IS NOT NULL"
            )
            
            mwg_by_customer = await conn.fetch("""
                SELECT 
                    customer_name,
                    SUM(mwg) as total_mwg,
                    COUNT(*) as project_count
                FROM rag_embeddings 
                WHERE mwg IS NOT NULL AND customer_name IS NOT NULL
                GROUP BY customer_name 
                ORDER BY total_mwg DESC 
                LIMIT 10
            """)
            
            customer_breakdown = [dict(row) for row in mwg_by_customer]
            
            return {
                'query_type': 'mwg_analysis',
                'total_mwg': total_mwg,
                'average_mwg': avg_mwg,
                'customer_breakdown': customer_breakdown,
                'success': True,
                'answer': f"Total MWG: {total_mwg:.2f}, Average MWG: {avg_mwg:.2f}. Top customers by MWG: {customer_breakdown[0]['customer_name']} ({customer_breakdown[0]['total_mwg']:.2f}).",
                'confidence': 1.0
            }
    
    async def _get_deviation_analysis(self) -> Dict[str, Any]:
        """Get deviation analysis (plan vs actual)"""
        async with db_manager.get_connection() as conn:
            wtg_deviation_stats = await conn.fetchrow("""
                SELECT 
                    AVG(wtg_count_deviation) as avg_wtg_deviation,
                    SUM(wtg_count_deviation) as total_wtg_deviation,
                    COUNT(*) as records_with_deviation
                FROM rag_embeddings 
                WHERE wtg_count_deviation IS NOT NULL
            """)
            
            mwg_deviation_stats = await conn.fetchrow("""
                SELECT 
                    AVG(mwg_deviation) as avg_mwg_deviation,
                    SUM(mwg_deviation) as total_mwg_deviation
                FROM rag_embeddings 
                WHERE mwg_deviation IS NOT NULL
            """)
            
            return {
                'query_type': 'deviation_analysis',
                'wtg_deviation': dict(wtg_deviation_stats),
                'mwg_deviation': dict(mwg_deviation_stats),
                'success': True,
                'answer': f"Average WTG deviation: {wtg_deviation_stats['avg_wtg_deviation']:.2f}, Average MWG deviation: {mwg_deviation_stats['avg_mwg_deviation']:.2f}.",
                'confidence': 1.0
            }
    
    async def _get_project_phase_analysis(self) -> Dict[str, Any]:
        """Get project phase analysis"""
        async with db_manager.get_connection() as conn:
            phase_analysis = await conn.fetch("""
                SELECT 
                    project_phase,
                    COUNT(*) as project_count,
                    SUM(capacity) as total_capacity,
                    COUNT(DISTINCT customer_name) as customer_count
                FROM rag_embeddings 
                WHERE project_phase IS NOT NULL
                GROUP BY project_phase 
                ORDER BY project_count DESC
            """)
            
            phase_breakdown = [dict(row) for row in phase_analysis]
            
            return {
                'query_type': 'project_phase_analysis',
                'phase_breakdown': phase_breakdown,
                'success': True,
                'answer': f"Project phases: {phase_breakdown[0]['project_phase']} ({phase_breakdown[0]['project_count']} projects), {phase_breakdown[1]['project_phase']} ({phase_breakdown[1]['project_count']} projects).",
                'confidence': 1.0
            }
    
    async def _get_fiscal_year_analysis(self) -> Dict[str, Any]:
        """Get fiscal year analysis"""
        async with db_manager.get_connection() as conn:
            fy_analysis = await conn.fetch("""
                SELECT 
                    fiscalyear,
                    COUNT(*) as project_count,
                    SUM(capacity) as total_capacity,
                    COUNT(DISTINCT customer_name) as customer_count
                FROM rag_embeddings 
                WHERE fiscalyear IS NOT NULL
                GROUP BY fiscalyear 
                ORDER BY fiscalyear DESC
            """)
            
            fy_breakdown = [dict(row) for row in fy_analysis]
            
            return {
                'query_type': 'fiscal_year_analysis',
                'fy_breakdown': fy_breakdown,
                'success': True,
                'answer': f"Recent fiscal years: {fy_breakdown[0]['fiscalyear']} ({fy_breakdown[0]['project_count']} projects), {fy_breakdown[1]['fiscalyear']} ({fy_breakdown[1]['project_count']} projects).",
                'confidence': 1.0
            }
    
    async def _get_data_type_analysis(self) -> Dict[str, Any]:
        """Get data type analysis (plan vs actual)"""
        async with db_manager.get_connection() as conn:
            data_type_analysis = await conn.fetch("""
                SELECT 
                    data_type,
                    COUNT(*) as record_count,
                    SUM(capacity) as total_capacity
                FROM rag_embeddings 
                WHERE data_type IS NOT NULL
                GROUP BY data_type 
                ORDER BY record_count DESC
            """)
            
            type_breakdown = [dict(row) for row in data_type_analysis]
            
            return {
                'query_type': 'data_type_analysis',
                'type_breakdown': type_breakdown,
                'success': True,
                'answer': f"Data types: {type_breakdown[0]['data_type']} ({type_breakdown[0]['record_count']} records), {type_breakdown[1]['data_type']} ({type_breakdown[1]['record_count']} records).",
                'confidence': 1.0
            }
    
    async def _get_source_analysis(self) -> Dict[str, Any]:
        """Get source file analysis"""
        async with db_manager.get_connection() as conn:
            source_analysis = await conn.fetch("""
                SELECT 
                    source_file,
                    COUNT(*) as record_count
                FROM rag_embeddings 
                WHERE source_file IS NOT NULL
                GROUP BY source_file 
                ORDER BY record_count DESC
                LIMIT 10
            """)
            
            source_breakdown = [dict(row) for row in source_analysis]
            
            return {
                'query_type': 'source_analysis',
                'source_breakdown': source_breakdown,
                'success': True,
                'answer': f"Top sources: {source_breakdown[0]['source_file']} ({source_breakdown[0]['record_count']} records).",
                'confidence': 1.0
            }
    
    async def _get_ryear_analysis(self) -> Dict[str, Any]:
        """Get R-year analysis"""
        async with db_manager.get_connection() as conn:
            ryear_analysis = await conn.fetch("""
                SELECT 
                    ryear,
                    COUNT(*) as project_count,
                    SUM(capacity) as total_capacity
                FROM rag_embeddings 
                WHERE ryear IS NOT NULL
                GROUP BY ryear 
                ORDER BY ryear DESC
            """)
            
            ryear_breakdown = [dict(row) for row in ryear_analysis]
            
            return {
                'query_type': 'ryear_analysis',
                'ryear_breakdown': ryear_breakdown,
                'success': True,
                'answer': f"R-year breakdown: {ryear_breakdown[0]['ryear']} ({ryear_breakdown[0]['project_count']} projects).",
                'confidence': 1.0
            }
    
    async def _get_average_analysis(self) -> Dict[str, Any]:
        """Get average/mean analysis"""
        async with db_manager.get_connection() as conn:
            avg_stats = await conn.fetchrow("""
                SELECT 
                    AVG(capacity) as avg_capacity,
                    AVG(wtg_count) as avg_wtg_count,
                    AVG(mwg) as avg_mwg
                FROM rag_embeddings 
                WHERE capacity IS NOT NULL
            """)
            
            return {
                'query_type': 'average_analysis',
                'averages': dict(avg_stats),
                'success': True,
                'answer': f"Average capacity: {avg_stats['avg_capacity']:.2f} MW, Average WTG count: {avg_stats['avg_wtg_count']:.2f}, Average MWG: {avg_stats['avg_mwg']:.2f}.",
                'confidence': 1.0
            }
    
    async def _get_min_max_analysis(self) -> Dict[str, Any]:
        """Get minimum/maximum analysis"""
        async with db_manager.get_connection() as conn:
            min_max_stats = await conn.fetchrow("""
                SELECT 
                    MIN(capacity) as min_capacity,
                    MAX(capacity) as max_capacity,
                    MIN(wtg_count) as min_wtg_count,
                    MAX(wtg_count) as max_wtg_count
                FROM rag_embeddings 
                WHERE capacity IS NOT NULL
            """)
            
            return {
                'query_type': 'min_max_analysis',
                'min_max': dict(min_max_stats),
                'success': True,
                'answer': f"Capacity range: {min_max_stats['min_capacity']:.2f} - {min_max_stats['max_capacity']:.2f} MW, WTG count range: {min_max_stats['min_wtg_count']:.0f} - {min_max_stats['max_wtg_count']:.0f}.",
                'confidence': 1.0
            }
    
    async def _get_count_analysis(self) -> Dict[str, Any]:
        """Get count analysis"""
        async with db_manager.get_connection() as conn:
            total_projects = await conn.fetchval(
                "SELECT COUNT(*) FROM rag_embeddings"
            )
            
            projects_with_capacity = await conn.fetchval(
                "SELECT COUNT(*) FROM rag_embeddings WHERE capacity IS NOT NULL"
            )
            
            return {
                'query_type': 'count_analysis',
                'total_projects': total_projects,
                'projects_with_capacity': projects_with_capacity,
                'success': True,
                'answer': f"Total projects: {total_projects}, Projects with capacity data: {projects_with_capacity}.",
                'confidence': 1.0
            }
    
    async def _get_ranking_analysis(self) -> Dict[str, Any]:
        """Get ranking analysis"""
        # This will use existing customer_capacity method
        return await self._get_customer_capacity_breakdown()
    
    async def _get_comparison_analysis(self) -> Dict[str, Any]:
        """Get comparison analysis"""
        # This will provide a general comparison overview
        async with db_manager.get_connection() as conn:
            comparison_data = await conn.fetchrow("""
                SELECT 
                    COUNT(DISTINCT customer_name) as unique_customers,
                    COUNT(DISTINCT state) as unique_states,
                    COUNT(DISTINCT business_module) as unique_modules,
                    COUNT(DISTINCT wtg_model) as unique_models
                FROM rag_embeddings
            """)
            
            return {
                'query_type': 'comparison_analysis',
                'comparison_data': dict(comparison_data),
                'success': True,
                'answer': f"Comparison overview: {comparison_data['unique_customers']} customers across {comparison_data['unique_states']} states, {comparison_data['unique_modules']} business modules, {comparison_data['unique_models']} WTG models.",
                'confidence': 1.0
            }
    
    async def _get_filter_analysis(self) -> Dict[str, Any]:
        """Get filter-based analysis"""
        # This will provide a general overview that can be filtered
        return await self._get_total_capacity()
    
    async def _get_portfolio_analysis(self) -> Dict[str, Any]:
        """Get comprehensive portfolio analysis"""
        async with db_manager.get_connection() as conn:
            # Total portfolio metrics
            portfolio_summary = await conn.fetchrow("""
                SELECT 
                    SUM(capacity) as total_capacity,
                    COUNT(DISTINCT customer_name) as total_customers,
                    COUNT(DISTINCT state) as states_covered,
                    COUNT(*) as total_projects,
                    AVG(capacity) as avg_project_size
                FROM rag_embeddings 
                WHERE capacity IS NOT NULL
            """)
            
            # Breakdown by business module
            module_breakdown = await conn.fetch("""
                SELECT 
                    business_module,
                    SUM(capacity) as total_capacity,
                    COUNT(DISTINCT customer_name) as customer_count,
                    COUNT(*) as project_count,
                    CAST((SUM(capacity) * 100.0 / (SELECT SUM(capacity) FROM rag_embeddings WHERE capacity IS NOT NULL)) AS DECIMAL(10,2)) as capacity_percentage
                FROM rag_embeddings 
                WHERE capacity IS NOT NULL AND business_module IS NOT NULL
                GROUP BY business_module 
                ORDER BY total_capacity DESC
            """)
            
            module_data = [dict(row) for row in module_breakdown]
            
            return {
                'query_type': 'portfolio_analysis',
                'portfolio_summary': dict(portfolio_summary),
                'module_breakdown': module_data,
                'success': True,
                'answer': f"Portfolio Analysis: Total capacity of {portfolio_summary['total_capacity']:.2f} MW across {portfolio_summary['total_customers']} customers in {portfolio_summary['states_covered']} states. Business module breakdown: {module_data[0]['business_module']} ({module_data[0]['capacity_percentage']:.1f}%), {module_data[1]['business_module']} ({module_data[1]['capacity_percentage']:.1f}%), {module_data[2]['business_module']} ({module_data[2]['capacity_percentage']:.1f}%).",
                'confidence': 1.0
            }
    
    async def _get_concentration_risk_analysis(self) -> Dict[str, Any]:
        """Get customer concentration risk analysis"""
        async with db_manager.get_connection() as conn:
            # Total capacity
            total_capacity = await conn.fetchval(
                "SELECT SUM(capacity) FROM rag_embeddings WHERE capacity IS NOT NULL"
            )
            
            # Top 5 customers
            top_customers = await conn.fetch("""
                SELECT 
                    customer_name,
                    SUM(capacity) as customer_capacity,
                    CAST((SUM(capacity) * 100.0 / $1) AS DECIMAL(10,2)) as percentage_of_total
                FROM rag_embeddings 
                WHERE capacity IS NOT NULL AND customer_name IS NOT NULL
                GROUP BY customer_name 
                ORDER BY customer_capacity DESC 
                LIMIT 5
            """, total_capacity)
            
            top_5_percentage = sum(row['percentage_of_total'] for row in top_customers)
            customer_data = [dict(row) for row in top_customers]
            
            # Risk assessment
            risk_level = "HIGH" if top_5_percentage > 60 else "MEDIUM" if top_5_percentage > 40 else "LOW"
            
            return {
                'query_type': 'concentration_risk',
                'total_capacity': total_capacity,
                'top_customers': customer_data,
                'top_5_concentration': top_5_percentage,
                'risk_level': risk_level,
                'success': True,
                'answer': f"Customer Concentration Risk: Top 5 customers represent {top_5_percentage:.1f}% of total capacity ({total_capacity:.2f} MW). Risk Level: {risk_level}. Top customer: {customer_data[0]['customer_name']} ({customer_data[0]['percentage_of_total']:.1f}%).",
                'confidence': 1.0
            }
    
    async def _get_geographic_analysis(self) -> Dict[str, Any]:
        """Get geographic risk and market penetration analysis"""
        async with db_manager.get_connection() as conn:
            # Geographic distribution
            geographic_breakdown = await conn.fetch("""
                SELECT 
                    state,
                    SUM(capacity) as state_capacity,
                    COUNT(DISTINCT customer_name) as customer_count,
                    COUNT(*) as project_count,
                    CAST((SUM(capacity) * 100.0 / (SELECT SUM(capacity) FROM rag_embeddings WHERE capacity IS NOT NULL)) AS DECIMAL(10,2)) as percentage_of_total
                FROM rag_embeddings 
                WHERE capacity IS NOT NULL AND state IS NOT NULL
                GROUP BY state 
                ORDER BY state_capacity DESC
            """)
            
            geographic_data = [dict(row) for row in geographic_breakdown]
            top_3_states = sum(row['percentage_of_total'] for row in geographic_data[:3])
            
            return {
                'query_type': 'geographic_analysis',
                'geographic_breakdown': geographic_data,
                'top_3_concentration': top_3_states,
                'success': True,
                'answer': f"Geographic Analysis: Operations in {len(geographic_data)} states. Top 3 states represent {top_3_states:.1f}% of capacity. Leading state: {geographic_data[0]['state']} ({geographic_data[0]['percentage_of_total']:.1f}%, {geographic_data[0]['customer_count']} customers).",
                'confidence': 1.0
            }
    
    async def _get_pipeline_analysis(self) -> Dict[str, Any]:
        """Get project pipeline analysis"""
        async with db_manager.get_connection() as conn:
            # Pipeline by phase
            pipeline_breakdown = await conn.fetch("""
                SELECT 
                    project_phase,
                    COUNT(*) as project_count,
                    SUM(capacity) as phase_capacity,
                    COUNT(DISTINCT customer_name) as customer_count
                FROM rag_embeddings 
                WHERE project_phase IS NOT NULL AND capacity IS NOT NULL
                GROUP BY project_phase 
                ORDER BY phase_capacity DESC
            """)
            
            pipeline_data = [dict(row) for row in pipeline_breakdown]
            total_pipeline_capacity = sum(row['phase_capacity'] for row in pipeline_data)
            
            return {
                'query_type': 'pipeline_analysis',
                'pipeline_breakdown': pipeline_data,
                'total_pipeline_capacity': total_pipeline_capacity,
                'success': True,
                'answer': f"Pipeline Analysis: {total_pipeline_capacity:.2f} MW across {len(pipeline_data)} phases. Largest phase: {pipeline_data[0]['project_phase']} ({pipeline_data[0]['phase_capacity']:.2f} MW, {pipeline_data[0]['project_count']} projects).",
                'confidence': 1.0
            }
    
    async def _get_technology_analysis(self) -> Dict[str, Any]:
        """Get technology mix and risk analysis"""
        async with db_manager.get_connection() as conn:
            # WTG model distribution
            model_distribution = await conn.fetch("""
                SELECT 
                    wtg_model,
                    wtg_type,
                    SUM(capacity) as model_capacity,
                    SUM(wtg_count) as total_wtg,
                    COUNT(*) as project_count,
                    CAST((SUM(capacity) * 100.0 / (SELECT SUM(capacity) FROM rag_embeddings WHERE capacity IS NOT NULL)) AS DECIMAL(10,2)) as capacity_percentage
                FROM rag_embeddings 
                WHERE wtg_model IS NOT NULL AND capacity IS NOT NULL
                GROUP BY wtg_model, wtg_type 
                ORDER BY model_capacity DESC
                LIMIT 10
            """)
            
            technology_data = [dict(row) for row in model_distribution]
            
            # Type distribution
            type_distribution = await conn.fetch("""
                SELECT 
                    wtg_type,
                    SUM(capacity) as type_capacity,
                    COUNT(*) as project_count
                FROM rag_embeddings 
                WHERE wtg_type IS NOT NULL AND capacity IS NOT NULL
                GROUP BY wtg_type 
                ORDER BY type_capacity DESC
            """)
            
            type_data = [dict(row) for row in type_distribution]
            
            return {
                'query_type': 'technology_analysis',
                'model_distribution': technology_data,
                'type_distribution': type_data,
                'success': True,
                'answer': f"Technology Mix: {len(technology_data)} WTG models deployed. Top model: {technology_data[0]['wtg_model']} ({technology_data[0]['capacity_percentage']:.1f}% of capacity). Type distribution: {type_data[0]['wtg_type']} ({type_data[0]['type_capacity']:.2f} MW).",
                'confidence': 1.0
            }
    
    async def _get_performance_comparison(self) -> Dict[str, Any]:
        """Get year-over-year performance comparison"""
        async with db_manager.get_connection() as conn:
            # Fiscal year comparison
            fy_comparison = await conn.fetch("""
                SELECT 
                    fiscalyear,
                    SUM(capacity) as fy_capacity,
                    COUNT(*) as project_count,
                    COUNT(DISTINCT customer_name) as customer_count
                FROM rag_embeddings 
                WHERE fiscalyear IS NOT NULL AND capacity IS NOT NULL
                GROUP BY fiscalyear 
                ORDER BY fiscalyear DESC
            """)
            
            fy_data = [dict(row) for row in fy_comparison]
            
            # Calculate growth if we have multiple years
            growth_rate = 0
            if len(fy_data) >= 2:
                current_year = fy_data[0]['fy_capacity']
                previous_year = fy_data[1]['fy_capacity']
                growth_rate = ((current_year - previous_year) / previous_year) * 100
            
            return {
                'query_type': 'performance_comparison',
                'fy_comparison': fy_data,
                'growth_rate': growth_rate,
                'success': True,
                'answer': f"Performance Comparison: {fy_data[0]['fiscalyear']}: {fy_data[0]['fy_capacity']:.2f} MW ({fy_data[0]['project_count']} projects), {fy_data[1]['fiscalyear']}: {fy_data[1]['fy_capacity']:.2f} MW. Growth rate: {growth_rate:.1f}%.",
                'confidence': 1.0
            }
    
    async def _get_efficiency_metrics(self) -> Dict[str, Any]:
        """Get operational efficiency metrics"""
        async with db_manager.get_connection() as conn:
            # Efficiency metrics by business module
            efficiency_metrics = await conn.fetch("""
                SELECT 
                    business_module,
                    AVG(capacity) as avg_project_size,
                    AVG(wtg_count) as avg_wtg_per_project,
                    AVG(mwg) as avg_mwg,
                    SUM(capacity)/SUM(wtg_count) as capacity_per_wtg
                FROM rag_embeddings 
                WHERE business_module IS NOT NULL AND capacity IS NOT NULL AND wtg_count IS NOT NULL
                GROUP BY business_module 
                ORDER BY avg_project_size DESC
            """)
            
            efficiency_data = [dict(row) for row in efficiency_metrics]
            
            # Overall efficiency
            overall_efficiency = await conn.fetchrow("""
                SELECT 
                    AVG(capacity) as overall_avg_project_size,
                    SUM(capacity)/SUM(wtg_count) as overall_capacity_per_wtg,
                    AVG(mwg/capacity) as capacity_utilization_ratio
                FROM rag_embeddings 
                WHERE capacity IS NOT NULL AND wtg_count IS NOT NULL AND mwg IS NOT NULL
            """)
            
            return {
                'query_type': 'efficiency_metrics',
                'module_efficiency': efficiency_data,
                'overall_metrics': dict(overall_efficiency),
                'success': True,
                'answer': f"Efficiency Metrics: Average project size: {overall_efficiency['overall_avg_project_size']:.2f} MW. Capacity per WTG: {overall_efficiency['overall_capacity_per_wtg']:.2f} MW. Most efficient module: {efficiency_data[0]['business_module']} ({efficiency_data[0]['avg_project_size']:.2f} MW avg).",
                'confidence': 1.0
            }
    
    async def _get_variance_analysis(self) -> Dict[str, Any]:
        """Get variance analysis for execution risk"""
        async with db_manager.get_connection() as conn:
            # Variance by customer
            customer_variance = await conn.fetch("""
                SELECT 
                    customer_name,
                    AVG(wtg_count_deviation) as avg_wtg_deviation,
                    AVG(mwg_deviation) as avg_mwg_deviation,
                    COUNT(*) as project_count,
                    ABS(AVG(wtg_count_deviation)) + ABS(AVG(mwg_deviation)) as total_variance_score
                FROM rag_embeddings 
                WHERE customer_name IS NOT NULL AND wtg_count_deviation IS NOT NULL AND mwg_deviation IS NOT NULL
                GROUP BY customer_name 
                ORDER BY total_variance_score DESC
                LIMIT 10
            """)
            
            # Variance by state
            state_variance = await conn.fetch("""
                SELECT 
                    state,
                    AVG(wtg_count_deviation) as avg_wtg_deviation,
                    AVG(mwg_deviation) as avg_mwg_deviation,
                    COUNT(*) as project_count
                FROM rag_embeddings 
                WHERE state IS NOT NULL AND wtg_count_deviation IS NOT NULL AND mwg_deviation IS NOT NULL
                GROUP BY state 
                ORDER BY ABS(AVG(wtg_count_deviation)) + ABS(AVG(mwg_deviation)) DESC
            """)
            
            customer_data = [dict(row) for row in customer_variance]
            state_data = [dict(row) for row in state_variance]
            
            return {
                'query_type': 'variance_analysis',
                'customer_variance': customer_data,
                'state_variance': state_data,
                'success': True,
                'answer': f"Variance Analysis: Highest variance customer: {customer_data[0]['customer_name']} (WTG deviation: {customer_data[0]['avg_wtg_deviation']:.2f}, MWG deviation: {customer_data[0]['avg_mwg_deviation']:.2f}). Highest variance state: {state_data[0]['state']}.",
                'confidence': 1.0
            }
    
    async def _get_business_unit_performance(self) -> Dict[str, Any]:
        """Get business unit performance analysis"""
        async with db_manager.get_connection() as conn:
            # Business unit ranking
            unit_performance = await conn.fetch("""
                SELECT 
                    business_module,
                    SUM(capacity) as total_capacity,
                    COUNT(DISTINCT customer_name) as customer_count,
                    COUNT(*) as project_count,
                    AVG(capacity) as avg_project_size,
                    SUM(mwg) as total_mwg,
                    RANK() OVER (ORDER BY SUM(capacity) DESC) as capacity_rank,
                    RANK() OVER (ORDER BY COUNT(DISTINCT customer_name) DESC) as customer_rank
                FROM rag_embeddings 
                WHERE business_module IS NOT NULL AND capacity IS NOT NULL
                GROUP BY business_module 
                ORDER BY total_capacity DESC
            """)
            
            performance_data = [dict(row) for row in unit_performance]
            
            return {
                'query_type': 'business_unit_performance',
                'unit_performance': performance_data,
                'success': True,
                'answer': f"Business Unit Performance: Top performer: {performance_data[0]['business_module']} ({performance_data[0]['total_capacity']:.2f} MW, {performance_data[0]['customer_count']} customers). Second: {performance_data[1]['business_module']} ({performance_data[1]['total_capacity']:.2f} MW).",
                'confidence': 1.0
            }

# Global statistical query handler
statistical_handler = StatisticalQueryHandler()