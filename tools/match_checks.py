"""Match Ship of Harkinian checks to the remake's item placements.

usage: python -I match_checks.py <repo dir>
reads  soh_locations.json, remake_checks.json, data/manual_map.json
writes data/check_map.json  {rc_enum: {folder, hash, actor, how}}   and prints what is left unmatched.

Automatic rule: inside one area, a SoH check whose vanilla item maps to a remake actor that appears exactly once
(among that area's chests/freestanding spots) and exactly once among the area's SoH checks is matched to it.
Everything else comes from data/manual_map.json (hand-checked: room index, position, events)."""
import json, os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from remake_items import CHEST, PROGRESSIVE

root = sys.argv[1]
J = lambda p: json.load(open(os.path.join(root, p), encoding='utf-8'))

AREA = {  # SoH check prefix -> remake Banc folder
    'KF': 'KokiriForest', 'LW': 'LostWood', 'SFM': 'SacredForestMeadow', 'HF': 'HyruleField', 'LLR': 'HyruleField',
    'MARKET': 'Market', 'TOT': 'Market', 'HC': 'HyruleCastle', 'KAK': 'KakarikoVillage', 'GRAVEYARD': 'Graveyard',
    'DMT': 'DeathMountainTrail', 'GC': 'GoronCity', 'DMC': 'DeathMountainCrater', 'ZR': 'ZoraRiver', 'ZD': 'ZoraDomain',
    'ZF': 'ZoraFountain', 'LH': 'HyruleField', 'GV': 'GerudoValley', 'GF': 'GerudoFortress', 'WASTELAND': 'HountedWasteland',
    'COLOSSUS': 'DesertColossus', 'OGC': 'GanonCastle', 'DEKU_TREE': 'InsideTheDekuTree', 'DODONGOS_CAVERN': 'DodongoCavern',
    'JABU_JABUS_BELLY': 'InsideJabuJabuBelly', 'FOREST_TEMPLE': 'ForestTemple', 'FIRE_TEMPLE': 'FireTemple',
    'WATER_TEMPLE': 'WaterTemple', 'SPIRIT_TEMPLE': 'SpiritTemple', 'SHADOW_TEMPLE': 'ShadowTemple',
    'BOTTOM_OF_THE_WELL': 'BottomOfTheWell', 'ICE_CAVERN': 'IceCavern', 'GERUDO_TRAINING_GROUND': 'GerudoTrainingGround',
    'GANONS_CASTLE': 'InsideGanonCastle', 'GANONS_TOWER': 'InsideGanonCastle',
}
HOLDERS = ('Obj_TBox', 'Obj_HrlCity_Shop_TBox', 'HeartPieceAnchor')  # chests and freestanding heart pieces


def area_of(rc):
    p = rc[3:]
    best = max((k for k in AREA if p == k or p.startswith(k + '_')), key=len, default=None)
    return AREA.get(best)


def actor_of(rg):
    return CHEST.get(rg) or (PROGRESSIVE.get(rg) or [None])[0]


soh = [a for a in J('soh_locations.json') if 'RCQUEST_MQ' not in a['args'] and a['kind'] in ('Chest', 'Collectable')]
remake = {}
for x in J('remake_checks.json'):
    if 'Drop__DropActor' not in x['dynamic'] or not x['gyaml'].startswith(HOLDERS) and x['dynamic']['Drop__DropActor'] not in ('Obj_Heart_Piece', 'Item_Dungeon_SmallKey', 'Obj_Dungeon_SmallKey'):
        continue
    folder = x['file'].split('/')[1]
    remake.setdefault((folder, x['hash']), x)

manual = J('data/manual_map.json') if os.path.exists(os.path.join(root, 'data/manual_map.json')) else {}
out, used = {}, set()
for rc, m in manual.items():
    if m.get('hash') is None:
        continue
    key = (m['folder'], m['hash'])
    out[rc] = {'folder': m['folder'], 'hash': m['hash'], 'how': 'manual', 'note': m.get('note', ''),
               'mode': m.get('mode', 'drop'), 'keep_event': m.get('keep_event', False)}
    used.add(key)

ev_path = os.path.join(root, 'data/event_map.json')  # NPC gifts, songs, rewards: item grants in event flows
for rc, m in (json.load(open(ev_path)) if os.path.exists(ev_path) else {}).items():
    out[rc] = dict(m, how='event')

by_area = collections.defaultdict(list)
for a in soh:
    if a['rc'] in manual:
        continue
    f = area_of(a['rc'])
    rg = [x for x in a['args'] if x.startswith('RG_')]
    by_area[f].append((a['rc'], actor_of(rg[-1]) if rg else None))
for f, checks in by_area.items():
    if f is None:
        continue
    here = [(k, x) for k, x in remake.items() if k[0] == f and k not in used]
    cnt_r = collections.Counter(x['dynamic']['Drop__DropActor'] for k, x in here)
    cnt_s = collections.Counter(act for rc, act in checks)
    for rc, act in checks:
        if act and cnt_r[act] == 1 and cnt_s[act] == 1:
            k, x = next((k, x) for k, x in here if x['dynamic']['Drop__DropActor'] == act)
            out[rc] = {'folder': f, 'hash': x['hash'], 'how': 'auto', 'note': act}
            used.add(k)

os.makedirs(os.path.join(root, 'data'), exist_ok=True)
json.dump(out, open(os.path.join(root, 'data/check_map.json'), 'w'), indent=1)
left_s = [a['rc'] for a in soh if a['rc'] not in out and a['rc'] not in manual]
left_r = [k for k in remake if k not in used]
print(f'matched {len(out)} ({sum(v["how"] == "manual" for v in out.values())} manual), '
      f'SoH chest/freestanding checks unmatched {len(left_s)}, remake spots unmatched {len(left_r)}')
