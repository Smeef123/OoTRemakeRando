// Remake support for SoH's fill: checks the remake cannot change keep their vanilla item, so SoH's logic only ever
// places shuffled items at checks the installer can write into the remake's map files.
#include <set>
#include <algorithm>
#include "soh/Enhancements/randomizer/SeedContext.h"
#include "soh/Enhancements/randomizer/static_data.h"
#include "soh/Enhancements/randomizer/3drando/item_pool.hpp"

std::set<RandomizerCheck> gRemakeMapped;
bool gRemakeLock = false;

static const std::set<RandomizerGet> kJunk = {
    RG_GREEN_RUPEE, RG_BLUE_RUPEE, RG_RED_RUPEE, RG_PURPLE_RUPEE, RG_HUGE_RUPEE, RG_RECOVERY_HEART, RG_ICE_TRAP,
    RG_ARROWS_5, RG_ARROWS_10, RG_ARROWS_30, RG_BOMBS_5, RG_BOMBS_10, RG_BOMBS_20, RG_DEKU_NUTS_5, RG_DEKU_NUTS_10,
    RG_DEKU_SEEDS_30, RG_DEKU_STICK_1,
};

void Remake_LockUnmapped() {
    if (!gRemakeLock) return;
    auto ctx = Rando::Context::GetInstance();
    for (RandomizerCheck rc : ctx->allLocations) {
        if (gRemakeMapped.count(rc)) continue;
        auto loc = Rando::StaticData::GetLocation(rc);
        if (loc->GetRCType() == RCTYPE_SHOP) continue; // shops: SoH places them itself (shopsanity is forced off)
        auto il = ctx->GetItemLocation(rc);
        if (il->GetPlacedRandomizerGet() != RG_NONE) continue;
        RandomizerGet v = loc->GetVanillaItem();
        if (v == RG_NONE) continue;
        auto it = std::find(itemPool.begin(), itemPool.end(), v);
        if (it == itemPool.end())
            it = std::find_if(itemPool.begin(), itemPool.end(), [](RandomizerGet g) { return kJunk.count(g) != 0; });
        if (it != itemPool.end()) itemPool.erase(it);
        ctx->PlaceItemInLocation(rc, v);
    }
    void Remake_DebugCounts(); Remake_DebugCounts();
}

// SOHRANDO_DEBUG: after locking, how many free checks each area has and which dungeon items / songs are still to place
#include <map>
#include <cstdio>
#include <cstdlib>
void Remake_DebugCounts() {
    if (!getenv("SOHRANDO_DEBUG")) return;
    auto ctx = Rando::Context::GetInstance();
    std::map<int, int> freeByArea;
    for (RandomizerCheck rc : ctx->allLocations)
        if (ctx->GetItemLocation(rc)->GetPlacedRandomizerGet() == RG_NONE)
            for (auto a : ctx->GetItemLocation(rc)->GetAreas()) freeByArea[a]++;
    std::map<std::string, int> items;
    for (auto g : itemPool) {
        auto t = Rando::StaticData::RetrieveItem(g).GetItemType();
        if (t == ITEMTYPE_SMALLKEY || t == ITEMTYPE_MAP || t == ITEMTYPE_COMPASS || t == ITEMTYPE_BOSSKEY || t == ITEMTYPE_SONG)
            items[Rando::StaticData::RetrieveItem(g).GetName().GetEnglish()]++;
    }
    for (auto& [a, n] : freeByArea) fprintf(stderr, "free area %d: %d\n", a, n);
    for (auto& [k, n] : items) fprintf(stderr, "pool %s: %d\n", k.c_str(), n);
}
