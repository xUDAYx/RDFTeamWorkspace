import re
import json
import os
from PyQt6.QtWidgets import QPlainTextEdit
from terminal_widget import TerminalWidget
from mobile_view import MobileView
from PyQt6.Qsci import QsciScintilla
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class RuleEngine:
    def __init__(self, tab_widget, rules, mobile_view):
        self.tab_widget = tab_widget
        self.rules = rules
        self.mobile_view = mobile_view

    def validate_file(self):
        try:
            current_widget = self.tab_widget.currentWidget()
            if current_widget:
                self.validate_and_apply_rules(current_widget.file_path)
            else:
                current_widget.findChild(TerminalWidget).write("No file opened to validate.\n")
        except Exception as e:
            print(f"Error validating file: {e}")
            logging.error(f"Error validating file: {e}")

    def validate_and_apply_rules(self, file_path):
        try:
            file_name = os.path.basename(file_path)
            file_base_name = os.path.splitext(file_name)[0]

            rule_file = None
            for key in self.rules:
                if file_base_name.endswith(key):
                    rule_file = self.rules[key]
                    break

            if rule_file:
                with open(rule_file, 'r') as file:
                    rules = json.load(file)

                current_widget = self.tab_widget.currentWidget()
                editor = current_widget.findChild(QsciScintilla)
                if editor:
                    editor.setObjectName("codeEditor")
                    content = editor.text()
                    errors = self.apply_rules(content, rules)
                    terminal = current_widget.findChild(TerminalWidget)
                    if errors:
                        for error in errors:
                            terminal.write(f"Error: {error}\n", color="red")
                        editor.setStyleSheet("#codeEditor { border: 1px solid red; }")
                    else:
                        terminal.write("No errors found.\n", color="white")
                        editor.setStyleSheet("#codeEditor { border: none; }")
                else:
                    terminal.write("Editor not found.\n", color="yellow")

            else:
                terminal.write("No rule file found for this file.\n")
        except Exception as e:
            print(f"Error validating and applying rules: {e}")
            logging.error(f"Error validating and applying rules: {e}")

    def apply_rules(self, content, rules):
        try:
            errors = []
            table_rule_present = False
            section_rule_present = False
            get_rule_present = False
            table_rule = None
            section_rule = None
            get_rule = None

            lines = content.splitlines()

            for rule in rules["rules"]:
                # Check for specific descriptions and set flags
                if rule["description"] == "Table tag should be present":
                    table_rule_present = True
                    table_rule = rule
                    continue
                elif rule["description"] == "File must contain a table tag with class 'section'":
                    section_rule_present = True
                    section_rule = rule
                    continue
                elif rule["description"] == "PHP Rule: only call getYYY() functions":
                    get_rule_present = True
                    get_rule = rule
                    continue

                # Apply other rules
                # Apply other rules
                for i, line in enumerate(lines, start=1):
                    if re.search(rule["pattern"], line):
                        errors.append(f"Line {i}: {rule['description']}")

            # Check table rules
            if table_rule_present and not re.search(table_rule["pattern"], content):
                errors.append(table_rule["description"])

            # Check section rules
            if section_rule_present and not re.search(section_rule["pattern"], content):
                errors.append(section_rule["description"])

            if get_rule_present and not re.search(get_rule["pattern"], content):
                errors.append(get_rule["description"])

            return errors
        except Exception as e:
            return [str(e)]
