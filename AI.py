import google.generativeai as genai
import re

class CodeFormatter:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def format_code(self, code: str) :
        prompt = f"Format the following code and return only the formatted code without adding any additional comments, text, or descriptions. Only return the codeand at the top of the code add comment RDF Studio AI has Formatted code successfully:\n\n{code}"
        response = self.model.generate_content(prompt)

        # Extract the formatted code, remove any extra content
        formatted_code = response.text.strip()
        
        # Clean up extra markers or comments added by the model
        formatted_code = re.sub(r"```[\w]*\n", '', formatted_code)
        formatted_code = re.sub(r"\n```", '', formatted_code)

        return formatted_code

    
class ImproveAlgorithm:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def improve_algorithm(self, algorithm_code: str) -> str:
        try:
            # Construct the precise prompt
            prompt = (f"Improve the following algorithm and return only the improved code. "
                      f"Do not add any explanations or comments. Only return the improved code and at the top of the code add comment RDF Studio AI has Improved Algorithm successfully:\n\n{algorithm_code}")
            
            # Generate content using the model
            response = self.model.generate_content(prompt)

            # Extract the improved code, remove any extra text
            improved_algo = response.text.strip()
            
            # Clean up extra markers or comments added by the model
            improved_algo = re.sub(r"```[\w]*\n", '', improved_algo)
            improved_algo = re.sub(r"\n```", '', improved_algo)

            return improved_algo
        
        except Exception as e:
            # Handle exceptions and return an appropriate message
            return f"An error occurred while enhancing the algorithm: {str(e)}"

        
class CodeImprover:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def improve_names(self, code: str):
        prompt = (
            f"Improve the variable and function names of the given code. Return only the improved code without any descriptions or explanationsand at the top of the code add comment RDF Studio AI has Improved Variable and Functions name successfully:\n\n{code}"
        )
        response = self.model.generate_content(prompt)

        # Extract improved code, remove any extra content
        improved_code = response.text.strip()
        improved_code = re.sub(r"```[\w]*\n", '', improved_code)
        improved_code = re.sub(r"\n```", '', improved_code)

        return improved_code

    
class CommentAdder:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def add_comments(self, code: str) -> str:
        # Prepare prompt to add comments without any extra content
        prompt = f"Add explanatory comments to each line of the following code and return only the code with comments. Do not include any code block markers or extra text and at the top of the code add comment RDF Studio AI has commented code successfully:\n\n{code}"
        response = self.model.generate_content(prompt)
        
        # Extract the commented code, clean up extra content
        commented_code = response.text.strip()
        commented_code = re.sub(r"```[\w]*\n", '', commented_code)
        commented_code = re.sub(r"\n```", '', commented_code)

        return commented_code

    
class ImprovedCode:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def improve_code(self, code: str) :
        prompt = f"Improve the following code and return only the improved code. Do not add any  descriptions. Only return the improved code and at the top of the code add comment RDF Studio AI has Improved code successfully :\n\n{code}"
        response = self.model.generate_content(prompt) 

        # Extract the improved code, clean up extra text
        improved_code = response.text.strip()
        improved_code = re.sub(r"```[\w]*\n", '', improved_code)
        improved_code = re.sub(r"\n```", '', improved_code)

        return improved_code
