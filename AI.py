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