
import os

file_path = r'f:\Моделювання\R1\frontend\src\views\Inventory\ProductTabs\SpecificationTab.vue'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

script_start = content.find('<script')
script_end = content.find('</script>')
if script_start != -1 and script_end != -1:
    script = content[script_start:script_end]
    open_braces = script.count('{')
    close_braces = script.count('}')
    print(f"Braces in script: {open_braces} open, {close_braces} close")
    
    open_parens = script.count('(')
    close_parens = script.count(')')
    print(f"Parens in script: {open_parens} open, {close_parens} close")

    open_brackets = script.count('[')
    close_brackets = script.count(']')
    print(f"Brackets in script: {open_brackets} open, {close_brackets} close")
else:
    print("Script tags not found")
