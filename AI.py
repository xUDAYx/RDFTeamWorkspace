import google.generativeai as genai
import re

class CodeFormatter:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def format_code(self, code: str) :
        prompt = f"Format the following  code and return only the formatted code and at the top of the line add comment that 'RDF Studio AI has formatted your code Successfully' and dont add comment '''php '''.:\n\n{code}"
        response = self.model.generate_content(prompt)
        
        # Attempt to remove any extra text that might have been added by the model
        formatted_code = response.text

        formatted_code = re.sub(r"```[\w]*\n", '', formatted_code)
        formatted_code = re.sub(r"\n```", '', formatted_code)


        # If necessary, you can apply additional rules to further refine the output
        # For example, you might check for code-specific patterns, comments, or remove unwanted lines

        return formatted_code
    
class ImproveAlgorithm:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def improve_algorithm(self, algorithm_code: str) -> str:
        try:
            # Construct the prompt for the generative model
            prompt = (f"Improve the following algorithm and return only the improved code. "
                      f"At the top of the line, add a comment that 'RDF Studio AI has improved your algorithm successfully' "
                      f"and don't add a comment '''python'''.\n\n{algorithm_code}")
            
            # Generate content using the model
            response = self.model.generate_content(prompt)
            
            # Extract the generated text
            improved_algo = response.text
            
            # Clean up any extra formatting or comments that might have been added by the model
            improved_algo = re.sub(r"```[\w]*\n", '', improved_algo)
            improved_algo = re.sub(r"\n```", '', improved_algo)

            return improved_algo
        
        except Exception as e:
            # Handle exceptions and return a message or an empty string
            return f"An error occurred while enhancing the algorithm: {str(e)}"