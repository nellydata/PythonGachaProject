# 🐛 Known Issues & Bugs

This document tracks known issues, bugs, and limitations in Nightmare Nexus v1.2. If you encounter any of these issues, they are already on our radar for future fixes.

---

## 🔴 **Critical Issues**

### Multi-Battle System Persistence
**Issue:** Multi-battle mode continues running even after player navigates away from battle screens  
**Symptoms:**
- Multi-battle counter continues incrementing in background
- Battle notifications appear while in other game sections
- Cannot properly start new battles until multi-battle is manually stopped
- Game may attempt to launch battles while in facility management or other screens

**Workaround:** 
- Always use "Exit" button to properly end multi-battle before navigating
- Restart the game if multi-battle gets stuck in background

**Status:** 🔧 *Fix in progress*

---

## 🟠 **Major Issues**

### Auto-Battle Preference Persistence
**Issue:** Auto-battle settings persist across different content areas  
**Symptoms:**
- Auto-battle enabled in campaign carries over to Depths battles
- Manual battle preference doesn't reset properly between different battle types
- Player loses control in unexpected battle scenarios

**Workaround:**
- Manually toggle auto-battle settings when switching between game modes
- Check battle controls at start of each new battle type

**Status:** 🔍 *Under investigation*

### Depths Boss Wave Loading
**Issue:** Rune Sanctum boss battles have inconsistent wave progression  
**Symptoms:**
- Some waves load with no enemies
- Wave counter may skip numbers (e.g., 1 → 3 → 5)
- Boss may appear in wrong wave or not appear at all
- Battle gets stuck on empty waves with no way to progress

**Affected Content:**
- Rune Sanctums (all bosses)
- Some Endless Delve floors with boss encounters

**Workaround:**
- Retreat and restart the boss battle if wave loads empty
- Use single battles instead of multi-battle for boss content
- Turn on auto battle if no enemies or actions load

**Status:** 🔧 *Fix planned for v1.3*

---

## 🟡 **Minor Issues**

### Battle Speed Settings
**Issue:** Battle speed preferences don't always save correctly  
**Symptoms:**
- Speed resets to 1x after closing and reopening game
- Speed changes don't apply immediately in some battles
- Multi-battle speed differs from single battle speed

**Status:** 🔧 *Fix in progress*

### UI Navigation Stack
**Issue:** Back button history can become corrupted during certain navigation paths  
**Symptoms:**
- Back button leads to unexpected screens
- Navigation history includes battle screens that should be excluded
- Cannot return to previous screen after some facility visits

**Workaround:** Use Home button to reset navigation

**Status:** 📋 *Planned fix*

### Rune Auto-Equip Logic
**Issue:** Auto-equip function sometimes removes better runes  
**Symptoms:**
- Lower level runes replace higher level ones
- Set bonuses ignored in favor of individual stat priorities
- Epic/Legendary runes replaced with Rare runes

**Workaround:** Manually equip runes for optimal builds

**Status:** 📋 *Enhancement planned*

---

## 🟢 **Cosmetic Issues**

### Status Effect Display
**Issue:** Status effect icons sometimes overlap in battle UI  
**Symptoms:**
- Multiple effects show as garbled text
- Effect counters display incorrectly
- Icons don't update properly when effects expire

**Status:** 📋 *Low priority*

### Unit Collection Scrolling
**Issue:** Unit collection scroll position resets when applying filters  
**Symptoms:**
- Scroll jumps to top when changing sort order
- Filter changes lose current viewing position

**Status:** 📋 *Quality of life improvement*

### Battle Log Timestamps
**Issue:** Timestamps occasionally show out of order  
**Symptoms:**
- Battle events appear with earlier timestamps than previous events
- Time display inconsistent during fast battle speeds

**Status:** 📋 *Low priority*

---

## 🔵 **Platform-Specific Issues**

### Windows
- **High DPI Scaling:** UI elements may appear too small on high-DPI displays
- **Long Path Names:** Save files may fail if username contains special characters

### Linux
- **Font Rendering:** Some Unicode characters in entity names may not display correctly
- **Window Decorations:** Title bar appearance varies by desktop environment

### macOS
- **Menu Integration:** Standard macOS menu integration not implemented
- **Retina Display:** Some UI elements may appear blurry on Retina displays

---

## 🛠️ **Workarounds & Tips**

### General Stability
1. **Save frequently** - Use manual save in Account Manager before major battles
2. **Restart periodically** - Close and reopen game after extended play sessions
3. **Avoid rapid navigation** - Allow screens to fully load before clicking

### Multi-Battle Issues
1. **Monitor carefully** - Don't navigate away during multi-battle sequences
2. **Use stop conditions** - Set defeat or level-up stop conditions to prevent runaway battles
3. **Single battle preferred** - Use single battles for story progression and boss fights

### Battle System
1. **Manual mode for bosses** - Use manual control for important battles
2. **Speed settings** - Keep battle speed at 1x or 2x for stability
3. **Team validation** - Check team composition before starting battles

---

## 📋 **Issue Reporting**

### Using In-Game Bug Reporter
The game includes a built-in bug reporting system (Help → Bug Report):
- Automatically captures system info and game state
- Saves reports to `bug_reports/` folder
- Include screenshots if possible

### GitHub Issues
Report new bugs or confirm existing ones:
1. Check this document first to avoid duplicates
2. Use the bug report template in Issues
3. Include steps to reproduce
4. Specify your platform (Windows/Mac/Linux)

### Priority Classification
- 🔴 **Critical:** Game-breaking, prevents normal play
- 🟠 **Major:** Significant impact on gameplay experience  
- 🟡 **Minor:** Noticeable but doesn't break functionality
- 🟢 **Cosmetic:** Visual issues that don't affect gameplay
- 🔵 **Platform:** Issues specific to certain operating systems

---

## 🔄 **Version History**

### Known Issues Fixed in v1.2
- ✅ Developer account credentials no longer visible in login hints
- ✅ Eight Pages passive now only triggers when Slender is involved in battle
- ✅ Battle preferences now save properly between sessions
- ✅ JSON save data compatibility improved
- ✅ Unit stats calculation accuracy enhanced

### Issues Targeted for v1.3
- 🎯 Multi-battle system persistence fix
- 🎯 Depths boss wave loading improvements
- 🎯 Auto-battle preference isolation by game mode
- 🎯 Navigation stack corruption prevention
- 🎯 UI scaling improvements for high-DPI displays

---

## 💡 **Contributing Fixes**

If you've found a fix for any of these issues:
1. Fork the repository
2. Create a feature branch: `git checkout -b fix/issue-name`
3. Test thoroughly across different scenarios
4. Submit a pull request with detailed description

See [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines.

---

## ⚠️ **Disclaimer**

This is an educational project demonstrating game development concepts. While we strive to fix bugs, the primary focus is on learning and code quality rather than commercial-grade stability.

**Last Updated:** August 16, 2024  
**Game Version:** v1.2 Battle System Enhancement Edition

---

*Found a new bug? Help us improve Nightmare Nexus by reporting it! 🕷️*

