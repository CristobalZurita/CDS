#!/usr/bin/env python3
"""
Añade el bloque `image` a cada instrument en src/assets/data/instruments.json
"""
import json
from pathlib import Path

p = Path('src/assets/data/instruments.json')
if not p.exists():
    print('File not found:', p)
    raise SystemExit(1)

with p.open('r', encoding='utf-8') as f:
    data = json.load(f)

instruments = data.get('instruments', [])
count_added = 0
for instr in instruments:
    if 'image' not in instr:
        instr['image'] = {'url': None, 'status': 'pending'}
        count_added += 1
    else:
        # ensure keys exist
        im = instr['image']
        if 'url' not in im:
            im['url'] = None
        if 'status' not in im:
            im['status'] = 'pending'

with p.open('w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ image block added/validated for {count_added} instruments")
