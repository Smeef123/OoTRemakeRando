"""Make the generated build inputs from the Ship of Harkinian checkout (soh-src), so this repository holds none of
SoH's code. Everything written here goes to build/ (not in git).

usage: python -I tools/prepare_soh.py
  build/gen/fill_remake.cpp      SoH's fill.cpp + one call to Remake_LockUnmapped (gen/remake_lock.cpp)
  build/gen/locations_gen.cpp    SoH's Register*Locations functions from its Shuffle*.cpp, without the game code
  build/gen/Lang.cpp             SoH's Lang.cpp with LoadLangs reading the language files from disk
  build/gen/ShipRng.cpp          SoH's random number functions from ShipUtils.cpp (same seeds as SoH)
  build/gen/inventory_tables.inc SoH's inventory bit tables from z_inventory.c
  build/shim/...                 two actor headers the fishsanity code includes
  build/lang/*.json              SoH's English text"""
import glob, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(ROOT, 'soh-src', 'soh')
R = os.path.join(S, 'soh', 'Enhancements', 'randomizer')
G = os.path.join(ROOT, 'build', 'gen')
os.makedirs(G, exist_ok=True)


def read(p):
    return open(p, encoding='utf-8').read()


def write(name, text):
    open(os.path.join(G, name), 'w', encoding='utf-8', newline='\n').write(text)


# fill.cpp + the remake hook
fill = read(os.path.join(R, '3drando', 'fill.cpp'))
assert fill.count('\n        FillExcludedLocations();\n') == 1
fill = fill.replace('\n        FillExcludedLocations();\n', '\n        FillExcludedLocations();\n        Remake_LockUnmapped();\n')
fill = fill.replace('\nint Fill() {', '\nvoid Remake_LockUnmapped();\nint Fill() {', 1)
write('fill_remake.cpp', '#line 1 "fill.cpp"\n' + fill)

# location tables
subprocess.check_call([sys.executable, '-I', os.path.join(ROOT, 'tools', 'extract_locations.py'), R,
                       os.path.join(G, 'locations_gen.cpp')], stdout=subprocess.DEVNULL)

# Lang.cpp: LoadLangs from disk
lang = read(os.path.join(S, 'soh', 'Enhancements', 'Lang', 'Lang.cpp'))
a, b = lang.index('void Lang::LoadLangs() {'), lang.index('void LanguageCustomWidget')
lang = lang[:a] + '''// sohrando: read the language files from disk instead of SoH's archive
#include <fstream>
#include <filesystem>
extern std::string gLangDir;
void Lang::LoadLangs() {
    for (auto& e : std::filesystem::directory_iterator(gLangDir)) {
        if (e.path().extension() != ".json") continue;
        langs.insert_or_assign(e.path().stem().string(), nlohmann::json::parse(std::ifstream(e.path())));
    }
    initialized = true;
}

''' + lang[b:]
write('Lang.cpp', lang.replace('#include "Lang.h"', '#include "soh/Enhancements/Lang/Lang.h"'))

# RNG from ShipUtils.cpp
su = read(os.path.join(S, 'soh', 'ShipUtils.cpp'))
a = su.index('static bool default_init')
b = su.index('double ShipUtils::RandomDouble')
b = su.index('}', b) + 1
write('ShipRng.cpp', '#include <cstdint>\n#include <cassert>\n#include <cmath>\n#include <bit>\n#include <random>\n'
      '#include "soh/ShipUtils.h"\n' + su[a:b] + '\n')

# inventory tables from z_inventory.c
inv = read(os.path.join(S, 'src', 'code', 'z_inventory.c'))
parts = []
for name in ('gBitFlags', 'gUpgradeMasks', 'gUpgradeNegMasks', 'gUpgradeShifts', 'gItemSlots'):
    m = re.search(r'\n(u\d+ ' + name + r'\[\] = \{.*?\};)', inv, re.S)
    parts.append(m.group(1))
write('inventory_tables.inc', '\n'.join(parts) + '\n')

# two headers fishsanity.cpp includes
for h in ('ovl_Fishing/z_fishing.h', 'ovl_En_Fish/z_en_fish.h'):
    dst = os.path.join(ROOT, 'build', 'shim', 'src', 'overlays', 'actors', h)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy(os.path.join(S, 'src', 'overlays', 'actors', h), dst)

# English text
L = os.path.join(ROOT, 'build', 'lang')
os.makedirs(L, exist_ok=True)
for f in glob.glob(os.path.join(S, 'assets', 'custom', 'lang', '*.json')):
    shutil.copy(f, L)
print('prepared build/gen, build/shim, build/lang from soh-src')
