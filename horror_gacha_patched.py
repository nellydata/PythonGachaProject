import random
import time
import json
import os
from colorama import Fore, Style, init
import math

# Initialize colorama
init(autoreset=True)

# ==========================
# Game Data
# ==========================

# Game Configuration
GAME_TITLE = "NIGHTMARE NEXUS"
GAME_SUBTITLE = "Summon • Manage • Conquer"

# Currency symbols
GEM_SYMBOL = "💎"
CASH_SYMBOL = "🪙"
XP_SYMBOL = "⭐"

rarity_colors = {
    "Common": Fore.WHITE,
    "Rare": Fore.BLUE,
    "Epic": Fore.MAGENTA,
    "Legendary": Fore.RED
}

entities = [
    # Common
    {"name": "Zombie", "rarity": "Common", "hp": 50, "attack": 5, "defense": 2, "speed": 10, "skill": None, "crit_rate": 0, "passive": "None",
     "description": "A mindless undead creature that craves flesh."},
    {"name": "Vampire", "rarity": "Common", "hp": 55, "attack": 6, "defense": 3, "speed": 12, "skill": None, "crit_rate": 0,
     "passive": "Heals 10% of damage dealt.",
     "description": "A bloodthirsty immortal that drains life from its victims."},
    {"name": "Werewolf", "rarity": "Common", "hp": 60, "attack": 7, "defense": 3, "speed": 14, "skill": None, "crit_rate": 0,
     "passive": "Gains 5% attack when below 50% HP.",
     "description": "A savage beast that transforms under the full moon."},
    {"name": "Ghoul", "rarity": "Common", "hp": 50, "attack": 5, "defense": 2, "speed": 11, "skill": None, "crit_rate": 0, "passive": "None",
     "description": "A graveyard-dwelling monster that feeds on the dead."},
    {"name": "Ghost", "rarity": "Common", "hp": 45, "attack": 4, "defense": 1, "speed": 16, "skill": None, "crit_rate": 0, "passive": "None",
     "description": "A restless spirit that haunts the living."},
    # Rare
    {"name": "Frankenstein", "rarity": "Rare", "hp": 100, "attack": 15, "defense": 8, "speed": 8, "skill": None, "crit_rate": 0, "passive": "None",
     "description": "A patchwork monster brought to life by science."},
    {"name": "Banshee", "rarity": "Rare", "hp": 80, "attack": 12, "defense": 5, "speed": 18, "skill": "scream", "crit_rate": 0, "passive": "None",
     "description": "A wailing spirit whose cry foretells death."},
    {"name": "Mummy", "rarity": "Rare", "hp": 90, "attack": 14, "defense": 7, "speed": 7, "skill": None, "crit_rate": 0, "passive": "None",
     "description": "An ancient corpse wrapped in bandages, cursed to walk the earth."},
    {"name": "Chupacabra", "rarity": "Rare", "hp": 85, "attack": 13, "defense": 6, "speed": 15, "skill": None, "crit_rate": 0, "passive": "None",
     "description": "A legendary creature known for attacking livestock."},
    {"name": "Poltergeist", "rarity": "Rare", "hp": 80, "attack": 12, "defense": 5, "speed": 17, "skill": "push", "crit_rate": 0, "passive": "None",
     "description": "A mischievous spirit that moves objects and causes chaos."},
    # Epic
    {"name": "SCP-999", "rarity": "Epic", "hp": 100, "attack": 5, "defense": 5, "speed": 25, "skill": "joyful_regeneration", "crit_rate": 0, "passive": "None",
     "description": "The Tickle Monster. A friendly, gelatinous SCP that brings joy and heals others."},
    {"name": "The Rake", "rarity": "Epic", "hp": 160, "attack": 30, "defense": 12, "speed": 28, "skill": "night_ambush", "crit_rate": 0, "passive": "None",
     "description": "A pale, humanoid creature known for its terrifying nocturnal attacks."},
    {"name": "Kuchisake-onna", "rarity": "Epic", "hp": 85, "attack": 20, "defense": 5, "speed": 20, "skill": "bloody_smile", "crit_rate": 15, "passive": "None",
     "description": "The Slit-Mouthed Woman. A vengeful spirit from Japanese folklore."},
    {"name": "Mothman", "rarity": "Epic", "hp": 95, "attack": 18, "defense": 6, "speed": 23, "skill": "mothmans_omen", "crit_rate": 0, "passive": "None",
     "description": "A mysterious winged cryptid said to predict disasters."},
    {"name": "Bloody Mary", "rarity": "Epic", "hp": 90, "attack": 15, "defense": 4, "speed": 19, "skill": "mirror_curse", "crit_rate": 0,
     "passive": "50% chance to inflict bleed when attacked. Heals 50% of damage taken if attacker has bleed.",
     "description": "A vengeful spirit summoned through mirrors."},
    # Legendary
    {"name": "Slender", "rarity": "Legendary", "hp": 150, "attack": 20, "defense": 10, "speed": 25, "skill": "faceless_terror", "crit_rate": 0,
     "passive": "Eight Pages: Attacker/target gains stack, stun at 8.",
     "description": "A tall, faceless entity that stalks and abducts victims."},
    {"name": "Jeff the Killer", "rarity": "Legendary", "hp": 90, "attack": 25, "defense": 5, "speed": 30, "skill": "killer_burst", "crit_rate": 30,
     "passive": "Starts with 3 Ghost stacks. Gains Ghost on crit. Cannot be targeted unless last alive.",
     "description": "A notorious creepypasta killer with a haunting smile."},
    {"name": "SCP-682", "rarity": "Legendary", "hp": 200, "attack": 40, "defense": 20, "speed": 24, "skill": "indestructible_regeneration", "crit_rate": 0,
     "passive": "Gains 5% DEF when attacked. Skill applies taunt.",
     "description": "The Hard to Destroy Reptile. An extremely dangerous, adaptive SCP."},
    {"name": "Iris", "rarity": "Legendary", "hp": 180, "attack": 25, "defense": 15, "speed": 20, "skill": "analog_distortion", "crit_rate": 0,
     "passive": "Basic attack hits all enemies, 40% chance to slow.",
     "description": "A mysterious analogue horror entity with reality-warping powers."},
]

# Status effect colors for display
status_colors = {
    "bleed": Fore.RED,
    "burn": Fore.LIGHTRED_EX,
    "poison": Fore.GREEN,
    "stun": Fore.YELLOW,
    "fear": Fore.LIGHTBLACK_EX,
    "ghost": Fore.CYAN,
    "crit_up": Fore.LIGHTMAGENTA_EX,
    "def_up": Fore.BLUE,
    "atk_up": Fore.LIGHTYELLOW_EX,
    "heal_over_time": Fore.LIGHTGREEN_EX,
    "heal_amount_up": Fore.LIGHTGREEN_EX,
    "shield": Fore.LIGHTWHITE_EX,
    "taunt": Fore.LIGHTBLUE_EX,
    "eight_pages": Fore.LIGHTBLACK_EX,
}

def fmt_hp_sp(unit):
    """Format HP and SP for display"""
    hp = unit.get("battle_hp", unit.get("hp", 0))
    sp = unit.get("sp", 0)
    max_hp = unit.get("entity", {}).get("hp", hp)
    return f"HP:{hp}/{max_hp}  SP:{sp}"

def format_unit_status(unit, is_player=True, compact=False):
    """Format a unit's status - ultra clean version"""
    if is_player:
        name = unit["entity"]["name"]
        hp = unit["battle_hp"]
        max_hp = unit["entity"]["hp"]
        sp = unit.get("sp", 0)
        rarity = unit["entity"]["rarity"]
    else:
        name = unit["name"]
        hp = unit["hp"]
        max_hp = unit.get("max_hp", hp)
        sp = unit.get("sp", 0)
        rarity = unit["rarity"]
    
    # Compact mode for listings
    if compact:
        hp_percent = max(0, hp) / max_hp if max_hp > 0 else 0
        hp_icon = "🟢" if hp_percent > 0.6 else "🟡" if hp_percent > 0.3 else "🔴"
        color = rarity_colors.get(rarity, Fore.WHITE)
        return f"{color}{name[:10]:<10}{Style.RESET_ALL} {hp_icon} {hp}/{max_hp}"
    
    # Full display for battle
    hp_percent = max(0, hp) / max_hp if max_hp > 0 else 0
    bar_length = 6  # Shorter bar
    filled = int(hp_percent * bar_length)
    health_bar = "█" * filled + "░" * (bar_length - filled)
    
    hp_color = Fore.GREEN if hp_percent > 0.6 else Fore.YELLOW if hp_percent > 0.3 else Fore.RED
    
    # Minimal effects display
    effects = unit.get("effects", [])
    if effects:
        effect_icons = []
        for eff in effects[:2]:  # Only show first 2 effects
            eff_type = eff.get("type", "")
            symbols = {"bleed": "🩸", "stun": "⚡", "ghost": "👻", "buff": "⬆", "debuff": "⬇"}
            effect_icons.append(symbols.get(eff_type, "●"))
        
        if len(effects) > 2:
            effect_icons.append("+")
        status_text = "".join(effect_icons)
    else:
        status_text = ""
    
    color = rarity_colors.get(rarity, Fore.WHITE)
    return f"{color}{name[:12]:<12}{Style.RESET_ALL} {hp_color}{health_bar}{Style.RESET_ALL} {hp:>3} {status_text}"

def display_battle_header(current_unit, is_player=True):
    """Minimal battle header"""
    unit_display = format_unit_status(current_unit, is_player)
    icon = "🎯" if is_player else "⚔️"
    print(f"\n{icon} {unit_display}")

def display_turn_order(combatants, current_index):
    """Minimal turn display"""
    next_units = []
    for i in range(current_index + 1, min(current_index + 3, len(combatants))):
        c = combatants[i]
        unit = c["unit"]
        if (c["type"] == "player" and unit["battle_hp"] > 0) or (c["type"] == "enemy" and unit["hp"] > 0):
            name = unit["entity"]["name"] if c["type"] == "player" else unit["name"]
            next_units.append(name[:8])
    
    if next_units:
        print(f"📋 Next: {' → '.join(next_units)}")

def display_enemies_clean(enemies):
    """Minimal enemy display"""
    alive_enemies = [e for e in enemies if e["hp"] > 0]
    if not alive_enemies:
        return
    
    enemy_list = []
    for idx, e in enumerate(alive_enemies):
        unit_display = format_unit_status(e, False, compact=True)
        enemy_list.append(f"{idx + 1}.{unit_display}")
    
    print(f"👹 {' | '.join(enemy_list)}")

def display_team_summary(team):
    """Minimal team display"""
    team_list = []
    for unit in team:
        if unit["battle_hp"] > 0:
            unit_display = format_unit_status(unit, True, compact=True)
            team_list.append(f"●{unit_display}")
        else:
            name = unit["entity"]["name"][:8]
            team_list.append(f"✗{Fore.RED}{name}{Style.RESET_ALL}")
    
    print(f"👥 {' | '.join(team_list)}")

def format_effects(effects):
    effect_strs = []
    for eff in effects:
        eff_type = eff.get("type", "")
        color = status_colors.get(eff_type, "")
        stat = eff.get("stat", "")
        amount = eff.get("amount", "")
        turns = eff.get("turns", "")
        stacks = eff.get("stacks", "")
        shield = eff.get("shield", "")
        desc = f"{color}{eff_type.replace('_',' ').title()}{Style.RESET_ALL}"
        if stat:
            desc += f"({stat})"
        if amount:
            desc += f":{amount}"
        if turns:
            desc += f" [{turns}T]"
        if stacks:
            desc += f" [{stacks}x]"
        if shield:
            desc += f" [{shield} Shield]"
        effect_strs.append(desc)
    return " | ".join(effect_strs) if effect_strs else "None"

def notify_status_effect(target_name, effect_type, duration=0, amount=0, stacks=1):
    """Display a clear status effect notification"""
    symbols = {
        "bleed": "🩸", "burn": "🔥", "poison": "☠️", 
        "stun": "⚡", "ghost": "👻", "taunt": "🎯", "shield": "🛡️",
        "buff": "⬆️", "debuff": "⬇️", "heal": "💚"
    }
    
    symbol = symbols.get(effect_type, "●")
    color = status_colors.get(effect_type, Fore.WHITE)
    
    effect_name = effect_type.replace('_', ' ').title()
    
    if stacks > 1:
        stacks_text = f" (×{stacks})"
    else:
        stacks_text = ""
        
    if duration > 0:
        duration_text = f" for {duration} turns"
    else:
        duration_text = ""
        
    if amount > 0:
        amount_text = f" ({amount} damage/heal)"
    else:
        amount_text = ""
    
    print(f"   {symbol} {color}{target_name} is inflicted with {effect_name}{stacks_text}{amount_text}{duration_text}!{Style.RESET_ALL}")

skill_costs = {
    "joyful_regeneration": 40,
    "killer_burst": 50,
    "bloody_smile": 35,
    "mothmans_omen": 30,
    "mirror_curse": 40,
    "night_ambush": 50,
    "faceless_terror": 45,
    "analog_distortion": 40,
    "indestructible_regeneration": 60
}

rarity_chances = {
    "Common": 60,
    "Rare": 25,
    "Epic": 10,
    "Legendary": 5
}

SAVE_FILE = "savegame.json"

banners = {
    "Creepypasta": {
        "boosted": ["Slender", "Jeff the Killer", "The Rake"],
        "desc": "Boosted rates for Slender, Jeff the Killer, The Rake"
    },
    "SCP": {
        "boosted": ["SCP-999", "SCP-682"],
        "desc": "Boosted rates for SCP-999, SCP-682"
    },
    "Analogue": {
        "boosted": ["Iris"],
        "desc": "Boosted rate for Iris"
    }
}

# ==========================
# Player Data
# ==========================
player_inventory = []
player_gems = 100
player_cash = 500
player_items = {"Small XP Pot": 0, "Medium XP Pot": 0, "Large XP Pot": 0}

# Facility system
facility_data = {
    "level": 1,
    "max_units": 50,
    "structures": {
        "Nightmare Laboratory": {"level": 1, "max_level": 10, "unlocked": True},
        "Summoning Chamber": {"level": 1, "max_level": 10, "unlocked": True},
        "Training Grounds": {"level": 0, "max_level": 10, "unlocked": False},
        "Gem Mine": {"level": 0, "max_level": 5, "unlocked": False},
        "Resource Vault": {"level": 0, "max_level": 8, "unlocked": False},
        "Research Center": {"level": 0, "max_level": 5, "unlocked": False}
    }
}

xp_values = {
    "Common": 10,
    "Rare": 30,
    "Epic": 100,
    "Legendary": 300
}

player_level = 1
player_xp = 0

def player_xp_needed(level):
    return 100 + (level - 1) * 50

NUM_WORLDS = 5
STAGES_PER_WORLD = 20

worlds = [
    {"name": "Abandoned Hospital"},
    {"name": "Haunted Forest"},
    {"name": "Forgotten Laboratory"},
    {"name": "Cursed Town"},
    {"name": "Nightmare Realm"}
]

player_progress = {
    "world": 0,
    "stage": 0,
    "unlocked": [[1] + [0]*(STAGES_PER_WORLD-1) for _ in range(NUM_WORLDS)]  # Only stage 1 of world 1 unlocked
}

# ==========================
# Save/Load Functions
# ==========================
def save_game():
    data = {
        "player_gems": player_gems,
        "player_cash": player_cash,
        "player_inventory": player_inventory,
        "player_items": player_items
    }
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)
    print(Fore.GREEN + "Game saved!" + Style.RESET_ALL)

def load_game():
    """Enhanced load function that loads all game data silently"""
    global player_gems, player_cash, player_inventory, player_items, facility_data, player_level, player_xp, player_progress, rarity_chances
    
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                data = json.load(f)
                
            # Load core player data
            player_gems = data.get("player_gems", 100)
            player_cash = data.get("player_cash", 500)
            player_inventory = data.get("player_inventory", [])
            player_items = data.get("player_items", {"Small XP Pot": 0, "Medium XP Pot": 0, "Large XP Pot": 0})
            
            # Load facility data
            if "facility_data" in data:
                facility_data.update(data["facility_data"])
            
            # Load player progression
            player_level = data.get("player_level", 1)
            player_xp = data.get("player_xp", 0)
            
            # Load world progress
            if "player_progress" in data:
                player_progress.update(data["player_progress"])
            
            # Load custom rarity rates (for dev mode)
            if "rarity_chances" in data:
                rarity_chances.update(data["rarity_chances"])
                
            print(f"{Fore.GREEN}🌟 Welcome back to the nightmare! Progress restored.{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️ Save file corrupted, starting fresh. Error: {e}{Style.RESET_ALL}")
            # Reset to defaults if save is corrupted
            initialize_new_game()
    else:
        print(f"{Fore.CYAN}🌟 Welcome to {GAME_TITLE}! Your nightmare begins...{Style.RESET_ALL}")
        initialize_new_game()

def initialize_new_game():
    """Initialize default values for a new game"""
    global player_gems, player_cash, player_inventory, player_items, facility_data, player_level, player_xp, player_progress
    
    player_gems = 100
    player_cash = 500
    player_inventory = []
    player_items = {"Small XP Pot": 0, "Medium XP Pot": 0, "Large XP Pot": 0}
    player_level = 1
    player_xp = 0
    
    # Reset facility data to defaults (keeping the structure intact)
    facility_data["level"] = 1
    facility_data["max_units"] = 50
    for structure in facility_data["structures"].values():
        if structure.get("unlocked", False) and structure != facility_data["structures"]["Nightmare Laboratory"] and structure != facility_data["structures"]["Summoning Chamber"]:
            structure["unlocked"] = False
            structure["level"] = 0
        elif structure == facility_data["structures"]["Nightmare Laboratory"] or structure == facility_data["structures"]["Summoning Chamber"]:
            structure["level"] = 1
    
    # Reset world progress
    player_progress["world"] = 0
    player_progress["stage"] = 0
    player_progress["unlocked"] = [[1] + [0]*(STAGES_PER_WORLD-1) for _ in range(NUM_WORLDS)]

def autosave():
    """Enhanced autosave function that saves silently"""
    try:
        data = {
            "player_gems": player_gems,
            "player_cash": player_cash,
            "player_inventory": player_inventory,
            "player_items": player_items,
            "facility_data": facility_data,
            "player_level": player_level,
            "player_xp": player_xp,
            "player_progress": player_progress,
            "rarity_chances": rarity_chances
        }
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f, indent=2)
        # Only show autosave message in dev mode or on major milestones
        if globals().get('dev_mode', False):
            print(f"{Fore.GREEN}[Autosaved]{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}⚠️ Autosave failed: {e}{Style.RESET_ALL}")

# ==========================
# Gacha Functions
# ==========================

def summon_entity(banner=None):
    chances = rarity_chances.copy()
    boosted_legendaries = []
    if banner and banner in banners:
        boosted_legendaries = banners[banner]["boosted"]
        boosted_rate = chances["Legendary"] // 2
        normal_rate = chances["Legendary"] - boosted_rate
        roll = random.randint(1, 100)
        if roll <= boosted_rate:
            possible = [e for e in entities if e["rarity"] == "Legendary" and e["name"] in boosted_legendaries]
            entity = random.choice(possible) if possible else random.choice([e for e in entities if e["rarity"] == "Legendary"])
        elif roll <= chances["Legendary"]:
            possible = [e for e in entities if e["rarity"] == "Legendary" and e["name"] not in boosted_legendaries]
            entity = random.choice(possible) if possible else random.choice([e for e in entities if e["rarity"] == "Legendary"])
        elif roll <= chances["Legendary"] + chances["Epic"]:
            rarity = "Epic"
            possible = [e for e in entities if e["rarity"] == rarity]
            entity = random.choice(possible)
        elif roll <= chances["Legendary"] + chances["Epic"] + chances["Rare"]:
            rarity = "Rare"
            possible = [e for e in entities if e["rarity"] == rarity]
            entity = random.choice(possible)
        else:
            rarity = "Common"
            possible = [e for e in entities if e["rarity"] == rarity]
            entity = random.choice(possible)
    else:
        roll = random.randint(1, 100)
        if roll <= chances["Legendary"]:
            rarity = "Legendary"
        elif roll <= chances["Legendary"] + chances["Epic"]:
            rarity = "Epic"
        elif roll <= chances["Legendary"] + chances["Epic"] + chances["Rare"]:
            rarity = "Rare"
        else:
            rarity = "Common"
        possible = [e for e in entities if e["rarity"] == rarity]
        entity = random.choice(possible)
    skill_level = 1 if entity["rarity"] in ["Epic", "Legendary"] and entity["skill"] else 0

    # Duplicates allowed
    player_inventory.append({"entity": entity, "level": 1, "exp": 0, "skill_level": skill_level})
    print(f"✨ {rarity_colors[entity['rarity']]}{entity['name']}{Style.RESET_ALL}")
    
    # Auto-save after summoning
    autosave()
    return entity

def multi_summon(times=10, banner=None):
    results = []
    for _ in range(times):
        entity = summon_entity(banner)
        results.append(entity)
    
    # Summary only
    rarity_counts = {"Legendary": 0, "Epic": 0, "Rare": 0, "Common": 0}
    for entity in results:
        rarity_counts[entity["rarity"]] += 1
    
    summary = []
    for rarity, count in rarity_counts.items():
        if count > 0:
            summary.append(f"{rarity_colors[rarity]}{count} {rarity}{Style.RESET_ALL}")
    
    print(f"📦 Summary: {' | '.join(summary)}")

# ==========================
# Facility Functions
# ==========================

def get_facility_bonuses():
    """Calculate all facility bonuses"""
    bonuses = {
        "unit_capacity": facility_data["max_units"],
        "gem_production": 0,
        "cash_production": 0,
        "xp_bonus": 0,
        "summon_discount": 0,
        "upgrade_discount": 0
    }
    
    structures = facility_data["structures"]
    
    # Nightmare Laboratory - Unit upgrades and XP bonus
    if structures["Nightmare Laboratory"]["unlocked"]:
        lab_level = structures["Nightmare Laboratory"]["level"]
        bonuses["xp_bonus"] = lab_level * 5  # 5% XP bonus per level
        bonuses["upgrade_discount"] = lab_level * 2  # 2% upgrade cost reduction per level
    
    # Summoning Chamber - Summon discounts
    if structures["Summoning Chamber"]["unlocked"]:
        chamber_level = structures["Summoning Chamber"]["level"]
        bonuses["summon_discount"] = min(chamber_level * 3, 20)  # Max 20% discount
    
    # Training Grounds - Additional unit capacity
    if structures["Training Grounds"]["unlocked"]:
        training_level = structures["Training Grounds"]["level"]
        bonuses["unit_capacity"] += training_level * 10
    
    # Gem Mine - Passive gem generation
    if structures["Gem Mine"]["unlocked"]:
        mine_level = structures["Gem Mine"]["level"]
        bonuses["gem_production"] = mine_level * 2  # 2 gems per day per level
    
    # Resource Vault - Cash storage and production
    if structures["Resource Vault"]["unlocked"]:
        vault_level = structures["Resource Vault"]["level"]
        bonuses["cash_production"] = vault_level * 100  # 100 cash per day per level
    
    return bonuses

def get_structure_upgrade_cost(structure_name, current_level):
    """Calculate upgrade cost for a structure"""
    base_costs = {
        "Nightmare Laboratory": 500,
        "Summoning Chamber": 300,
        "Training Grounds": 1000,
        "Gem Mine": 2000,
        "Resource Vault": 800,
        "Research Center": 1500
    }
    
    base_cost = base_costs.get(structure_name, 500)
    return int(base_cost * (1.5 ** current_level))

def get_structure_unlock_cost(structure_name):
    """Get cost to unlock a new structure"""
    unlock_costs = {
        "Training Grounds": 1500,
        "Gem Mine": 3000,
        "Resource Vault": 2000,
        "Research Center": 2500
    }
    return unlock_costs.get(structure_name, 1000)

def show_facility_menu():
    global player_cash, player_gems
    
    while True:
        bonuses = get_facility_bonuses()
        
        print("\n" + "═" * 70)
        print(f"{Fore.CYAN}🏭 NIGHTMARE NEXUS FACILITY 🏭{Style.RESET_ALL}")
        print("═" * 70)
        print(f"{Fore.YELLOW}{GEM_SYMBOL} Gems: {player_gems:,}{Style.RESET_ALL} | {Fore.GREEN}{CASH_SYMBOL} Cash: {player_cash:,}{Style.RESET_ALL} | {Fore.MAGENTA}📊 Facility Lv.{facility_data['level']}{Style.RESET_ALL}")
        
        # Show facility bonuses
        print(f"\n{Fore.LIGHTGREEN_EX}🎯 ACTIVE BONUSES:{Style.RESET_ALL}")
        print(f"  👥 Unit Capacity: {bonuses['unit_capacity']} ({len(player_inventory)}/{bonuses['unit_capacity']})")
        if bonuses['xp_bonus'] > 0:
            print(f"  {XP_SYMBOL} XP Bonus: +{bonuses['xp_bonus']}%")
        if bonuses['summon_discount'] > 0:
            print(f"  💎 Summon Discount: -{bonuses['summon_discount']}%")
        if bonuses['upgrade_discount'] > 0:
            print(f"  🔧 Upgrade Discount: -{bonuses['upgrade_discount']}%")
        if bonuses['gem_production'] > 0:
            print(f"  💎 Daily Gems: +{bonuses['gem_production']}")
        if bonuses['cash_production'] > 0:
            print(f"  {CASH_SYMBOL} Daily Cash: +{bonuses['cash_production']}")
        
        print("\n🏗️  FACILITY OPTIONS:")
        print("┌" + "─" * 68 + "┐")
        print(f"│ {Fore.BLUE}1.{Style.RESET_ALL} 🔬 Structure Management - Upgrade and unlock facilities    │")
        print(f"│ {Fore.GREEN}2.{Style.RESET_ALL} ⚡ Unit Enhancement    - Enhance your nightmare units      │")
        print(f"│ {Fore.MAGENTA}3.{Style.RESET_ALL} 👥 Unit Collection     - View your assembled horrors       │")
        print(f"│ {Fore.YELLOW}4.{Style.RESET_ALL} 📈 Daily Operations    - Collect daily rewards             │")
        print(f"│ {Fore.RED}5.{Style.RESET_ALL} 🚪 Return to Main      - Exit facility management         │")
        print("└" + "─" * 68 + "┘")
        
        choice = input(f"{Fore.CYAN}➤ Select operation: {Style.RESET_ALL}")
        
        if choice == "1":
            structure_management_menu()
        elif choice == "2":
            upgrade_units()
        elif choice == "3":
            show_units()
            view_unit_details()
        elif choice == "4":
            collect_daily_rewards()
        elif choice == "5":
            break
        else:
            print(f"{Fore.RED}❌ Invalid choice. Please select 1-5.{Style.RESET_ALL}")
        
        autosave()

def structure_management_menu():
    """Menu for managing facility structures"""
    global player_cash, player_gems
    
    while True:
        print("\n" + "═" * 70)
        print(f"{Fore.CYAN}🏗️  STRUCTURE MANAGEMENT 🏗️{Style.RESET_ALL}")
        print("═" * 70)
        
        structures = facility_data["structures"]
        
        print(f"\n{Fore.LIGHTCYAN_EX}📋 FACILITY STRUCTURES:{Style.RESET_ALL}")
        
        structure_list = []
        for idx, (name, data) in enumerate(structures.items()):
            structure_list.append(name)
            
            if data["unlocked"]:
                level = data["level"]
                max_level = data["max_level"]
                
                # Structure icons
                icons = {
                    "Nightmare Laboratory": "🔬",
                    "Summoning Chamber": "✨",
                    "Training Grounds": "🥋",
                    "Gem Mine": "💎",
                    "Resource Vault": "🏦",
                    "Research Center": "🧪"
                }
                
                icon = icons.get(name, "🏗️")
                status = f"Level {level}/{max_level}"
                
                if level < max_level:
                    upgrade_cost = get_structure_upgrade_cost(name, level)
                    cost_text = f"({CASH_SYMBOL} {upgrade_cost:,} to upgrade)"
                else:
                    cost_text = "(MAX LEVEL)"
                
                color = Fore.GREEN if level == max_level else Fore.YELLOW
                print(f"  {color}{idx + 1}. {icon} {name:<20} - {status} {cost_text}{Style.RESET_ALL}")
            else:
                unlock_cost = get_structure_unlock_cost(name)
                print(f"  {Fore.RED}{idx + 1}. 🔒 {name:<20} - LOCKED ({CASH_SYMBOL} {unlock_cost:,} to unlock){Style.RESET_ALL}")
        
        print(f"\n{len(structures) + 1}. 🔙 Return to Facility Menu")
        
        choice = input(f"{Fore.CYAN}➤ Select structure: {Style.RESET_ALL}")
        
        try:
            choice_idx = int(choice) - 1
            if choice_idx == len(structures):
                break
            elif 0 <= choice_idx < len(structures):
                structure_name = structure_list[choice_idx]
                manage_structure(structure_name)
            else:
                print(f"{Fore.RED}❌ Invalid selection.{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}❌ Please enter a valid number.{Style.RESET_ALL}")

def manage_structure(structure_name):
    """Manage individual structure upgrades/unlocks"""
    global player_cash, player_gems
    
    structure = facility_data["structures"][structure_name]
    
    if not structure["unlocked"]:
        # Unlock structure
        unlock_cost = get_structure_unlock_cost(structure_name)
        print(f"\n🔓 UNLOCK {structure_name.upper()}")
        print(f"Cost: {CASH_SYMBOL} {unlock_cost:,}")
        
        # Show structure benefits
        benefits = {
            "Training Grounds": "Increases unit capacity by 10 per level",
            "Gem Mine": "Generates 2 gems per day per level",
            "Resource Vault": "Generates 100 cash per day per level",
            "Research Center": "Unlocks advanced unit research features"
        }
        
        if structure_name in benefits:
            print(f"Benefits: {benefits[structure_name]}")
        
        confirm = input(f"Unlock {structure_name}? (y/n): ").lower()
        if confirm == 'y':
            if player_cash >= unlock_cost:
                player_cash -= unlock_cost
                structure["unlocked"] = True
                structure["level"] = 1
                print(f"{Fore.GREEN}✅ {structure_name} unlocked!{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ Insufficient cash! Need {CASH_SYMBOL} {unlock_cost:,}.{Style.RESET_ALL}")
    else:
        # Upgrade structure
        if structure["level"] < structure["max_level"]:
            upgrade_cost = get_structure_upgrade_cost(structure_name, structure["level"])
            
            print(f"\n⬆️  UPGRADE {structure_name.upper()}")
            print(f"Current Level: {structure['level']}/{structure['max_level']}")
            print(f"Upgrade Cost: {CASH_SYMBOL} {upgrade_cost:,}")
            
            confirm = input(f"Upgrade {structure_name}? (y/n): ").lower()
            if confirm == 'y':
                if player_cash >= upgrade_cost:
                    player_cash -= upgrade_cost
                    structure["level"] += 1
                    
                    # Check facility level up
                    total_levels = sum(s["level"] for s in facility_data["structures"].values() if s["unlocked"])
                    new_facility_level = min(total_levels // 5 + 1, 20)  # Max facility level 20
                    if new_facility_level > facility_data["level"]:
                        facility_data["level"] = new_facility_level
                        facility_data["max_units"] = 50 + (new_facility_level - 1) * 25
                        print(f"{Fore.LIGHTMAGENTA_EX}🎉 Facility leveled up to Level {new_facility_level}! Unit capacity increased!{Style.RESET_ALL}")
                    
                    print(f"{Fore.GREEN}✅ {structure_name} upgraded to Level {structure['level']}!{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}❌ Insufficient cash! Need {CASH_SYMBOL} {upgrade_cost:,}.{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⭐ {structure_name} is already at maximum level!{Style.RESET_ALL}")

def collect_daily_rewards():
    """Collect daily rewards from facility structures"""
    global player_gems, player_cash
    
    bonuses = get_facility_bonuses()
    
    print(f"\n{Fore.LIGHTGREEN_EX}🎁 DAILY REWARDS COLLECTION 🎁{Style.RESET_ALL}")
    print("═" * 50)
    
    total_gems = bonuses['gem_production']
    total_cash = bonuses['cash_production']
    
    if total_gems > 0 or total_cash > 0:
        if total_gems > 0:
            player_gems += total_gems
            print(f"💎 Collected {total_gems} gems from Gem Mine!")
        
        if total_cash > 0:
            player_cash += total_cash
            print(f"{CASH_SYMBOL} Collected {total_cash} cash from Resource Vault!")
        
        print(f"\n{Fore.GREEN}✅ Daily rewards collected successfully!{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}📭 No daily rewards available. Upgrade your Gem Mine or Resource Vault!{Style.RESET_ALL}")
    
    input("\nPress Enter to continue...")

def upgrade_cost(base_unit, fodder_units):
    base = 100 + base_unit["level"] * 50
    fodder_cost = sum(50 + xp_values[u["entity"]["rarity"]] for u in fodder_units)
    return base + fodder_cost

def xp_needed(level):
    return 100 + (level - 1) * 50

def upgrade_units():
    global player_cash, player_items
    if len(player_inventory) < 1:
        print("\n❌ You need at least 1 unit to upgrade.")
        return
    
    # Enhanced unit selection display
    print("\n" + "═" * 70)
    print(f"{Fore.CYAN}⚡ UNIT ENHANCEMENT CENTER ⚡{Style.RESET_ALL}")
    print("═" * 70)
    
    print(f"{Fore.YELLOW}💼 Available Units ({len(player_inventory)} total):{Style.RESET_ALL}")
    for idx, u in enumerate(player_inventory):
        e = u["entity"]
        skill_info = f" SkillLv:{u.get('skill_level',0)}" if e["rarity"] in ["Epic", "Legendary"] and e["skill"] else ""
        xp_progress = f"{u['exp']}/{xp_needed(u['level'])}"
        
        # Color-coded level status
        level_color = Fore.GREEN if u['level'] >= 50 else Fore.YELLOW if u['level'] >= 25 else Fore.WHITE
        
        print(f"   {idx+1:2}. {rarity_colors[e['rarity']]}{e['name']:<15}{Style.RESET_ALL} │ {level_color}Lv.{u['level']:2}{Style.RESET_ALL} │ EXP: {xp_progress:<8} │ HP:{e['hp']:3} ATK:{e['attack']:2} DEF:{e['defense']:2}{skill_info}")
    
    print(f"\n{len(player_inventory)+1}. 🔙 Return to Facility")
    
    try:
        base_choice = input(f"\n{Fore.CYAN}➤ Select unit to upgrade: {Style.RESET_ALL}")
        base_idx = int(base_choice) - 1
        
        if base_idx == len(player_inventory):
            return
        if base_idx < 0 or base_idx >= len(player_inventory):
            print(f"{Fore.RED}❌ Invalid selection.{Style.RESET_ALL}")
            return
    except ValueError:
        print(f"{Fore.RED}❌ Please enter a valid number.{Style.RESET_ALL}")
        return
    
    base_unit = player_inventory[base_idx]
    base_entity = base_unit["entity"]
    
    # Show selected unit info
    print("\n" + "─" * 60)
    print(f"{Fore.LIGHTCYAN_EX}🎯 SELECTED UNIT:{Style.RESET_ALL}")
    skill_info = f" │ SkillLv:{base_unit.get('skill_level',0)}" if base_entity["rarity"] in ["Epic", "Legendary"] and base_entity["skill"] else ""
    print(f"   {rarity_colors[base_entity['rarity']]}{base_entity['name']}{Style.RESET_ALL} │ Level {base_unit['level']} │ EXP: {base_unit['exp']}/{xp_needed(base_unit['level'])}{skill_info}")
    print("─" * 60)
    
    # Enhanced upgrade options menu
    print(f"\n{Fore.YELLOW}🔧 UPGRADE OPTIONS:{Style.RESET_ALL}")
    print("┌" + "─" * 58 + "┐")
    print(f"│ {Fore.RED}1.{Style.RESET_ALL} 🍖 Use Fodder Units    - Sacrifice other units for XP  │")
    print(f"│ {Fore.BLUE}2.{Style.RESET_ALL} 🧪 Use XP Potions      - Consume stored experience     │")
    print(f"│ {Fore.GREEN}3.{Style.RESET_ALL} 📊 View Unit Details   - Check stats and abilities    │")
    print(f"│ {Fore.WHITE}4.{Style.RESET_ALL} ❌ Cancel Enhancement  - Return to unit selection     │")
    print("└" + "─" * 58 + "┘")
    
    choice = input(f"\n{Fore.CYAN}➤ Choose upgrade method: {Style.RESET_ALL}")
    
    if choice == "1":
        upgrade_with_fodder(base_unit, base_idx)
    elif choice == "2":
        upgrade_with_xp_pots(base_unit)
    elif choice == "3":
        view_unit_details_inline(base_unit)
        input("\nPress Enter to continue...")
        upgrade_units()  # Return to upgrade menu
    elif choice == "4":
        print(f"{Fore.YELLOW}🔙 Enhancement cancelled.{Style.RESET_ALL}")
        return
    else:
        print(f"{Fore.RED}❌ Invalid choice. Please select 1-4.{Style.RESET_ALL}")

def upgrade_with_fodder(base_unit, base_idx):
    """Enhanced fodder upgrade process with multiple selection methods"""
    global player_cash, player_inventory
    
    # Filter out the base unit for selection
    available_units = [(idx, u) for idx, u in enumerate(player_inventory) if idx != base_idx]
    
    if len(available_units) == 0:
        print(f"{Fore.YELLOW}⚠️ No other units available for fodder.{Style.RESET_ALL}")
        return
    
    print("\n" + "═" * 70)
    print(f"{Fore.RED}🍖 FODDER SELECTION 🍖{Style.RESET_ALL}")
    print("═" * 70)
    
    # Show available fodder units
    print(f"{Fore.YELLOW}🎯 Available Fodder Units:{Style.RESET_ALL}")
    for display_idx, (real_idx, u) in enumerate(available_units):
        e = u["entity"]
        xp_value = xp_values[e["rarity"]]
        skill_same = "🔥 SKILL UP!" if (e["name"] == base_unit["entity"]["name"] and 
                                      base_unit["entity"]["rarity"] in ["Epic", "Legendary"] and 
                                      base_unit["entity"]["skill"]) else ""
        
        print(f"   {display_idx+1:2}. {rarity_colors[e['rarity']]}{e['name']:<15}{Style.RESET_ALL} │ Lv.{u['level']:2} │ XP Value: {xp_value:3} │ {skill_same}")
    
    print("\n📝 SELECTION METHODS:")
    print("   • Single: Enter one number (e.g., '3')")
    print("   • Multiple: Space-separated numbers (e.g., '1 3 5 7')")
    print("   • Range: Use dash (e.g., '2-6' for units 2 through 6)")
    print("   • Rarity: 'common', 'rare', 'epic', 'legendary'")
    print("   • Mixed: Combine methods (e.g., '1-3 5 common')")
    
    fodder_input = input(f"\n{Fore.CYAN}➤ Select fodder units (or 'cancel'): {Style.RESET_ALL}").strip().lower()
    
    if fodder_input == 'cancel':
        return
    
    fodder_idxs = parse_fodder_selection(fodder_input, available_units, base_unit)
    
    if not fodder_idxs:
        print(f"{Fore.RED}❌ No valid fodder units selected.{Style.RESET_ALL}")
        return
    
    # Show selected fodder units
    selected_fodders = [player_inventory[i] for i in fodder_idxs]
    print(f"\n{Fore.LIGHTGREEN_EX}✅ SELECTED FODDER ({len(selected_fodders)} units):{Style.RESET_ALL}")
    
    total_xp = 0
    skill_ups = 0
    total_cost = 100 + base_unit["level"] * 50  # Base upgrade cost
    
    for u in selected_fodders:
        e = u["entity"]
        xp_val = xp_values[e["rarity"]]
        total_xp += xp_val
        total_cost += 50 + xp_val
        
        # Check for skill level up
        if (e["name"] == base_unit["entity"]["name"] and 
            base_unit["entity"]["rarity"] in ["Epic", "Legendary"] and 
            base_unit["entity"]["skill"]):
            skill_ups += 1
        
        skill_indicator = "🔥" if skill_ups > 0 else "  "
        print(f"   {skill_indicator} {rarity_colors[e['rarity']]}{e['name']:<15}{Style.RESET_ALL} │ Lv.{u['level']} │ +{xp_val} XP")
    
    # Calculate level predictions
    predicted_levels = calculate_level_gains(base_unit, total_xp)
    
    print("\n" + "─" * 50)
    print(f"{Fore.LIGHTCYAN_EX}📊 UPGRADE PREVIEW:{Style.RESET_ALL}")
    print(f"   💫 Total XP Gain: {total_xp:,}")
    print(f"   📈 Predicted Levels: {predicted_levels['levels_gained']} (Lv.{base_unit['level']} → Lv.{predicted_levels['final_level']})")
    if skill_ups > 0:
        current_skill = base_unit.get('skill_level', 1)
        print(f"   🔥 Skill Level Up: +{skill_ups} (Lv.{current_skill} → Lv.{min(current_skill + skill_ups, 5)})")
    print(f"   💰 Total Cost: ${total_cost:,}")
    print("─" * 50)
    
    if player_cash < total_cost:
        print(f"{Fore.RED}❌ Insufficient cash! Need ${total_cost:,}, have ${player_cash:,}.{Style.RESET_ALL}")
        return
    
    # Confirmation
    confirm = input(f"\n{Fore.YELLOW}⚡ Proceed with enhancement? (y/n): {Style.RESET_ALL}").lower()
    if confirm != 'y':
        print(f"{Fore.YELLOW}🔙 Enhancement cancelled.{Style.RESET_ALL}")
        return
    
    # Perform the upgrade
    perform_fodder_upgrade(base_unit, selected_fodders, fodder_idxs, total_cost, skill_ups)

def parse_fodder_selection(input_str, available_units, base_unit):
    """Parse various fodder selection methods"""
    selected_indices = set()
    tokens = input_str.split()
    
    for token in tokens:
        if token in ['common', 'rare', 'epic', 'legendary']:
            # Select by rarity
            target_rarity = token.title()
            for display_idx, (real_idx, u) in enumerate(available_units):
                if u["entity"]["rarity"] == target_rarity:
                    selected_indices.add(real_idx)
        
        elif '-' in token and token.replace('-', '').isdigit():
            # Handle range selection (e.g., "2-5")
            try:
                start, end = map(int, token.split('-'))
                for i in range(start-1, min(end, len(available_units))):
                    if 0 <= i < len(available_units):
                        selected_indices.add(available_units[i][0])
            except ValueError:
                continue
        
        elif token.isdigit():
            # Single unit selection
            idx = int(token) - 1
            if 0 <= idx < len(available_units):
                selected_indices.add(available_units[idx][0])
    
    return sorted(selected_indices, reverse=True)  # Reverse order for safe removal

def calculate_level_gains(base_unit, total_xp):
    """Calculate how many levels a unit will gain from XP"""
    current_level = base_unit["level"]
    current_xp = base_unit["exp"]
    remaining_xp = total_xp + current_xp
    
    levels_gained = 0
    test_level = current_level
    
    while remaining_xp >= xp_needed(test_level):
        remaining_xp -= xp_needed(test_level)
        test_level += 1
        levels_gained += 1
    
    return {
        'levels_gained': levels_gained,
        'final_level': test_level,
        'remaining_xp': remaining_xp
    }

def perform_fodder_upgrade(base_unit, selected_fodders, fodder_idxs, total_cost, skill_ups):
    """Execute the fodder upgrade with enhanced feedback"""
    global player_cash
    
    # Calculate total XP
    total_xp = sum(xp_values[u["entity"]["rarity"]] for u in selected_fodders)
    
    print(f"\n{Fore.LIGHTMAGENTA_EX}⚡ ENHANCEMENT IN PROGRESS... ⚡{Style.RESET_ALL}")
    
    # Remove fodder units (in reverse order to maintain indices)
    for idx in fodder_idxs:
        removed_unit = player_inventory.pop(idx)
        print(f"   🔥 {removed_unit['entity']['name']} sacrificed for {xp_values[removed_unit['entity']['rarity']]} XP")
    
    # Apply XP and level up
    base_unit["exp"] += total_xp
    levels_gained = 0
    
    while base_unit["exp"] >= xp_needed(base_unit["level"]):
        base_unit["exp"] -= xp_needed(base_unit["level"])
        base_unit["level"] += 1
        levels_gained += 1
        
        # Stat increases per level
        base_unit["entity"]["hp"] += 10
        base_unit["entity"]["attack"] += 2
        base_unit["entity"]["defense"] += 1
        
        if levels_gained % 5 == 0:  # Show every 5 levels to avoid spam
            print(f"   📈 {rarity_colors[base_unit['entity']['rarity']]}{base_unit['entity']['name']}{Style.RESET_ALL} reached Level {base_unit['level']}!")
    
    # Apply skill level ups
    if skill_ups > 0:
        base_unit.setdefault("skill_level", 1)
        old_skill_level = base_unit["skill_level"]
        base_unit["skill_level"] = min(base_unit["skill_level"] + skill_ups, 5)
        print(f"   🔥 Skill Level increased from {old_skill_level} to {base_unit['skill_level']}!")
    
    # Deduct cost
    player_cash -= total_cost
    
    # Final summary
    print(f"\n{Fore.LIGHTGREEN_EX}✅ ENHANCEMENT COMPLETE! ✅{Style.RESET_ALL}")
    print(f"   📊 {base_unit['entity']['name']} gained {levels_gained} levels (now Level {base_unit['level']})")
    print(f"   💰 Cost: ${total_cost:,} (Remaining: ${player_cash:,})")
    print(f"   💫 Remaining XP: {base_unit['exp']}/{xp_needed(base_unit['level'])}")
    
    # Auto-save after unit enhancement
    autosave()

def upgrade_with_xp_pots(base_unit):
    """Enhanced XP pot upgrade with better interface"""
    global player_items
    
    print("\n" + "═" * 60)
    print(f"{Fore.BLUE}🧪 XP POTION ENHANCEMENT 🧪{Style.RESET_ALL}")
    print("═" * 60)
    
    # Show available XP pots
    print(f"{Fore.YELLOW}📦 Available XP Potions:{Style.RESET_ALL}")
    pot_info = [
        ("Small XP Pot", 10, "🧪"),
        ("Medium XP Pot", 20, "🧪"),
        ("Large XP Pot", 50, "🧪")
    ]
    
    total_available = sum(player_items[pot[0]] for pot in pot_info)
    if total_available == 0:
        print(f"{Fore.RED}❌ No XP potions available!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💡 Tip: Earn XP potions from battle rewards or events.{Style.RESET_ALL}")
        return
    
    for name, xp_value, icon in pot_info:
        count = player_items[name]
        color = Fore.GREEN if count > 0 else Fore.RED
        print(f"   {icon} {color}{name:<15}{Style.RESET_ALL} │ Count: {count:3} │ XP Value: {xp_value} each │ Total: {count * xp_value}")
    
    print(f"\n{Fore.LIGHTCYAN_EX}🎯 Current Unit:{Style.RESET_ALL}")
    print(f"   {rarity_colors[base_unit['entity']['rarity']]}{base_unit['entity']['name']}{Style.RESET_ALL} │ Level {base_unit['level']} │ XP: {base_unit['exp']}/{xp_needed(base_unit['level'])}")
    
    # XP pot selection
    print(f"\n{Fore.YELLOW}💊 Select XP Potions to Use:{Style.RESET_ALL}")
    
    use_amounts = {}
    total_xp_gain = 0
    
    for name, xp_value, icon in pot_info:
        available = player_items[name]
        if available > 0:
            while True:
                try:
                    amount = input(f"   {icon} How many {name}s? (0-{available}): ")
                    amount = int(amount)
                    if 0 <= amount <= available:
                        use_amounts[name] = amount
                        total_xp_gain += amount * xp_value
                        break
                    else:
                        print(f"     {Fore.RED}❌ Invalid amount. Enter 0-{available}.{Style.RESET_ALL}")
                except ValueError:
                    print(f"     {Fore.RED}❌ Please enter a valid number.{Style.RESET_ALL}")
        else:
            use_amounts[name] = 0
    
    if total_xp_gain == 0:
        print(f"{Fore.YELLOW}🔙 No potions selected.{Style.RESET_ALL}")
        return
    
    # Calculate level prediction
    predicted = calculate_level_gains(base_unit, total_xp_gain)
    
    # Show summary
    print("\n" + "─" * 50)
    print(f"{Fore.LIGHTCYAN_EX}📊 POTION ENHANCEMENT PREVIEW:{Style.RESET_ALL}")
    for name, amount in use_amounts.items():
        if amount > 0:
            xp_per_pot = next(pot[1] for pot in pot_info if pot[0] == name)
            print(f"   🧪 {name}: {amount} × {xp_per_pot} = {amount * xp_per_pot} XP")
    print(f"   💫 Total XP Gain: {total_xp_gain:,}")
    print(f"   📈 Level Gain: {predicted['levels_gained']} (Lv.{base_unit['level']} → Lv.{predicted['final_level']})")
    print("─" * 50)
    
    # Confirmation
    confirm = input(f"\n{Fore.YELLOW}⚡ Use these potions? (y/n): {Style.RESET_ALL}").lower()
    if confirm != 'y':
        print(f"{Fore.YELLOW}🔙 Enhancement cancelled.{Style.RESET_ALL}")
        return
    
    # Apply the upgrade
    perform_potion_upgrade(base_unit, use_amounts, total_xp_gain, predicted)

def perform_potion_upgrade(base_unit, use_amounts, total_xp_gain, predicted):
    """Execute XP potion upgrade"""
    global player_items
    
    print(f"\n{Fore.LIGHTMAGENTA_EX}🧪 POTION ENHANCEMENT IN PROGRESS... 🧪{Style.RESET_ALL}")
    
    # Deduct potions
    for name, amount in use_amounts.items():
        if amount > 0:
            player_items[name] -= amount
            print(f"   🧪 Used {amount} {name}(s)")
    
    # Apply XP and level up
    base_unit["exp"] += total_xp_gain
    levels_gained = 0
    
    while base_unit["exp"] >= xp_needed(base_unit["level"]):
        base_unit["exp"] -= xp_needed(base_unit["level"])
        base_unit["level"] += 1
        levels_gained += 1
        
        # Stat increases per level
        base_unit["entity"]["hp"] += 10
        base_unit["entity"]["attack"] += 2
        base_unit["entity"]["defense"] += 1
        
        if levels_gained % 5 == 0:
            print(f"   📈 {rarity_colors[base_unit['entity']['rarity']]}{base_unit['entity']['name']}{Style.RESET_ALL} reached Level {base_unit['level']}!")
    
    # Final summary
    print(f"\n{Fore.LIGHTGREEN_EX}✅ POTION ENHANCEMENT COMPLETE! ✅{Style.RESET_ALL}")
    print(f"   📊 {base_unit['entity']['name']} gained {levels_gained} levels (now Level {base_unit['level']})")
    print(f"   💫 Remaining XP: {base_unit['exp']}/{xp_needed(base_unit['level'])}")
    
    # Show remaining potions
    print(f"\n{Fore.LIGHTCYAN_EX}📦 Remaining Potions:{Style.RESET_ALL}")
    for name in player_items:
        if "XP Pot" in name:
            print(f"   🧪 {name}: {player_items[name]}")
    
    # Auto-save after using potions
    autosave()

def view_unit_details_inline(unit):
    """Display unit details inline during upgrade process"""
    e = unit["entity"]
    skill_lv = unit.get('skill_level', 1 if e["rarity"] in ["Epic", "Legendary"] and e["skill"] else 0)
    
    print("\n" + "═" * 70)
    print(f"{Fore.LIGHTCYAN_EX}📊 UNIT DETAILS: {rarity_colors[e['rarity']]}{e['name']}{Style.RESET_ALL}")
    print("═" * 70)
    
    # Basic stats
    print(f"{Fore.YELLOW}📈 STATS:{Style.RESET_ALL}")
    print(f"   🔢 Level: {unit['level']} │ ⭐ XP: {unit['exp']}/{xp_needed(unit['level'])}")
    print(f"   ❤️  HP: {e['hp']} │ ⚔️  ATK: {e['attack']} │ 🛡️  DEF: {e['defense']} │ ⚡ SPD: {e['speed']} │ 💥 CRIT: {e.get('crit_rate', 0)}%")
    print(f"   🌟 Rarity: {rarity_colors[e['rarity']]}{e['rarity']}{Style.RESET_ALL}")
    
    # Description
    if "description" in e:
        print(f"\n{Fore.YELLOW}📖 DESCRIPTION:{Style.RESET_ALL}")
        print(f"   {e['description']}")
    
    # Active skill
    if e['skill'] and skill_lv > 0:
        print(f"\n{Fore.YELLOW}✨ ACTIVE SKILL:{Style.RESET_ALL}")
        skill_desc = get_skill_description(e['skill'], skill_lv)
        print(f"   {skill_desc}")
    
    # Passive skill
    passive = e.get('passive')
    if passive and passive != "None":
        print(f"\n{Fore.YELLOW}🔮 PASSIVE SKILL:{Style.RESET_ALL}")
        print(f"   {passive}")
    
    print("═" * 70)

# ==========================
# Unit Display & Selection
# ==========================

def show_units():
    if not player_inventory:
        print("No units.")
        return

    print(f"\n👥 Units ({len(player_inventory)}):")
    for idx, u in enumerate(player_inventory):
        e = u["entity"]
        skill_lv = f"S{u.get('skill_level',0)}" if e["rarity"] in ["Epic", "Legendary"] and e["skill"] else ""
        print(f"{idx+1:2}. {rarity_colors[e['rarity']]}{e['name'][:12]:<12}{Style.RESET_ALL} Lv{u['level']:2} {e['hp']:3}HP {e['attack']:2}ATK {skill_lv}")

def get_skill_description(skill, skill_lv):
    """Get detailed skill description with level scaling"""
    if skill == "joyful_regeneration":  # SCP-999
        base_heal = 8 + (skill_lv * 4)  # 12% at lv1 -> 28% at lv5
        heal_turns = 3 + skill_lv  # 4 turns at lv1 -> 8 turns at lv5
        atk_buff = 10 + (skill_lv * 5)  # 15% at lv1 -> 35% at lv5
        def_buff = 10 + (skill_lv * 5)  # 15% at lv1 -> 35% at lv5
        
        desc = f"🧡 Joyful Regeneration (Level {skill_lv})\n"
        desc += f"   💚 Heals all allies {base_heal}% HP per turn for {heal_turns} turns\n"
        desc += f"   ⚔️ Grants +{atk_buff}% Attack buff for {heal_turns} turns\n"
        desc += f"   🛡️ Grants +{def_buff}% Defense buff for {heal_turns} turns"
        
        if skill_lv >= 3:
            desc += f"\n   ✨ Bonus: Removes all debuffs from party"
        if skill_lv == 5:
            desc += f"\n   🌟 MASTERY: +25% heal effectiveness on all healing"
        
        return desc
        
    elif skill == "killer_burst":  # Jeff the Killer
        crit_rate = min(25 + (skill_lv * 15), 100)  # 40% at lv1 -> 100% at lv5
        bleed_power = 10 + (skill_lv * 5)  # 15% at lv1 -> 35% at lv5
        speed_buff = 15 + (skill_lv * 5)  # 20% at lv1 -> 40% at lv5
        
        desc = f"🔪 Killer Burst (Level {skill_lv})\n"
        desc += f"   💥 Guaranteed critical hit with {crit_rate}% base crit rate\n"
        desc += f"   🩸 Inflicts bleed dealing {bleed_power}% ATK per turn for 4 turns\n"
        desc += f"   💨 Grants team +{speed_buff}% Speed for 3 turns\n"
        desc += f"   👻 Jeff gains Ghost status on crit (untargetable)"
        
        if skill_lv >= 3:
            desc += f"\n   ✨ Bonus: Resets skill cooldown on kill"
        if skill_lv == 5:
            desc += f"\n   🌟 MASTERY: Multiple kills grant permanent ATK stacks"
            
        return desc
        
    elif skill == "bloody_smile":  # Kuchisake-onna
        bleed_dmg = 8 + (skill_lv * 3)  # 11% at lv1 -> 23% at lv5
        crit_buff = 25 + (skill_lv * 15)  # 40% at lv1 -> 100% at lv5
        fear_chance = skill_lv * 15  # 15% at lv1 -> 75% at lv5
        
        desc = f"😈 Bloody Smile (Level {skill_lv})\n"
        desc += f"   🩸 All enemies bleed for {bleed_dmg}% ATK per turn (4 turns)\n"
        desc += f"   💥 Team gains +{crit_buff}% Crit Rate for 3 turns\n"
        desc += f"   😰 {fear_chance}% chance to inflict Fear (skip turn)"
        
        if skill_lv >= 3:
            desc += f"\n   ✨ Bonus: Bleeding enemies take +50% crit damage"
        if skill_lv == 5:
            desc += f"\n   🌟 MASTERY: Fear spreads to adjacent enemies"
            
        return desc
        
    elif skill == "mothmans_omen":  # Mothman
        atk_debuff = 15 + (skill_lv * 8)  # 23% at lv1 -> 55% at lv5
        vision_debuff = skill_lv * 10  # 10% at lv1 -> 50% at lv5
        duration = 2 + skill_lv  # 3 turns at lv1 -> 7 turns at lv5
        
        desc = f"🦋 Mothman's Omen (Level {skill_lv})\n"
        desc += f"   ⚔️ Reduces all enemies' Attack by {atk_debuff}% for {duration} turns\n"
        desc += f"   👁️ Reduces accuracy by {vision_debuff}% (miss chance)\n"
        desc += f"   🔮 Reveals enemy intentions (shows next action)"
        
        if skill_lv >= 3:
            desc += f"\n   ✨ Bonus: Debuffed enemies move 30% slower"
        if skill_lv == 5:
            desc += f"\n   🌟 MASTERY: Omen spreads fear, reducing enemy SP generation"
            
        return desc
        
    elif skill == "mirror_curse":  # Bloody Mary
        reflect_dmg = 15 + (skill_lv * 10)  # 25% at lv1 -> 65% at lv5
        curse_duration = 2 + skill_lv  # 3 turns at lv1 -> 7 turns at lv5
        lifesteal = skill_lv * 5  # 5% at lv1 -> 25% at lv5
        
        desc = f"🪞 Mirror Curse (Level {skill_lv})\n"
        desc += f"   🔄 Party reflects {reflect_dmg}% damage for {curse_duration} turns\n"
        desc += f"   🩸 Reflected damage heals team for {lifesteal}% of damage\n"
        desc += f"   👁️ Attackers see disturbing visions (accuracy debuff)"
        
        if skill_lv >= 3:
            desc += f"\n   ✨ Bonus: Curse spreads on attacker death"
        if skill_lv == 5:
            desc += f"\n   🌟 MASTERY: Mirror fragments cause bleeding"
            
        return desc
        
    elif skill == "night_ambush":  # The Rake
        base_dmg = 80 + (skill_lv * 20)  # 100% at lv1 -> 180% at lv5
        bleed_dmg = 12 + (skill_lv * 4)  # 16% at lv1 -> 32% at lv5
        stealth_turns = skill_lv  # 1 turn at lv1 -> 5 turns at lv5
        
        desc = f"🌙 Night Ambush (Level {skill_lv})\n"
        desc += f"   🗡️ AOE attack dealing {base_dmg}% ATK to all enemies\n"
        desc += f"   🩸 Inflicts bleed ({bleed_dmg}% ATK per turn for 5 turns)\n"
        desc += f"   👻 Grants stealth for {stealth_turns} turns (untargetable)"
        
        if skill_lv >= 3:
            desc += f"\n   ✨ Bonus: Kills in stealth reset stealth duration"
        if skill_lv == 5:
            desc += f"\n   🌟 MASTERY: Each kill increases damage by 25%"
            
        return desc
        
    elif skill == "faceless_terror":  # Slender
        atk_debuff = 20 + (skill_lv * 8)  # 28% at lv1 -> 52% at lv5
        def_debuff = 20 + (skill_lv * 8)  # 28% at lv1 -> 52% at lv5
        page_stacks = skill_lv  # 1 stack at lv1 -> 5 stacks at lv5
        
        desc = f"📄 Faceless Terror (Level {skill_lv})\n"
        desc += f"   ⚔️ Reduces all enemies' ATK by {atk_debuff}% for 4 turns\n"
        desc += f"   🛡️ Reduces all enemies' DEF by {def_debuff}% for 4 turns\n"
        desc += f"   📋 Applies {page_stacks} Eight Pages stacks to each enemy"
        
        if skill_lv >= 3:
            desc += f"\n   ✨ Bonus: Enemies with 4+ pages lose SP per turn"
        if skill_lv == 5:
            desc += f"\n   🌟 MASTERY: Page collection grants team buffs"
            
        return desc
        
    elif skill == "analog_distortion":  # Iris
        def_debuff = 30 + (skill_lv * 15)  # 45% at lv1 -> 90% at lv5
        sp_gain = 8 + (skill_lv * 4)  # 12 at lv1 -> 28 at lv5
        reality_dmg = skill_lv * 10  # 10% at lv1 -> 50% at lv5
        
        desc = f"📺 Analog Distortion (Level {skill_lv})\n"
        desc += f"   🛡️ Reduces all enemies' DEF by {def_debuff}% for 4 turns\n"
        desc += f"   ⚡ Team gains {sp_gain} SP immediately\n"
        desc += f"   🌀 Reality damage: {reality_dmg}% max HP to all enemies"
        
        if skill_lv >= 3:
            desc += f"\n   ✨ Bonus: Distortion creates afterimages (team evasion)"
        if skill_lv == 5:
            desc += f"\n   🌟 MASTERY: Reality breaks - enemies skip random turns"
            
        return desc
        
    elif skill == "indestructible_regeneration":  # SCP-682
        heal_percent = 30 + (skill_lv * 15)  # 45% at lv1 -> 105% at lv5
        def_gain = 8 + (skill_lv * 4)  # 12% at lv1 -> 28% at lv5
        taunt_duration = 2 + skill_lv  # 3 turns at lv1 -> 7 turns at lv5
        
        desc = f"🦎 Indestructible Regeneration (Level {skill_lv})\n"
        desc += f"   💚 Heals self {heal_percent}% max HP over 3 turns\n"
        desc += f"   🛡️ Gains +{def_gain}% DEF permanently (stacks)\n"
        desc += f"   🎯 Taunts all enemies for {taunt_duration} turns"
        
        if skill_lv >= 3:
            desc += f"\n   ✨ Bonus: Damage taken heals other party members"
        if skill_lv == 5:
            desc += f"\n   🌟 MASTERY: Becomes more powerful when damaged"
            
        return desc
    
    return "No skill description available."

def view_unit_details():
    if not player_inventory:
        return
    
    try:
        sel = int(input("Unit #: ")) - 1
        if not (0 <= sel < len(player_inventory)):
            return
    except ValueError:
        return
    
    u = player_inventory[sel]
    e = u["entity"]
    skill_lv = u.get('skill_level', 1)
    
    print(f"\n{rarity_colors[e['rarity']]}{e['name']}{Style.RESET_ALL} Lv{u['level']} | {e['hp']}HP {e['attack']}ATK {e['defense']}DEF")
    
    if e['skill']:
        print(f"✨ {e['skill'].replace('_',' ').title()} (Lv{skill_lv})")
    
    passive = e.get('passive')
    if passive and passive != "None":
        print(f"🔮 {passive}")

def select_team():
    if len(player_inventory) < 1:
        print("Need at least 1 unit.")
        return None
    
    show_units()
    selected = []
    print(f"\nTeam (max 4):")
    
    while len(selected) < 4:
        try:
            choice = input(f"Unit {len(selected)+1} (# or Enter to finish): ").strip()
            if not choice and len(selected) >= 1:
                break
            
            idx = int(choice) - 1
            if 0 <= idx < len(player_inventory) and player_inventory[idx] not in selected:
                selected.append(player_inventory[idx])
                name = player_inventory[idx]["entity"]["name"]
                print(f"✓ {name}")
        except (ValueError, IndexError):
            if choice:
                print("Invalid.")
    
    return selected

def get_enemy_for_stage(world_idx, stage_idx, phase, boss=False):
    base_hp = 40 + world_idx*30 + stage_idx*10 + phase*10
    base_atk = 5 + world_idx*5 + stage_idx*2 + phase*2
    base_def = 2 + world_idx*2 + stage_idx + phase
    base_spd = 10 + world_idx*2 + stage_idx + phase
    if boss:
        possible = [e for e in entities if e["rarity"] in ["Epic", "Legendary"]]
        entity = random.choice(possible)
        hp = int(base_hp * 2.5)
        atk = int(base_atk * 2)
        defense = int(base_def * 2)
        speed = int(entity["speed"] * 1.2)
        crit_rate = entity.get("crit_rate", 0)
    else:
        possible = [e for e in entities if e["rarity"] in ["Common", "Rare"]]
        entity = random.choice(possible)
        hp = int(base_hp * (1.2 if entity["rarity"] == "Rare" else 1))
        atk = int(base_atk * (1.2 if entity["rarity"] == "Rare" else 1))
        defense = int(base_def * (1.2 if entity["rarity"] == "Rare" else 1))
        speed = int(entity["speed"] * 1.1)
        crit_rate = entity.get("crit_rate", 0)
    return {
        "name": entity["name"],
        "rarity": entity["rarity"],
        "hp": hp,
        "max_hp": hp,
        "attack": atk,
        "defense": defense,
        "speed": speed,
        "skill": entity["skill"],
        "skill_level": 1 if entity["rarity"] in ["Epic", "Legendary"] and entity["skill"] else 0,
        "sp": 0,
        "effects": [],
        "crit_rate": crit_rate
    }

# ==========================
# Battle System
# ==========================

def apply_eight_pages(target):
    stacks = 0
    for eff in target.get("effects", []):
        if eff.get("type") == "eight_pages":
            stacks = eff["stacks"]
            eff["stacks"] += 1
            eff["turns"] = 999
            break
    else:
        target["effects"].append({"type": "eight_pages", "stacks": 1, "turns": 999})
    stacks += 1
    speed = target["entity"]["speed"] if "entity" in target else target.get("speed", 10)
    defense = target["entity"]["defense"] if "entity" in target else target.get("defense", 2)
    name = target["entity"]["name"] if "entity" in target else target.get("name", "Enemy")
    target["effects"].append({"type": "debuff", "stat": "speed", "amount": int(speed * 0.05), "turns": 999, "source": "Slender"})
    target["effects"].append({"type": "debuff", "stat": "defense", "amount": int(defense * 0.05), "turns": 999, "source": "Slender"})
    if stacks >= 8:
        target["effects"].append({"type": "stun", "turns": 3, "source": "Slender"})
        target["effects"] = [e for e in target["effects"] if e.get("type") != "eight_pages"]
        print(f"{name} is stunned by Eight Pages!")

def apply_scp682_defense(unit):
    defense = unit["entity"]["defense"] if "entity" in unit else unit.get("defense", 2)
    unit["effects"].append({"type": "buff", "stat": "defense", "amount": int(defense * 0.05), "turns": 999, "source": "SCP-682"})

def process_effects(unit):
    remove = []
    for effect in unit.get("effects", []):
        hp_key = "battle_hp" if "battle_hp" in unit else "hp"
        if effect["type"] == "heal":
            unit[hp_key] = min(unit[hp_key] + effect["amount"], unit.get("entity", unit).get("hp", unit.get("max_hp", 9999)))
            print(f"{unit.get('entity', unit).get('name', 'Enemy')} heals {effect['amount']} HP!")
            effect["turns"] -= 1
        elif effect["type"] == "bleed":
            unit[hp_key] -= effect["amount"]
            print(f"{unit.get('entity', unit).get('name', 'Enemy')} takes {effect['amount']} bleed damage!")
            effect["turns"] -= 1
        elif effect["type"] == "buff" or effect["type"] == "debuff":
            effect["turns"] -= 1
        elif effect["type"] == "stun":
            effect["turns"] -= 1
        elif effect["type"] == "ghost":
            effect["turns"] -= 1
        elif effect["type"] == "taunt":
            effect["turns"] -= 1
        if effect["turns"] <= 0:
            remove.append(effect)
    unit["effects"] = [e for e in unit.get("effects", []) if e not in remove]

def get_effective_stat(unit, stat):
    value = unit["entity"].get(stat, 0) if "entity" in unit else unit.get(stat, 0)
    sources = set()
    for effect in unit.get("effects", []):
        if effect.get("stat") == stat:
            src = effect.get("source", None)
            if src and src in sources:
                continue
            sources.add(src)
            if effect["type"] == "buff":
                value += effect["amount"]
            elif effect["type"] == "debuff":
                value -= effect["amount"]
    return max(0, value)

def is_stunned(unit):
    return any(eff.get("type") == "stun" and eff.get("turns", 0) > 0 for eff in unit.get("effects", []))

def has_ghost(unit):
    return sum(eff.get("type") == "ghost" and eff.get("turns", 0) > 0 for eff in unit.get("effects", [])) > 0

def has_taunt(team):
    for u in team:
        if any(eff.get("type") == "taunt" and eff.get("turns", 0) > 0 for eff in u.get("effects", [])):
            return u
    return None

def calculate_damage(attacker, defender, is_enemy=False, force_crit=False):
    # Support both player and enemy units
    if "entity" in attacker:
        atk = get_effective_stat(attacker, "attack")
        name = attacker["entity"]["name"]
        crit_rate = get_effective_stat(attacker, "crit_rate")
        # Jeff crit rate scaling
        if name == "Jeff the Killer":
            skill_lv = attacker.get("skill_level", 1)
            crit_rate = min(30 + 10 * (skill_lv - 1), 80)
    else:
        atk = get_effective_stat(attacker, "attack")
        name = attacker.get("name", "")
        crit_rate = attacker.get("crit_rate", 0)
        if name == "Jeff the Killer":
            skill_lv = attacker.get("skill_level", 1)
            crit_rate = min(30 + 10 * (skill_lv - 1), 80)

    def_stat = get_effective_stat(defender, "defense")
    is_crit = force_crit or (random.randint(1, 100) <= crit_rate)
    if is_crit:
        dmg = atk * 2
        print(f"{Fore.RED}CRIT!{Style.RESET_ALL}", end=' ')
    else:
        dmg = max(1, atk - def_stat)
    return int(dmg), is_crit

def drop_items(stage):
    drops = []
    roll = random.randint(1,100)
    if roll <= min(10 + stage, 50):
        drops.append("Small XP Pot")
    if roll <= min(5 + stage//2, 30):
        drops.append("Medium XP Pot")
    if roll <= min(2 + stage//4, 15):
        drops.append("Large XP Pot")
    for item in drops:
        player_items[item] += 1
    print("You received:", ", ".join(drops) if drops else "No items.")

def use_skill(unit, team, enemies):
    skill = unit["entity"]["skill"]
    lvl = min(unit.get("skill_level", 1), 5)
    name = unit["entity"]["name"]
    if skill == "joyful_regeneration":  # SCP-999
        heal_percent = 0.10 + 0.025 * (lvl - 1)
        heal_turns = 5
        heal_boost = 0.0 if lvl < 5 else 0.2
        for u in team:
            u["effects"].append({"type": "heal", "amount": int(u["entity"]["hp"] * heal_percent), "turns": heal_turns, "source": name})
            if heal_boost > 0:
                u["effects"].append({"type": "buff", "stat": "heal_boost", "amount": heal_boost, "turns": heal_turns, "source": name})
            u["effects"].append({"type": "buff", "stat": "attack", "amount": int(u["entity"]["attack"] * 0.2), "turns": heal_turns, "source": name})
            u["effects"].append({"type": "buff", "stat": "defense", "amount": int(u["entity"]["defense"] * 0.2), "turns": heal_turns, "source": name})
        print(f"{name} uses 'Joyful Regeneration'! Party heals {int(heal_percent*100)}% HP per turn for {heal_turns} turns and gains ATK/DEF up. Max skill adds 20% heal boost.")
    elif skill == "killer_burst":  # Jeff the Killer
        target = choose_enemy(enemies)
        crit_dmg, is_crit = calculate_damage(unit, target, force_crit=True)
        target["hp"] -= crit_dmg
        target["effects"].append({"type": "bleed", "amount": int(unit["entity"]["attack"] * 0.15 * lvl), "turns": 3, "source": name})
        for u in team:
            u["effects"].append({"type": "buff", "stat": "speed", "amount": int(u["entity"]["speed"] * 0.2), "turns": 3, "source": name})
        if is_crit:
            unit["effects"].append({"type": "ghost", "turns": 3, "source": name})
        print(f"{name} uses 'Killer Burst'! Deals {Fore.RED}{crit_dmg}{Style.RESET_ALL} crit damage, inflicts bleed, and boosts team speed.")
    elif skill == "bloody_smile":  # Kuchisake-onna
        for e in enemies:
            if e["hp"] > 0:
                e["effects"].append({"type": "bleed", "amount": int(unit["entity"]["attack"] * 0.1 * lvl), "turns": 3, "source": name})
        for u in team:
            u["effects"].append({"type": "buff", "stat": "crit_rate", "amount": 100, "turns": 2, "source": name})
        print(f"{name} uses 'Bloody Smile'! All enemies take bleed, team crit rate boosted for 2 turns.")
    elif skill == "mothmans_omen":  # Mothman
        for e in enemies:
            if e["hp"] > 0:
                e["effects"].append({"type": "debuff", "stat": "attack", "amount": int(e["attack"] * 0.2), "turns": 3, "source": name})
        print(f"{name} uses 'Mothman's Omen'! All enemies lose 20% ATK for 3 turns.")
    elif skill == "mirror_curse":  # Bloody Mary
        for u in team:
            u["effects"].append({"type": "buff", "stat": "curse", "amount": 0.2, "turns": 3, "source": name})
        print(f"{name} uses 'Mirror Curse'! Party reflects 20% damage for 3 turns.")
    elif skill == "night_ambush":  # The Rake
        for e in enemies:
            if e["hp"] > 0:
                aoe_dmg, _ = calculate_damage(unit, e)
                e["hp"] -= aoe_dmg
                e["effects"].append({"type": "bleed", "amount": int(unit["entity"]["attack"] * 0.1 * lvl), "turns": 3, "source": name})
        print(f"{name} uses 'Night Ambush'! Burst damage and bleed to all enemies.")
    elif skill == "faceless_terror":  # Slender
        for e in enemies:
            if e["hp"] > 0:
                e["effects"].append({"type": "debuff", "stat": "attack", "amount": int(e["attack"] * 0.3), "turns": 3, "source": name})
                e["effects"].append({"type": "debuff", "stat": "defense", "amount": int(e["defense"] * 0.3), "turns": 3, "source": name})
        print(f"{name} uses 'Faceless Terror'! All enemies lose 30% ATK/DEF for 3 turns.")
    elif skill == "analog_distortion":  # Iris
        for e in enemies:
            if e["hp"] > 0:
                e["effects"].append({"type": "debuff", "stat": "defense", "amount": int(e["defense"] * 0.5), "turns": 3, "source": name})
        for u in team:
            u["sp"] += 5
        print(f"{name} uses 'Analog Distortion'! All enemies lose 50% DEF for 3 turns, party gains SP.")
    elif skill == "indestructible_regeneration":  # SCP-682
        unit["effects"].append({"type": "heal", "amount": int(unit["entity"]["hp"] * 0.5), "turns": 3, "source": name})
        unit["effects"].append({"type": "buff", "stat": "defense", "amount": int(unit["entity"]["defense"] * 0.1), "turns": 3, "source": name})
        unit["effects"].append({"type": "taunt", "turns": 3, "source": name})
        print(f"{name} uses 'Indestructible Regeneration'! Heals self, gains DEF up, and taunts for 3 turns.")

def choose_enemy(enemies, team=None):
    alive = [e for e in enemies if e["hp"] > 0]
    if not alive:
        return None
    print("Choose enemy to target:")
    for idx, e in enumerate(alive):
        print(f"{idx+1}. {rarity_colors[e['rarity']]}{e['name']}{Style.RESET_ALL} HP:{e['hp']}")
    while True:
        try:
            choice = int(input("Enemy number: ")) - 1
            if 0 <= choice < len(alive):
                return alive[choice]
        except:
            pass
        print("Invalid choice.")

def turn_based_battle(team, world_idx, stage_idx):
    global player_cash, player_xp, player_gems
    print(f"\n🏰 Entering {worlds[world_idx]['name']} - Stage {stage_idx+1}")
    phases = 3
    boss_stage = (stage_idx+1) % 10 == 0
    # Persist stats and effects across phases
    for phase in range(phases):
        print(f"\n--- Phase {phase+1} ---")
        num_enemies = random.randint(2, 4) if not (boss_stage and phase == phases-1) else random.randint(1, 2)
        enemies = []
        for _ in range(num_enemies):
            boss = boss_stage and phase == phases-1
            e = get_enemy_for_stage(world_idx, stage_idx, phase, boss)
            e["sp"] = 100
            e["effects"] = []
            enemies.append(e)
        # Initialize team only on first phase
        if phase == 0:
            for unit in team:
                unit["battle_hp"] = unit["entity"]["hp"]
                unit["sp"] = 100
                unit["defending"] = False
                unit["effects"] = []
                # Jeff starts with 3 ghost stacks (single effect with 3 stacks)
                if unit["entity"]["name"] == "Jeff the Killer":
                    unit["effects"].append({"type": "ghost", "turns": 3, "stacks": 3, "source": "Jeff the Killer"})
        while any(e["hp"] > 0 for e in enemies) and any(u["battle_hp"] > 0 for u in team):
            combatants = [{"type": "player", "unit": u} for u in team if u["battle_hp"] > 0] + [{"type": "enemy", "unit": e} for e in enemies if e["hp"] > 0]
            combatants.sort(key=lambda c: c["unit"]["entity"]["speed"] if c["type"] == "player" else c["unit"]["speed"], reverse=True)
            for idx, c in enumerate(combatants):
                if not any(u["battle_hp"] > 0 for u in team):
                    print("💀 Your team was defeated!")
                    autosave()
                    drop_items(stage_idx+1)
                    return
                unit = c["unit"]
                process_effects(unit)
                unit["sp"] += 10
                unit["defending"] = False
                if is_stunned(unit):
                    name = unit["entity"]["name"] if c["type"] == "player" else unit["name"]
                    print(f"⚡ {name} is stunned and cannot act!")
                    continue
                if c["type"] == "player":
                    while True:
                        # Clear display
                        display_battle_header(unit, True)
                        
                        # Show turn order (next 3 units)
                        display_turn_order(combatants, idx)
                        
                        # Show team summary
                        display_team_summary(team)
                        
                        # Show enemies cleanly
                        display_enemies_clean(enemies)
                        
        # Compact action menu
                        actions = ["1.⚔️Attack", "3.🛡️Defend", "4.🚪Quit"]
                        if unit["entity"]["skill"] and unit["sp"] >= skill_costs.get(unit["entity"]["skill"], 999):
                            actions.insert(1, "2.✨Skill")
                        
                        print(f"\n{' | '.join(actions)}")
                        action = input("Action: ")
                        
                        if action == "1":
                            target = choose_enemy(enemies)
                            if target:
                                # Slender Eight Pages
                                if unit["entity"]["name"] == "Slender":
                                    apply_eight_pages(target)
                                dmg, is_crit = calculate_damage(unit, target)
                                target["hp"] -= dmg
                                crit_icon = "💥" if is_crit else "⚔️"
                                print(f"{crit_icon} {dmg} → {target['name']}")
                                # Slender applies Eight Pages when attacked
                                if target["name"] == "Slender":
                                    apply_eight_pages(unit)
                                # Bloody Mary bleed counter
                                if target["name"] == "Bloody Mary":
                                    bleed_amount = int(target.get("attack", 10) * 0.1)
                                    if random.randint(1,100) <= 50:
                                        unit["effects"].append({"type": "bleed", "amount": bleed_amount, "turns": 3, "source": "Bloody Mary"})
                                        notify_status_effect(unit["entity"]["name"], "bleed", duration=3, amount=bleed_amount)
                                # SCP-682 defense up when attacked
                                if target["name"] == "SCP-682":
                                    apply_scp682_defense(target)
                                # SP recovery for not using skill
                                unit["sp"] = min(unit["sp"] + 5, 150)  # Cap at 150 SP
                            break
                        elif action == "2" and unit["entity"]["skill"] and unit["sp"] >= skill_costs.get(unit["entity"]["skill"], 999):
                            use_skill(unit, team, enemies)
                            unit["sp"] -= skill_costs[unit["entity"]["skill"]]
                            break
                        elif action == "3":
                            unit["defending"] = True
                            # SP recovery for defending (extra recovery)
                            unit["sp"] = min(unit["sp"] + 10, 150)  # More SP for defending
                            print(f"🛡️ Defending")
                            break
                        elif action == "4":
                            print("🚪 Battle quit early.")
                            autosave()
                            return
                        else:
                            print("❌ Invalid action. Please choose 1-4.")
                else:
                    if unit["hp"] <= 0:
                        continue
                    # Enemy turn display
                    display_battle_header(unit, False)
                    
                    # Taunt logic
                    taunt_unit = has_taunt(team)
                    valid_targets = [u for u in team if u["battle_hp"] > 0 and not has_ghost(u)]
                    if taunt_unit and taunt_unit["battle_hp"] > 0:
                        target = taunt_unit
                    elif valid_targets:
                        target = random.choice(valid_targets)
                    else:
                        target = random.choice([u for u in team if u["battle_hp"] > 0])
                    
                    # Slender Eight Pages
                    if unit["name"] == "Slender":
                        apply_eight_pages(target)
                    
                    # SCP-682 defense up when attacked
                    if target["entity"]["name"] == "SCP-682":
                        apply_scp682_defense(target)
                    
                    # Enemy attack
                    dmg, is_crit = calculate_damage(unit, target, is_enemy=True)
                    if target.get("defending"):
                        dmg = dmg // 2
                    target["battle_hp"] -= dmg
                    crit_icon = "💥" if is_crit else "⚔️"
                    print(f"{crit_icon} {unit['name']} → {dmg} → {target['entity']['name']}")
                    
                    # Bloody Mary lifesteal
                    if target["entity"]["name"] == "Bloody Mary":
                        if any(eff.get("type") == "bleed" for eff in unit.get("effects", [])):
                            heal = int(dmg * 0.5)
                            target["battle_hp"] = min(target["battle_hp"] + heal, target["entity"]["hp"])
                            print(f"💉 Bloody Mary heals {heal} from bleed lifesteal!")
                    
                    # Bloody Mary bleed counter
                    if target["entity"]["name"] == "Bloody Mary":
                        if random.randint(1,100) <= 50:
                            unit["effects"].append({"type": "bleed", "amount": int(target["attack"] * 0.1), "turns": 3, "source": "Bloody Mary"})
                            print(f"🩸 {unit['entity']['name']} is inflicted with bleed by Bloody Mary!")
                    
                    time.sleep(1.5)  # Brief pause for enemy actions
        print(f"Phase {phase+1} cleared!")
        drop_items(stage_idx+1)
        autosave()
    exp_gain = 50 + world_idx*20 + stage_idx*10
    for unit in team:
        unit["exp"] += exp_gain
    player_cash_gain = 100 + world_idx*50 + stage_idx*20
    global player_cash
    player_cash += player_cash_gain
    print(f"✅ +{exp_gain}XP +${player_cash_gain}")
    
    player_xp_gain = exp_gain
    player_xp += player_xp_gain
    while player_xp >= player_xp_needed(player_level):
        player_xp -= player_xp_needed(player_level)
        player_level += 1
        player_gems += 20
        print(f"🎉 Level {player_level}! +20💎")
    
    autosave()

def world_battle_menu():
    global dev_mode
    print(f"\n🌍 Worlds:")
    available_worlds = []
    for idx, w in enumerate(worlds):
        if any(player_progress["unlocked"][idx]) or dev_mode:
            available_worlds.append((idx, w))
            print(f"{len(available_worlds)}. {w['name']}")
    
    try:
        choice = int(input("World: ")) - 1
        world_idx = available_worlds[choice][0]
    except (ValueError, IndexError):
        return

    print(f"\n📍 {worlds[world_idx]['name']} Stages:")
    available_stages = []
    for i in range(STAGES_PER_WORLD):
        if player_progress["unlocked"][world_idx][i] or dev_mode:
            available_stages.append(i)
            print(f"{len(available_stages)}. Stage {i+1}")
    
    try:
        choice = int(input("Stage: ")) - 1
        stage_idx = available_stages[choice]
    except (ValueError, IndexError):
        return

    team = select_team()
    if not team:
        return

    win = turn_based_battle(team, world_idx, stage_idx)
    if win and not dev_mode:
        if stage_idx + 1 < STAGES_PER_WORLD:
            player_progress["unlocked"][world_idx][stage_idx+1] = 1
        elif world_idx + 1 < NUM_WORLDS:
            player_progress["unlocked"][world_idx+1][0] = 1
    autosave()

def dungeon_excursion_menu():
    print("\n" + "═" * 70)
    print(f"{Fore.YELLOW}🕳️  ENDLESS DUNGEON DIVE 🕳️{Style.RESET_ALL}")
    print("═" * 70)
    print(f"{Fore.LIGHTCYAN_EX}💀 Descend into the infinite depths of nightmare...{Style.RESET_ALL}")
    print(f"{Fore.WHITE}🎯 Choose your challenge level (1-100):{Style.RESET_ALL}")
    print(f"   📊 Higher levels = Greater rewards & tougher enemies")
    print(f"   💎 Boss floors (every 10 levels) give bonus loot")
    
    try:
        level = int(input(f"\n{Fore.CYAN}➤ Enter dungeon level: {Style.RESET_ALL}"))
    except ValueError:
        print(f"{Fore.RED}❌ Invalid input. Please enter a number.{Style.RESET_ALL}")
        return
    if not (1 <= level <= 100):
        print(f"{Fore.RED}❌ Invalid level. Choose between 1-100.{Style.RESET_ALL}")
        return
        
    # Show level info
    is_boss_floor = level % 10 == 0
    danger_level = "🟢 Safe" if level <= 10 else "🟡 Moderate" if level <= 30 else "🟠 Dangerous" if level <= 60 else "🔴 Deadly" if level <= 90 else "💀 NIGHTMARE"
    
    print(f"\n📋 DUNGEON FLOOR {level} INFO:")
    print(f"   🎭 Type: {'👑 BOSS FLOOR' if is_boss_floor else '⚔️ Standard Floor'}")
    print(f"   ⚠️  Danger: {danger_level}")
    print(f"   💰 Rewards: {level * 20} cash + {level * 10} XP per unit")
    
    confirm = input(f"\n{Fore.YELLOW}⚡ Ready to dive? (y/n): {Style.RESET_ALL}").lower()
    if confirm != 'y':
        return
        
    team = select_team()
    if not team:
        return
    dungeon_battle(team, level)

def dungeon_battle(team, level):
    global player_cash, player_xp, player_gems
    
    # Enhanced dungeon intro
    print("\n" + "▓" * 70)
    print(f"{Fore.YELLOW}🕳️  DUNGEON FLOOR {level} 🕳️{Style.RESET_ALL}")
    print("▓" * 70)
    
    # Atmospheric text based on level
    if level <= 10:
        print(f"{Fore.LIGHTBLUE_EX}The air grows cold as you descend...{Style.RESET_ALL}")
    elif level <= 30:
        print(f"{Fore.YELLOW}Shadows writhe in the flickering torchlight...{Style.RESET_ALL}")
    elif level <= 60:
        print(f"{Fore.LIGHTRED_EX}The walls seem to pulse with malevolent energy...{Style.RESET_ALL}")
    elif level <= 90:
        print(f"{Fore.RED}Reality bends and twists in this accursed place...{Style.RESET_ALL}")
    else:
        print(f"{Fore.LIGHTMAGENTA_EX}You have entered the realm of pure nightmare...{Style.RESET_ALL}")
    num_enemies = random.randint(3, 5)
    enemies = []
    for _ in range(num_enemies):
        e = get_enemy_for_stage(level//20, level, 0, boss=(level%10==0))
        e["hp"] = int(e["hp"] * (1.5 + level * 0.05))
        e["attack"] = int(e["attack"] * (1.3 + level * 0.03))
        e["defense"] = int(e["defense"] * (1.2 + level * 0.02))
        e["speed"] = int(e["speed"] * (1.1 + level * 0.01))
        e["sp"] = 100
        e["effects"] = []
        enemies.append(e)
    for unit in team:
        unit["battle_hp"] = unit["entity"]["hp"]
        unit["sp"] = 100
        unit["effects"] = []
        unit["defending"] = False
    while any(e["hp"] > 0 for e in enemies) and any(u["battle_hp"] > 0 for u in team):
        combatants = [{"type": "player", "unit": u} for u in team if u["battle_hp"] > 0] + [{"type": "enemy", "unit": e} for e in enemies if e["hp"] > 0]
        combatants.sort(key=lambda c: c["unit"]["entity"]["speed"] if c["type"] == "player" else c["unit"]["speed"], reverse=True)
        for c in combatants:
            # End battle immediately if all player units are dead
            if not any(u["battle_hp"] > 0 for u in team):
                print("Your team was defeated!")
                autosave()
                return
            unit = c["unit"]
            process_effects(unit)
            unit["sp"] += 10
            unit["defending"] = False
            if c["type"] == "player":
                while True:
                    # Enhanced dungeon battle display
                    print("\n" + "═" * 80)
                    unit_display = format_unit_status(unit, True)
                    print(f"{Fore.YELLOW}🏴‍☠️ DUNGEON FLOOR {level} - YOUR TURN:{Style.RESET_ALL} {unit_display}")
                    print("═" * 80)
                    # Show turn order (next 3 units)
                    print("\n📋 NEXT UP:")
                    shown = 0
                    for i, c_next in enumerate(combatants):
                        if shown >= 3:
                            break
                        if i == 0:  # Skip current unit
                            continue
                        u_next = c_next["unit"]
                        if c_next["type"] == "player" and u_next["battle_hp"] > 0:
                            unit_display = format_unit_status(u_next, True)
                            print(f"   {shown + 1}. {unit_display}")
                            shown += 1
                        elif c_next["type"] == "enemy" and u_next["hp"] > 0:
                            unit_display = format_unit_status(u_next, False)
                            print(f"   {shown + 1}. {unit_display}")
                            shown += 1
                    
                    if shown == 0:
                        print("   (End of round)")
                    # Show enemies cleanly
                    print("\n👹 DUNGEON MONSTERS:")
                    alive_enemies = [e for e in enemies if e["hp"] > 0]
                    if not alive_enemies:
                        print("   (All monsters defeated!)")
                    else:
                        for idx, e in enumerate(alive_enemies):
                            unit_display = format_unit_status(e, False)
                            floor_boost = f"🏴‍☠️Lv.{level}" if level > 1 else ""
                            print(f"   {idx + 1}. {unit_display} {floor_boost}")
                    # Enhanced action menu
                    print("\n⚔️  DUNGEON ACTIONS:")
                    print("   1. 🗡️ Attack")
                    if unit["entity"]["skill"] and unit["sp"] >= skill_costs.get(unit["entity"]["skill"], 999):
                        skill_name = unit["entity"]["skill"].replace('_', ' ').title()
                        sp_cost = skill_costs.get(unit["entity"]["skill"], 0)
                        print(f"   2. ✨ {skill_name} (Skill - {sp_cost} SP)")
                    print("   3. 🛡️ Defend")
                    print("   4. 🚪 Abandon Dive")
                    
                    action = input(f"\n{Fore.CYAN}🎮 Choose action: {Style.RESET_ALL}")
                    if action == "1":
                        target = choose_enemy(enemies)
                        if target:
                            # Slender Eight Pages
                            if unit["entity"]["name"] == "Slender":
                                apply_eight_pages(target)
                            dmg, is_crit = calculate_damage(unit, target)
                            target["hp"] -= dmg
                            print(f"{unit['entity']['name']} attacks {target['name']} for {Fore.RED if is_crit else ''}{dmg}{Style.RESET_ALL if is_crit else ''}!")
                            # Slender applies Eight Pages when attacked
                            if target["name"] == "Slender":
                                apply_eight_pages(unit)
                            # Bloody Mary bleed counter
                            if target["name"] == "Bloody Mary":
                                # FIX: Use get("attack", 10) to avoid KeyError
                                bleed_amount = int(target.get("attack", 10) * 0.1)
                                if random.randint(1,100) <= 50:
                                    unit["effects"].append({"type": "bleed", "amount": bleed_amount, "turns": 3, "source": "Bloody Mary"})
                                    notify_status_effect(unit["entity"]["name"], "bleed", duration=3, amount=bleed_amount)
                            # SCP-682 defense up when attacked
                            if target["name"] == "SCP-682":
                                apply_scp682_defense(target)
                            # SP recovery for not using skill
                            unit["sp"] = min(unit["sp"] + 5, 150)  # Cap at 150 SP
                            break
                    elif action == "2" and unit["entity"]["skill"] and unit["sp"] >= skill_costs.get(unit["entity"]["skill"], 999):
                        use_skill(unit, team, enemies)
                        unit["sp"] -= skill_costs[unit["entity"]["skill"]]
                        break
                    elif action == "3":
                        unit["defending"] = True
                        # SP recovery for defending (extra recovery)
                        unit["sp"] = min(unit["sp"] + 10, 150)  # More SP for defending
                        print(f"{unit['entity']['name']} is defending this turn!")
                        break
                    elif action == "4":
                        print("Battle quit early.")
                        autosave()
                        return
                    else:
                        print("Invalid action.")
            else:
                if unit["hp"] <= 0:
                    continue
                # Taunt logic
                taunt_unit = has_taunt(team)
                valid_targets = [u for u in team if u["battle_hp"] > 0 and not has_ghost(u)]
                if taunt_unit and taunt_unit["battle_hp"] > 0:
                    target = taunt_unit
                elif valid_targets:
                    target = random.choice(valid_targets)
                else:
                    target = random.choice([u for u in team if u["battle_hp"] > 0])
                # Slender Eight Pages
                if unit["name"] == "Slender":
                    apply_eight_pages(target)
                # SCP-682 defense up when attacked
                if target["entity"]["name"] == "SCP-682":
                    apply_scp682_defense(target)
                # Bloody Mary lifesteal
                dmg, is_crit = calculate_damage(unit, target, is_enemy=True)
                if target.get("defending"):
                    dmg = dmg // 2
                    print(f"{target['entity']['name']} defended! Damage reduced to {dmg}.")
                target["battle_hp"] -= dmg
                print(f"{unit['name']} attacks {target['entity']['name']} for {Fore.RED if is_crit else ''}{dmg}{Style.RESET_ALL if is_crit else ''}!")
                # Bloody Mary lifesteal
                if target["entity"]["name"] == "Bloody Mary":
                    if any(eff.get("type") == "bleed" for eff in unit.get("effects", [])):
                        heal = int(dmg * 0.5)
                        target["battle_hp"] = min(target["battle_hp"] + heal, target["entity"]["hp"])
                        print(f"Bloody Mary heals {heal} from bleed lifesteal!")
                # Bloody Mary bleed counter
                if target["entity"]["name"] == "Bloody Mary":
                    if random.randint(1,100) <= 50:
                        bleed_amount = int(target["attack"] * 0.1)
                        unit["effects"].append({"type": "bleed", "amount": bleed_amount, "turns": 3, "source": "Bloody Mary"})
                        notify_status_effect(unit["name"], "bleed", duration=3, amount=bleed_amount)
    print("Dungeon battle cleared!")
    drop_items(level)
    exp_gain = 50 + level * 10
    for unit in team:
        unit["exp"] += exp_gain
    player_cash_gain = 100 + level * 20
    global player_cash, player_xp, player_level, player_gems
    player_cash += player_cash_gain
    print(f"Dungeon cleared! All team units gain {exp_gain} EXP. You earn ${player_cash_gain}.")
    # Player XP and level up
    player_xp_gain = exp_gain
    player_xp += player_xp_gain
    while player_xp >= player_xp_needed(player_level):
        player_xp -= player_xp_needed(player_level)
        player_level += 1
        player_gems += 20
        print(f"You leveled up! Now level {player_level}. You earned 20 gems!")
    print(f"You gained {player_xp_gain} player XP. Current: {player_xp}/{player_xp_needed(player_level)}")
    
    # Auto-save after completing dungeon
    autosave()

def developer_menu():
    global player_gems, player_cash, rarity_chances, player_progress
    while True:
        print("\n--- Developer Menu ---")
        print("1. Add Gems")
        print("2. Add Cash")
        print("3. Set Rarity Rates")
        print("4. View Current Rates")
        print("5. Unlock All Worlds/Stages")
        print("6. Back to Main Menu")
        choice = input("Choose: ")
        if choice == "1":
            amt = int(input("Amount of gems to add: "))
            player_gems += amt
            print(f"Added {amt} gems.")
        elif choice == "2":
            amt = int(input("Amount of cash to add: "))
            player_cash += amt
            print(f"Added ${amt} cash.")
        elif choice == "3":
            print("Current rates (must total 100):")
            for r in rarity_chances:
                val = int(input(f"{r} rate (%): "))
                rarity_chances[r] = val
            total = sum(rarity_chances.values())
            if total != 100:
                print("Warning: Rates do not total 100%.")
        elif choice == "4":
            print("Current rarity rates:")
            for r, v in rarity_chances.items():
                print(f"{r}: {v}%")
        elif choice == "5":
            for w in range(NUM_WORLDS):
                for s in range(STAGES_PER_WORLD):
                    player_progress["unlocked"][w][s] = 1
            print("All worlds and stages unlocked!")
        elif choice == "6":
            break
        else:
            print("Invalid choice.")

def display_banner_card(name, info, index, is_selected=False):
    """Display a fancy banner card"""
    border = "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓" if is_selected else "┌──────────────────────────────────────────────────────────┐"
    footer = "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛" if is_selected else "└──────────────────────────────────────────────────────────┘"
    
    # Banner-specific emojis and colors
    banner_themes = {
        "Creepypasta": {"emoji": "👻", "color": Fore.RED},
        "SCP": {"emoji": "🔬", "color": Fore.YELLOW},
        "Analogue": {"emoji": "📺", "color": Fore.MAGENTA},
        "Normal": {"emoji": "✨", "color": Fore.WHITE}
    }
    
    theme = banner_themes.get(name, banner_themes["Normal"])
    color = theme["color"]
    emoji = theme["emoji"]
    
    print(border)
    print(f"│ {color}{index}. {emoji} {name.upper()} BANNER{Style.RESET_ALL}" + " " * (55 - len(f"{index}. {name.upper()} BANNER") - 2) + "│")
    desc_lines = [info["desc"][i:i+52] for i in range(0, len(info["desc"]), 52)] if "desc" in info else ["Standard summon rates"]
    for line in desc_lines:
        print(f"│ {line}" + " " * (57 - len(line)) + "│")
    print(footer)

def summon_menu():
    global player_gems
    while True:
        print("\n" + "═" * 60)
        print(f"{Fore.CYAN}✨ NIGHTMARE SUMMON PORTAL ✨{Style.RESET_ALL}")
        print("═" * 60)
        print(f"{Fore.YELLOW}💎 Gems: {player_gems}{Style.RESET_ALL} | {Fore.GREEN}Current Rates:{Style.RESET_ALL}")
        print(f"   {Fore.WHITE}Common: {rarity_chances['Common']}%{Style.RESET_ALL} | {Fore.BLUE}Rare: {rarity_chances['Rare']}%{Style.RESET_ALL} | {Fore.MAGENTA}Epic: {rarity_chances['Epic']}%{Style.RESET_ALL} | {Fore.RED}Legendary: {rarity_chances['Legendary']}%{Style.RESET_ALL}")
        print("\n🎴 SELECT A BANNER:")
        
        # Display banner cards
        for idx, (name, info) in enumerate(banners.items()):
            display_banner_card(name, info, idx + 1)
            print()  # Spacing between cards
        
        # Normal summon option
        display_banner_card("Normal", {"desc": "Standard summon rates - no rate boosts"}, len(banners) + 1)
        print()
        
        print(f"{len(banners) + 2}. 🚪 Return to Main Menu")
        print("═" * 60)
        
        banner_choice = input(f"{Fore.CYAN}➤ Select banner: {Style.RESET_ALL}")
        
        try:
            banner_idx = int(banner_choice) - 1
        except ValueError:
            print(f"{Fore.RED}❌ Invalid selection. Please enter a number.{Style.RESET_ALL}")
            continue
            
        if banner_idx == len(banners):
            selected_banner = None
            banner_name = "Normal"
        elif banner_idx == len(banners) + 1:
            break
        elif 0 <= banner_idx < len(banners):
            selected_banner = list(banners.keys())[banner_idx]
            banner_name = selected_banner
        else:
            print(f"{Fore.RED}❌ Invalid banner selection.{Style.RESET_ALL}")
            continue

        # Summon options for selected banner
        print("\n" + "═" * 50)
        print(f"{Fore.MAGENTA}🎯 {banner_name.upper()} BANNER SELECTED{Style.RESET_ALL}")
        print("═" * 50)
        
        print(f"┌{'─' * 48}┐")
        print(f"│ {Fore.GREEN}1.{Style.RESET_ALL} 🌟 Single Summon          {Fore.YELLOW}💎 5 Gems{Style.RESET_ALL}     │")
        print(f"│ {Fore.BLUE}2.{Style.RESET_ALL} ✨ Multi Summon (10x)      {Fore.YELLOW}💎 50 Gems{Style.RESET_ALL}    │")
        if selected_banner:
            print(f"│    {Fore.LIGHTMAGENTA_EX}⚡ BOOSTED RATES FOR THIS BANNER!{Style.RESET_ALL}      │")
        print(f"│ {Fore.RED}3.{Style.RESET_ALL} 🔙 Back to Banner Selection              │")
        print(f"└{'─' * 48}┘")
        
        summon_choice = input(f"{Fore.CYAN}➤ Choose summon type: {Style.RESET_ALL}")
        
        if summon_choice == "1":
            if player_gems >= 5:
                player_gems -= 5
                print(f"\n{Fore.LIGHTMAGENTA_EX}🌟 SUMMONING...{Style.RESET_ALL}")
                time.sleep(0.5)
                summon_entity(selected_banner)
            else:
                print(f"{Fore.RED}❌ Insufficient gems! Need 5 gems for single summon.{Style.RESET_ALL}")
        elif summon_choice == "2":
            if player_gems >= 50:
                player_gems -= 50
                print(f"\n{Fore.LIGHTCYAN_EX}✨ MULTI SUMMONING 10x...{Style.RESET_ALL}")
                multi_summon(10, selected_banner)
            else:
                print(f"{Fore.RED}❌ Insufficient gems! Need 50 gems for multi summon.{Style.RESET_ALL}")
        elif summon_choice == "3":
            continue
        else:
            print(f"{Fore.RED}❌ Invalid choice. Please select 1, 2, or 3.{Style.RESET_ALL}")

# ==========================
# Main Game Loop
# ==========================

def display_main_menu_header():
    """Display the game title and player stats"""
    print("\n" + "═" * 70)
    print(f"{Fore.RED}💀 {GAME_TITLE} 💀{Style.RESET_ALL}")
    print("═" * 70)
    print(f"{Fore.YELLOW}{GEM_SYMBOL} Gems: {player_gems:,}{Style.RESET_ALL} | {Fore.GREEN}{CASH_SYMBOL} Cash: {player_cash:,}{Style.RESET_ALL} | {Fore.CYAN}🎯 Level: {player_level}{Style.RESET_ALL}")
    xp_progress = f"{player_xp}/{player_xp_needed(player_level)}"
    print(f"{Fore.LIGHTBLUE_EX}{XP_SYMBOL} EXP: {xp_progress}{Style.RESET_ALL}")
    
    # Show unit count
    unit_count = len(player_inventory)
    legendary_count = len([u for u in player_inventory if u["entity"]["rarity"] == "Legendary"])
    print(f"{Fore.MAGENTA}👥 Units: {unit_count}{Style.RESET_ALL} | {Fore.RED}🌟 Legendary: {legendary_count}{Style.RESET_ALL}")
    print("═" * 70)

def main():
    global player_gems, player_cash, rarity_chances, dev_mode, player_items
    dev_mode = False
    load_game()
    
    # Game intro
    print("\n" + "▓" * 80)
    print(f"{Fore.RED}{Style.BRIGHT}     ╔══════════════════════════════════════════════════════════════╗{Style.RESET_ALL}")
    print(f"{Fore.RED}{Style.BRIGHT}     ║                    {GAME_TITLE}                     ║{Style.RESET_ALL}")
    print(f"{Fore.RED}{Style.BRIGHT}     ║                  {GAME_SUBTITLE}                  ║{Style.RESET_ALL}")
    print(f"{Fore.RED}{Style.BRIGHT}     ╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
    print("▓" * 80)
    
    pwd = input(f"{Fore.YELLOW}🔐 Enter developer password (leave blank for normal play): {Style.RESET_ALL}")
    if pwd == "devmode":
        dev_mode = True
        print(f"{Fore.YELLOW}🛠️ Developer mode enabled!{Style.RESET_ALL}")
        # Unlock all units at max skill level
        for e in entities:
            if not any(u["entity"]["name"] == e["name"] for u in player_inventory):
                skill_level = 5 if e["rarity"] in ["Epic", "Legendary"] and e["skill"] else 0
                player_inventory.append({"entity": e, "level": 1, "exp": 0, "skill_level": skill_level})
        for k in player_items:
            player_items[k] = 99999
    
    while True:
        display_main_menu_header()
        
        # Main menu options
        print(f"\n{Fore.CYAN}🎮 MAIN MENU{Style.RESET_ALL}")
        print("┌" + "─" * 68 + "┐")
        print(f"│ {Fore.MAGENTA}1.{Style.RESET_ALL} ✨ Summon Portal     - Acquire new nightmare entities    │")
        print(f"│ {Fore.BLUE}2.{Style.RESET_ALL} 🏭 Facility Hub      - Manage and upgrade your units     │")
        print(f"│ {Fore.RED}3.{Style.RESET_ALL} 🌍 World Campaign    - Explore cursed realms             │")
        print(f"│ {Fore.YELLOW}4.{Style.RESET_ALL} 🕳️  Dungeon Dive      - Challenge endless floors          │")
        print(f"│ {Fore.GREEN}5.{Style.RESET_ALL} 👥 Unit Collection   - View your assembled horrors       │")
        print("├" + "─" * 68 + "┤")
        print(f"│ {Fore.WHITE}6.{Style.RESET_ALL} 🚪 Exit Game        - Escape the facility              │")
        
        if dev_mode:
            print(f"│ {Fore.YELLOW}7.{Style.RESET_ALL} 🛠️  Developer Tools   - [DEV MODE ACTIVE]                 │")
            print(f"│ {Fore.LIGHTBLACK_EX}8.{Style.RESET_ALL} 💾 Manual Save       - Force save progress               │")
            print(f"│ {Fore.LIGHTBLACK_EX}9.{Style.RESET_ALL} 📁 Reload Game       - Reload from save file            │")
        
        print("└" + "─" * 68 + "┘")
        
        choice = input(f"{Fore.CYAN}➤ Select your destination: {Style.RESET_ALL}")
        
        if choice == "1":
            summon_menu()
        elif choice == "2":
            show_facility_menu()
        elif choice == "3":
            world_battle_menu()
        elif choice == "4":
            dungeon_excursion_menu()
        elif choice == "5":
            show_units()
            view_unit_details()
        elif choice == "6":
            print(f"\n{Fore.RED}💀 Thanks for playing {GAME_TITLE}!{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}May your nightmares be legendary...{Style.RESET_ALL}")
            # Final autosave before exit
            autosave()
            break
        elif choice == "7" and dev_mode:
            developer_menu()
        elif choice == "8" and dev_mode:
            save_game()
        elif choice == "9" and dev_mode:
            load_game()
        else:
            if dev_mode:
                print(f"{Fore.RED}❌ Invalid choice. Please select a number from the menu (1-9).{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ Invalid choice. Please select a number from the menu (1-6).{Style.RESET_ALL}")

if __name__ == "__main__":
    main()



def list_enemies(enemies):
    lines = []
    for i, e in enumerate(enemies, 1):
        hp = e.get('battle_hp', e.get('hp', 0))
        max_hp = e.get('entity',{}).get('max_hp', e.get('entity',{}).get('hp', hp))
        unit_proxy = {'battle_hp': hp, 'sp': 0, 'entity': {'max_hp': max_hp, 'rarity': e.get('entity',{}).get('rarity', 'C')}}
        name = e.get('entity',{}).get('name', e.get('name','Enemy'))
        lines.append(f"{i}. {name} {fmt_hp_sp(unit_proxy).split('  ')[0]} [{format_effects(e.get('effects', []))}]")
    return lines
