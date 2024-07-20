# autocompleter.py

from PyQt6.Qsci import QsciAPIs
import keyword
import builtins
import json

class AutoCompleter:
    def __init__(self, lexer):
        self.apis = QsciAPIs(lexer)

    def add_python_apis(self):
        # Add Python keywords
        for kw in keyword.kwlist:
            self.apis.add(kw)

        # Add Python built-in functions
        for func in dir(builtins):
            if not func.startswith('_'):
                self.apis.add(func)

    def add_custom_apis(self, words):
        for word in words:
            self.apis.add(word)

    def prepare(self):
        self.apis.prepare()

def get_autocompleter(lexer, language):
    completer = AutoCompleter(lexer)
    
    with open('auto_complete','keywords.json', 'r') as f:
        suggestions = json.load(f)
    
    if language == 'python':
        completer.add_python_apis()
    elif language in suggestions:
        completer.add_custom_apis(suggestions[language])

    completer.prepare()
    return completer
