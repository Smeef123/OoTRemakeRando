#!/bin/sh
# Build build/sohrando.exe: Ship of Harkinian's randomizer generator, unchanged, plus this repo's command-line front end
# (gen/). Needs the sources from tools/fetch_deps.sh and a g++ (WinLibs) on PATH.
# usage: sh tools/build_gen.sh [syntax]
cd "$(dirname "$0")/.."
PY=${PYTHON:-python}
R=soh-src/soh/soh/Enhancements/randomizer
E=soh-src/soh/soh/Enhancements
"$PY" -I tools/prepare_soh.py || exit 1
FILES="$(ls $R/3drando/*.cpp $R/3drando/hint_list/*.cpp $R/location_access/*.cpp $R/location_access/*/*.cpp | grep -v '/3drando/fill.cpp$' | grep -v '/3drando/fill_remake.cpp$')
 $R/logic.cpp $R/settings.cpp $R/option.cpp $R/item.cpp $R/item_list.cpp $R/location.cpp $R/location_list.cpp
 $R/static_data.cpp $R/SeedContext.cpp $R/dungeon.cpp $R/entrance.cpp $R/hint.cpp $R/trial.cpp $R/tricks.cpp
 $R/fishsanity.cpp $R/item_location.cpp $R/item_override.cpp $R/randomizerEnumStrings.cpp $R/location_access.cpp
 $R/Traps.cpp $R/RCToRandInf.cpp $E/custom-message/text.cpp $E/custom-message/CustomMessageManager.cpp
 $E/debugger/performanceTimer.cpp $E/item-tables/ItemTableManager.cpp soh-src/soh/soh/util.cpp
 deps/imgui/imgui.cpp deps/imgui/imgui_widgets.cpp deps/imgui/imgui_draw.cpp deps/imgui/imgui_tables.cpp
 lus/src/ship/utils/StringHelper.cpp
 build/gen/fill_remake.cpp build/gen/locations_gen.cpp build/gen/Lang.cpp build/gen/ShipRng.cpp
 gen/main.cpp gen/stubs.cpp gen/remake_lock.cpp"
DEFS='-include shim/force.h -DIMGUI_DEFINE_MATH_OPERATORS -DNOMINMAX'
INC="-Ibuild/shim -Ishim -Ibuild/gen -Isoh-src/soh -Isoh-src/soh/include -Isoh-src/soh/soh -Isoh-src -Ilus/include -Ilus/src -Ilus/include/libultraship -Ideps/spdlog/include -Ideps/json/include -Ideps/imgui -Ideps/sdlinc -Ideps/sdl2/include -Ideps/btp/include -I$R -I$R/3drando"
mkdir -p build/obj build/err
MODE=${1:-obj}
JOBS=${JOBS:-$(( $(nproc 2>/dev/null || echo 4) / 2 ))}
[ "$JOBS" -lt 1 ] && JOBS=1
for f in $FILES; do echo "$f"; done | xargs -P "$JOBS" -I{} sh -c '
f={}; b=$(echo $f | sed "s#/#_#g; s#\.cpp##")
if [ "'$MODE'" = syntax ]; then g++ -std=c++20 -fsyntax-only -fpermissive -w '"$DEFS $INC"' "$f" 2> build/err/$b.txt || echo "FAIL $b $(grep -m1 -E "error|fatal" build/err/$b.txt | cut -c1-220)";
else [ build/obj/$b.o -nt $f ] || g++ -std=c++20 -O1 -fpermissive -w -c '"$DEFS $INC"' "$f" -o build/obj/$b.o 2> build/err/$b.txt || echo "FAIL $b $(grep -m1 -E "error|fatal" build/err/$b.txt | cut -c1-220)"; fi'
[ "$MODE" = syntax ] && exit 0
gcc -c -w -Ibuild/gen -Isoh-src/soh/include -Isoh-src/soh -Ilus/include -Ilus/include/libultraship -Ishim gen/stubs_c.c -o build/obj/stubs_c.o || exit 1
g++ -static -o build/sohrando.exe build/obj/*.o || exit 1
build/sohrando.exe --dump-options build/soh_options.json build/lang > /dev/null || exit 1
echo "built build/sohrando.exe"
