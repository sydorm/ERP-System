
import sys

path = r'f:\Моделювання\R1\frontend\src\views\Inventory\ProductTabs\SpecificationTab.vue'
with open(path, 'rb') as f:
    content = f.read()

# Replace any weird bytes if they exist (though unlikely)
# But more importantly, rewrite as clean UTF-8
text = content.decode('utf-8', errors='ignore')

with open(path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(text)

print("File re-written as clean UTF-8")
