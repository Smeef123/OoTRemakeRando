"""Parse every SoH randomizer source that defines locations (location_list.cpp, Shuffle*.cpp, ...) into JSON.
usage: python -I soh_locations.py <randomizer dir> <out.json>"""
import re, json, sys, glob, os
rows, seen = [], set()
for p in sorted(glob.glob(os.path.join(sys.argv[1], '*.cpp'))):
    src = open(p, encoding='utf-8').read()
    for m in re.finditer(r'locationTable\[(RC_\w+)\]\s*=\s*Location::(\w+)\((.*?)\);', src, re.S):
        if m.group(1) in seen: continue
        seen.add(m.group(1))
        args = [a.strip() for a in re.split(r',(?=(?:[^"]*"[^"]*")*[^"]*$)', m.group(3))]
        rows.append({'rc': m.group(1), 'kind': m.group(2), 'args': args, 'src': os.path.basename(p)})
json.dump(rows, open(sys.argv[2], 'w'), indent=0)
print(len(rows))
