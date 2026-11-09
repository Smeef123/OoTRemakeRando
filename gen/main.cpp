// Headless front end for Ship of Harkinian's randomizer generator (unchanged SoH code).
// usage: sohrando <settings.json> <out dir> [seed]
//   settings.json: SoH CVars, e.g. {"gRandoSettings.ShuffleSongs": 1, "gRandoSettings.EnabledTricks": "..."}
//   writes <out dir>/spoiler.json (SoH's own spoiler log) and <out dir>/placement.json (check -> item)
#include <cstdio>
#include <fstream>
#include <sstream>
#include <filesystem>
#include <nlohmann/json.hpp>
#include <spdlog/spdlog.h>
#include <libultraship/bridge/consolevariablebridge.h>
#include "soh/Enhancements/randomizer/SeedContext.h"
#include "soh/Enhancements/randomizer/settings.h"
#include "soh/Enhancements/randomizer/static_data.h"
#include "soh/Enhancements/randomizer/randomizerEnumStrings.h"
#include "soh/Enhancements/randomizer/3drando/menu.hpp"
#include "soh/Enhancements/randomizer/3drando/spoiler_log.hpp"
#include "soh/Enhancements/Lang/Lang.h"
#include "soh/OTRGlobals.h"
#include "soh/ShipInit.hpp"

std::string gOutDir = ".";
std::string gLangDir = "lang";
extern std::set<RandomizerCheck> gRemakeMapped;
extern bool gRemakeLock;

// --dump-options <out.json>: SoH's own randomizer menu (sidebar tabs > columns > sections > options) and tricks
static nlohmann::json DumpGroup(const Rando::OptionGroup& g) {
    nlohmann::json j;
    j["name"] = g.GetName();
    for (auto* sub : g.GetSubGroups()) j["groups"].push_back(DumpGroup(*sub));
    for (auto* o : g.GetOptions()) {
        nlohmann::json oj;
        oj["name"] = o->GetName();
        oj["cvar"] = o->GetCVarName();
        oj["default"] = o->GetMenuOptionDefault();
        oj["description"] = o->GetDescription();
        for (size_t i = 0; i < o->GetOptionCount(); i++) oj["choices"].push_back(o->GetOptionText(i));
        j["options"].push_back(oj);
    }
    return j;
}
static int DumpOptions(const char* path) {
    auto s = Rando::Settings::GetInstance();
    nlohmann::json out;
    for (auto key : { RSG_MENU_SIDEBAR_LOGIC_ACCESS, RSG_MENU_SIDEBAR_SHUFFLES, RSG_MENU_SIDEBAR_DUNGEONS,
                      RSG_MENU_SIDEBAR_HINTS_TRAPS })
        out["tabs"].push_back(DumpGroup(s->GetOptionGroup(key)));
    for (auto& [key, rt] : Rando::StaticData::trickToEnum) {
        auto& t = s->GetTrickSetting(rt);
        out["tricks"].push_back({ { "key", key }, { "name", t.GetName() }, { "description", t.GetDescription() },
                                  { "mq", t.GetQuest() == RCQUEST_MQ } });
    }
    std::ofstream(path) << out.dump(1);
    printf("options written to %s\n", path);
    return 0;
}

int main(int argc, char** argv) {
    if (argc == 4 && std::string(argv[1]) == "--dump-options") { // sohrando --dump-options <out.json> <lang dir>
        gLangDir = argv[3];
        Lang::LoadLangs();
        Rando::Context().InitStaticData();
        auto ctx = Rando::Context::CreateInstance();
        OTRGlobals::Instance->gRandoContext = ctx;
        Rando::Settings::GetInstance()->CreateOptions();
        Rando::StaticData::InitHashMaps();
        return DumpOptions(argv[2]);
    }
    if (argc < 3) {
        fprintf(stderr, "usage: sohrando <settings.json> <out dir> [seed]\n");
        return 2;
    }
    gOutDir = argv[2];
    std::filesystem::create_directories(gOutDir);
    nlohmann::json cfg = nlohmann::json::parse(std::ifstream(argv[1]));
    for (auto& [k, v] : cfg.items()) {
        if (v.is_string()) CVarSetString(k.c_str(), v.get<std::string>().c_str());
        else if (v.is_number_float()) CVarSetFloat(k.c_str(), v.get<float>());
        else CVarSetInteger(k.c_str(), v.get<int>());
    }
    std::string seed = argc > 3 ? argv[3] : "";
    if (argc > 4) gLangDir = argv[4];
    Lang::LoadLangs();
    if (getenv("SOHRANDO_DEBUG")) spdlog::set_level(spdlog::level::debug);
    if (argc > 5) { // remake check map: only these checks get shuffled items, the rest keep vanilla
        nlohmann::json map = nlohmann::json::parse(std::ifstream(argv[5]));
        for (int rc = 1; rc < RC_MAX; rc++)
            if (map.contains(std::string(EnumToString((RandomizerCheck)rc)))) gRemakeMapped.insert((RandomizerCheck)rc);
        gRemakeLock = true;
        printf("remake checks: %zu\n", gRemakeMapped.size());
    }

    Rando::Context().InitStaticData();
    auto ctx = Rando::Context::CreateInstance();
    OTRGlobals::Instance->gRandoContext = ctx;
    Rando::Settings::GetInstance()->CreateOptions(); // SoH builds its settings (names, defaults) when its menu opens
    Rando::Settings::GetInstance()->AssignContext(ctx);
    Rando::StaticData::InitItemTable();
    void Remake_RegisterAllLocations(); Remake_RegisterAllLocations(); // SoH Shuffle*.cpp location tables (songs, pots, cows, ...)
    Rando::StaticData::InitHashMaps();
    ctx->AddExcludedOptions();
    Rando::Settings::GetInstance()->SetAllToContext();

    std::set<RandomizerCheck> excluded =
        Rando::StaticData::ParseExcludedLocations(CVarGetString(CVAR_RANDOMIZER_SETTING("ExcludedLocations"), ""));
    std::set<RandomizerTrick> tricks;
    std::stringstream ts(CVarGetString(CVAR_RANDOMIZER_SETTING("EnabledTricks"), ""));
    for (std::string t; getline(ts, t, ',');)
        if (Rando::StaticData::trickToEnum.contains(t)) tricks.insert(Rando::StaticData::trickToEnum[t]);

    if (!GenerateRandomizer(excluded, tricks, seed)) {
        fprintf(stderr, "generation failed\n");
        return 1;
    }

    nlohmann::json out;
    out["seed"] = ctx->GetSeedString();
    out["hash"] = ctx->GetHash();
    for (int rc = 1; rc < RC_MAX; rc++) {
        auto loc = Rando::StaticData::GetLocation((RandomizerCheck)rc);
        auto il = ctx->GetItemLocation((RandomizerCheck)rc);
        RandomizerGet rg = il->GetPlacedRandomizerGet();
        if (rg == RG_NONE) continue;
        nlohmann::json row;
        row["rc"] = rc;
        row["check"] = loc->GetName();
        row["rc_enum"] = std::string(EnumToString((RandomizerCheck)rc));
        row["item"] = Rando::StaticData::RetrieveItem(rg).GetName().GetEnglish();
        row["rg"] = rg;
        row["rg_enum"] = std::string(EnumToString(rg));
        row["vanilla_rg"] = loc->GetVanillaItem();
        out["placements"].push_back(row);
    }
    std::ofstream(gOutDir + "/placement.json") << out.dump(1);
    printf("ok seed=%s placements=%zu\n", ctx->GetSeedString().c_str(), out["placements"].size());
    return 0;
}
