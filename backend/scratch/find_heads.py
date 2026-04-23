import os
import re

versions_dir = r'g:\Моделювання\R1\backend\alembic\versions'
files = [f for f in os.listdir(versions_dir) if f.endswith('.py')]

revisions = {}
children = {}

for f in files:
    path = os.path.join(versions_dir, f)
    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()
        rev_match = re.search(r"revision(?:\s*:\s*str)?\s*=\s*['\"]([^'\"]+)['\"]", content)
        down_match = re.search(r"down_revision(?:\s*:\s*(?:Union\[str, Sequence\[str\], None\]|Union\[str, None\]|str|None))?\s*=\s*(['\"]([^'\"]+)['\"]|\(([^)]+)\)|None)", content)
        
        if rev_match:
            rev = rev_match.group(1)
            revisions[rev] = f
            
            if down_match:
                down = down_match.group(1)
                if down == 'None':
                    down = None
                elif down.startswith('('):
                    # Tuple of heads
                    down = [d.strip().strip("'").strip('"') for d in down[1:-1].split(',')]
                else:
                    down = down_match.group(2)
                
                if down:
                    if isinstance(down, list):
                        for d in down:
                            children.setdefault(d, []).append(rev)
                    else:
                        children.setdefault(down, []).append(rev)

heads = [rev for rev in revisions if rev not in children]
print(f"Heads found: {heads}")
for h in heads:
    print(f"  {h} -> {revisions[h]}")
