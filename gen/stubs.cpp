// Stand-ins for the parts of Ship of Harkinian the seed generator links against but that belong to the game or its
// menus (drawing, save data, ImGui windows). CVars are real: a plain map filled from the settings file.
#include <map>
#include <string>
#include <variant>
#include <filesystem>
#include <libultraship/bridge/consolevariablebridge.h>
#include <ship/Context.h>
#include <ship/window/Window.h>
#include <ship/window/gui/Gui.h>
#include "soh/OTRGlobals.h"
#include "soh/SohGui/SohMenu.h"
#include "soh/SohGui/UIWidgets.hpp"
#include "soh/Enhancements/kaleido.h"
#include "soh/Enhancements/game-interactor/GameInteractor.h"
#include "soh/Enhancements/randomizer/randomizer.h"
#include "soh/Enhancements/randomizer/randomizer_check_tracker.h"
#include "soh/Enhancements/randomizer/randomizer_entrance_tracker.h"
#include "soh/Enhancements/randomizer/SeedContext.h"
#include "soh/Enhancements/randomizer/RCToRandInf.h"
#include "soh/Enhancements/item-tables/ItemTableManager.h"

extern std::string gOutDir;

// ---- CVars
static std::map<std::string, std::variant<int32_t, float, std::string>> sCVars;
extern "C" {
int32_t CVarGetInteger(const char* n, int32_t d) {
    auto it = sCVars.find(n);
    if (it == sCVars.end()) return d;
    if (auto* i = std::get_if<int32_t>(&it->second)) return *i;
    if (auto* f = std::get_if<float>(&it->second)) return (int32_t)*f;
    return d;
}
float CVarGetFloat(const char* n, float d) {
    auto it = sCVars.find(n);
    if (it == sCVars.end()) return d;
    if (auto* f = std::get_if<float>(&it->second)) return *f;
    if (auto* i = std::get_if<int32_t>(&it->second)) return (float)*i;
    return d;
}
const char* CVarGetString(const char* n, const char* d) {
    auto it = sCVars.find(n);
    if (it == sCVars.end()) return d;
    if (auto* s = std::get_if<std::string>(&it->second)) return s->c_str();
    return d;
}
void CVarSetInteger(const char* n, int32_t v) { sCVars[n] = v; }
void CVarSetFloat(const char* n, float v) { sCVars[n] = v; }
void CVarSetString(const char* n, const char* v) { sCVars[n] = std::string(v); }
void CVarClear(const char* n) { sCVars.erase(n); }
bool CVarExists(const char* n) { return sCVars.count(n) != 0; }
}

// ---- Ship / OTRGlobals
OTRGlobals* OTRGlobals::Instance;
bool OTRGlobals::HasMasterQuest() { return false; } // the remake is vanilla quest only
bool OTRGlobals::HasOriginal() { return true; }
Ship::Context* Ship::Context::GetRawInstance() { return nullptr; }
std::string Ship::Context::GetPathRelativeToAppDirectory(const std::string& path, const std::string&) {
    return (std::filesystem::path(gOutDir) / path).string();
}
std::shared_ptr<Ship::Window> Ship::Context::GetWindow() const { return nullptr; }
std::shared_ptr<Ship::Gui> Ship::Window::GetGui() { return nullptr; }
void Ship::Gui::SaveConsoleVariablesNextFrame() {}

// ---- menus
namespace SohGui {
std::shared_ptr<SohMenu> mSohMenu;
void SohMenu::AddSidebarEntry(std::string, std::string, uint32_t) {}
WidgetInfo& SohMenu::AddWidget(WidgetPath&, std::string, WidgetType) {
    static WidgetInfo w;
    return w;
}
} // namespace SohGui
namespace UIWidgets {
void PushStyleButton(const ImVec4&, ImVec2) {}
void PopStyleButton() {}
} // namespace UIWidgets
namespace CheckTracker {
void SpoilAreaFromCantObtain(RandomizerGet) {}
} // namespace CheckTracker
namespace EntranceTracker {
const EntranceData* GetEntranceData(s16) { return nullptr; }
} // namespace EntranceTracker
Rando::Kaleido::Kaleido() {}
GameInteractor* GameInteractor::Instance;

// ---- Randomizer (game-side class; only the lookups the generator touches)
Randomizer::Randomizer() {}
Randomizer::~Randomizer() {}
u8 Randomizer::GetRandoSettingValue(RandomizerSettingKey k) { return Rando::Context::GetInstance()->GetOption(k).Get(); }
RandomizerInf Randomizer::GetRandomizerInfFromCheck(RandomizerCheck rc) {
    auto it = rcToRandomizerInf.find(rc);
    return it == rcToRandomizerInf.end() ? RAND_INF_MAX : it->second;
}
Rando::Location* Randomizer::GetCheckObjectFromActor(s16, s16, s32) { return nullptr; }
ItemObtainability Randomizer::GetItemObtainabilityFromRandomizerGet(RandomizerGet) { return CAN_OBTAIN; }
s8 Randomizer::SilverTotal(RandomizerGet) { return 5; }
s8* Randomizer::SilverFieldFromSaveContext(SaveContext*, RandomizerGet) {
    static s8 v;
    return &v;
}

struct OTRInit {
    OTRInit() {
        alignas(OTRGlobals) static unsigned char buf[sizeof(OTRGlobals)] = {};
        OTRGlobals::Instance = reinterpret_cast<OTRGlobals*>(buf);
        new (&OTRGlobals::Instance->gRandomizer) std::shared_ptr<Randomizer>(std::make_shared<Randomizer>());
    }
} sOTRInit;
ItemTableManager* ItemTableManager::Instance;
