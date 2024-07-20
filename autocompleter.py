# autocompleter.py

from PyQt6.Qsci import QsciAPIs
import keyword
import builtins

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
        
        if language == 'python':
            completer.add_python_apis()
        elif language == 'html':
            completer.add_custom_apis(['html', 'head', 'body', 'div', 'span', 'p', 'a', 'img', 'table', 'tr', 'td', 'th'])
        elif language == 'javascript':
            completer.add_custom_apis(['function', 'var', 'let', 'const', 'if', 'else', 'for', 'while', 'return', 'console.log', 'document', 'window'])
        elif language == 'css':
            completer.add_custom_apis(['color', 'background-color', 'font-size', 'margin', 'padding', 'border'])
        elif language == 'php':
            completer.add_custom_apis(['<?php', '?>', 'echo', 'function', 'class', 'public', 'private', 'protected', '$_GET', '$_POST', 'if', 'else', 'foreach', 'while'])
        elif language == 'json':
            completer.add_custom_apis(['{', '}', '[', ']', ':', '"'])

        completer.prepare()
        return completer.apis