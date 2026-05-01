import sys

file_path = r'f:\Моделювання\R1\frontend\src\router\index.js'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_route = """                {
                    path: '/crm/insights',
                    name: 'crm-insights',
                    component: () => import('@/views/CRM/CrmInsights.vue'),
                    meta: { title: 'CRM Insights 2026' }
                },"""

if "path: '/crm/analytics'," in content:
    parts = content.split("path: '/crm/analytics',")
    # Find the end of this route block
    sub_parts = parts[1].split("},", 1)
    new_content = parts[0] + "path: '/crm/analytics'," + sub_parts[0] + "}," + "\n" + new_route + sub_parts[1]
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Success")
else:
    print("Target not found")
