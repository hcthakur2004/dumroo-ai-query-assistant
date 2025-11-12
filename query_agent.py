"""
LangChain-powered query agent for natural language data queries.
Uses Google Gemini to generate and execute pandas code.
"""
import os
import pandas as pd
import re
from langchain_google_genai import ChatGoogleGenerativeAI


class QueryAgent:
    """
    Natural language query agent using LangChain and Google Gemini.
    
    This agent can process natural language questions about student data
    and return structured results from a pandas DataFrame.
    """
    
    def __init__(self, gemini_api_key, model="gemini-2.0-flash", temperature=0):
        """
        Initialize the query agent.
        
        Args:
            gemini_api_key (str): Google Gemini API key
            model (str): Gemini model to use (default: gemini-2.0-flash)
            temperature (float): Model temperature (default: 0 for deterministic)
        """
        self.gemini_api_key = gemini_api_key
        self.model = model
        self.temperature = temperature
        self.llm = None
        self.df = None
    
    def setup_agent(self, dataframe):
        """
        Set up the LLM with the given data.
        
        Args:
            dataframe (pd.DataFrame): The filtered student data
        """
        self.df = dataframe
        
        # Initialize Google Gemini LLM
        self.llm = ChatGoogleGenerativeAI(
            google_api_key=self.gemini_api_key,
            model=self.model,
            temperature=self.temperature
        )
    
    def query(self, question):
        """
        Process a natural language query and return results.
        
        Args:
            question (str): Natural language question
            
        Returns:
            dict: Dictionary with 'success', 'result', and optional 'error' keys
        """
        if self.llm is None:
            return {
                "success": False,
                "error": "LLM not initialized. Call setup_agent() first."
            }
        
        if not question or not question.strip():
            return {
                "success": False,
                "error": "Empty query provided."
            }
        
        try:
            # Generate Python code to answer the question
            code = self._generate_code(question)
            
            # Execute the code
            result = self._execute_code(code)
            
            return {
                "success": True,
                "result": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Query processing error: {str(e)}"
            }
    
    def _generate_code(self, question):
        """
        Generate Python code to answer the question.
        
        Args:
            question (str): User's question
            
        Returns:
            str: Python code to execute
        """
        prompt = f"""You are a Python pandas expert. Given a pandas DataFrame called 'df' with the following columns:
{', '.join(self.df.columns.tolist())}

DataFrame info:
- Total rows: {len(self.df)}
- 'date' column is datetime format
- 'homework_submitted' contains 'Yes' or 'No'
- 'class' contains grade numbers (8, 9, etc.)
- 'region' contains region names

Question: {question}

Write Python code to answer this question. The code should:
1. Use the DataFrame 'df' (already loaded)
2. Store the result in a variable called 'result'
3. Format the result clearly (e.g., list, count, string)
4. Be a single expression or simple statement

Return ONLY the Python code, no explanations. Example format:
result = df[df['homework_submitted'] == 'No']['student_name'].tolist()
"""
        
        response = self.llm.invoke(prompt)
        code = response.content.strip()
        
        # Extract code from markdown code blocks if present
        if '```python' in code:
            code = re.search(r'```python\n(.+?)\n```', code, re.DOTALL).group(1)
        elif '```' in code:
            code = re.search(r'```\n(.+?)\n```', code, re.DOTALL).group(1)
        
        return code.strip()
    
    def _execute_code(self, code):
        """
        Execute Python code safely and return the result.
        
        Args:
            code (str): Python code to execute
            
        Returns:
            str: Formatted result
        """
        # Create a safe execution environment
        local_vars = {'df': self.df, 'pd': pd}
        
        try:
            # Execute the code
            exec(code, {}, local_vars)
            result = local_vars.get('result', 'No result generated')
            
            # Format the result
            if isinstance(result, pd.DataFrame):
                if len(result) == 0:
                    return "No results found."
                # Convert to markdown table for better display
                return result.to_markdown(index=False)
            elif isinstance(result, pd.Series):
                return result.to_string()
            elif isinstance(result, list):
                if len(result) == 0:
                    return "No results found."
                # Format list items with bullet points
                return "\n".join(f"• {item}" for item in result)
            elif isinstance(result, (int, float)):
                return f"**Result:** {result}"
            else:
                return str(result)
        except Exception as e:
            raise Exception(f"Code execution error: {str(e)}\nCode: {code}")
    
    def get_data_summary(self):
        """
        Get a summary of the current dataset.
        
        Returns:
            dict: Summary statistics about the dataset
        """
        if self.df is None:
            return {"error": "No data loaded"}
        
        return {
            "total_students": len(self.df),
            "classes": self.df['class'].unique().tolist(),
            "regions": self.df['region'].unique().tolist(),
            "homework_submitted_count": len(self.df[self.df['homework_submitted'] == 'Yes']),
            "homework_not_submitted_count": len(self.df[self.df['homework_submitted'] == 'No']),
            "average_quiz_score": round(self.df['quiz_score'].mean(), 2),
            "date_range": {
                "start": self.df['date'].min().strftime('%Y-%m-%d'),
                "end": self.df['date'].max().strftime('%Y-%m-%d')
            }
        }


def create_query_agent(gemini_api_key, dataframe, model="gemini-2.0-flash"):
    """
    Factory function to create and set up a query agent.
    
    Args:
        gemini_api_key (str): Google Gemini API key
        dataframe (pd.DataFrame): The filtered student data
        model (str): Gemini model to use
        
    Returns:
        QueryAgent: Configured query agent ready to process queries
    """
    agent = QueryAgent(gemini_api_key, model=model)
    agent.setup_agent(dataframe)
    return agent
