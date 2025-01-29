import sqlparse
from sqllineage.runner import LineageRunner
import pandas as pd
import re
from openai import OpenAI
import os
from functools import lru_cache
from typing import List, Dict, Any
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

class SQLColumnDescriptionGenerator:
    def __init__(self, sql_queries: str, openai_api_key: str):
        self.sql_queries = sql_queries
        self.openai_client = OpenAI(api_key=openai_api_key)  # Initialize OpenAI client with API key
        self.column_info = {}
        self.description_cache = {}

    def parse_sql_context(self, query: str) -> Dict[str, Any]:
        """Extract detailed context from SQL query"""
        try:
            parsed = sqlparse.parse(query)[0]
            context = {
                'full_query': query,
                'query_type': parsed.get_type(),
                'tables': [],
                'where_conditions': '',
                'joins': [],
                'group_by': '',
                'order_by': ''
            }
            
            # Extract table names and conditions
            for token in parsed.tokens:
                if token.is_group:
                    if 'JOIN' in token.value.upper():
                        context['joins'].append(token.value)
                    elif 'WHERE' in token.value.upper():
                        context['where_conditions'] = token.value
                    elif 'GROUP BY' in token.value.upper():
                        context['group_by'] = token.value
                    elif 'ORDER BY' in token.value.upper():
                        context['order_by'] = token.value

            return context
        except Exception as e:
            print(f"Error parsing SQL context: {e}")
            return {'full_query': query}

    def detect_transformations(self, query: str) -> List[str]:
        """Detect SQL transformations with detailed patterns"""
        transformations = []
        
        patterns = {
            'Aggregation': [
                r'\b(SUM|AVG|COUNT|MAX|MIN)\(',
                r'\bGROUP BY\b',
                r'\bHAVING\b'
            ],
            'Window Function': [
                r'\bOVER\s*\(',
                r'\bPARTITION BY\b',
                r'\b(ROW_NUMBER|RANK|DENSE_RANK|LAG|LEAD)\s*\('
            ],
            'Type Conversion': [
                r'\bCAST\s*\(',
                r'\bCONVERT\s*\(',
                r'\bTRY_CAST\s*\('
            ],
            'Text Operation': [
                r'\b(CONCAT|SUBSTRING|REPLACE|TRIM|UPPER|LOWER)\s*\(',
                r'\bLIKE\b'
            ],
            'Date Operation': [
                r'\b(DATEADD|DATEDIFF|DATETRUNC|DATE_TRUNC)\s*\(',
                r'\bDATEPART\s*\('
            ],
            'Case Statement': [
                r'\bCASE\b.*?\bEND\b',
                r'\bIIF\s*\('
            ],
            'Join Operation': [
                r'\b(INNER|LEFT|RIGHT|FULL|CROSS)\s+JOIN\b'
            ]
        }
        
        for category, pattern_list in patterns.items():
            if any(re.search(pattern, query, re.IGNORECASE) for pattern in pattern_list):
                transformations.append(category)
        
        return list(set(transformations))

    @lru_cache(maxsize=1000)
    def generate_column_description(self, column_signature: str, context: str) -> str:
        """Generate column description using GPT-4 with caching"""
        try:
            prompt = f"""
            Generate a precise, non-repetitive technical description for this SQL column:

            {context}

            Requirements:
            1. Explain both business meaning and technical derivation
            2. Describe key transformations and their purpose
            3. Note important filters or conditions
            4. Highlight data quality considerations
            5. Keep it concise - no repetition
            6. Use technical language appropriate for data documentation
            7. Maximum 3 sentences
            """

            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert SQL analyst providing technical column documentation."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            description = response.choices[0].message.content.strip()
            return self.validate_description(description)
            
        except Exception as e:
            return f"Error generating description: {str(e)}"

    def validate_description(self, description: str) -> str:
        """Validate and clean up generated descriptions"""
        # Remove common repetitive phrases
        repetitive_phrases = [
            "as mentioned above",
            "as noted",
            "it is worth noting that",
            "it should be noted that"
        ]
        
        for phrase in repetitive_phrases:
            description = description.replace(phrase, "")
        
        # Ensure proper ending
        if not description.endswith('.'):
            description += '.'
            
        return description.strip()

    def process_query(self, query):
        """Process a single SQL query"""
        results = []
        try:
            # Parse SQL context
            context = self.parse_sql_context(query)
            
            # Get column lineage
            analyzer = LineageRunner(query)
            lineage_result = analyzer.get_column_lineage()
            
            # Process each column
            for result in lineage_result:
                try:
                    # Handle different result formats by converting result to a tuple
                    result_tuple = tuple(result)  # Ensure result is a tuple
                    
                    if len(result_tuple) == 2:  # For (source, target) structure
                        source, target = result_tuple
                    elif len(result_tuple) > 2:  # For structures with more than 2 values
                        source, target = result_tuple[0], result_tuple[1]
                    else:
                        print(f"Unexpected format in result: {result_tuple}")
                        continue
                    
                    source = str(source)
                    target = str(target)
                    
                    # Build column context
                    column_context = {
                        'name': target,
                        'source_columns': [source],
                        'transformations': self.detect_transformations(query),
                        'sql_context': context
                    }
                    
                    # Generate description
                    description_context = json.dumps(column_context, indent=2)
                    description = self.generate_column_description(target, description_context)
                    
                    # Store results
                    self.column_info[target] = {
                        **column_context,
                        'description': description
                    }
                    
                except Exception as e:
                    print(f"Error processing column {result}: {e}")
                    continue

        except Exception as e:
            print(f"Error processing query: {e}")

        return results

    def analyze_columns(self):
        """Analyze all columns from SQL queries"""
        queries = sqlparse.split(self.sql_queries)
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(self.process_query, query): query for query in queries}
            for future in as_completed(futures):
                try:
                    result = future.result()
                except Exception as e:
                    print(f"Error processing query: {e}")

    def generate_report(self) -> pd.DataFrame:
        """Generate comprehensive report"""
        report_data = []
        
        for column, info in self.column_info.items():
            report_data.append({
                'Column Name': column,
                'Source Columns': ', '.join(info['source_columns']),
                'Transformations': ', '.join(info['transformations']),
                'Description': info['description']
            })
            
        return pd.DataFrame(report_data)

    def export_report(self, filename: str = 'column_descriptions.xlsx'):
        """Export report to Excel/CSV"""
        df = self.generate_report()
        try:
            df.to_excel(filename, index=False)
            print(f"Report exported to {filename}")
        except ImportError:
            print("Error: 'openpyxl' library is not installed. Install it using 'pip install openpyxl'.")
        except Exception as e:
            csv_filename = filename.replace('.xlsx', '.csv')
            df.to_csv(csv_filename, index=False)
            print(f"Fallback: Report exported to {csv_filename} due to error: {e}")
