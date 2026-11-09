#!/bin/sh
# Download the source the generator is built from, at the exact versions this randomizer was made with.
# Nothing here is part of this repository: Ship of Harkinian and its libraries are fetched from their own repositories.
set -e
cd "$(dirname "$0")/.."

fetch() { # fetch <dir> <url> <commit or tag> [sparse paths...]
    dir=$1; url=$2; rev=$3; shift 3
    if [ ! -d "$dir/.git" ]; then
        git clone -q --filter=blob:none --no-checkout "$url" "$dir"
    fi
    if [ $# -gt 0 ]; then
        git -C "$dir" sparse-checkout init --no-cone
        printf '%s\n' "$@" > "$dir/.git/info/sparse-checkout"
    fi
    git -C "$dir" fetch -q --depth 1 origin "$rev" 2>/dev/null || git -C "$dir" fetch -q origin
    git -C "$dir" checkout -q --force "$rev" 2>/dev/null || git -C "$dir" checkout -q --force FETCH_HEAD
    echo "$dir @ $(git -C "$dir" rev-parse --short HEAD)"
}

# Ship of Harkinian (randomizer, headers, the few game files the generator needs)
fetch soh-src https://github.com/HarbourMasters/Shipwright.git d4bf6528a3bb242bc5d862e4f1ab2b6d385c157b \
    /soh/include/ /soh/soh/ /soh/assets/custom/lang/ /soh/src/code/z_inventory.c \
    /soh/src/overlays/actors/ovl_Fishing/ /soh/src/overlays/actors/ovl_En_Fish/
fetch lus https://github.com/kenix3/libultraship.git da6daf1a50a5e46d6641408d52227e31e85e46df
mkdir -p deps
fetch deps/imgui https://github.com/ocornut/imgui.git v1.91.9b-docking
fetch deps/btp https://github.com/bshoshany/thread-pool.git v4.1.0
fetch deps/spdlog https://github.com/gabime/spdlog.git 6d9805df3f588402b17073dcd13eb569ceda864d
fetch deps/json https://github.com/nlohmann/json.git 6f01030c4e6b27027ddd015807c3c5e5694cd5b1
fetch deps/sdl2 https://github.com/libsdl-org/SDL.git cee83f2d9a916e9de30c5712e798541fdc134b06
rm -rf deps/sdlinc && mkdir -p deps/sdlinc && cp -r deps/sdl2/include deps/sdlinc/SDL2
echo "sources ready"
