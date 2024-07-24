import subprocess
import os
import jsbeautifier
import json
from bs4 import BeautifulSoup
import tempfile

class CodeFormatter:
    @staticmethod
    def format_html(html_code):
        soup = BeautifulSoup(html_code, 'html.parser')
        return soup.prettify()

    @staticmethod
    def format_php(php_code):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".php") as temp_file:
            temp_file.write(php_code.encode('utf-8'))
            temp_file_path = temp_file.name

        process = subprocess.run(
            ['php', 'tools/php-cs-fixer/vendor/bin/php-cs-fixer', 'fix', temp_file_path],
            capture_output=True,
            text=True
        )

        with open(temp_file_path, 'r', encoding='utf-8') as temp_file:
            formatted_code = temp_file.read()

        os.remove(temp_file_path)
        return formatted_code

    @staticmethod
    def format_js(js_code):
        options = jsbeautifier.default_options()
        formatted_code = jsbeautifier.beautify(js_code, options)
        return formatted_code

    @staticmethod
    def format_json(json_code):
        try:
            parsed_json = json.loads(json_code)
            formatted_code = json.dumps(parsed_json, indent=4)
            return formatted_code
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to format JSON: {e}")

    @staticmethod
    def format_code(file_path, code):
        if file_path.endswith("UI.php"):
            return CodeFormatter.format_html(code)
        elif file_path.endswith("BVO.php") or file_path.endswith("BW.php"):
            return CodeFormatter.format_php(code)
        elif file_path.endswith(".js"):
            return CodeFormatter.format_js(code)
        elif file_path.endswith(".json"):
            return CodeFormatter.format_json(code)
        else:
            raise Exception("Unsupported file type")