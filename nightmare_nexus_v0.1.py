#!/usr/bin/env python3
"""
Nightmare Nexus - Enhanced Single-Window GUI
Complete single-window interface with enhanced UX and proper navigation

CHANGELOG:
# v1.2 Battle System Enhancement Edition - December 2024
+ Persistent battle preferences (auto-battle, speed settings)
+ Enhanced multi-wave boss battles with improved scaling 
+ Advanced status effect system with proper stacking
+ Improved battle UI with better turn order display
+ Enhanced rune drop rates and progression rewards
+ Battle log enhancements with timestamps and details
+ Post-battle options system with multi-battle support
+ Auto-battle preference saving and restoration
+ Developer account security improvements
+ JSON save data compatibility fixes
+ Unit testing practice battle mode
+ Enhanced stat calculation and display systems
+ Removed public developer account hints for security
+ Fixed Eight Pages passive to only trigger when Slender is involved
+ Added comprehensive unit details interface with rune management
+ Improved enemy preview system for better strategic planning
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
import json
import os
import random
import time
import threading
from datetime import datetime
import hashlib
import uuid
import re
from typing import Optional, Dict, List, Any

class NightmareNexusGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("NIGHTMARE NEXUS - Horror Gacha Game")
        self.root.geometry("1400x900")
        self.root.configure(bg='black')
        self.root.resizable(True, True)
        
        # Import original game data and functions
        self.import_game_data()
        
        # GUI State
        self.current_screen = "startup"
        self.screen_history = []  # Proper screen history stack
        self.battle_state = {}
        self.auto_battle_active = False
        self.selected_units = []  # For unit selection
        self.saved_teams = {}  # For team save/load system
        self.battle_log = []  # For in-game battle log instead of console
        self.logged_in = False  # Track login state
        
        # Battle preferences and settings - persistent across battles
        self.last_team_used = []  # Remember last team selection (by unit objects)
        self.auto_battle_preference = False  # Remember auto battle setting
        self.battle_speed_preference = 1  # Remember battle speed setting (index in speeds array)
        self.battle_speeds = [0.5, 1, 2, 4]  # Speed multipliers
        self.multi_battle_active = False  # Multi-battle system
        self.turn_counter = 0  # Battle turn counter
        
        # Setup fonts
        self.setup_fonts()
        
        # Create initial startup container (no navigation)
        self.setup_startup_container()
        
        # Start with studio intro
        self.show_studio_intro()
        
    def setup_fonts(self):
        """Setup custom fonts for the GUI"""
        self.title_font = font.Font(family="Consolas", size=16, weight="bold")
        self.header_font = font.Font(family="Consolas", size=12, weight="bold")
        self.body_font = font.Font(family="Consolas", size=10)
        self.small_font = font.Font(family="Consolas", size=8)
        
    def setup_startup_container(self):
        """Setup the startup container without navigation"""
        # Main content area
        self.main_frame = tk.Frame(self.root, bg='black')
        self.main_frame.pack(fill='both', expand=True)
        
        # Content frame
        self.content_frame = tk.Frame(self.main_frame, bg='black')
        self.content_frame.pack(fill='both', expand=True)
        
    def setup_main_container(self):
        """Setup the main container with navigation (called after login)"""
        # Clear startup container and any existing main containers to prevent duplicates
        if hasattr(self, 'main_frame') and self.main_frame.winfo_exists():
            self.main_frame.destroy()
        if hasattr(self, 'nav_frame') and self.nav_frame.winfo_exists():
            self.nav_frame.destroy()
        if hasattr(self, 'notification_frame') and self.notification_frame.winfo_exists():
            self.notification_frame.destroy()
        
        # Top navigation bar
        self.nav_frame = tk.Frame(self.root, bg='#2a2a2a', height=60)
        self.nav_frame.pack(fill='x', side='top')
        self.nav_frame.pack_propagate(False)
        
        # Navigation buttons
        nav_buttons_frame = tk.Frame(self.nav_frame, bg='#2a2a2a')
        nav_buttons_frame.pack(side='left', padx=10, pady=10)
        
        self.home_btn = tk.Button(
            nav_buttons_frame,
            text="🏠 Home",
            command=self.go_home,
            font=self.body_font,
            bg='#006600',
            fg='white',
            width=10
        )
        self.home_btn.pack(side='left', padx=(0, 5))
        
        self.back_btn = tk.Button(
            nav_buttons_frame,
            text="🔙 Back",
            command=self.go_back,
            font=self.body_font,
            bg='#666666',
            fg='white',
            width=10,
            state='disabled'
        )
        self.back_btn.pack(side='left', padx=5)
        
        # Game title and stats in nav
        title_frame = tk.Frame(self.nav_frame, bg='#2a2a2a')
        title_frame.pack(side='right', padx=10, pady=5)
        
        self.stats_label = tk.Label(
            title_frame,
            text="",
            font=self.body_font,
            bg='#2a2a2a',
            fg='#FFFF66'
        )
        self.stats_label.pack()
        
        # Main content area
        self.main_frame = tk.Frame(self.root, bg='black')
        self.main_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Content frame
        self.content_frame = tk.Frame(self.main_frame, bg='black')
        self.content_frame.pack(fill='both', expand=True)
        
        # Notification area at bottom
        self.notification_frame = tk.Frame(self.main_frame, bg='#1a1a1a', height=100)
        self.notification_frame.pack(fill='x', pady=(10, 0))
        self.notification_frame.pack_propagate(False)
        
        self.notification_text = tk.Text(
            self.notification_frame, 
            bg='#1a1a1a', 
            fg='#66FF66',
            font=self.small_font,
            height=4,
            wrap=tk.WORD,
            state='disabled'
        )
        self.notification_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Update stats display
        self.update_stats_display()
        
    def import_game_data(self):
        """Import all game data from original game file"""
        # Initialize all game variables from the original game
        self.entities = [
            # Common
            {"name": "Zombie", "rarity": "Common", "hp": 50, "attack": 5, "defense": 2, "speed": 10, "skill": None, "crit_rate": 0, "crit_damage": 150, "accuracy": 85, "evasion": 10, "passive": "None", "description": "A mindless undead creature that craves flesh."},
            {"name": "Vampire", "rarity": "Common", "hp": 55, "attack": 6, "defense": 3, "speed": 12, "skill": None, "crit_rate": 0, "crit_damage": 150, "accuracy": 85, "evasion": 10, "passive": "Heals 10% of damage dealt.", "description": "A bloodthirsty immortal that drains life from its victims."},
            {"name": "Werewolf", "rarity": "Common", "hp": 60, "attack": 7, "defense": 3, "speed": 14, "skill": None, "crit_rate": 0, "crit_damage": 150, "accuracy": 85, "evasion": 10, "passive": "Gains 5% attack when below 50% HP.", "description": "A savage beast that transforms under the full moon."},
            {"name": "Ghoul", "rarity": "Common", "hp": 50, "attack": 5, "defense": 2, "speed": 11, "skill": None, "crit_rate": 0, "crit_damage": 150, "accuracy": 85, "evasion": 10, "passive": "None", "description": "A graveyard-dwelling monster that feeds on the dead."},
            {"name": "Ghost", "rarity": "Common", "hp": 45, "attack": 4, "defense": 1, "speed": 16, "skill": None, "crit_rate": 0, "crit_damage": 150, "accuracy": 85, "evasion": 25, "passive": "None", "description": "A restless spirit that haunts the living."},
            {"name": "Skeleton", "rarity": "Common", "hp": 40, "attack": 6, "defense": 2, "speed": 12, "skill": None, "crit_rate": 5, "crit_damage": 175, "accuracy": 90, "evasion": 15, "passive": "None", "description": "An animated pile of bones that refuses to stay buried."},
            {"name": "Spider", "rarity": "Common", "hp": 35, "attack": 5, "defense": 1, "speed": 18, "skill": None, "crit_rate": 0, "crit_damage": 150, "accuracy": 95, "evasion": 20, "passive": "10% chance to poison on attack.", "description": "A venomous arachnid that lurks in dark corners."},
            {"name": "Bat", "rarity": "Common", "hp": 30, "attack": 4, "defense": 1, "speed": 20, "skill": None, "crit_rate": 0, "crit_damage": 150, "accuracy": 80, "evasion": 30, "passive": "None", "description": "A bloodthirsty flying creature of the night."},
            {"name": "Rat", "rarity": "Common", "hp": 25, "attack": 3, "defense": 1, "speed": 22, "skill": None, "crit_rate": 0, "crit_damage": 150, "accuracy": 75, "evasion": 35, "passive": "None", "description": "A disease-carrying rodent that swarms in numbers."},
            {"name": "Imp", "rarity": "Common", "hp": 38, "attack": 5, "defense": 2, "speed": 15, "skill": None, "crit_rate": 0, "crit_damage": 150, "accuracy": 85, "evasion": 15, "passive": "None", "description": "A mischievous lesser demon with sharp claws."},
            {"name": "Shadow", "rarity": "Common", "hp": 42, "attack": 4, "defense": 1, "speed": 17, "skill": None, "crit_rate": 0, "crit_damage": 150, "accuracy": 85, "evasion": 40, "passive": "20% chance to dodge attacks.", "description": "A dark entity that feeds on fear and despair."},
            {"name": "Wraith", "rarity": "Common", "hp": 48, "attack": 5, "defense": 2, "speed": 14, "skill": None, "crit_rate": 0, "crit_damage": 150, "accuracy": 85, "evasion": 20, "passive": "None", "description": "A tormented soul trapped between life and death."},
            # Rare
            {"name": "Frankenstein", "rarity": "Rare", "hp": 100, "attack": 15, "defense": 8, "speed": 8, "skill": None, "crit_rate": 0, "crit_damage": 150, "accuracy": 85, "evasion": 5, "passive": "None", "description": "A patchwork monster brought to life by science."},
            {"name": "Banshee", "rarity": "Rare", "hp": 80, "attack": 12, "defense": 5, "speed": 18, "skill": "scream", "crit_rate": 0, "crit_damage": 150, "accuracy": 90, "evasion": 25, "passive": "None", "description": "A wailing spirit whose cry foretells death."},
            {"name": "Mummy", "rarity": "Rare", "hp": 90, "attack": 14, "defense": 7, "speed": 7, "skill": None, "crit_rate": 0, "crit_damage": 150, "accuracy": 85, "evasion": 10, "passive": "None", "description": "An ancient corpse wrapped in bandages, cursed to walk the earth."},
            {"name": "Chupacabra", "rarity": "Rare", "hp": 85, "attack": 13, "defense": 6, "speed": 15, "skill": None, "crit_rate": 0, "crit_damage": 150, "accuracy": 90, "evasion": 15, "passive": "None", "description": "A legendary creature known for attacking livestock."},
            {"name": "Poltergeist", "rarity": "Rare", "hp": 80, "attack": 12, "defense": 5, "speed": 17, "skill": "push", "crit_rate": 0, "crit_damage": 150, "accuracy": 85, "evasion": 30, "passive": "None", "description": "A mischievous spirit that moves objects and causes chaos."},
            # Epic
            {"name": "SCP-999", "rarity": "Epic", "hp": 100, "attack": 5, "defense": 5, "speed": 25, "skill": "joyful_regeneration", "crit_rate": 0, "crit_damage": 150, "accuracy": 85, "evasion": 10, "passive": "Joyful Aura: All allies regenerate 5% HP per turn.", "description": "The Tickle Monster. A friendly, gelatinous SCP that brings joy and heals others."},
            {"name": "The Rake", "rarity": "Epic", "hp": 160, "attack": 30, "defense": 12, "speed": 28, "skill": "night_ambush", "crit_rate": 0, "crit_damage": 200, "accuracy": 95, "evasion": 25, "passive": "None", "description": "A pale, humanoid creature known for its terrifying nocturnal attacks."},
            {"name": "Kuchisake-onna", "rarity": "Epic", "hp": 85, "attack": 20, "defense": 5, "speed": 20, "skill": "bloody_smile", "crit_rate": 15, "crit_damage": 180, "accuracy": 90, "evasion": 15, "passive": "None", "description": "The Slit-Mouthed Woman. A vengeful spirit from Japanese folklore."},
            {"name": "Mothman", "rarity": "Epic", "hp": 95, "attack": 18, "defense": 6, "speed": 23, "skill": "mothmans_omen", "crit_rate": 0, "crit_damage": 150, "accuracy": 100, "evasion": 20, "passive": "None", "description": "A mysterious winged cryptid said to predict disasters."},
            {"name": "Bloody Mary", "rarity": "Epic", "hp": 90, "attack": 15, "defense": 4, "speed": 19, "skill": "mirror_curse", "crit_rate": 0, "crit_damage": 150, "accuracy": 85, "evasion": 15, "passive": "50% chance to inflict bleed when attacked. Heals 50% of damage taken if attacker has bleed.", "description": "A vengeful spirit summoned through mirrors."},
            # Legendary
            {"name": "Slender", "rarity": "Legendary", "hp": 150, "attack": 20, "defense": 10, "speed": 25, "skill": "faceless_terror", "crit_rate": 0, "crit_damage": 150, "accuracy": 100, "evasion": 35, "passive": "Eight Pages: Attacker/target gains stack, stun at 8.", "description": "A tall, faceless entity that stalks and abducts victims."},
            {"name": "Jeff the Killer", "rarity": "Legendary", "hp": 90, "attack": 25, "defense": 5, "speed": 30, "skill": "killer_burst", "crit_rate": 30, "crit_damage": 250, "accuracy": 95, "evasion": 20, "passive": "Go to Sleep: Starts with 1 Ghost stack. Gains 1 Ghost stack on critical hits. Cannot be targeted unless last alive.", "description": "A notorious creepypasta killer with a haunting smile."},
            {"name": "SCP-682", "rarity": "Legendary", "hp": 200, "attack": 40, "defense": 20, "speed": 24, "skill": "indestructible_regeneration", "crit_rate": 0, "crit_damage": 150, "accuracy": 85, "evasion": 5, "passive": "Gains 5% DEF when attacked. Skill applies taunt.", "description": "The Hard to Destroy Reptile. An extremely dangerous, adaptive SCP."},
            {"name": "Iris", "rarity": "Legendary", "hp": 180, "attack": 25, "defense": 15, "speed": 20, "skill": "analog_distortion", "crit_rate": 0, "crit_damage": 200, "accuracy": 100, "evasion": 15, "passive": "Basic attack hits all enemies, 40% chance to slow.", "description": "A mysterious analogue horror entity with reality-warping powers."},
        ]
        
        self.rarity_colors = {
            "Common": "#FFFFFF",
            "Rare": "#0066FF", 
            "Epic": "#9933CC",
            "Legendary": "#FF3333"
        }
        
        self.rarity_chances = {
            "Common": 60,
            "Rare": 25,
            "Epic": 10,
            "Legendary": 5
        }
        
        self.skill_costs = {
            "joyful_regeneration": 40,
            "killer_burst": 50,
            "bloody_smile": 35,
            "mothmans_omen": 30,
            "mirror_curse": 40,
            "night_ambush": 50,
            "faceless_terror": 45,
            "analog_distortion": 40,
            "indestructible_regeneration": 60,
            "scream": 30,
            "push": 25
        }
        
        # Skill descriptions for UI display
        self.skill_descriptions = {
            "joyful_regeneration": "Grants all allies 20% HP regeneration per turn for 3 turns. At skill level 5, also grants 50% increased healing effects.",
            "killer_burst": "High-damage attack with guaranteed critical hit. Gains 1 Ghost stack after use.",
            "bloody_smile": "Slashing attack with high critical chance that inflicts bleeding for 4 turns.",
            "mothmans_omen": "Reduces all enemies' accuracy by 30% for 3 turns while dealing moderate damage.",
            "mirror_curse": "Curses target to reflect 50% of damage taken back to attackers for 5 turns.",
            "night_ambush": "Multi-hit attack (2-4 hits) with 30% bonus damage in darkness.",
            "faceless_terror": "Unblockable attack that adds Eight Pages stacks. At max level, 8 stacks cause stun and fear.",
            "analog_distortion": "Reality-warping AoE attack that damages and reduces enemy defense by 30% for 4 turns.",
            "indestructible_regeneration": "Heals 40% max HP and forces all enemies to target this unit for 3 turns.",
            "scream": "Terrifying wail that stuns all enemies for 1 turn and reduces their attack by 20%.",
            "push": "Telekinetic force that damages and pushes back enemies, reducing their speed by 25% for 2 turns."
        }
        
        # World and stage data
        self.worlds = [
            {"name": "Abandoned Hospital"},
            {"name": "Haunted Forest"},
            {"name": "Forgotten Laboratory"},
            {"name": "Cursed Town"},
            {"name": "Nightmare Realm"}
        ]
        self.NUM_WORLDS = 5
        self.STAGES_PER_WORLD = 20
        
        # Depths data
        self.depths_levels = {
            "Endless Delve": {
                "name": "Endless Delve",
                "description": "Infinite floors of escalating nightmare",
                "icon": "🕳️",
                "color": "#FF6666",
                "unlock_level": 1
            },
            "Rune Sanctums": {
                "name": "Rune Sanctums", 
                "description": "Boss battles for powerful rune equipment",
                "icon": "🎰",
                "color": "#66CCFF",
                "unlock_level": 10
            },
            "XP Training": {
                "name": "XP Training Grounds",
                "description": "Battle trainers to earn XP potions",
                "icon": "⭐",
                "color": "#66FF66", 
                "unlock_level": 5
            }
        }
        
        # Initialize rune data
        self.initialize_rune_data()
        
        # Initialize player data
        self.initialize_player_data()
        
        # Setup autosave timer (saves every 2 minutes)
        self.setup_autosave()
        
    def initialize_rune_data(self):
        """Initialize comprehensive rune system data"""
        # Rune types and their effects
        self.rune_types = {
            "Weapon": {"slot": 1, "icon": "⚔️", "color": "#FF6666"},
            "Armor": {"slot": 2, "icon": "🛡️", "color": "#66CCFF"},
            "Accessory": {"slot": 3, "icon": "💎", "color": "#FFCC66"},
            "Enhancement": {"slot": [4, 5, 6], "icon": "✨", "color": "#CC66FF"}
        }
        
        # Rune rarities
        self.rune_rarities = {
            "Common": {"color": "#FFFFFF", "stat_mult": 1.0, "substats": 1},
            "Rare": {"color": "#0066FF", "stat_mult": 1.3, "substats": 2},
            "Epic": {"color": "#9933CC", "stat_mult": 1.6, "substats": 3},
            "Legendary": {"color": "#FF3333", "stat_mult": 2.0, "substats": 4}
        }
        
        # Rune stat types
        self.rune_stats = {
            "HP": {"icon": "❤️", "base": 50, "type": "flat"},
            "HP%": {"icon": "❤️", "base": 15, "type": "percent"},
            "Attack": {"icon": "⚔️", "base": 10, "type": "flat"},
            "Attack%": {"icon": "⚔️", "base": 15, "type": "percent"},
            "Defense": {"icon": "🛡️", "base": 8, "type": "flat"},
            "Defense%": {"icon": "🛡️", "base": 15, "type": "percent"},
            "Speed": {"icon": "⚡", "base": 5, "type": "flat"},
            "Crit Rate": {"icon": "💥", "base": 5, "type": "percent"},
            "Crit Damage": {"icon": "🎯", "base": 10, "type": "percent"},
            "Accuracy": {"icon": "📊", "base": 8, "type": "percent"},
            "Evasion": {"icon": "👻", "base": 8, "type": "percent"}
        }
        
        # Rune set effects - organized by boss drops
        self.rune_sets = {
            # Forge Master drops (Weapon/Attack focused)
            "Nightmare": {"pieces": 4, "effect": "Nightmare Aura: +25% Attack", "stats": {"attack_percent": 25}},
            "Terror": {"pieces": 2, "effect": "Terror Strike: +15% Crit Rate", "stats": {"crit_rate": 15}},
            
            # Guardian Goliath drops (Defense focused)
            "Spectral": {"pieces": 4, "effect": "Spectral Form: +30% HP", "stats": {"hp_percent": 30}},
            "Void": {"pieces": 2, "effect": "Void Protection: +15% Defense", "stats": {"defense_percent": 15}},
            
            # Mystic Oracle drops (Utility focused)
            "Soul": {"pieces": 2, "effect": "Soul Drain: +10% Speed and +10% Accuracy", "stats": {"speed": 10, "accuracy": 10}},
            "Destiny": {"pieces": 4, "effect": "Destiny's Favor: +20% Crit Damage", "stats": {"crit_damage": 20}},
            
            # Nightmare Sovereign drops (Debuff focused)
            "Dread": {"pieces": 4, "effect": "Dread Presence: 25% chance to stun on attack", "stats": {"stun_chance": 25}},
            "Chaos": {"pieces": 2, "effect": "Chaos Shield: +20% Debuff Resistance", "stats": {"evasion": 20}}
        }
        
        # Sample runes will be generated in setup_developer_content()
        
    def generate_sample_runes(self):
        """Generate sample runes for developer account"""
        self.player_runes = []
        
        # Generate a variety of runes for testing
        rune_names = [
            "Spectral Blade", "Nightmare Shield", "Horror's Eye", "Soul Drain", "Fear Aura", "Dark Might",
            "Phantom Cloak", "Terror Spike", "Void Guard", "Dread Focus", "Cursed Ring", "Death's Mark"
        ]
        
        for i in range(20):  # Generate 20 sample runes
            rarity = random.choice(["Common", "Rare", "Epic", "Legendary"])
            rtype = random.choice(list(self.rune_types.keys()))
            
            # Main stat
            main_stat = random.choice(list(self.rune_stats.keys()))
            main_value = int(self.rune_stats[main_stat]["base"] * self.rune_rarities[rarity]["stat_mult"])
            
            # Sub stats
            substats = {}
            available_substats = [s for s in self.rune_stats.keys() if s != main_stat]
            num_substats = min(self.rune_rarities[rarity]["substats"], len(available_substats))
            
            for _ in range(num_substats):
                if available_substats:
                    substat = random.choice(available_substats)
                    available_substats.remove(substat)
                    substats[substat] = int(self.rune_stats[substat]["base"] * 0.6)
            
            # Assign set name
            set_name = random.choice(list(self.rune_sets.keys()))
            
            rune = {
                "id": str(uuid.uuid4()),
                "name": random.choice(rune_names),
                "type": rtype,
                "rarity": rarity,
                "level": random.randint(1, 15),
                "main_stat": main_stat,
                "main_value": main_value,
                "substats": substats,
                "set": set_name,
                "equipped_unit": None,
                "equipped_slot": None
            }
            
            self.player_runes.append(rune)
            
    def generate_rune(self, rarity=None, rtype=None):
        """Generate a new rune"""
        if not rarity:
            rarity = random.choice(["Common", "Rare", "Epic", "Legendary"])
        if not rtype:
            rtype = random.choice(list(self.rune_types.keys()))
            
        # Rune names by type
        rune_names = {
            "Weapon": ["Spectral Blade", "Nightmare Edge", "Terror Fang", "Soul Cleaver", "Dread Scythe"],
            "Armor": ["Nightmare Shield", "Phantom Plate", "Void Guard", "Horror's Embrace", "Dark Barrier"],
            "Accessory": ["Horror's Eye", "Cursed Ring", "Soul Gem", "Terror Charm", "Dread Amulet"],
            "Enhancement": ["Fear Aura", "Dark Might", "Soul Drain", "Terror Boost", "Nightmare Power"]
        }
        
        # Main stat based on type
        main_stat_pools = {
            "Weapon": ["Attack", "Attack%", "Crit Rate", "Crit Damage"],
            "Armor": ["HP", "HP%", "Defense", "Defense%"],
            "Accessory": ["HP%", "Attack%", "Speed", "Accuracy", "Evasion"],
            "Enhancement": ["Crit Rate", "Crit Damage", "Speed", "Accuracy", "Evasion"]
        }
        
        main_stat = random.choice(main_stat_pools[rtype])
        main_value = int(self.rune_stats[main_stat]["base"] * self.rune_rarities[rarity]["stat_mult"])
        
        # Sub stats
        substats = {}
        available_substats = [s for s in self.rune_stats.keys() if s != main_stat]
        num_substats = min(self.rune_rarities[rarity]["substats"], len(available_substats))
        
        for _ in range(num_substats):
            if available_substats:
                substat = random.choice(available_substats)
                available_substats.remove(substat)
                substats[substat] = int(self.rune_stats[substat]["base"] * random.uniform(0.4, 0.8))
        
        # Assign set name
        set_name = random.choice(list(self.rune_sets.keys()))
        
        rune = {
            "id": str(uuid.uuid4()),
            "name": random.choice(rune_names[rtype]),
            "type": rtype,
            "rarity": rarity,
            "level": 1,
            "main_stat": main_stat,
            "main_value": main_value,
            "substats": substats,
            "set": set_name,
            "equipped_unit": None,
            "equipped_slot": None
        }
        
        return rune
        
    def equip_rune(self, unit_idx, slot, rune_id):
        """Equip a rune to a unit's slot"""
        if unit_idx >= len(self.player_inventory):
            return False
            
        unit = self.player_inventory[unit_idx]
        rune = next((r for r in self.player_runes if r["id"] == rune_id), None)
        
        if not rune or rune["equipped_unit"] is not None:
            return False
            
        # Check if rune type is compatible with slot
        rune_type_info = self.rune_types[rune["type"]]
        if isinstance(rune_type_info["slot"], list):
            if slot not in rune_type_info["slot"]:
                return False
        else:
            if slot != rune_type_info["slot"]:
                return False
                
        # Unequip any existing rune in that slot
        if slot in unit.get("runes", {}):
            old_rune_id = unit["runes"][slot]
            old_rune = next((r for r in self.player_runes if r["id"] == old_rune_id), None)
            if old_rune:
                old_rune["equipped_unit"] = None
                old_rune["equipped_slot"] = None
                
        # Equip new rune
        if "runes" not in unit:
            unit["runes"] = {}
        unit["runes"][slot] = rune_id
        rune["equipped_unit"] = unit_idx
        rune["equipped_slot"] = slot
        
        return True
        
    def unequip_rune(self, unit_idx, slot):
        """Unequip a rune from a unit's slot"""
        if unit_idx >= len(self.player_inventory):
            return False
            
        unit = self.player_inventory[unit_idx]
        
        if "runes" not in unit or slot not in unit["runes"]:
            return False
            
        rune_id = unit["runes"][slot]
        rune = next((r for r in self.player_runes if r["id"] == rune_id), None)
        
        if rune:
            rune["equipped_unit"] = None
            rune["equipped_slot"] = None
            
        del unit["runes"][slot]
        return True
        
    def calculate_unit_level_stats(self, unit):
        """Calculate unit stats with exponential level scaling (HP, ATK, DEF only)"""
        base_entity = unit["entity"]
        level = unit["level"]
        
        # Exponential growth formula for core stats only
        hp_multiplier = 1.10 ** (level - 1)      # HP grows slightly slower
        attack_multiplier = 1.12 ** (level - 1)   # Attack grows at standard rate
        defense_multiplier = 1.08 ** (level - 1)  # Defense grows slower for balance
        
        # Calculate SP cap (150 + 5 per level after 10)
        sp_cap = 150 + max(0, (level - 10) * 5)
        
        # Cap the multipliers at reasonable levels to prevent overflow
        hp_multiplier = min(hp_multiplier, 5000)      # Cap at 5000x base HP
        attack_multiplier = min(attack_multiplier, 10000)  # Cap at 10000x base attack
        defense_multiplier = min(defense_multiplier, 3000)  # Cap at 3000x base defense
        
        return {
            "hp": int(base_entity["hp"] * hp_multiplier),
            "attack": int(base_entity["attack"] * attack_multiplier),
            "defense": int(base_entity["defense"] * defense_multiplier),
            "speed": base_entity["speed"],  # Speed doesn't scale with level - only affected by runes/kit
            "crit_rate": base_entity["crit_rate"],  # Base 0 unless unit has unique exception - only affected by runes/kit
            "crit_damage": base_entity["crit_damage"],  # Base 100% - only affected by runes/kit
            "accuracy": base_entity["accuracy"],  # Base 0 - only affected by runes/kit
            "evasion": base_entity["evasion"],  # Base 0 debuff resistance - only affected by runes/kit
            "sp_cap": sp_cap
        }
    
    def calculate_unit_stats_with_runes(self, unit):
        """Calculate a unit's total stats including level scaling, rune bonuses, and set effects"""
        # Start with level-scaled stats
        base_stats = self.calculate_unit_level_stats(unit)
        
        # Apply rune bonuses
        flat_bonuses = {}
        percent_bonuses = {}
        equipped_runes = []
        
        for slot, rune_id in unit.get("runes", {}).items():
            rune = next((r for r in self.player_runes if r["id"] == rune_id), None)
            if rune:
                equipped_runes.append(rune)
                # Main stat (scaled by rune level)
                main_value = rune["main_value"] * (1 + (rune["level"] - 1) * 0.1)  # 10% per level
                stat = rune["main_stat"].replace("%", "").lower().replace(" ", "_")
                if rune["main_stat"].endswith("%"):
                    percent_bonuses[stat] = percent_bonuses.get(stat, 0) + main_value
                else:
                    flat_bonuses[stat] = flat_bonuses.get(stat, 0) + main_value
                    
                # Sub stats (scaled by rune level)
                for substat, value in rune["substats"].items():
                    scaled_value = value * (1 + (rune["level"] - 1) * 0.05)  # 5% per level
                    sub = substat.replace("%", "").lower().replace(" ", "_")
                    if substat.endswith("%"):
                        percent_bonuses[sub] = percent_bonuses.get(sub, 0) + scaled_value
                    else:
                        flat_bonuses[sub] = flat_bonuses.get(sub, 0) + scaled_value
        
        # Apply set effects
        set_bonuses = self.calculate_set_effects(equipped_runes)
        for stat, value in set_bonuses.items():
            if stat.endswith("_percent"):
                base_stat = stat.replace("_percent", "")
                percent_bonuses[base_stat] = percent_bonuses.get(base_stat, 0) + value
            else:
                flat_bonuses[stat] = flat_bonuses.get(stat, 0) + value
        
        # Apply bonuses
        final_stats = base_stats.copy()
        
        for stat in final_stats:
            # Apply flat bonuses first
            if stat in flat_bonuses:
                final_stats[stat] += int(flat_bonuses[stat])
                
            # Then apply percent bonuses
            if stat in percent_bonuses:
                final_stats[stat] = int(final_stats[stat] * (1 + percent_bonuses[stat] / 100))
        
        # Cap crit rate at 100%
        if 'crit_rate' in final_stats:
            final_stats['crit_rate'] = min(final_stats['crit_rate'], 100)
                
        # Add rune bonus breakdown for UI display
        final_stats["rune_bonuses"] = {
            "flat": {k: int(v) for k, v in flat_bonuses.items()},
            "percent": {k: int(v) for k, v in percent_bonuses.items()}
        }
        final_stats["active_sets"] = self.get_active_set_names(equipped_runes)
        final_stats["equipped_runes"] = equipped_runes
        
        return final_stats
    
    def calculate_set_effects(self, equipped_runes):
        """Calculate set effect bonuses from equipped runes"""
        if not equipped_runes:
            return {}
            
        # Count runes by set
        set_counts = {}
        for rune in equipped_runes:
            set_name = rune.get("set", "")
            if set_name:
                set_counts[set_name] = set_counts.get(set_name, 0) + 1
        
        # Calculate active set bonuses
        set_bonuses = {}
        for set_name, count in set_counts.items():
            if set_name in self.rune_sets:
                required_pieces = self.rune_sets[set_name]["pieces"]
                if count >= required_pieces:
                    # Add set bonus stats
                    for stat, value in self.rune_sets[set_name]["stats"].items():
                        set_bonuses[stat] = set_bonuses.get(stat, 0) + value
        
        return set_bonuses
    
    def get_active_set_names(self, equipped_runes):
        """Get names of active sets"""
        if not equipped_runes:
            return []
            
        set_counts = {}
        for rune in equipped_runes:
            set_name = rune.get("set", "")
            if set_name:
                set_counts[set_name] = set_counts.get(set_name, 0) + 1
        
        active_sets = []
        for set_name, count in set_counts.items():
            if set_name in self.rune_sets:
                required_pieces = self.rune_sets[set_name]["pieces"]
                if count >= required_pieces:
                    active_sets.append(set_name)
        
        return active_sets
        
    def initialize_player_data(self):
        """Initialize player data - check if dev account should be loaded"""
        self.current_user = None
        self.player_gems = 100
        self.player_cash = 500
        self.player_level = 1
        self.player_xp = 0
        self.player_inventory = []
        self.player_items = {"Small XP Pot": 0, "Medium XP Pot": 0, "Large XP Pot": 0}
        self.player_runes = []
        self.player_progress = {
            "world": 0,
            "stage": 0,
            "unlocked": [[1] + [0]*19] + [[0]*20 for _ in range(4)],
            "dungeon_highest": 1,
            "cleared_stages": []  # Track first-time clears for gem rewards (list for JSON compatibility)
        }
        
        # Initialize facilities and research data
        self.player_facilities = {}
        self.player_research = {}
        
        # Turn counter for battles
        self.turn_counter = 0
        
        # Load existing save data
        self.load_game_data()
        
        # Don't auto-login anyone - always start with welcome screen
        
    def show_studio_intro(self):
        """Show the studio intro screen"""
        self.clear_content()
        
        # Studio logo/title
        studio_label = tk.Label(
            self.content_frame,
            text="🎮 People's Gospel Presents 🎮",
            font=self.title_font,
            bg='black',
            fg='#66CCFF'
        )
        studio_label.pack(pady=100)
        
        # Subtitle
        subtitle_label = tk.Label(
            self.content_frame,
            text="A Horror Gaming Experience",
            font=self.body_font,
            bg='black',
            fg='#CCCCCC'
        )
        subtitle_label.pack(pady=20)
        
        # Auto-progress to welcome screen after 3 seconds
        self.root.after(3000, self.show_welcome_screen)
        
    def show_welcome_screen(self):
        """Show the welcome/home screen with Login, Register, Quit options"""
        self.clear_content()
        
        # Game title
        title_label = tk.Label(
            self.content_frame,
            text="NIGHTMARE NEXUS",
            font=self.title_font,
            bg='black',
            fg='#FF3333'
        )
        title_label.pack(pady=50)
        
        # Game subtitle
        subtitle_label = tk.Label(
            self.content_frame,
            text="Horror Gacha Collection Game",
            font=self.header_font,
            bg='black',
            fg='#CCCCCC'
        )
        subtitle_label.pack(pady=10)
        
        # Main menu options
        menu_frame = tk.Frame(self.content_frame, bg='black')
        menu_frame.pack(pady=80)
        
        # Login button
        login_btn = tk.Button(
            menu_frame,
            text="🔑 Login",
            command=self.show_login_screen,
            font=self.title_font,
            bg='#006600',
            fg='white',
            width=12,
            height=2
        )
        login_btn.pack(pady=15)
        
        # Register button
        register_btn = tk.Button(
            menu_frame,
            text="✨ Register",
            command=self.show_register_screen,
            font=self.title_font,
            bg='#0066CC',
            fg='white',
            width=12,
            height=2
        )
        register_btn.pack(pady=15)
        
        # Quit button
        quit_btn = tk.Button(
            menu_frame,
            text="🚪 Quit",
            command=self.exit_game,
            font=self.title_font,
            bg='#666666',
            fg='white',
            width=12,
            height=2
        )
        quit_btn.pack(pady=15)
        
        # Credit label
        credit_label = tk.Label(
            self.content_frame,
            text="Developed by People's Gospel",
            font=self.small_font,
            bg='black',
            fg='#666666'
        )
        credit_label.pack(side='bottom', pady=20)
        
    def show_register_screen(self):
        """Show dedicated registration screen with improved validation"""
        self.current_screen = "register"
        self.clear_content()
        
        # Title
        title_label = tk.Label(
            self.content_frame,
            text="✨ CREATE NEW ACCOUNT ✨",
            font=self.title_font,
            bg='black',
            fg='#66CCFF'
        )
        title_label.pack(pady=40)
        
        # Registration form
        register_frame = tk.LabelFrame(
            self.content_frame,
            text="Account Registration",
            font=self.header_font,
            bg='#1a1a1a',
            fg='#66CCFF',
            bd=3,
            relief='ridge'
        )
        register_frame.pack(pady=30, padx=100, fill='x')
        
        # Instructions
        instructions = tk.Label(
            register_frame,
            text="Create your nightmare nexus account\nPassword must be at least 8 characters with 2+ numbers",
            font=self.body_font,
            bg='#1a1a1a',
            fg='white',
            justify='center'
        )
        instructions.pack(pady=15)
        
        # Username entry
        username_frame = tk.Frame(register_frame, bg='#1a1a1a')
        username_frame.pack(pady=20)
        
        username_label = tk.Label(
            username_frame,
            text="Username (min 3 characters):",
            font=self.header_font,
            bg='#1a1a1a',
            fg='white'
        )
        username_label.pack(pady=5)
        
        self.reg_username_entry = tk.Entry(
            username_frame,
            font=self.header_font,
            bg='#2a2a2a',
            fg='white',
            width=25,
            relief='solid',
            bd=2,
            justify='center'
        )
        self.reg_username_entry.pack(pady=5)
        
        # Password entry
        password_label = tk.Label(
            username_frame,
            text="Password (min 8 chars, 2+ numbers):",
            font=self.header_font,
            bg='#1a1a1a',
            fg='white'
        )
        password_label.pack(pady=(15, 5))
        
        self.reg_password_entry = tk.Entry(
            username_frame,
            font=self.header_font,
            bg='#2a2a2a',
            fg='white',
            width=25,
            relief='solid',
            bd=2,
            justify='center',
            show='*'
        )
        self.reg_password_entry.pack(pady=5)
        
        # Confirm password entry
        confirm_label = tk.Label(
            username_frame,
            text="Confirm Password:",
            font=self.header_font,
            bg='#1a1a1a',
            fg='white'
        )
        confirm_label.pack(pady=(15, 5))
        
        self.reg_confirm_entry = tk.Entry(
            username_frame,
            font=self.header_font,
            bg='#2a2a2a',
            fg='white',
            width=25,
            relief='solid',
            bd=2,
            justify='center',
            show='*'
        )
        self.reg_confirm_entry.pack(pady=5)
        
        # Show/Hide Password button
        toggle_frame = tk.Frame(username_frame, bg='#1a1a1a')
        toggle_frame.pack(pady=5)
        
        self.reg_password_visible = False
        self.reg_toggle_password_btn = tk.Button(
            toggle_frame,
            text="👁️ Show Passwords",
            command=self.toggle_reg_password_visibility,
            font=self.small_font,
            bg='#333333',
            fg='white',
            width=15
        )
        self.reg_toggle_password_btn.pack()
        
        # Bind Enter key
        self.reg_username_entry.bind('<Return>', lambda e: self.reg_password_entry.focus_set())
        self.reg_password_entry.bind('<Return>', lambda e: self.reg_confirm_entry.focus_set())
        self.reg_confirm_entry.bind('<Return>', lambda e: self.handle_registration())
        
        # Buttons frame
        buttons_frame = tk.Frame(register_frame, bg='#1a1a1a')
        buttons_frame.pack(pady=20)
        
        # Register button
        register_btn = tk.Button(
            buttons_frame,
            text="✨ Create Account",
            command=self.handle_registration,
            font=self.header_font,
            bg='#0066CC',
            fg='white',
            width=15,
            height=2
        )
        register_btn.pack(side='left', padx=10)
        
        # Back button
        back_btn = tk.Button(
            buttons_frame,
            text="🔙 Back",
            command=self.show_welcome_screen,
            font=self.header_font,
            bg='#666666',
            fg='white',
            width=15,
            height=2
        )
        back_btn.pack(side='left', padx=10)
        
        # Status message area
        self.reg_status_label = tk.Label(
            register_frame,
            text="",
            font=self.body_font,
            bg='#1a1a1a',
            fg='#66FF66'
        )
        self.reg_status_label.pack(pady=5)
        
        # Focus on username entry
        self.reg_username_entry.focus_set()
    
    def handle_registration(self):
        """Handle account registration with improved password validation"""
        username = self.reg_username_entry.get().strip()
        password = self.reg_password_entry.get().strip()
        confirm = self.reg_confirm_entry.get().strip()
        
        # Validate username
        if not username:
            self.reg_status_label.config(text="❌ Please enter a username!", fg='#FF6666')
            return
        
        if len(username) < 3:
            self.reg_status_label.config(text="❌ Username must be at least 3 characters!", fg='#FF6666')
            return
        
        # Validate password
        if not password:
            self.reg_status_label.config(text="❌ Please enter a password!", fg='#FF6666')
            return
        
        if len(password) < 8:
            self.reg_status_label.config(text="❌ Password must be at least 8 characters!", fg='#FF6666')
            return
        
        # Check for at least 2 numbers
        numbers_count = sum(1 for char in password if char.isdigit())
        if numbers_count < 2:
            self.reg_status_label.config(text="❌ Password must contain at least 2 numbers!", fg='#FF6666')
            return
        
        # Confirm password
        if password != confirm:
            self.reg_status_label.config(text="❌ Passwords do not match!", fg='#FF6666')
            return
        
        # Check if account already exists
        player_save_path = f"saves/player_{username.lower()}.json"
        if os.path.exists(player_save_path):
            self.reg_status_label.config(text="❌ Username already exists! Please choose another.", fg='#FF6666')
            return
        
        # Create new account
        try:
            self.create_player_account(username, password)
            self.reg_status_label.config(text=f"✅ Account '{username}' created successfully!", fg='#66FF66')
            self.show_notification(f"✨ Welcome to Nightmare Nexus, {username}!")
            # Setup main container and navigate to main menu
            self.setup_main_container()
            self.logged_in = True
            self.update_stats_display()
            self.root.after(1500, self.show_main_menu)
        except Exception as e:
            self.reg_status_label.config(text=f"❌ Error creating account: {str(e)}", fg='#FF6666')
            
    def check_for_saved_login(self):
        """Check for saved login preferences"""
        # Check if there's auto-login preference
        try:
            if os.path.exists("saves/login_prefs.json"):
                with open("saves/login_prefs.json", "r") as f:
                    login_prefs = json.load(f)
                    if login_prefs.get("auto_login") and login_prefs.get("username"):
                        # Try to auto-login
                        username = login_prefs["username"]
                        if login_prefs.get("is_developer"):
                            # Show welcome screen with auto-login option for dev
                            self.show_welcome_screen_with_autologin(username, True)
                        else:
                            # For regular users, just show welcome screen
                            self.show_welcome_screen()
                    else:
                        self.show_welcome_screen()
            else:
                self.show_welcome_screen()
        except:
            self.show_welcome_screen()
        
    def setup_developer_content(self):
        """Setup developer account with maxed content"""
        self.player_gems = 999999
        self.player_cash = 9999999
        self.player_level = 100
        self.player_xp = 9999999
        
        # Max items
        self.player_items = {"Small XP Pot": 9999, "Medium XP Pot": 9999, "Large XP Pot": 9999}
        
        # Unlock all content
        self.player_progress = {
            "world": self.NUM_WORLDS - 1,
            "stage": self.STAGES_PER_WORLD - 1,
            "unlocked": [[1] * self.STAGES_PER_WORLD for _ in range(self.NUM_WORLDS)],
            "dungeon_highest": 999
        }
        
        # Max all facilities
        self.player_facilities = {
            'research_lab': 10,
            'training_grounds': 15, 
            'rune_forge': 12,
            'nexus_core': 5,
            'bank_vault': 8,
            'gem_mine': 6
        }
        
        # Complete all research
        self.player_research = {
            'enhanced_summoning': True,
            'battle_efficiency': True,
            'rune_mastery': True,
            'nightmare_amplification': True
        }
        
        # Max rarity rates for epics/legendaries
        self.rarity_chances = {"Common": 0, "Rare": 0, "Epic": 50, "Legendary": 50}
        
        # Clear existing inventory and runes to rebuild with optimal setup
        self.player_inventory = []
        self.player_runes = []
        
        # Generate high-level legendary and epic runes
        for _ in range(50):
            rarity = random.choice(["Epic", "Legendary"])
            rune_type = random.choice(list(self.rune_types.keys()))
            rune = self.generate_rune(rarity, rune_type)
            rune['level'] = random.randint(12, 15)  # High level runes
            # Boost stats for developer account
            rune['main_value'] = int(rune['main_value'] * 1.8)
            for substat in rune['substats']:
                rune['substats'][substat] = int(rune['substats'][substat] * 1.5)
            self.player_runes.append(rune)
        
        # Add all Epic and Legendary units at max level with perfect stats
        for entity in self.entities:
            if entity["rarity"] in ["Epic", "Legendary"]:
                skill_level = 5 if entity["skill"] else 0
                unit = {
                    "entity": entity.copy(),
                    "level": 100, 
                    "exp": 0, 
                    "skill_level": skill_level,
                    "runes": {}  # Will store optimal rune equipment
                }
                self.player_inventory.append(unit)
                    
        # Auto-equip best runes optimally for each unit's playstyle
        self.auto_equip_best_runes()
        
        # Initialize multi-battle system
        self.multi_battle_active = False
        self.multi_battle_config = {}
                    
    def show_developer_welcome(self):
        """Show developer welcome notification after GUI is ready"""
        self.show_notification(f"🔧 Welcome, Developer! Account loaded with {len(self.player_inventory)} Epic/Legendary units.")
        self.show_notification("💡 All features unlocked for testing. Summon rates boosted to Epic/Legendary only.")
    
    def update_stats_display(self):
        """Update the stats display in navigation"""
        # Only update if stats label exists and current user is logged in
        if not hasattr(self, 'stats_label') or not self.stats_label.winfo_exists():
            return
            
        if self.current_user and self.logged_in:
            user_text = f"👤 {self.current_user['username']}"
            if self.current_user.get('is_developer'):
                user_text += " [DEV]"
            stats_text = f"{user_text} | 💎 {self.player_gems:,} | 🪙 {self.player_cash:,} | Lv.{self.player_level} | Units: {len(self.player_inventory)}"
        else:
            stats_text = "Not logged in"
            
        self.stats_label.config(text=stats_text)
    
    def show_notification(self, message, color='#66FF66'):
        """Show notification in the notification area"""
        # Check if notification_text widget exists (only in main container)
        if hasattr(self, 'notification_text') and self.notification_text:
            self.notification_text.config(state='normal')
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.notification_text.insert('end', f"[{timestamp}] {message}\n")
            self.notification_text.see('end')
            self.notification_text.config(state='disabled')
            
            # Auto-scroll and limit lines
            lines = self.notification_text.get('1.0', 'end').count('\n')
            if lines > 20:
                self.notification_text.config(state='normal')
                self.notification_text.delete('1.0', '2.0')
                self.notification_text.config(state='disabled')
        else:
            # Fallback for startup screens - print to console or store for later
            print(f"[NOTIFICATION] {message}")
            
    def add_battle_log(self, message, color='white'):
        """Add message to battle log display"""
        if hasattr(self, 'battle_log_display'):
            self.battle_log_display.config(state='normal')
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.battle_log_display.insert('end', f"[{timestamp}] {message}\n")
            self.battle_log_display.see('end')
            self.battle_log_display.config(state='disabled')
            
            # Auto-scroll and limit lines
            lines = self.battle_log_display.get('1.0', 'end').count('\n')
            if lines > 50:
                self.battle_log_display.config(state='normal')
                self.battle_log_display.delete('1.0', '2.0')
                self.battle_log_display.config(state='disabled')
            
    def clear_content(self):
        """Clear the content area"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
    def navigate_to(self, screen_name, *args):
        """Navigate to a screen and update history stack"""
        # Add current screen to history if different from target
        if self.current_screen != screen_name and self.current_screen:
            # Avoid duplicate consecutive entries
            if not self.screen_history or self.screen_history[-1] != self.current_screen:
                self.screen_history.append(self.current_screen)
        
        self.current_screen = screen_name
        
        # Update back button state
        self.back_btn.config(state='normal' if self.screen_history else 'disabled')
        
    def go_home(self):
        """Go to home screen and clear history"""
        # Only allow home navigation if user is logged in
        if not self.current_user or not self.logged_in:
            self.show_notification("❌ Please log in first!")
            self.show_welcome_screen()
            return
            
        self.screen_history.clear()
        if hasattr(self, 'back_btn') and self.back_btn.winfo_exists():
            self.back_btn.config(state='disabled')
        self.current_screen = "main_menu"
        self.show_main_menu()
        
    def go_back(self):
        """Go back to previous screen using history stack"""
        # Only allow back navigation if user is logged in
        if not self.current_user or not self.logged_in:
            self.show_notification("❌ Please log in first!")
            self.show_welcome_screen()
            return
            
        if not self.screen_history:
            # If no history, go to main menu
            self.go_home()
            return
        
        # Pop the most recent screen from history
        previous_screen = self.screen_history.pop()
        self.current_screen = previous_screen
        
        # Navigate to the previous screen
        self._navigate_to_screen(previous_screen)
        
        # Update back button state
        if hasattr(self, 'back_btn') and self.back_btn.winfo_exists():
            self.back_btn.config(state='normal' if self.screen_history else 'disabled')
    
    def _navigate_to_screen(self, screen_name):
        """Navigate to a specific screen by name without updating history"""
        navigation_map = {
            "main_menu": self.show_main_menu,
            "summon": self.show_summon_portal,
            "campaign": self.show_world_campaign,
            "units": self.show_unit_collection,
            "depths": self.show_depths_hub,
            "facility_hub": self.show_facility_hub,
            "rune_management": self.show_rune_management,
            "account_manager": self.show_account_manager,
            "help_menu": self.show_help_menu,
            "endless_delve": self.show_endless_delve,
            "rune_sanctums": self.show_rune_sanctums,
            "xp_training": self.show_xp_training,
            "research_lab": self.show_research_lab,
            "training_grounds": self.show_training_grounds,
            "rune_forge": self.show_rune_forge,
            "nexus_core": self.show_nexus_core,
            "bank_vault": self.show_bank_vault,
            "gem_mine": self.show_gem_mine
        }
        
        # Handle special cases with parameters
        if screen_name.startswith("world_"):
            world_idx = int(screen_name.split("_")[1]) if "_" in screen_name else 0
            self.enter_world(world_idx)
        elif screen_name in navigation_map:
            navigation_map[screen_name]()
        else:
            # Fallback to main menu for unknown screens
            self.show_main_menu()
        
    def show_login_screen(self):
        """Show the login screen with proper navigation and login functionality"""
        self.current_screen = "login"
        self.clear_content()
        
        # Title
        title_label = tk.Label(
            self.content_frame,
            text="🔑 LOGIN TO NIGHTMARE NEXUS 🔑",
            font=self.title_font,
            bg='black',
            fg='#FF3333'
        )
        title_label.pack(pady=30)
        
        # Login form frame
        login_frame = tk.LabelFrame(
            self.content_frame,
            text="Account Login",
            font=self.header_font,
            bg='#1a1a1a',
            fg='#66CCFF',
            bd=3,
            relief='ridge'
        )
        login_frame.pack(pady=30, padx=100, fill='x')
        
        # Instructions
        instructions = tk.Label(
            login_frame,
            text="Enter your credentials to access your account",
            font=self.body_font,
            bg='#1a1a1a',
            fg='white',
            justify='center'
        )
        instructions.pack(pady=15)
        
        # Username entry
        username_frame = tk.Frame(login_frame, bg='#1a1a1a')
        username_frame.pack(pady=20)
        
        username_label = tk.Label(
            username_frame,
            text="Username:",
            font=self.header_font,
            bg='#1a1a1a',
            fg='white'
        )
        username_label.pack(pady=5)
        
        self.username_entry = tk.Entry(
            username_frame,
            font=self.header_font,
            bg='#2a2a2a',
            fg='white',
            width=25,
            relief='solid',
            bd=2,
            justify='center'
        )
        self.username_entry.pack(pady=5)
        
        # Password entry
        password_label = tk.Label(
            username_frame,
            text="Password:",
            font=self.header_font,
            bg='#1a1a1a',
            fg='white'
        )
        password_label.pack(pady=(15, 5))
        
        self.password_entry = tk.Entry(
            username_frame,
            font=self.header_font,
            bg='#2a2a2a',
            fg='white',
            width=25,
            relief='solid',
            bd=2,
            justify='center',
            show='*'  # Hide password characters
        )
        self.password_entry.pack(pady=5)
        
        # Show/Hide Password button
        toggle_frame = tk.Frame(username_frame, bg='#1a1a1a')
        toggle_frame.pack(pady=5)
        
        self.password_visible = False
        self.toggle_password_btn = tk.Button(
            toggle_frame,
            text="👁️ Show Password",
            command=self.toggle_password_visibility,
            font=self.small_font,
            bg='#333333',
            fg='white',
            width=15
        )
        self.toggle_password_btn.pack()
        
        # Bind Enter key to both fields
        self.username_entry.bind('<Return>', lambda e: self.password_entry.focus_set())
        self.password_entry.bind('<Return>', lambda e: self.handle_login())
        
        # Buttons frame
        buttons_frame = tk.Frame(login_frame, bg='#1a1a1a')
        buttons_frame.pack(pady=20)
        
        # Login button
        login_btn = tk.Button(
            buttons_frame,
            text="🔑 Login",
            command=self.handle_login,
            font=self.header_font,
            bg='#006600',
            fg='white',
            width=12,
            height=2
        )
        login_btn.pack(side='left', padx=10)
        
        # Back to welcome button
        back_btn = tk.Button(
            buttons_frame,
            text="🔙 Back",
            command=self.show_welcome_screen,
            font=self.header_font,
            bg='#666666',
            fg='white',
            width=12,
            height=2
        )
        back_btn.pack(side='left', padx=10)
        
        # Status message area
        self.login_status_label = tk.Label(
            login_frame,
            text="",
            font=self.body_font,
            bg='#1a1a1a',
            fg='#66FF66'
        )
        self.login_status_label.pack(pady=5)
        
        # Tips
        tips_label = tk.Label(
            self.content_frame,
            text="💡 Tips:\n" +
                 "• Enter your username and password, then click Login\n" +
                 "• New user? Go back and select Register\n" +
                 "• Create a new account to start your nightmare collection!",
            font=self.small_font,
            bg='black',
            fg='#CCCCCC',
            justify='center'
        )
        tips_label.pack(pady=30)
        
        # Focus on username entry
        self.username_entry.focus_set()
    
    def toggle_password_visibility(self):
        """Toggle password visibility"""
        self.password_visible = not self.password_visible
        if self.password_visible:
            self.password_entry.config(show='')
            self.toggle_password_btn.config(text="🙈 Hide Password")
        else:
            self.password_entry.config(show='*')
            self.toggle_password_btn.config(text="👁️ Show Password")
    
    def toggle_reg_password_visibility(self):
        """Toggle registration password visibility"""
        self.reg_password_visible = not self.reg_password_visible
        if self.reg_password_visible:
            self.reg_password_entry.config(show='')
            self.reg_confirm_entry.config(show='')
            self.reg_toggle_password_btn.config(text="🙈 Hide Passwords")
        else:
            self.reg_password_entry.config(show='*')
            self.reg_confirm_entry.config(show='*')
            self.reg_toggle_password_btn.config(text="👁️ Show Passwords")
    
    def handle_login(self):
        """Handle user login"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        # Validate username
        if not username:
            self.login_status_label.config(text="❌ Please enter a username!", fg='#FF6666')
            return
        
        if len(username) < 3:
            self.login_status_label.config(text="❌ Username must be at least 3 characters!", fg='#FF6666')
            return
        
        # Validate password
        if not password:
            self.login_status_label.config(text="❌ Please enter a password!", fg='#FF6666')
            return
        
        # Check for developer account first
        if username.lower() == "dev_nn":
            self.login_developer_account(password)
            return
            
        # Handle regular accounts
        self.login_regular_account(username, password)
        """Handle unified login/register process with password authentication"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        # Validate username
        if not username:
            self.login_status_label.config(text="❌ Please enter a username!", fg='#FF6666')
            return
        
        if len(username) < 3:
            self.login_status_label.config(text="❌ Username must be at least 3 characters!", fg='#FF6666')
            return
        
        # Validate password
        if not password:
            self.login_status_label.config(text="❌ Please enter a password!", fg='#FF6666')
            return
        
        if len(password) < 6:
            self.login_status_label.config(text="❌ Password must be at least 6 characters!", fg='#FF6666')
            return
        
        # Check for developer account
        if username.lower() == "dev_nn":
            self.login_developer_account(password)
            return
            
        # Handle regular accounts
        self.login_regular_account(username, password)
    
    def hash_password(self, password):
        """Hash password for secure storage"""
        # Simple but effective password hashing using hashlib
        import hashlib
        salt = "nightmare_nexus_salt_2024"  # Static salt for simplicity
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def verify_password(self, password, hashed_password):
        """Verify password against hash"""
        return self.hash_password(password) == hashed_password
    
    def login_developer_account(self, password):
        """Login to the developer account with password verification"""
        # Developer password verification
        dev_password = "akorede12"  # Developer password
        
        if password != dev_password:
            self.login_status_label.config(text="❌ Invalid developer credentials!", fg='#FF6666')
            return
        
        self.current_user = {
            "username": "dev_nn",
            "is_developer": True
        }
        
        # Setup developer content
        self.setup_developer_content()
        
        self.login_status_label.config(text="✅ Developer account loaded!", fg='#66FF66')
        self.show_notification("🔧 Welcome, Developer! All features unlocked.")
        
        # Setup main container and navigate to main menu
        self.setup_main_container()
        self.logged_in = True
        self.update_stats_display()
        
        # Navigate to main menu after brief delay
        self.root.after(1000, self.show_main_menu)
    def login_regular_account(self, username, password):
        """Login or create a regular account with password authentication"""
        # Check if account exists
        player_save_path = f"saves/player_{username.lower()}.json"
        
        if os.path.exists(player_save_path):
            # Load existing account and verify password
            try:
                account_data = self.load_account_data(player_save_path)
                stored_password_hash = account_data.get('password_hash')
                
                if not stored_password_hash:
                    # Legacy account without password - deny login for security
                    self.login_status_label.config(text="❌ Account exists but no password set. Contact admin.", fg='#FF6666')
                    return
                elif self.verify_password(password, stored_password_hash):
                    # Correct password
                    self.load_player_account_from_data(username, account_data)
                    self.login_status_label.config(text=f"✅ Welcome back, {username}!", fg='#66FF66')
                    self.show_notification(f"👤 Account loaded: {username}")
                    
                    # Setup main container and navigate to main menu
                    self.setup_main_container()
                    self.logged_in = True
                    self.update_stats_display()
                    self.root.after(1000, self.show_main_menu)
                else:
                    # Wrong password
                    self.login_status_label.config(text="❌ Invalid username or password!", fg='#FF6666')
                    return
            except Exception as e:
                self.login_status_label.config(text=f"❌ Error loading account: {str(e)}", fg='#FF6666')
                return
        else:
            # Account doesn't exist
            self.login_status_label.config(text="❌ Account not found! Please register first.", fg='#FF6666')
            return
    
    def load_account_data(self, save_path):
        """Load account data from file"""
        with open(save_path, "r") as f:
            return json.load(f)
    
    def save_account_data(self, save_path, account_data):
        """Save account data to file"""
        with open(save_path, "w") as f:
            json.dump(account_data, f, indent=2)
    
    def load_player_account_from_data(self, username, save_data):
        """Load player account from data dict"""
        self.current_user = {
            "username": username,
            "is_developer": False
        }
        
        # Load player data
        self.player_gems = save_data.get("player_gems", 100)
        self.player_cash = save_data.get("player_cash", 500)
        self.player_level = save_data.get("player_level", 1)
        self.player_xp = save_data.get("player_xp", 0)
        self.player_inventory = save_data.get("player_inventory", [])
        self.player_items = save_data.get("player_items", {"Small XP Pot": 5, "Medium XP Pot": 2, "Large XP Pot": 0})
        self.player_runes = save_data.get("player_runes", [])
        self.player_progress = save_data.get("player_progress", {
            "world": 0,
            "stage": 0,
            "unlocked": [[1] + [0]*19] + [[0]*20 for _ in range(4)],
            "dungeon_highest": 1
        })
        self.player_facilities = save_data.get("player_facilities", {
            'research_lab': 1, 'training_grounds': 1, 'rune_forge': 1,
            'nexus_core': 1, 'bank_vault': 1, 'gem_mine': 1
        })
        self.player_research = save_data.get("player_research", {})
        
        # Reset to normal rarity chances for player accounts
        self.rarity_chances = {
            "Common": 60,
            "Rare": 25,
            "Epic": 10,
            "Legendary": 5
        }
        
        # Ensure backward compatibility
        for rune in self.player_runes:
            if "set" not in rune:
                rune["set"] = random.choice(list(self.rune_sets.keys()))
        
        for unit in self.player_inventory:
            if "runes" not in unit:
                unit["runes"] = {}
    
    def create_player_account(self, username, password):
        """Create a new player account with starter content and password"""
        self.current_user = {
            "username": username,
            "is_developer": False
        }
        
        # Reset to normal starting values
        self.player_gems = 100
        self.player_cash = 500
        self.player_level = 1
        self.player_xp = 0
        self.player_inventory = []
        self.player_items = {"Small XP Pot": 5, "Medium XP Pot": 2, "Large XP Pot": 0}
        self.player_runes = []
        self.player_progress = {
            "world": 0,
            "stage": 0,
            "unlocked": [[1] + [0]*19] + [[0]*20 for _ in range(4)],
            "dungeon_highest": 1
        }
        self.player_facilities = {
            'research_lab': 1,
            'training_grounds': 1,
            'rune_forge': 1,
            'nexus_core': 1,
            'bank_vault': 1,
            'gem_mine': 1
        }
        self.player_research = {}
        
        # Reset rarity chances to normal
        self.rarity_chances = {
            "Common": 60,
            "Rare": 25,
            "Epic": 10,
            "Legendary": 5
        }
        
        # Give starter units (2 common, 1 rare)
        starter_commons = [e for e in self.entities if e["rarity"] == "Common"]
        starter_rares = [e for e in self.entities if e["rarity"] == "Rare"]
        
        for _ in range(2):
            if starter_commons:
                entity = random.choice(starter_commons).copy()
                unit = {
                    "entity": entity,
                    "level": 1,
                    "exp": 0,
                    "skill_level": 0,
                    "runes": {}
                }
                self.player_inventory.append(unit)
        
        if starter_rares:
            entity = random.choice(starter_rares).copy()
            unit = {
                "entity": entity,
                "level": 1,
                "exp": 0,
                "skill_level": 0,
                "runes": {}
            }
            self.player_inventory.append(unit)
        
        # Give starter runes
        for _ in range(5):
            rune = self.generate_rune("Common")
            self.player_runes.append(rune)
        
        for _ in range(2):
            rune = self.generate_rune("Rare")
            self.player_runes.append(rune)
        
        # Save the new account with password hash
        self.save_player_account_with_password(password)
    
    def load_player_account(self, username, save_path):
        """Load an existing player account"""
        try:
            with open(save_path, "r") as f:
                save_data = json.load(f)
            
            self.current_user = {
                "username": username,
                "is_developer": False
            }
            
            # Load player data
            self.player_gems = save_data.get("player_gems", 100)
            self.player_cash = save_data.get("player_cash", 500)
            self.player_level = save_data.get("player_level", 1)
            self.player_xp = save_data.get("player_xp", 0)
            self.player_inventory = save_data.get("player_inventory", [])
            self.player_items = save_data.get("player_items", {"Small XP Pot": 5, "Medium XP Pot": 2, "Large XP Pot": 0})
            self.player_runes = save_data.get("player_runes", [])
            self.player_progress = save_data.get("player_progress", {
                "world": 0,
                "stage": 0,
                "unlocked": [[1] + [0]*19] + [[0]*20 for _ in range(4)],
                "dungeon_highest": 1
            })
            self.player_facilities = save_data.get("player_facilities", {
                'research_lab': 1, 'training_grounds': 1, 'rune_forge': 1,
                'nexus_core': 1, 'bank_vault': 1, 'gem_mine': 1
            })
            self.player_research = save_data.get("player_research", {})
            
            # Load battle preferences
            battle_prefs = save_data.get("battle_preferences", {})
            self.auto_battle_preference = battle_prefs.get("auto_battle_preference", False)
            self.battle_speed_preference = battle_prefs.get("battle_speed_preference", 1)
            
            # Reset to normal rarity chances for player accounts
            self.rarity_chances = {
                "Common": 60,
                "Rare": 25,
                "Epic": 10,
                "Legendary": 5
            }
            
            # Ensure backward compatibility
            for rune in self.player_runes:
                if "set" not in rune:
                    rune["set"] = random.choice(list(self.rune_sets.keys()))
            
            for unit in self.player_inventory:
                if "runes" not in unit:
                    unit["runes"] = {}
                    
        except Exception as e:
            self.show_notification(f"❌ Error loading account: {e}. Creating new account.", '#FF6666')
            self.create_player_account(username)
    
    def save_player_account(self):
        """Save current player account data"""
        if not self.current_user or self.current_user.get('is_developer'):
            return  # Don't save developer account as player data
        
        username = self.current_user['username']
        save_path = f"saves/player_{username.lower()}.json"
        
        # Load existing data to preserve password hash
        existing_password_hash = None
        if os.path.exists(save_path):
            try:
                with open(save_path, "r") as f:
                    existing_data = json.load(f)
                    existing_password_hash = existing_data.get('password_hash')
            except:
                pass
        
        # Ensure cleared_stages is a list for JSON compatibility
        progress_copy = self.player_progress.copy()
        if "cleared_stages" in progress_copy and isinstance(progress_copy["cleared_stages"], set):
            progress_copy["cleared_stages"] = list(progress_copy["cleared_stages"])
        
        save_data = {
            "version": "1.2",
            "username": username,
            "password_hash": existing_password_hash,  # Preserve existing password hash
            "player_gems": self.player_gems,
            "player_cash": self.player_cash,
            "player_level": self.player_level,
            "player_xp": self.player_xp,
            "player_inventory": self.player_inventory,
            "player_items": self.player_items,
            "player_runes": self.player_runes,
            "player_progress": progress_copy,
            "player_facilities": self.player_facilities,
            "player_research": self.player_research,
            "battle_preferences": {
                "auto_battle_preference": self.auto_battle_preference,
                "battle_speed_preference": self.battle_speed_preference
            }
        }
        
        # Ensure save directory exists
        os.makedirs("saves", exist_ok=True)
        
        # Save to user-specific file
        with open(save_path, "w") as f:
            json.dump(save_data, f, indent=2)
    
    def save_player_account_with_password(self, password):
        """Save new player account with password hash"""
        if not self.current_user or self.current_user.get('is_developer'):
            return
        
        username = self.current_user['username']
        # Ensure cleared_stages is a list for JSON compatibility
        progress_copy = self.player_progress.copy()
        if "cleared_stages" in progress_copy and isinstance(progress_copy["cleared_stages"], set):
            progress_copy["cleared_stages"] = list(progress_copy["cleared_stages"])
        
        save_data = {
            "version": "1.2",
            "username": username,
            "password_hash": self.hash_password(password),
            "player_gems": self.player_gems,
            "player_cash": self.player_cash,
            "player_level": self.player_level,
            "player_xp": self.player_xp,
            "player_inventory": self.player_inventory,
            "player_items": self.player_items,
            "player_runes": self.player_runes,
            "player_progress": progress_copy,
            "player_facilities": self.player_facilities,
            "player_research": self.player_research,
            "battle_preferences": {
                "auto_battle_preference": self.auto_battle_preference,
                "battle_speed_preference": self.battle_speed_preference
            }
        }
        
        # Ensure save directory exists
        os.makedirs("saves", exist_ok=True)
        
        # Save to user-specific file
        save_path = f"saves/player_{username.lower()}.json"
        with open(save_path, "w") as f:
            json.dump(save_data, f, indent=2)
    
    def logout(self):
        """Logout current user and return to login screen"""
        # Save current account before logout
        if self.current_user and not self.current_user.get('is_developer'):
            self.save_player_account()
        elif self.current_user and self.current_user.get('is_developer'):
            # Save developer progress to main save file
            self.save_game_data()
        
        # Clear current user and login state
        self.current_user = None
        self.logged_in = False
        
        # Clear navigation history
        self.screen_history.clear()
        
        # Destroy the main container completely to avoid UI persistence
        if hasattr(self, 'main_frame') and self.main_frame.winfo_exists():
            self.main_frame.destroy()
        if hasattr(self, 'nav_frame') and self.nav_frame.winfo_exists():
            self.nav_frame.destroy()
        if hasattr(self, 'notification_frame') and self.nav_frame.winfo_exists():
            self.notification_frame.destroy()
        
        # Clear references to avoid accessing destroyed widgets
        if hasattr(self, 'back_btn'):
            del self.back_btn
        if hasattr(self, 'home_btn'):
            del self.home_btn
        if hasattr(self, 'stats_label'):
            del self.stats_label
        if hasattr(self, 'notification_text'):
            del self.notification_text
        
        # Reset to startup container
        self.setup_startup_container()
        
        print("[NOTIFICATION] 👋 Logged out successfully!")
        self.show_welcome_screen()

    def show_main_menu(self):
        """Show the main menu"""
        self.current_screen = "main_menu"
        self.clear_content()
        
        # Main title
        title_label = tk.Label(
            self.content_frame,
            text="NIGHTMARE NEXUS",
            font=self.title_font,
            bg='black',
            fg='#FF3333'
        )
        title_label.pack(pady=20)
        
        subtitle_label = tk.Label(
            self.content_frame,
            text="Summon • Manage • Conquer",
            font=self.header_font,
            bg='black',
            fg='#CCCCCC'
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Create main menu buttons in a grid
        menu_frame = tk.Frame(self.content_frame, bg='black')
        menu_frame.pack(expand=True)
        
        buttons = [
            ("🌟 Summon Portal", self.show_summon_portal, 0, 0),
            ("🏭 Facility Hub", self.show_facility_hub, 0, 1),
            ("🗺️ World Campaign", self.show_world_campaign, 0, 2),
            ("🕳️ The Depths", self.show_depths_hub, 1, 0),
            ("👥 Unit Collection", self.show_unit_collection, 1, 1),
            ("🎰 Rune Management", self.show_rune_management, 1, 2),
            ("👤 Account Manager", self.show_account_manager, 2, 0),
            ("❓ Help & Options", self.show_help_menu, 2, 1),
            ("🚪 Exit Game", self.exit_game, 2, 2),
        ]
        
        for text, command, row, col in buttons:
            btn = tk.Button(
                menu_frame,
                text=text,
                command=command,
                font=self.header_font,
                bg='#333333',
                fg='white',
                relief='raised',
                bd=3,
                width=18,
                height=3
            )
            btn.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
            
        # Configure grid weights
        for i in range(3):
            menu_frame.grid_rowconfigure(i, weight=1)
            menu_frame.grid_columnconfigure(i, weight=1)
            
    def show_summon_portal(self):
        """Show the summon portal interface"""
        self.navigate_to("summon")
        self.clear_content()
        
        # Title
        title_label = tk.Label(
            self.content_frame,
            text="✨ NIGHTMARE SUMMON PORTAL ✨",
            font=self.title_font,
            bg='black',
            fg='#66CCFF'
        )
        title_label.pack(pady=20)
        
        # Current gems display
        gems_label = tk.Label(
            self.content_frame,
            text=f"💎 Gems: {self.player_gems:,}",
            font=self.header_font,
            bg='black',
            fg='#FFFF66'
        )
        gems_label.pack(pady=10)
        
        # Banners frame
        banners_frame = tk.Frame(self.content_frame, bg='black')
        banners_frame.pack(pady=20, padx=20, fill='both', expand=True)
        
        banners = [
            ("Normal Banner", "Standard rates - no boosts", None),
            ("Creepypasta Banner", "Boosted rates for Slender, Jeff the Killer, The Rake", "Creepypasta"),
            ("SCP Banner", "Boosted rates for SCP-999, SCP-682", "SCP"),
            ("Analogue Banner", "Boosted rate for Iris", "Analogue")
        ]
        
        for i, (name, desc, banner_type) in enumerate(banners):
            banner_frame = tk.LabelFrame(
                banners_frame,
                text=name,
                font=self.header_font,
                bg='#1a1a1a',
                fg='#FFCC66',
                bd=2,
                relief='ridge'
            )
            banner_frame.pack(fill='x', pady=10, padx=10)
            
            # Description
            desc_label = tk.Label(
                banner_frame,
                text=desc,
                font=self.body_font,
                bg='#1a1a1a',
                fg='white',
                wraplength=400
            )
            desc_label.pack(pady=5)
            
            # Buttons frame
            btn_frame = tk.Frame(banner_frame, bg='#1a1a1a')
            btn_frame.pack(pady=10)
            
            # Single summon
            single_btn = tk.Button(
                btn_frame,
                text="🌟 Single (5 💎)",
                command=lambda bt=banner_type: self.single_summon(bt),
                font=self.body_font,
                bg='#006600',
                fg='white',
                width=15
            )
            single_btn.pack(side='left', padx=5)
            
            # Multi summon
            multi_btn = tk.Button(
                btn_frame,
                text="✨ Multi 10x (50 💎)",
                command=lambda bt=banner_type: self.multi_summon(bt),
                font=self.body_font,
                bg='#0066CC',
                fg='white',
                width=15
            )
            multi_btn.pack(side='left', padx=5)
            
    def single_summon(self, banner_type=None):
        """Perform a single summon"""
        if self.player_gems < 5:
            self.show_notification("❌ Insufficient gems! Need 5 gems for single summon.", '#FF6666')
            return
            
        self.player_gems -= 5
        entity = self.summon_entity(banner_type)
        
        if entity:
            # Add to inventory
            unit = {
                "entity": entity.copy(),
                "level": 1,
                "exp": 0,
                "skill_level": 0,
                "runes": {}
            }
            self.player_inventory.append(unit)
            
            color = self.rarity_colors[entity["rarity"]]
            self.show_notification(f"⭐ Summoned: {entity['name']} ({entity['rarity']})!")
            
        # Refresh stats display
        self.update_stats_display()
        
    def multi_summon(self, banner_type=None):
        """Perform a multi summon (10x)"""
        if self.player_gems < 50:
            self.show_notification("❌ Insufficient gems! Need 50 gems for multi summon.", '#FF6666')
            return
            
        self.player_gems -= 50
        results = []
        
        for _ in range(10):
            entity = self.summon_entity(banner_type)
            if entity:
                unit = {
                    "entity": entity.copy(),
                    "level": 1,
                    "exp": 0,
                    "skill_level": 0,
                    "runes": {}
                }
                self.player_inventory.append(unit)
                results.append(entity)
                
        # Show results
        if results:
            self.show_notification("✨ Multi Summon Results:")
            rarity_counts = {"Common": 0, "Rare": 0, "Epic": 0, "Legendary": 0}
            
            for entity in results:
                rarity_counts[entity["rarity"]] += 1
                self.show_notification(f"  • {entity['name']} ({entity['rarity']})")
                
            # Summary
            summary = " | ".join([f"{r}: {c}" for r, c in rarity_counts.items() if c > 0])
            self.show_notification(f"Summary: {summary}")
            
        # Refresh stats
        self.update_stats_display()
        
    def summon_entity(self, banner_type=None):
        """Summon a single entity with rarity chances"""
        # Calculate rarity based on banner
        chances = self.rarity_chances.copy()
        
        if banner_type:
            # Apply banner boosts (simplified)
            if banner_type == "Creepypasta":
                chances["Legendary"] = min(chances["Legendary"] * 2, 25)
            elif banner_type == "SCP":
                chances["Epic"] = min(chances["Epic"] * 1.5, 20)
                chances["Legendary"] = min(chances["Legendary"] * 1.5, 15)
            elif banner_type == "Analogue":
                chances["Legendary"] = min(chances["Legendary"] * 3, 30)
                
        # Normalize to 100%
        total = sum(chances.values())
        for rarity in chances:
            chances[rarity] = (chances[rarity] / total) * 100
            
        # Roll for rarity
        roll = random.randint(1, 100)
        cumulative = 0
        selected_rarity = "Common"
        
        for rarity in ["Legendary", "Epic", "Rare", "Common"]:
            cumulative += chances[rarity]
            if roll <= cumulative:
                selected_rarity = rarity
                break
                
        # Get entities of selected rarity
        rarity_entities = [e for e in self.entities if e["rarity"] == selected_rarity]
        
        if rarity_entities:
            return random.choice(rarity_entities).copy()
        return None
        
    def show_unit_collection(self):
        """Show the enhanced unit collection interface"""
        self.navigate_to("units")
        self.clear_content()
        
        # Title
        title_label = tk.Label(
            self.content_frame,
            text="👥 UNIT COLLECTION 👥",
            font=self.title_font,
            bg='black',
            fg='#66FFCC'
        )
        title_label.pack(pady=20)
        
        # Filter and sort controls
        controls_frame = tk.Frame(self.content_frame, bg='black')
        controls_frame.pack(fill='x', padx=20, pady=10)
        
        # Sort dropdown
        sort_label = tk.Label(controls_frame, text="Sort by:", font=self.body_font, bg='black', fg='white')
        sort_label.pack(side='left', padx=5)
        
        self.unit_sort_var = tk.StringVar(value="name")
        sort_menu = ttk.Combobox(controls_frame, textvariable=self.unit_sort_var, 
                                values=["name", "level", "rarity", "hp", "attack"], state="readonly", width=10)
        sort_menu.pack(side='left', padx=5)
        sort_menu.bind("<<ComboboxSelected>>", lambda e: self.refresh_unit_display())
        
        # Filter by rarity
        filter_label = tk.Label(controls_frame, text="Filter:", font=self.body_font, bg='black', fg='white')
        filter_label.pack(side='left', padx=(20, 5))
        
        self.unit_filter_var = tk.StringVar(value="All")
        filter_menu = ttk.Combobox(controls_frame, textvariable=self.unit_filter_var,
                                  values=["All", "Common", "Rare", "Epic", "Legendary"], state="readonly", width=10)
        filter_menu.pack(side='left', padx=5)
        filter_menu.bind("<<ComboboxSelected>>", lambda e: self.refresh_unit_display())
        
        # Units count
        self.unit_count_label = tk.Label(controls_frame, text="", font=self.body_font, bg='black', fg='#CCCCCC')
        self.unit_count_label.pack(side='right', padx=10)
        
        # Units display frame
        self.units_display_frame = tk.Frame(self.content_frame, bg='black')
        self.units_display_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        self.refresh_unit_display()
        
    def refresh_unit_display(self):
        """Refresh the unit display with current filters and sorting"""
        # Clear existing display
        for widget in self.units_display_frame.winfo_children():
            widget.destroy()
            
        # Get filtered and sorted units
        filtered_units = self.get_filtered_units()
        
        # Update count
        self.unit_count_label.config(text=f"Showing {len(filtered_units)} units")
        
        if not filtered_units:
            no_units_label = tk.Label(self.units_display_frame, text="No units match the current filter", 
                                     font=self.body_font, bg='black', fg='#666666')
            no_units_label.pack(pady=50)
            return
        
        # Scrollable frame for units
        canvas = tk.Canvas(self.units_display_frame, bg='black', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.units_display_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='black')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Display units in grid
        for i, (unit, original_idx) in enumerate(filtered_units):
            row = i // 3
            col = i % 3
            
            # Calculate level-scaled base stats and final stats with runes
            base_stats = self.calculate_unit_level_stats(unit)
            final_stats = self.calculate_unit_stats_with_runes(unit)
            
            unit_frame = tk.LabelFrame(
                scrollable_frame,
                text=f"{unit['entity']['name']} (Lv.{unit['level']})",
                font=self.body_font,
                bg='#1a1a1a',
                fg=self.rarity_colors[unit['entity']['rarity']],
                bd=2,
                relief='ridge'
            )
            unit_frame.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
            
            # Unit stats display: Base on left, bonus on right in green
            stats_frame = tk.Frame(unit_frame, bg='#1a1a1a')
            stats_frame.pack(pady=5, padx=5, fill='x')
            
            # HP display
            hp_frame = tk.Frame(stats_frame, bg='#1a1a1a')
            hp_frame.pack(fill='x', pady=1)
            
            hp_base_label = tk.Label(hp_frame, text=f"❤️ {base_stats['hp']}", font=self.small_font, bg='#1a1a1a', fg='white')
            hp_base_label.pack(side='left')
            
            hp_bonus = final_stats['hp'] - base_stats['hp']
            if hp_bonus > 0:
                hp_bonus_label = tk.Label(hp_frame, text=f" +{hp_bonus}", font=self.small_font, bg='#1a1a1a', fg='#66FF66')
                hp_bonus_label.pack(side='left')
            
            # Attack display
            atk_frame = tk.Frame(stats_frame, bg='#1a1a1a')
            atk_frame.pack(fill='x', pady=1)
            
            atk_base_label = tk.Label(atk_frame, text=f"⚔️ {base_stats['attack']}", font=self.small_font, bg='#1a1a1a', fg='white')
            atk_base_label.pack(side='left')
            
            atk_bonus = final_stats['attack'] - base_stats['attack']
            if atk_bonus > 0:
                atk_bonus_label = tk.Label(atk_frame, text=f" +{atk_bonus}", font=self.small_font, bg='#1a1a1a', fg='#66FF66')
                atk_bonus_label.pack(side='left')
            
            # Defense display
            def_frame = tk.Frame(stats_frame, bg='#1a1a1a')
            def_frame.pack(fill='x', pady=1)
            
            def_base_label = tk.Label(def_frame, text=f"🛡️ {base_stats['defense']}", font=self.small_font, bg='#1a1a1a', fg='white')
            def_base_label.pack(side='left')
            
            def_bonus = final_stats['defense'] - base_stats['defense']
            if def_bonus > 0:
                def_bonus_label = tk.Label(def_frame, text=f" +{def_bonus}", font=self.small_font, bg='#1a1a1a', fg='#66FF66')
                def_bonus_label.pack(side='left')
            
            # Speed display
            spd_frame = tk.Frame(stats_frame, bg='#1a1a1a')
            spd_frame.pack(fill='x', pady=1)
            
            spd_base_label = tk.Label(spd_frame, text=f"⚡ {base_stats['speed']}", font=self.small_font, bg='#1a1a1a', fg='white')
            spd_base_label.pack(side='left')
            
            spd_bonus = final_stats['speed'] - base_stats['speed']
            if spd_bonus > 0:
                spd_bonus_label = tk.Label(spd_frame, text=f" +{spd_bonus}", font=self.small_font, bg='#1a1a1a', fg='#66FF66')
                spd_bonus_label.pack(side='left')
            
            # No stats_text variable exists anymore - removed this label
            
            # Rune slots display
            runes_frame = tk.Frame(unit_frame, bg='#1a1a1a')
            runes_frame.pack(pady=5)
            
            runes_label = tk.Label(
                runes_frame,
                text="Rune Slots:",
                font=self.small_font,
                bg='#1a1a1a',
                fg='#CCCCCC'
            )
            runes_label.pack()
            
            slots_frame = tk.Frame(runes_frame, bg='#1a1a1a')
            slots_frame.pack()
            
            # 6 rune slots with types
            slot_types = ["⚔️", "🛡️", "💎", "✨", "✨", "✨"]
            for slot in range(1, 7):
                equipped_rune = None
                if slot in unit.get('runes', {}):
                    rune_id = unit['runes'][slot]
                    equipped_rune = next((r for r in self.player_runes if r["id"] == rune_id), None)
                
                slot_color = '#006600' if equipped_rune else '#333333'
                slot_text = slot_types[slot-1] if equipped_rune else f"[{slot}]"
                
                slot_btn = tk.Button(
                    slots_frame,
                    text=slot_text,
                    command=lambda u=original_idx, s=slot: self.manage_rune_slot_inline(u, s),
                    font=self.small_font,
                    bg=slot_color,
                    fg='white',
                    width=4,
                    height=1
                )
                slot_btn.pack(side='left', padx=1)
                
            # Buttons frame
            btn_frame = tk.Frame(unit_frame, bg='#1a1a1a')
            btn_frame.pack(pady=5)
                
            # Details button
            details_btn = tk.Button(
                btn_frame,
                text="📋 Details",
                command=lambda u=original_idx: self.show_unit_details_inline(u),
                font=self.small_font,
                bg='#006666',
                fg='white',
                width=10
            )
            details_btn.pack(side='left', padx=2)
            
            # Test Unit button
            test_btn = tk.Button(
                btn_frame,
                text="⚔️ Test",
                command=lambda u=original_idx: self.start_unit_test(u),
                font=self.small_font,
                bg='#CC3300',
                fg='white',
                width=10
            )
            test_btn.pack(side='left', padx=2)
            
        # Configure grid weights
        for col in range(3):
            scrollable_frame.grid_columnconfigure(col, weight=1)
            
    def get_filtered_units(self):
        """Get filtered and sorted units with their original indices"""
        # Create list of (unit, original_index) tuples
        units_with_idx = [(unit, i) for i, unit in enumerate(self.player_inventory)]
        
        # Apply filter
        if hasattr(self, 'unit_filter_var') and self.unit_filter_var.get() != "All":
            filter_rarity = self.unit_filter_var.get()
            units_with_idx = [(unit, idx) for unit, idx in units_with_idx if unit['entity']['rarity'] == filter_rarity]
            
        # Apply sort
        if hasattr(self, 'unit_sort_var'):
            sort_by = self.unit_sort_var.get()
            if sort_by == "name":
                units_with_idx.sort(key=lambda x: x[0]['entity']['name'])
            elif sort_by == "level":
                units_with_idx.sort(key=lambda x: x[0]['level'], reverse=True)
            elif sort_by == "rarity":
                rarity_order = {"Common": 0, "Rare": 1, "Epic": 2, "Legendary": 3}
                units_with_idx.sort(key=lambda x: rarity_order.get(x[0]['entity']['rarity'], 0), reverse=True)
            elif sort_by == "hp":
                units_with_idx.sort(key=lambda x: x[0]['entity']['hp'], reverse=True)
            elif sort_by == "attack":
                units_with_idx.sort(key=lambda x: x[0]['entity']['attack'], reverse=True)
                
        return units_with_idx
            
    def show_unit_details_inline(self, unit_idx):
        """Show unit details in the same window"""
        if unit_idx >= len(self.player_inventory):
            return
            
        unit = self.player_inventory[unit_idx]
        entity = unit['entity']
        final_stats = self.calculate_unit_stats_with_runes(unit)
        base_stats = self.calculate_unit_level_stats(unit)
        
        # Clear content and show unit details
        self.clear_content()
        
        # Title
        title_label = tk.Label(
            self.content_frame,
            text=f"📋 UNIT DETAILS - {entity['name'].upper()}",
            font=self.title_font,
            bg='black',
            fg=self.rarity_colors[entity['rarity']]
        )
        title_label.pack(pady=20)
        
        # Main details frame
        details_frame = tk.Frame(self.content_frame, bg='black')
        details_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Left column - Stats with new layout
        left_frame = tk.LabelFrame(
            details_frame,
            text="Unit Statistics",
            font=self.header_font,
            bg='black',
            fg='#CCCCCC'
        )
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Basic info
        basic_info = tk.Frame(left_frame, bg='black')
        basic_info.pack(fill='x', padx=10, pady=10)
        
        info_text = f"Level: {unit['level']} | EXP: {unit['exp']} | Rarity: {entity['rarity']}"
        info_label = tk.Label(
            basic_info,
            text=info_text,
            font=self.body_font,
            bg='black',
            fg='white',
            justify='center'
        )
        info_label.pack()
        
        # Stats display with new format: Bonus (green) | Stat Name | Base Value (white)
        stats_frame = tk.Frame(left_frame, bg='black')
        stats_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        stats_title = tk.Label(
            stats_frame,
            text="RUNE BONUSES     |     STAT     |     BASE VALUES",
            font=self.small_font,
            bg='black',
            fg='#CCCCCC'
        )
        stats_title.pack(pady=(0, 10))
        
        # Show stats with new layout
        stats_display = [
            ("❤️  HP", "hp"),
            ("⚔️  Attack", "attack"),
            ("🛡️  Defense", "defense"),
            ("⚡ Speed", "speed"),
            ("💥 Crit Rate", "crit_rate"),
            ("🎯 Crit Damage", "crit_damage"),
            ("📊 Accuracy", "accuracy"),
            ("👻 Evasion", "evasion")
        ]
        
        for stat_name, stat_key in stats_display:
            base_val = base_stats[stat_key]
            final_val = final_stats[stat_key]
            bonus = final_val - base_val if final_val != base_val else 0
            
            stat_row = tk.Frame(stats_frame, bg='black')
            stat_row.pack(fill='x', pady=2)
            
            # Left: Bonus in green (or empty if no bonus)
            bonus_text = f"+{bonus}" if bonus > 0 else ""
            bonus_label = tk.Label(
                stat_row,
                text=bonus_text,
                font=self.body_font,
                bg='black',
                fg='#66FF66',
                width=12,
                anchor='w'
            )
            bonus_label.pack(side='left')
            
            # Center: Stat name
            name_label = tk.Label(
                stat_row,
                text=stat_name,
                font=self.body_font,
                bg='black',
                fg='#FFCC66',
                width=15,
                anchor='center'
            )
            name_label.pack(side='left')
            
            # Right: Base value in white
            base_label = tk.Label(
                stat_row,
                text=str(base_val),
                font=self.body_font,
                bg='black',
                fg='white',
                width=10,
                anchor='e'
            )
            base_label.pack(side='right')
        
        # Equipped runes section with set information
        runes_frame = tk.LabelFrame(
            left_frame,
            text="Equipped Runes",
            font=self.body_font,
            bg='black',
            fg='#FFCC66'
        )
        runes_frame.pack(fill='x', pady=10, padx=10)
        
        equipped_runes = unit.get('runes', {})
        if equipped_runes:
            for slot, rune_id in equipped_runes.items():
                rune = next((r for r in self.player_runes if r["id"] == rune_id), None)
                if rune:
                    slot_names = {1: "⚔️ Weapon", 2: "🛡️ Armor", 3: "💎 Accessory", 4: "✨ Enhance", 5: "✨ Enhance", 6: "✨ Enhance"}
                    rune_text = f"{slot_names.get(slot, f'Slot {slot}')}: {rune['name']} (Lv.{rune['level']})\n"
                    rune_text += f"  Set: {rune.get('set', 'None')} | Main: {rune['main_stat']} +{rune['main_value']}"
                    
                    rune_label = tk.Label(
                        runes_frame,
                        text=rune_text,
                        font=self.small_font,
                        bg='black',
                        fg=self.rarity_colors[rune['rarity']],
                        justify='left'
                    )
                    rune_label.pack(anchor='w', padx=5, pady=2)
                    
            # Show active set bonuses
            active_sets = self.get_active_set_names([r for r in self.player_runes if r['id'] in equipped_runes.values()])
            if active_sets:
                sets_title = tk.Label(
                    runes_frame,
                    text="\n🌟 Active Set Bonuses:",
                    font=self.small_font,
                    bg='black',
                    fg='#66FFCC'
                )
                sets_title.pack(anchor='w', padx=5)
                
                for set_name in active_sets:
                    set_info = self.rune_sets.get(set_name, {})
                    effect_desc = set_info.get('effect', 'Unknown effect')
                    pieces_req = set_info.get('pieces', 2)
                    
                    set_text = f"• {set_name} ({pieces_req}-Set): {effect_desc}"
                    set_label = tk.Label(
                        runes_frame,
                        text=set_text,
                        font=self.small_font,
                        bg='black',
                        fg='#66FFCC',
                        justify='left'
                    )
                    set_label.pack(anchor='w', padx=15, pady=1)
        else:
            no_runes_label = tk.Label(
                runes_frame,
                text="No runes equipped",
                font=self.small_font,
                bg='black',
                fg='#666666'
            )
            no_runes_label.pack(pady=5)
        
        # Right column - Skills and description
        right_frame = tk.LabelFrame(
            details_frame,
            text="Abilities & Description",
            font=self.header_font,
            bg='black',
            fg='#CCCCCC'
        )
        right_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Skill with description
        if entity['skill']:
            skill_frame = tk.LabelFrame(
                right_frame,
                text="Active Skill",
                font=self.body_font,
                bg='black',
                fg='#FFCC66'
            )
            skill_frame.pack(fill='x', pady=10, padx=10)
            
            skill_name = entity['skill'].replace('_', ' ').title()
            skill_cost = self.skill_costs.get(entity['skill'], 30)
            skill_desc = self.skill_descriptions.get(entity['skill'], "No description available.")
            
            skill_text = f"✨ {skill_name}\nLevel: {unit.get('skill_level', 0)}/5\nCost: {skill_cost} SP\n\n{skill_desc}"
            
            skill_label = tk.Label(
                skill_frame,
                text=skill_text,
                font=self.small_font,
                bg='black',
                fg='#FFCC66',
                justify='left',
                wraplength=280
            )
            skill_label.pack(pady=5, padx=10, anchor='w')
            
        # Passive
        if entity['passive'] and entity['passive'] != "None":
            passive_frame = tk.LabelFrame(
                right_frame,
                text="Passive Ability",
                font=self.body_font,
                bg='black',
                fg='#CCFF66'
            )
            passive_frame.pack(fill='x', pady=10, padx=10)
            
            passive_label = tk.Label(
                passive_frame,
                text=entity['passive'],
                font=self.small_font,
                bg='black',
                fg='#CCFF66',
                wraplength=280,
                justify='left'
            )
            passive_label.pack(pady=5, padx=10, anchor='w')
            
        # Description
        desc_frame = tk.LabelFrame(
            right_frame,
            text="Lore",
            font=self.body_font,
            bg='black',
            fg='#CCCCCC'
        )
        desc_frame.pack(fill='x', pady=10, padx=10)
        
        desc_label = tk.Label(
            desc_frame,
            text=entity['description'],
            font=self.small_font,
            bg='black',
            fg='white',
            wraplength=280,
            justify='left'
        )
        desc_label.pack(pady=5, padx=10, anchor='w')
        
        # Unit management buttons at bottom
        buttons_frame = tk.Frame(self.content_frame, bg='black')
        buttons_frame.pack(pady=20)
        
        # Upgrade unit button
        upgrade_btn = tk.Button(
            buttons_frame,
            text="⭐ Upgrade Unit",
            command=lambda: self.show_unit_upgrade_interface(unit_idx),
            font=self.body_font,
            bg='#006600',
            fg='white',
            width=15
        )
        upgrade_btn.pack(side='left', padx=5)
        
        # Test Unit button
        test_btn = tk.Button(
            buttons_frame,
            text="⚔️ Test Unit",
            command=lambda: self.start_unit_test(unit_idx),
            font=self.body_font,
            bg='#CC3300',
            fg='white',
            width=15
        )
        test_btn.pack(side='left', padx=5)
        
        # Manage Runes button
        runes_btn = tk.Button(
            buttons_frame,
            text="🎰 Manage Runes",
            command=lambda: self.show_unit_rune_management(unit_idx),
            font=self.body_font,
            bg='#663399',
            fg='white',
            width=15
        )
        runes_btn.pack(side='left', padx=5)
        
    def manage_rune_slot_inline(self, unit_idx, slot):
        """Manage rune equipment for a specific slot inline"""
        if unit_idx >= len(self.player_inventory):
            return
        unit = self.player_inventory[unit_idx]
        
        # Navigate to rune slot management view
        self.current_rune_slot_unit = unit_idx
        self.current_rune_slot = slot
        
        self.clear_content()
        
        # Title
        title_label = tk.Label(
            self.content_frame,
            text=f"⚡ RUNE SLOT MANAGEMENT ⚡",
            font=self.title_font,
            bg='black',
            fg='#FFCC66'
        )
        title_label.pack(pady=20)
        
        # Unit and slot info
        info_label = tk.Label(
            self.content_frame,
            text=f"Unit: {unit['entity']['name']} | Slot {slot}: {self.get_slot_type_name(slot)}",
            font=self.header_font,
            bg='black',
            fg='white'
        )
        info_label.pack(pady=10)
        
        # Currently equipped rune
        equipped_frame = tk.LabelFrame(
            self.content_frame,
            text="Currently Equipped",
            font=self.header_font,
            bg='black',
            fg='#66FF66'
        )
        equipped_frame.pack(fill='x', padx=50, pady=20)
        
        equipped_rune_id = unit.get('runes', {}).get(slot)
        equipped_rune = None
        if equipped_rune_id:
            equipped_rune = next((r for r in self.player_runes if r["id"] == equipped_rune_id), None)
            
        if equipped_rune:
            # Show equipped rune details
            eq_details_frame = tk.Frame(equipped_frame, bg='black')
            eq_details_frame.pack(padx=20, pady=15)
            
            eq_name_label = tk.Label(
                eq_details_frame,
                text=f"{equipped_rune['name']} (Lv.{equipped_rune['level']})",
                font=self.body_font,
                bg='black',
                fg=self.rarity_colors[equipped_rune['rarity']]
            )
            eq_name_label.pack()
            
            eq_stats_text = f"Type: {equipped_rune['type']} {self.rune_types[equipped_rune['type']]['icon']}\n"
            eq_stats_text += f"Main: {equipped_rune['main_stat']} +{equipped_rune['main_value']}\n"
            eq_stats_text += "Substats: "
            for substat, value in equipped_rune['substats'].items():
                eq_stats_text += f"{substat} +{value}, "
            eq_stats_text = eq_stats_text.rstrip(', ')
            
            eq_stats_label = tk.Label(
                eq_details_frame,
                text=eq_stats_text,
                font=self.small_font,
                bg='black',
                fg='white',
                justify='center'
            )
            eq_stats_label.pack(pady=5)
            
            # Unequip button
            unequip_btn = tk.Button(
                eq_details_frame,
                text="⚠️ Unequip Rune",
                command=self.unequip_current_rune_inline,
                font=self.body_font,
                bg='#CC3300',
                fg='white'
            )
            unequip_btn.pack(pady=10)
        else:
            no_eq_label = tk.Label(
                equipped_frame,
                text="No rune equipped in this slot",
                font=self.body_font,
                bg='black',
                fg='#666666'
            )
            no_eq_label.pack(pady=20)
            
        # Available runes
        available_frame = tk.LabelFrame(
            self.content_frame,
            text="Available Runes",
            font=self.header_font,
            bg='black',
            fg='#CCCCCC'
        )
        available_frame.pack(fill='both', expand=True, padx=50, pady=(10, 50))
        
        # Get compatible runes
        compatible_runes = self.get_compatible_runes(slot)
        
        if not compatible_runes:
            no_runes_label = tk.Label(
                available_frame,
                text="No compatible runes available",
                font=self.body_font,
                bg='black',
                fg='#666666'
            )
            no_runes_label.pack(pady=50)
        else:
            # Scrollable runes list
            canvas = tk.Canvas(available_frame, bg='black', highlightthickness=0)
            scrollbar = ttk.Scrollbar(available_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg='black')
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            scrollbar.pack(side="right", fill="y", pady=10)
            
            # Display compatible runes
            for i, rune in enumerate(compatible_runes):
                row = i // 2
                col = i % 2
                
                rune_frame = tk.LabelFrame(
                    scrollable_frame,
                    text=f"{rune['name']} (Lv.{rune['level']})",
                    font=self.body_font,
                    bg='#1a1a1a',
                    fg=self.rarity_colors[rune['rarity']],
                    bd=2,
                    relief='ridge'
                )
                rune_frame.grid(row=row, column=col, padx=15, pady=10, sticky='nsew')
                
                # Rune details
                details_text = f"Type: {rune['type']} {self.rune_types[rune['type']]['icon']}\n"
                details_text += f"Main: {rune['main_stat']} +{rune['main_value']}\n"
                details_text += "Substats:\n"
                for substat, value in rune['substats'].items():
                    details_text += f"  • {substat}: +{value}\n"
                
                details_label = tk.Label(
                    rune_frame,
                    text=details_text,
                    font=self.small_font,
                    bg='#1a1a1a',
                    fg='white',
                    justify='left'
                )
                details_label.pack(padx=10, pady=5)
                
                # Equip button
                equip_btn = tk.Button(
                    rune_frame,
                    text="✅ Equip Rune",
                    command=lambda r=rune: self.equip_rune_inline(r),
                    font=self.small_font,
                    bg='#006600',
                    fg='white',
                    width=12
                )
                equip_btn.pack(pady=10)
                
            # Configure grid weights
            for col in range(2):
                scrollable_frame.grid_columnconfigure(col, weight=1)
                
    def get_slot_type_name(self, slot):
        """Get the name/type of a rune slot"""
        slot_names = {1: "Weapon", 2: "Armor", 3: "Accessory", 4: "Enhancement", 5: "Enhancement", 6: "Enhancement"}
        return slot_names.get(slot, f"Slot {slot}")
        
    def get_compatible_runes(self, slot):
        """Get runes compatible with the specified slot"""
        compatible_runes = []
        
        for rune in self.player_runes:
            if rune["equipped_unit"] is not None:
                continue
                
            rune_type_info = self.rune_types.get(rune["type"])
            if rune_type_info:
                if isinstance(rune_type_info["slot"], list):
                    if slot in rune_type_info["slot"]:
                        compatible_runes.append(rune)
                else:
                    if slot == rune_type_info["slot"]:
                        compatible_runes.append(rune)
                        
        # Sort by rarity then level
        rarity_order = {"Common": 0, "Rare": 1, "Epic": 2, "Legendary": 3}
        compatible_runes.sort(key=lambda r: (rarity_order.get(r['rarity'], 0), r['level']), reverse=True)
        
        return compatible_runes
        
    def auto_equip_best_runes(self):
        """Auto-equip the best runes for all units based on their mechanics"""
        if not self.player_runes or not self.player_inventory:
            return
            
        # Define optimal stat priorities for each unit type
        unit_priorities = {
            "Jeff the Killer": ["Crit Rate", "Crit Damage", "Attack%", "Speed", "Attack"],
            "SCP-682": ["HP%", "Defense%", "HP", "Defense", "Attack%"],
            "Slender": ["Speed", "Accuracy", "HP%", "Evasion", "Attack%"],
            "Iris": ["Attack%", "Speed", "Accuracy", "Attack", "HP%"],
            "SCP-999": ["HP%", "Speed", "Defense%", "HP", "Defense"],
            "The Rake": ["Attack%", "Crit Rate", "Speed", "Crit Damage", "Attack"],
            "Kuchisake-onna": ["Crit Rate", "Crit Damage", "Attack%", "Speed", "Attack"],
            "Mothman": ["Speed", "Accuracy", "Attack%", "HP%", "Evasion"],
            "Bloody Mary": ["HP%", "Defense%", "Speed", "Attack%", "HP"]
        }
        
        for unit_idx, unit in enumerate(self.player_inventory):
            unit_name = unit['entity']['name']
            priorities = unit_priorities.get(unit_name, ["Attack%", "HP%", "Speed", "Defense%", "Crit Rate"])
            
            # Get available runes for each slot type
            for slot in range(1, 7):
                compatible_runes = self.get_compatible_runes(slot)
                
                if not compatible_runes:
                    continue
                    
                # Score runes based on unit priorities
                best_rune = None
                best_score = 0
                
                for rune in compatible_runes:
                    if rune['equipped_unit'] is not None:
                        continue
                        
                    score = 0
                    
                    # Score main stat
                    main_stat = rune['main_stat']
                    if main_stat in priorities:
                        score += (10 - priorities.index(main_stat)) * 100
                    
                    # Score substats
                    for substat in rune['substats']:
                        if substat in priorities:
                            score += (10 - priorities.index(substat)) * 10
                            
                    # Bonus for higher rarity and level
                    rarity_bonus = {"Common": 1, "Rare": 2, "Epic": 4, "Legendary": 8}
                    score += rarity_bonus[rune['rarity']] * 5
                    score += rune['level'] * 2
                    
                    if score > best_score:
                        best_score = score
                        best_rune = rune
                        
                # Equip the best rune found
                if best_rune:
                    self.equip_rune(unit_idx, slot, best_rune['id'])
        
    def equip_rune_inline(self, rune):
        """Equip a rune in the inline interface"""
        success = self.equip_rune(self.current_rune_slot_unit, self.current_rune_slot, rune["id"])
        if success:
            unit_name = self.player_inventory[self.current_rune_slot_unit]['entity']['name']
            self.show_notification(f"✅ Equipped {rune['name']} to {unit_name} slot {self.current_rune_slot}")
            # Refresh the rune slot management view
            self.manage_rune_slot_inline(self.current_rune_slot_unit, self.current_rune_slot)
        else:
            self.show_notification("❌ Failed to equip rune!", '#FF6666')
            
    def unequip_current_rune_inline(self):
        """Unequip the current rune in the inline interface"""
        success = self.unequip_rune(self.current_rune_slot_unit, self.current_rune_slot)
        if success:
            unit_name = self.player_inventory[self.current_rune_slot_unit]['entity']['name']
            self.show_notification(f"⚠️ Unequipped rune from {unit_name} slot {self.current_rune_slot}")
            # Refresh the rune slot management view
            self.manage_rune_slot_inline(self.current_rune_slot_unit, self.current_rune_slot)
        else:
            self.show_notification("❌ Failed to unequip rune!", '#FF6666')
            
    def show_world_campaign(self):
        """Show the world campaign interface"""
        self.navigate_to("campaign")
        self.clear_content()
        
        # Title
        title_label = tk.Label(
            self.content_frame,
            text="🗺️ WORLD CAMPAIGN 🗺️",
            font=self.title_font,
            bg='black',
            fg='#FF9966'
        )
        title_label.pack(pady=20)
        
        # World selection
        worlds_frame = tk.Frame(self.content_frame, bg='black')
        worlds_frame.pack(pady=20, padx=20, fill='both', expand=True)
        
        for i, world in enumerate(self.worlds):
            # Check if world is unlocked
            unlocked = any(self.player_progress["unlocked"][i])
            
            world_frame = tk.LabelFrame(
                worlds_frame,
                text=f"World {i+1}: {world['name']}" + ("" if unlocked else " [LOCKED]"),
                font=self.header_font,
                bg='#1a1a1a' if unlocked else '#0a0a0a',
                fg='#FFCC66' if unlocked else '#666666',
                bd=2,
                relief='ridge'
            )
            world_frame.pack(fill='x', pady=10)
            
            if unlocked:
                # Stages available
                unlocked_stages = sum(self.player_progress["unlocked"][i])
                progress_text = f"Stages Unlocked: {unlocked_stages}/{self.STAGES_PER_WORLD}"
                
                progress_label = tk.Label(
                    world_frame,
                    text=progress_text,
                    font=self.body_font,
                    bg='#1a1a1a',
                    fg='white'
                )
                progress_label.pack(pady=5)
                
                # Enter world button
                enter_btn = tk.Button(
                    world_frame,
                    text="🚪 Enter World",
                    command=lambda w=i: self.enter_world(w),
                    font=self.body_font,
                    bg='#006600',
                    fg='white'
                )
                enter_btn.pack(pady=10)
            else:
                locked_label = tk.Label(
                    world_frame,
                    text="Complete previous world to unlock",
                    font=self.body_font,
                    bg='#0a0a0a',
                    fg='#666666'
                )
                locked_label.pack(pady=10)
                
    def enter_world(self, world_idx):
        """Enter a specific world and show stage selection"""
        self.navigate_to(f"world_{world_idx}")
        self.clear_content()
        
        # Title
        title_label = tk.Label(
            self.content_frame,
            text=f"🗺️ {self.worlds[world_idx]['name'].upper()} 🗺️",
            font=self.title_font,
            bg='black',
            fg='#FF9966'
        )
        title_label.pack(pady=20)
        
        # Stages grid
        stages_frame = tk.Frame(self.content_frame, bg='black')
        stages_frame.pack(pady=20, padx=20, fill='both', expand=True)
        
        for stage in range(self.STAGES_PER_WORLD):
            row = stage // 5
            col = stage % 5
            
            unlocked = self.player_progress["unlocked"][world_idx][stage]
            is_boss = (stage + 1) % 10 == 0
            
            if unlocked:
                stage_btn = tk.Button(
                    stages_frame,
                    text=f"Stage {stage+1}" + (" 👑" if is_boss else ""),
                    command=lambda w=world_idx, s=stage: self.start_stage_battle(w, s),
                    font=self.body_font,
                    bg='#006600',
                    fg='white',
                    width=12,
                    height=2
                )
            else:
                stage_btn = tk.Button(
                    stages_frame,
                    text=f"Stage {stage+1}" + (" 👑" if is_boss else ""),
                    command=None,
                    font=self.body_font,
                    bg='#333333',
                    fg='#666666',
                    state='disabled',
                    width=12,
                    height=2
                )
            stage_btn.grid(row=row, column=col, padx=5, pady=5)
            
        # Configure grid
        for col in range(5):
            stages_frame.grid_columnconfigure(col, weight=1)
            
    def start_stage_battle(self, world_idx, stage_idx):
        """Start a battle for the specified stage"""
        # Generate enemies first to show preview
        enemies = self.generate_enemies(world_idx, stage_idx)
        
        # Show enemy preview then team selection
        self.show_enemy_preview(world_idx, stage_idx, enemies)
        
    def show_team_selection_inline(self, callback):
        """Show team selection in the same window"""
        self.clear_content()
        
        # Title
        title_label = tk.Label(
            self.content_frame,
            text="⚔️ SELECT YOUR TEAM ⚔️",
            font=self.title_font,
            bg='black',
            fg='#FF6666'
        )
        title_label.pack(pady=20)
        
        # Instructions
        inst_label = tk.Label(
            self.content_frame,
            text="Select up to 4 units for battle (click to select/deselect):",
            font=self.body_font,
            bg='black',
            fg='white'
        )
        inst_label.pack(pady=10)
        
        # Selected team display
        selected_frame = tk.LabelFrame(
            self.content_frame,
            text="Selected Team",
            font=self.header_font,
            bg='black',
            fg='#66FF66'
        )
        selected_frame.pack(fill='x', pady=20, padx=20)
        
        self.selected_display_frame = tk.Frame(selected_frame, bg='black')
        self.selected_display_frame.pack(fill='x', padx=10, pady=10)
        
        # Pre-select last used team if available
        if self.last_team_used:
            # Find matching units in current inventory
            self.selected_units = []
            for last_unit in self.last_team_used:
                # Match by entity name and level to find the same unit
                for current_unit in self.player_inventory:
                    if (current_unit['entity']['name'] == last_unit['entity']['name'] and 
                        current_unit['level'] == last_unit['level']):
                        self.selected_units.append(current_unit)
                        break
            # Limit to 4 units max
            self.selected_units = self.selected_units[:4]
        else:
            self.selected_units = []  # Reset selection if no last team
        
        # Available units
        units_frame = tk.LabelFrame(
            self.content_frame,
            text="Available Units",
            font=self.header_font,
            bg='black',
            fg='#CCCCCC'
        )
        units_frame.pack(fill='both', expand=True, pady=20, padx=20)
        
        # Scrollable units display
        canvas = tk.Canvas(units_frame, bg='black', highlightthickness=0)
        scrollbar = ttk.Scrollbar(units_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='black')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Display available units as colored name boxes
        for i, unit in enumerate(self.player_inventory):
            row = i // 6
            col = i % 6
            
            unit_btn = tk.Button(
                scrollable_frame,
                text=unit['entity']['name'],
                command=lambda idx=i: self.toggle_unit_selection(idx),
                font=self.body_font,
                bg=self.rarity_colors[unit['entity']['rarity']],
                fg='black' if unit['entity']['rarity'] in ['Common', 'Rare'] else 'white',
                width=15,
                height=2,
                relief='raised',
                bd=3
            )
            unit_btn.grid(row=row, column=col, padx=5, pady=5)
            
            # Bind hover for stats preview
            unit_btn.bind("<Enter>", lambda e, u=unit: self.show_unit_hover_stats(e, u))
            unit_btn.bind("<Leave>", self.hide_unit_hover_stats)
            
        # Configure grid
        for col in range(6):
            scrollable_frame.grid_columnconfigure(col, weight=1)
            
        # Bottom buttons
        btn_frame = tk.Frame(self.content_frame, bg='black')
        btn_frame.pack(pady=20)
        
        self.confirm_btn = tk.Button(
            btn_frame,
            text="⚔️ Confirm Team",
            command=lambda: callback(self.selected_units[:]) if self.selected_units else None,
            font=self.body_font,
            bg='#006600',
            fg='white',
            state='disabled'
        )
        self.confirm_btn.pack(side='left', padx=10)
        
        # Update selected display initially
        self.update_selected_display()
        
    def toggle_unit_selection(self, unit_idx):
        """Toggle unit selection"""
        unit = self.player_inventory[unit_idx]
        
        if unit in self.selected_units:
            self.selected_units.remove(unit)
        elif len(self.selected_units) < 4:
            self.selected_units.append(unit)
        else:
            self.show_notification("❌ Maximum 4 units can be selected for battle!")
            return
            
        self.update_selected_display()
        
    def update_selected_display(self):
        """Update the selected team display"""
        # Clear existing display
        for widget in self.selected_display_frame.winfo_children():
            widget.destroy()
            
        if not self.selected_units:
            empty_label = tk.Label(
                self.selected_display_frame,
                text="No units selected",
                font=self.body_font,
                bg='black',
                fg='#666666'
            )
            empty_label.pack()
            self.confirm_btn.config(state='disabled')
        else:
            for i, unit in enumerate(self.selected_units):
                unit_label = tk.Label(
                    self.selected_display_frame,
                    text=f"{i+1}. {unit['entity']['name']} (Lv.{unit['level']})",
                    font=self.body_font,
                    bg='black',
                    fg=self.rarity_colors[unit['entity']['rarity']]
                )
                unit_label.pack(side='left', padx=10)
                
            self.confirm_btn.config(state='normal')
            
    def show_unit_hover_stats(self, event, unit):
        """Show unit stats on hover with GUI tooltip instead of console"""
        # Calculate final stats with runes
        final_stats = self.calculate_unit_stats_with_runes(unit)
        base_stats = self.calculate_unit_level_stats(unit)
        
        # Create tooltip window
        tooltip = tk.Toplevel(self.root)
        tooltip.wm_overrideredirect(True)
        tooltip.configure(bg='#1a1a1a')
        
        # Position tooltip near mouse
        x = event.widget.winfo_rootx() + 20
        y = event.widget.winfo_rooty() + 20
        tooltip.geometry(f"+{x}+{y}")
        
        # Tooltip content
        tooltip_frame = tk.Frame(tooltip, bg='#1a1a1a', relief='solid', bd=1)
        tooltip_frame.pack(padx=5, pady=5)
        
        # Unit name and level
        name_label = tk.Label(
            tooltip_frame,
            text=f"{unit['entity']['name']} (Lv.{unit['level']})",
            font=('Consolas', 10, 'bold'),
            bg='#1a1a1a',
            fg=self.rarity_colors[unit['entity']['rarity']]
        )
        name_label.pack()
        
        # Stats comparison
        stat_comparisons = [
            ("❤️ HP", base_stats['hp'], final_stats['hp']),
            ("⚔️ ATK", base_stats['attack'], final_stats['attack']),
            ("🛡️ DEF", base_stats['defense'], final_stats['defense']),
            ("⚡ SPD", base_stats['speed'], final_stats['speed'])
        ]
        
        for stat_name, base_val, final_val in stat_comparisons:
            stat_frame = tk.Frame(tooltip_frame, bg='#1a1a1a')
            stat_frame.pack(fill='x', padx=5, pady=1)
            
            if base_val != final_val:
                bonus = final_val - base_val
                stat_text = f"{stat_name}: {base_val} (+{bonus}) = {final_val}"
                color = '#66FF66'
            else:
                stat_text = f"{stat_name}: {base_val}"
                color = 'white'
            
            stat_label = tk.Label(
                stat_frame,
                text=stat_text,
                font=('Consolas', 8),
                bg='#1a1a1a',
                fg=color,
                justify='left'
            )
            stat_label.pack(anchor='w')
        
        # Auto-destroy tooltip after 3 seconds or when mouse moves
        tooltip.after(3000, tooltip.destroy)
        event.widget.tooltip = tooltip  # Store reference for cleanup
        
    def hide_unit_hover_stats(self, event):
        """Hide unit stats hover tooltip"""
        if hasattr(event.widget, 'tooltip'):
            try:
                event.widget.tooltip.destroy()
                delattr(event.widget, 'tooltip')
            except:
                pass  # Tooltip already destroyed
        
    def launch_battle(self, world_idx, stage_idx, team):
        """Launch the battle system with selected team and multi-wave support"""
        if not team:
            self.show_notification("❌ No team selected for battle!")
            return
            
        self.show_notification(f"⚔️ Starting battle at World {world_idx+1}, Stage {stage_idx+1}...")
        
        # Determine number of waves based on stage type
        is_boss_stage = (stage_idx + 1) % 10 == 0  # Every 10th stage is a boss
        if is_boss_stage:
            total_waves = 5  # Boss stages have 5 waves
            self.show_notification(f"👑 Boss Stage Detected! Prepare for {total_waves} waves of enemies!")
        else:
            total_waves = 3  # Story stages have 3 waves
            self.show_notification(f"📖 Story Stage: Face {total_waves} waves of enemies!")
        
        # Initialize battle state with multi-wave support and user preferences
        self.battle_state = {
            "type": "campaign",
            "world_idx": world_idx,
            "stage_idx": stage_idx,
            "team": team.copy(),
            "enemies": self.generate_enemies(world_idx, stage_idx, wave=1),
            "current_turn": 0,
            "turn_order": [],
            "auto_battle": self.auto_battle_preference,  # Use saved preference
            "current_wave": 1,
            "total_waves": total_waves,
            "is_boss_stage": is_boss_stage
        }
        
        # Remember this team for next battles
        self.last_team_used = team.copy()
        
        # Initialize units with proper stat calculations
        for unit in self.battle_state["team"]:
            final_stats = self.calculate_unit_stats_with_runes(unit)
            unit["battle_stats"] = final_stats.copy()  # Store calculated stats for battle use
            unit["battle_hp"] = final_stats["hp"]  # Use final calculated HP
            unit["max_hp"] = final_stats["hp"]     # Store max HP from final stats
            unit["max_sp"] = final_stats["sp_cap"]
            unit["sp"] = int(final_stats["sp_cap"] * 0.7)  # Start with 70% SP
            unit["effects"] = []
            unit["defending"] = False
            # Jeff starts with 1 ghost stack (Go to Sleep passive)
            if unit["entity"]["name"] == "Jeff the Killer":
                unit["effects"].append({"type": "ghost", "turns": 99, "stacks": 1, "source": "Go to Sleep"})
                
        for enemy in self.battle_state["enemies"]:
            enemy["effects"] = []
            
        # Show battle interface
        self.show_battle_interface()
        
        # Apply auto battle preference if set
        if self.auto_battle_preference and hasattr(self, 'auto_btn'):
            # Small delay to ensure interface is ready, then enable auto battle
            self.root.after(500, self.apply_saved_auto_preference)
        
    def generate_enemies(self, world_idx, stage_idx, wave=1):
        """Generate enemies for a stage with enhanced difficulty scaling and progression gating"""
        is_boss_stage = (stage_idx + 1) % 10 == 0
        
        # Enhanced difficulty scaling - more aggressive progression
        world_difficulty = 1.0 + (world_idx * 0.5)  # Increased from 0.3
        stage_difficulty = 1.0 + (stage_idx * 0.15)  # Increased from 0.1
        wave_difficulty = 1.0 + ((wave - 1) * 0.25)  # Increased from 0.2
        
        # Progressive enemy rarity scaling based on world progression
        if world_idx == 0:  # World 1: Mostly Common/Rare
            story_rarities = [["Common"], ["Common", "Rare"], ["Rare"]]
            boss_rarities = [["Common", "Rare"], ["Rare"], ["Rare", "Epic"]]
        elif world_idx == 1:  # World 2: Rare/Epic introduction
            story_rarities = [["Common", "Rare"], ["Rare"], ["Rare", "Epic"]]
            boss_rarities = [["Rare"], ["Rare", "Epic"], ["Epic"]]
        elif world_idx == 2:  # World 3: Epic becomes common
            story_rarities = [["Rare"], ["Rare", "Epic"], ["Epic"]]
            boss_rarities = [["Rare", "Epic"], ["Epic"], ["Epic", "Legendary"]]
        elif world_idx == 3:  # World 4: Epic/Legendary
            story_rarities = [["Rare", "Epic"], ["Epic"], ["Epic", "Legendary"]]
            boss_rarities = [["Epic"], ["Epic", "Legendary"], ["Legendary"]]
        else:  # World 5+: End game content
            story_rarities = [["Epic"], ["Epic", "Legendary"], ["Legendary"]]
            boss_rarities = [["Epic", "Legendary"], ["Legendary"], ["Legendary"]]
        
        if is_boss_stage:
            # Boss stage enemy generation with enhanced scaling
            if wave < 5:
                num_enemies = min(3 + wave, 7)  # 4-8 enemies
                if wave <= 2:
                    enemy_rarities = boss_rarities[0]
                elif wave <= 4:
                    enemy_rarities = boss_rarities[1] 
                else:
                    enemy_rarities = boss_rarities[2]
            else:
                # Wave 5: The actual boss + elite minions
                num_enemies = random.randint(2, 4)  # Boss + 1-3 minions
                enemy_rarities = ["Epic", "Legendary"]
        else:
            # Story stage enemy generation with progression scaling
            if wave == 1:
                num_enemies = random.randint(3, 5)  # Slightly more enemies
                enemy_rarities = story_rarities[0]
            elif wave == 2:
                num_enemies = random.randint(4, 6)  # More challenging
                enemy_rarities = story_rarities[1]
            else:  # wave == 3
                num_enemies = random.randint(5, 7)  # Significantly more enemies
                enemy_rarities = story_rarities[2]
        
        enemies = []
        
        for _ in range(num_enemies):
            # Get base entity from appropriate rarity pool
            available_entities = [e for e in self.entities if e["rarity"] in enemy_rarities]
            if not available_entities:  # Fallback to common if no matches
                available_entities = [e for e in self.entities if e["rarity"] == "Common"]
            base_entity = random.choice(available_entities)
            
            # Enhanced scaling calculation
            total_scale = world_difficulty * stage_difficulty * wave_difficulty
            
            # Additional scaling for boss stages (increased from 1.5 to 2.0)
            if is_boss_stage:
                total_scale *= 2.0
            
            # Late world scaling becomes more aggressive
            if world_idx >= 3:
                total_scale *= 1.3  # 30% bonus for worlds 4-5
            if world_idx >= 4:
                total_scale *= 1.2  # Additional 20% for world 5
            
            enemy = {
                "name": f"{base_entity['name']} [W{world_idx+1}-{stage_idx+1}]",
                "rarity": base_entity["rarity"],
                "hp": int(base_entity["hp"] * total_scale),
                "max_hp": int(base_entity["hp"] * total_scale),
                "attack": int(base_entity["attack"] * total_scale),
                "defense": int(base_entity["defense"] * total_scale),
                "speed": int(base_entity["speed"] * min(total_scale, 2.0)),  # Cap speed scaling
                "skill": base_entity["skill"],
                "crit_rate": min(base_entity["crit_rate"] + (world_idx * 3) + (wave * 2), 30),
                "crit_damage": base_entity["crit_damage"] + (world_idx * 10) + (wave * 5),
                "accuracy": min(base_entity["accuracy"] + (world_idx * 5) + (wave * 3), 95),
                "evasion": min(base_entity["evasion"] + (world_idx * 2) + wave, 25),
                "sp": min(80 + (world_idx * 10) + (wave * 10), 150),
                "effects": []
            }
            
            # Enhanced boss generation for final wave
            if is_boss_stage and wave == 5 and len(enemies) == 0:
                boss_names = [
                    "Nightmare Sovereign", "Terror Lord", "Dread King", "Horror Master", 
                    "Void Emperor", "Abyssal Tyrant", "Shadow Overlord", "Crimson Despot"
                ]
                enemy["name"] = f"{random.choice(boss_names)} [W{world_idx+1} BOSS]"
                enemy["rarity"] = "Legendary"
                # More dramatic boss scaling
                enemy["hp"] = int(enemy["hp"] * 3.0)  # 3x HP instead of 2.5x
                enemy["max_hp"] = int(enemy["max_hp"] * 3.0)
                enemy["attack"] = int(enemy["attack"] * 2.0)  # 2x attack instead of 1.8x
                enemy["defense"] = int(enemy["defense"] * 1.8)  # 1.8x defense instead of 1.5x
                enemy["skill"] = "boss_ultimate"
                enemy["sp"] = 150
                enemy["crit_rate"] = min(enemy["crit_rate"] + 10, 35)  # Boss crit bonus
                enemy["crit_damage"] = enemy["crit_damage"] + 25  # Boss crit damage bonus
            
            enemies.append(enemy)
            
        return enemies
        
    def show_battle_interface(self):
        """Show the optimized battle interface with enhanced UX"""
        self.current_screen = "battle"
        self.clear_content()
        
        # Compact header with battle info and controls
        header_frame = tk.Frame(self.content_frame, bg='black')
        header_frame.pack(fill='x', pady=5, padx=10)
        
        # Battle title (compact)
        if self.battle_state.get("type") == "delve":
            title_text = f"🕳️ Delve Floor {self.battle_state['floor']}"
        elif self.battle_state.get("type") == "rune_boss":
            title_text = f"🎰 {self.battle_state['boss_data']['name']}"
        elif self.battle_state.get("type") == "xp_trainer":
            title_text = f"⭐ {self.battle_state['trainer_data']['name']}"
        else:
            title_text = f"⚔️ World {self.battle_state['world_idx']+1}-{self.battle_state['stage_idx']+1}"
            
        title_label = tk.Label(
            header_frame,
            text=title_text,
            font=self.header_font,
            bg='black',
            fg='#FF6666'
        )
        title_label.pack(side='left')
        
        # Battle controls (compact, right side)
        controls_frame = tk.Frame(header_frame, bg='black')
        controls_frame.pack(side='right')
        
        self.auto_btn = tk.Button(
            controls_frame,
            text="🤖 Auto",
            command=self.toggle_auto_battle,
            font=self.small_font,
            bg='#006600',
            fg='white',
            width=8,
            height=1
        )
        self.auto_btn.pack(side='left', padx=2)
        
        retreat_btn = tk.Button(
            controls_frame,
            text="🚪 Retreat",
            command=self.retreat_battle,
            font=self.small_font,
            bg='#CC6600',
            fg='white',
            width=8,
            height=1
        )
        retreat_btn.pack(side='left', padx=2)
        
        # Battle Speed Control
        speed_btn = tk.Button(
            controls_frame,
            text="⚡ x1",
            command=self.cycle_battle_speed,
            font=self.small_font,
            bg='#666666',
            fg='white',
            width=6,
            height=1
        )
        speed_btn.pack(side='left', padx=2)
        self.speed_btn = speed_btn
        
        # Main battle area with optimized layout
        battle_area = tk.Frame(self.content_frame, bg='black')
        battle_area.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Left side: Team and Enemies (stacked vertically for better space usage)
        units_frame = tk.Frame(battle_area, bg='black')
        units_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Team display (enhanced)
        team_frame = tk.LabelFrame(
            units_frame,
            text="🛡️ Your Team",
            font=self.body_font,
            bg='black',
            fg='#66FF66',
            labelanchor='nw'
        )
        team_frame.pack(fill='x', pady=(0, 5))
        
        self.team_display = tk.Frame(team_frame, bg='black')
        self.team_display.pack(fill='x', padx=5, pady=5)
        
        # Enemies display (enhanced)
        enemies_frame = tk.LabelFrame(
            units_frame,
            text="👹 Enemies",
            font=self.body_font,
            bg='black',
            fg='#FF6666',
            labelanchor='nw'
        )
        enemies_frame.pack(fill='x', pady=(5, 0))
        
        self.enemies_display = tk.Frame(enemies_frame, bg='black')
        self.enemies_display.pack(fill='x', padx=5, pady=5)
        
        # Right side: Turn order, battle log, and actions (stacked vertically)
        info_frame = tk.Frame(battle_area, bg='black', width=350)
        info_frame.pack(side='right', fill='y')
        info_frame.pack_propagate(False)
        
        # Turn order (compact but informative)
        turn_frame = tk.LabelFrame(
            info_frame,
            text="⚡ Turn Order",
            font=self.body_font,
            bg='black',
            fg='#66CCFF',
            labelanchor='nw'
        )
        turn_frame.pack(fill='x', pady=(0, 5))
        
        self.turn_display = tk.Text(
            turn_frame,
            bg='#0a0a0a',
            fg='white',
            font=self.small_font,
            height=6,
            state='disabled',
            wrap=tk.WORD,
            relief='flat',
            borderwidth=0
        )
        self.turn_display.pack(fill='x', padx=5, pady=3)
        
        # Battle log (compact)
        log_frame = tk.LabelFrame(
            info_frame,
            text="📜 Battle Log",
            font=self.body_font,
            bg='black',
            fg='#FF9966',
            labelanchor='nw'
        )
        log_frame.pack(fill='both', expand=True, pady=5)
        
        log_container = tk.Frame(log_frame, bg='black')
        log_container.pack(fill='both', expand=True, padx=5, pady=3)
        
        self.battle_log_display = tk.Text(
            log_container,
            bg='#0a0a0a',
            fg='white',
            font=self.small_font,
            state='disabled',
            wrap=tk.WORD,
            relief='flat',
            borderwidth=0
        )
        self.battle_log_display.pack(side='left', fill='both', expand=True)
        
        log_scrollbar = ttk.Scrollbar(log_container, orient="vertical", command=self.battle_log_display.yview)
        log_scrollbar.pack(side='right', fill='y')
        self.battle_log_display.configure(yscrollcommand=log_scrollbar.set)
        
        # Action buttons frame (enhanced)
        self.actions_frame = tk.LabelFrame(
            info_frame,
            text="⚔️ Actions",
            font=self.body_font,
            bg='black',
            fg='#FFFF66',
            labelanchor='nw'
        )
        self.actions_frame.pack(fill='x', pady=(5, 0))
        
        # Initialize battle speed from preferences
        self.battle_speed_index = self.battle_speed_preference
        self.battle_speed = self.battle_speeds[self.battle_speed_index]
        
        # Update speed button display
        speed_text = f"⚡ x{self.battle_speed}"
        if self.battle_speed < 1:
            speed_text = f"🐌 x{self.battle_speed}"
        elif self.battle_speed > 2:
            speed_text = f"💨 x{int(self.battle_speed)}"
        self.speed_btn.config(text=speed_text)
        
    def apply_saved_auto_preference(self):
        """Apply saved auto battle preference when battle starts"""
        if self.auto_battle_preference and hasattr(self, 'auto_btn'):
            # Enable auto battle if preference is set
            self.battle_state["auto_battle"] = True
            self.auto_btn.config(text="🖐️ Manual", bg='#CC6600')
            self.add_battle_log("🤖 Auto battle enabled from saved preference")
        
        # Initialize turn counter
        self.turn_counter = 1
        
        # Initialize battle
        self.update_battle_display()
        self.start_battle_turn()
        
    def update_battle_display(self):
        """Update the battle display with enhanced status tracking"""
        # Clear existing displays
        for widget in self.team_display.winfo_children():
            widget.destroy()
        for widget in self.enemies_display.winfo_children():
            widget.destroy()
            
        # Update team display with enhanced information
        alive_team = [unit for unit in self.battle_state["team"] if unit["battle_hp"] > 0]
        for i, unit in enumerate(alive_team):
            unit_frame = tk.Frame(self.team_display, bg='#1a1a1a', relief='solid', bd=1)
            unit_frame.pack(side='left', padx=3, pady=2, fill='both', expand=True)
            
            # Check if this unit's turn
            is_current_turn = (self.battle_state.get("turn_order") and 
                              self.battle_state["turn_order"] and
                              self.battle_state["turn_order"][0].get("type") == "player" and
                              self.battle_state["turn_order"][0].get("unit") == unit)
            
            if is_current_turn:
                unit_frame.config(bg='#2a3a2a', relief='solid', bd=2)
            
            # Unit name with level indicator
            name_text = unit["entity"]["name"]
            if len(name_text) > 12:
                name_text = name_text[:12] + "..."
                
            name_label = tk.Label(
                unit_frame,
                text=f"📗 {name_text}",
                font=self.small_font,
                bg=unit_frame['bg'],
                fg=self.rarity_colors[unit["entity"]["rarity"]]
            )
            name_label.pack(pady=1)
            
            # HP bar with percentage using correct battle stats
            # Use battle_stats if available, otherwise calculate on the fly
            if "battle_stats" in unit:
                max_hp = unit["battle_stats"]["hp"]
            else:
                final_stats = self.calculate_unit_stats_with_runes(unit)
                max_hp = final_stats["hp"]
                
            hp_percent = unit["battle_hp"] / max_hp if max_hp > 0 else 0
            hp_color = '#66FF66' if hp_percent > 0.6 else '#FFFF66' if hp_percent > 0.3 else '#FF6666'
            
            # Compact HP display using correct max HP
            hp_text = f"❤️ {unit['battle_hp']}/{max_hp} ({hp_percent*100:.0f}%)"
            if max_hp >= 10000:  # Handle large numbers
                hp_text = f"❤️ {unit['battle_hp']//1000}k/{max_hp//1000}k ({hp_percent*100:.0f}%)"
                
            hp_label = tk.Label(
                unit_frame,
                text=hp_text,
                font=('Consolas', 7),
                bg=unit_frame['bg'],
                fg=hp_color
            )
            hp_label.pack()
            
            # SP with skill availability indicator
            sp_color = '#66CCFF'
            sp_text = f"⚡ {unit['sp']}/150"
            
            # Check if skill is available
            if unit["entity"]["skill"]:
                skill_cost = self.skill_costs.get(unit["entity"]["skill"], 50)
                if unit["sp"] >= skill_cost:
                    sp_text = f"✨ {unit['sp']}/150"  # Skill ready indicator
                    sp_color = '#FFFF66'
            
            sp_label = tk.Label(
                unit_frame,
                text=sp_text,
                font=('Consolas', 7),
                bg=unit_frame['bg'],
                fg=sp_color
            )
            sp_label.pack()
            
            # Status effects (enhanced display)
            if unit.get("effects"):
                effects_info = self.get_effects_summary(unit["effects"])
                if effects_info:
                    effects_label = tk.Label(
                        unit_frame,
                        text=effects_info,
                        font=('Consolas', 7),
                        bg=unit_frame['bg'],
                        fg='#FFCC66',
                        wraplength=100
                    )
                    effects_label.pack(pady=1)
                    
            # Defending indicator
            if unit.get("defending"):
                defend_label = tk.Label(
                    unit_frame,
                    text="🛡️ DEF",
                    font=('Consolas', 7),
                    bg=unit_frame['bg'],
                    fg='#66CC66'
                )
                defend_label.pack()
                
        # Update enemies display with enhanced information
        alive_enemies = [enemy for enemy in self.battle_state["enemies"] if enemy["hp"] > 0]
        for i, enemy in enumerate(alive_enemies):
            enemy_frame = tk.Frame(self.enemies_display, bg='#2a1a1a', relief='solid', bd=1)
            enemy_frame.pack(side='left', padx=3, pady=2, fill='both', expand=True)
            
            # Check if this enemy's turn
            is_current_turn = (self.battle_state.get("turn_order") and 
                              self.battle_state["turn_order"] and
                              self.battle_state["turn_order"][0].get("type") == "enemy" and
                              self.battle_state["turn_order"][0].get("unit") == enemy)
            
            if is_current_turn:
                enemy_frame.config(bg='#3a2a2a', relief='solid', bd=2)
            
            # Enemy name with index
            name_text = enemy['name']
            if len(name_text) > 12:
                name_text = name_text[:12] + "..."
                
            name_label = tk.Label(
                enemy_frame,
                text=f"📕 {i+1}. {name_text}",
                font=self.small_font,
                bg=enemy_frame['bg'],
                fg=self.rarity_colors.get(enemy.get("rarity", "Common"), '#FFFFFF')
            )
            name_label.pack(pady=1)
            
            # HP with percentage
            max_hp = enemy.get("max_hp", enemy["hp"])
            hp_percent = enemy["hp"] / max_hp if max_hp > 0 else 0
            hp_color = '#66FF66' if hp_percent > 0.6 else '#FFFF66' if hp_percent > 0.3 else '#FF6666'
            
            hp_text = f"💀 {enemy['hp']}/{max_hp} ({hp_percent*100:.0f}%)"
            if enemy["hp"] >= 10000:  # Handle large numbers
                hp_text = f"💀 {enemy['hp']//1000}k/{max_hp//1000}k ({hp_percent*100:.0f}%)"
                
            hp_label = tk.Label(
                enemy_frame,
                text=hp_text,
                font=('Consolas', 7),
                bg=enemy_frame['bg'],
                fg=hp_color
            )
            hp_label.pack()
            
            # Status effects (enhanced display)
            if enemy.get("effects"):
                effects_info = self.get_effects_summary(enemy["effects"])
                if effects_info:
                    effects_label = tk.Label(
                        enemy_frame,
                        text=effects_info,
                        font=('Consolas', 7),
                        bg=enemy_frame['bg'],
                        fg='#FFCC66',
                        wraplength=100
                    )
                    effects_label.pack(pady=1)
        
        # Update turn order display immediately
        self.update_turn_display()
                
    def get_effect_icon(self, effect):
        """Get icon for status effect"""
        icons = {
            "bleed": "🩸",
            "burn": "🔥",
            "poison": "☠️",
            "stun": "⚡",
            "ghost": "👻",
            "taunt": "🎯",
            "shield": "🛡️",
            "buff": "⬆️",
            "debuff": "⬇️",
            "eight_pages": "📄",
            "fear": "😰",
            "slow": "🐌",
            "joyful_regen": "💚",
            "heal_boost": "✨",
            "mirror_curse": "🪞"
        }
        
        icon = icons.get(effect.get("type"), "●")
        stacks = effect.get("stacks", 1)
        turns = effect.get("turns", 0)
        
        if stacks > 1:
            return f"{icon}{stacks}"
        elif turns > 0 and effect.get("type") not in ["ghost", "eight_pages"]:
            return f"{icon}({turns})"
        else:
            return icon
    
    def get_effects_summary(self, effects):
        """Get a compact summary of all effects with proper stacking display"""
        if not effects:
            return ""
            
        # Group effects by type and source for proper counting
        effect_groups = {}
        for effect in effects:
            effect_type = effect.get("type", "unknown")
            effect_source = effect.get("source", "unknown")
            stacks = effect.get("stacks", 1)
            turns = effect.get("turns", 0)
            
            # For effects that should stack from different sources
            if effect_type in ["joyful_regen", "scp_regen", "bleed", "burn", "poison"]:
                key = f"{effect_type}_{effect_source}"
            else:
                # For effects that don't stack (just refresh duration)
                key = effect_type
            
            if key not in effect_groups:
                effect_groups[key] = {"type": effect_type, "stacks": 0, "turns": 0, "count": 0, "sources": []}
                
            effect_groups[key]["stacks"] = max(effect_groups[key]["stacks"], stacks)
            effect_groups[key]["turns"] = max(effect_groups[key]["turns"], turns)
            effect_groups[key]["count"] += 1
            if effect_source not in effect_groups[key]["sources"]:
                effect_groups[key]["sources"].append(effect_source)
        
        # Create compact display
        icons = {
            "bleed": "🩸", "burn": "🔥", "poison": "☠️", "stun": "⚡", "ghost": "👻",
            "taunt": "🎯", "shield": "🛡️", "buff": "⬆️", "debuff": "⬇️", "eight_pages": "📄",
            "fear": "😰", "slow": "🐌", "joyful_regen": "💚", "scp_regen": "🦎", 
            "heal_boost": "✨", "mirror_curse": "🪞"
        }
        
        effect_strings = []
        for key, data in effect_groups.items():
            effect_type = data["type"]
            icon = icons.get(effect_type, "●")
            
            # For stacking effects, show count of sources
            if effect_type in ["joyful_regen", "scp_regen", "bleed", "burn", "poison"] and len(data["sources"]) > 1:
                effect_strings.append(f"{icon}x{len(data['sources'])}")
            elif data["stacks"] > 1:
                effect_strings.append(f"{icon}{data['stacks']}")
            elif data["turns"] > 0 and effect_type not in ["ghost", "eight_pages"]:
                effect_strings.append(f"{icon}({data['turns']})")
            else:
                effect_strings.append(icon)
        
        return " ".join(effect_strings)
        
    def start_battle_turn(self):
        """Start the battle turn system"""
        if not self.check_battle_end():
            self.process_next_turn()
            
    def check_battle_end(self):
        """Check if battle has ended"""
        team_alive = any(unit["battle_hp"] > 0 for unit in self.battle_state["team"])
        enemies_alive = any(enemy["hp"] > 0 for enemy in self.battle_state["enemies"])
        
        if not team_alive:
            self.add_battle_log("💀 Your team has been defeated!")
            # Delay before showing defeat screen
            self.root.after(2000, self.battle_defeat)
            return True
        elif not enemies_alive:
            # Check if there are more waves to fight
            if hasattr(self.battle_state, 'current_wave') and hasattr(self.battle_state, 'total_waves'):
                if self.battle_state['current_wave'] < self.battle_state['total_waves']:
                    self.add_battle_log(f"🎉 Wave {self.battle_state['current_wave']} cleared! Preparing next wave...")
                    self.root.after(3000, self.start_next_wave)
                    return True
            
            self.add_battle_log("🎉 All enemies defeated! Victory!")
            # Delay before showing victory screen
            self.root.after(2000, self.battle_victory)
            return True
            
        return False
        
    def process_next_turn(self):
        """Process the next turn in battle"""
        # Create turn order if empty
        if not self.battle_state.get("turn_order"):
            self.create_turn_order()
            
        if not self.battle_state["turn_order"]:
            self.create_turn_order()
            return
            
        # Get current unit
        current = self.battle_state["turn_order"][0]
        self.battle_state["turn_order"].pop(0)
        
        # Check if unit is still alive
        if current["type"] == "player":
            unit = current["unit"]
            if unit["battle_hp"] <= 0:
                self.process_next_turn()
                return
        else:
            enemy = current["unit"]
            if enemy["hp"] <= 0:
                self.process_next_turn()
                return
                
        # Process turn
        if current["type"] == "player":
            if self.battle_state.get("auto_battle"):
                self.process_auto_player_turn(current["unit"])
            else:
                self.process_player_turn(current["unit"])
        else:
            self.process_enemy_turn(current["unit"])
            
    def create_turn_order(self):
        """Create turn order based on speed"""
        combatants = []
        
        # Add alive team members
        for unit in self.battle_state["team"]:
            if unit["battle_hp"] > 0:
                combatants.append({"type": "player", "unit": unit, "speed": unit["entity"]["speed"]})
                
        # Add alive enemies
        for enemy in self.battle_state["enemies"]:
            if enemy["hp"] > 0:
                combatants.append({"type": "enemy", "unit": enemy, "speed": enemy["speed"]})
                
        # Sort by speed (highest first)
        combatants.sort(key=lambda x: x["speed"], reverse=True)
        
        self.battle_state["turn_order"] = combatants
        self.update_turn_display()
        
    def update_turn_display(self):
        """Update the enhanced turn order display"""
        self.turn_display.config(state='normal')
        self.turn_display.delete('1.0', 'end')
        
        if self.battle_state.get("turn_order"):
            # Show next 8 turns for better planning
            for i, combatant in enumerate(self.battle_state["turn_order"][:8]):
                if combatant["type"] == "player":
                    name = combatant["unit"]["entity"]["name"]
                    # Truncate long names
                    if len(name) > 10:
                        name = name[:10] + "..."
                    prefix = "🛡️"
                    color_code = "[ALLY]"
                else:
                    name = combatant["unit"]["name"]
                    if len(name) > 10:
                        name = name[:10] + "..."
                    prefix = "⚔️"
                    color_code = "[ENEMY]"
                
                # Get speed for additional info
                speed = combatant.get("speed", 0)
                
                if i == 0:
                    # Current turn - highlighted
                    self.turn_display.insert('end', f"▶️ {prefix} {name} (SPD:{speed})\n")
                else:
                    # Upcoming turns
                    self.turn_display.insert('end', f"{i+1}. {prefix} {name}\n")
        else:
            self.turn_display.insert('end', "Calculating turn order...\n")
                    
        self.turn_display.config(state='disabled')
        
    def cycle_battle_speed(self):
        """Cycle through battle speeds and save preference"""
        self.battle_speed_index = (self.battle_speed_index + 1) % len(self.battle_speeds)
        self.battle_speed = self.battle_speeds[self.battle_speed_index]
        
        # Save speed preference
        self.battle_speed_preference = self.battle_speed_index
        
        speed_text = f"⚡ x{self.battle_speed}"
        if self.battle_speed < 1:
            speed_text = f"🐌 x{self.battle_speed}"
        elif self.battle_speed > 2:
            speed_text = f"💨 x{int(self.battle_speed)}"
            
        self.speed_btn.config(text=speed_text)
        self.show_notification(f"Battle speed set to {self.battle_speed}x")
        
    def process_player_turn(self, unit):
        """Process a player unit's turn with enhanced UI"""
        # Clear action buttons
        for widget in self.actions_frame.winfo_children():
            widget.destroy()
            
        # Current unit info with status
        unit_info_frame = tk.Frame(self.actions_frame, bg='black')
        unit_info_frame.pack(pady=5)
        
        # Unit name and current status
        current_label = tk.Label(
            unit_info_frame,
            text=f"⚔️ {unit['entity']['name']}'s Turn",
            font=self.header_font,
            bg='black',
            fg='#66FF66'
        )
        current_label.pack()
        
        # Quick stats display
        hp_percent = unit["battle_hp"] / unit["entity"]["hp"]
        hp_color = '#66FF66' if hp_percent > 0.6 else '#FFFF66' if hp_percent > 0.3 else '#FF6666'
        
        stats_text = f"❤️{unit['battle_hp']}/{unit['entity']['hp']} ⚡{unit['sp']}/150"
        if unit.get("effects"):
            effects_summary = self.get_effects_summary(unit["effects"])
            if effects_summary:
                stats_text += f" {effects_summary}"
        
        stats_label = tk.Label(
            unit_info_frame,
            text=stats_text,
            font=self.small_font,
            bg='black',
            fg='white'
        )
        stats_label.pack()
        
        # Action buttons with enhanced information
        actions_btn_frame = tk.Frame(self.actions_frame, bg='black')
        actions_btn_frame.pack(pady=10)
        
        # Attack button with damage preview
        alive_enemies = [e for e in self.battle_state["enemies"] if e["hp"] > 0]
        avg_damage = 0
        if alive_enemies:
            # Calculate average damage against enemies
            total_damage = 0
            for enemy in alive_enemies:
                damage, _ = self.calculate_damage(unit, enemy)
                total_damage += damage
            avg_damage = total_damage // len(alive_enemies)
        
        attack_btn = tk.Button(
            actions_btn_frame,
            text=f"⚔️ Attack\n(~{avg_damage} dmg)",
            command=lambda: self.player_attack(unit),
            font=self.small_font,
            bg='#CC3333',
            fg='white',
            width=12,
            height=2
        )
        attack_btn.pack(side='left', padx=3)
        
        # Skill button (if available) with cost info
        if unit["entity"]["skill"]:
            skill_cost = self.skill_costs.get(unit["entity"]["skill"], 50)
            skill_available = unit["sp"] >= skill_cost
            
            skill_name = unit["entity"]["skill"].replace('_', ' ').title()
            if len(skill_name) > 12:
                skill_name = skill_name[:12] + "..."
            
            skill_btn = tk.Button(
                actions_btn_frame,
                text=f"✨ {skill_name}\n(Cost: {skill_cost} SP)",
                command=lambda: self.player_skill(unit) if skill_available else None,
                font=self.small_font,
                bg='#3366CC' if skill_available else '#666666',
                fg='white' if skill_available else '#999999',
                width=12,
                height=2,
                state='normal' if skill_available else 'disabled'
            )
            skill_btn.pack(side='left', padx=3)
        
        # Defend button with benefit info
        defend_btn = tk.Button(
            actions_btn_frame,
            text="🛡️ Defend\n(-50% dmg, +10 SP)",
            command=lambda: self.player_defend(unit),
            font=self.small_font,
            bg='#669966',
            fg='white',
            width=12,
            height=2
        )
        defend_btn.pack(side='left', padx=3)
        
        # Add timer for turn (optional pressure)
        if not hasattr(self, 'turn_timer_active'):
            self.turn_timer_active = False
        
        # Turn info
        turn_info = tk.Label(
            self.actions_frame,
            text="Choose your action wisely!",
            font=self.small_font,
            bg='black',
            fg='#CCCCCC'
        )
        turn_info.pack(pady=5)
        
    def player_attack(self, unit):
        """Handle player attack action"""
        # Get alive enemies
        alive_enemies = [e for e in self.battle_state["enemies"] if e["hp"] > 0]
        if not alive_enemies:
            self.finish_turn(unit)
            return
            
        # Create target selection
        self.show_target_selection_inline(unit, alive_enemies, "attack")
        
    def show_target_selection_inline(self, unit, targets, action_type):
        """Show target selection in same window"""
        # Clear actions frame
        for widget in self.actions_frame.winfo_children():
            widget.destroy()
            
        # Title
        title_text = f"Select target for {unit['entity']['name']}'s {action_type}:"
        title_label = tk.Label(
            self.actions_frame,
            text=title_text,
            font=self.body_font,
            bg='black',
            fg='white'
        )
        title_label.pack(pady=10)
        
        # Target buttons
        targets_frame = tk.Frame(self.actions_frame, bg='black')
        targets_frame.pack(pady=10)
        
        for i, target in enumerate(targets):
            btn_text = f"{i+1}. {target['name']} (HP: {target['hp']}/{target.get('max_hp', target['hp'])})"
            target_btn = tk.Button(
                targets_frame,
                text=btn_text,
                command=lambda t=target: self.execute_player_action(unit, t, action_type),
                font=self.small_font,
                bg='#663333',
                fg='white',
                width=30
            )
            target_btn.pack(pady=2)
            
        # Cancel button
        cancel_btn = tk.Button(
            targets_frame,
            text="❌ Cancel",
            command=lambda: self.process_player_turn(unit),
            font=self.body_font,
            bg='#666666',
            fg='white'
        )
        cancel_btn.pack(pady=10)
        
    def execute_player_action(self, unit, target, action_type):
        """Execute the player's chosen action"""
        if action_type == "attack":
            # Calculate damage
            damage, is_crit = self.calculate_damage(unit, target)
            target["hp"] -= damage
            target["hp"] = max(0, target["hp"])
            
            # Apply Slender's Eight Pages passive (only when Slender is involved)
            self.apply_slender_eight_pages_passive(unit, target)
            
            # Apply Jeff's Go to Sleep passive on crit
            if is_crit and unit["entity"]["name"] == "Jeff the Killer":
                ghost_effect = None
                for effect in unit["effects"]:
                    if effect.get("type") == "ghost":
                        ghost_effect = effect
                        break
                if ghost_effect:
                    ghost_effect["stacks"] = min(ghost_effect["stacks"] + 1, 5)
                else:
                    unit["effects"].append({"type": "ghost", "turns": 99, "stacks": 1, "source": "Go to Sleep"})
                self.add_battle_log(f"👻 {unit['entity']['name']} gains Ghost stack on critical hit!")
            
            # Special effects
            if unit["entity"]["name"] == "Iris":
                # Iris AoE attack
                self.add_battle_log(f"⚔️ {unit['entity']['name']} attacks ALL enemies for {damage} damage!")
                for enemy in self.battle_state["enemies"]:
                    if enemy["hp"] > 0 and enemy != target:
                        enemy["hp"] -= damage
                        enemy["hp"] = max(0, enemy["hp"])
                        # 40% chance to slow
                        if random.randint(1, 100) <= 40:
                            enemy["effects"].append({"type": "slow", "turns": 3, "source": "Iris"})
                        # Apply Slender passive for AoE targets too
                        self.apply_slender_eight_pages_passive(unit, enemy)
            else:
                crit_text = " [CRITICAL HIT]" if is_crit else ""
                self.add_battle_log(f"⚔️ {unit['entity']['name']} attacks {target['name']} for {damage} damage!{crit_text}")
                
            # SP gain
            unit["sp"] = min(unit["sp"] + 5, 150)
            
        elif action_type == "skill":
            # Use skill on target
            self.use_skill(unit, target)
            unit["sp"] -= self.skill_costs[unit["entity"]["skill"]]
            
        self.finish_turn(unit)
        
    def player_skill(self, unit):
        """Handle player skill action"""
        skill = unit["entity"]["skill"]
        
        # Skills that require target selection
        target_required_skills = ["killer_burst", "faceless_terror", "bloody_smile", "mirror_curse"]
        
        if skill in target_required_skills:
            # Show target selection for skills that need it
            alive_enemies = [e for e in self.battle_state["enemies"] if e["hp"] > 0]
            if alive_enemies:
                self.show_target_selection_inline(unit, alive_enemies, "skill")
                return
        
        # Use skill without target selection
        self.use_skill(unit, None)
        unit["sp"] -= self.skill_costs[skill]
        self.finish_turn(unit)
        
    def player_defend(self, unit):
        """Handle player defend action"""
        unit["defending"] = True
        unit["sp"] = min(unit["sp"] + 10, 150)
        self.show_notification(f"🛡️ {unit['entity']['name']} is defending!")
        self.finish_turn(unit)
        
    def use_skill(self, unit, target):
        """Use a unit's skill"""
        skill = unit["entity"]["skill"]
        name = unit["entity"]["name"]
        skill_level = unit.get("skill_level", 0)
        
        if skill == "joyful_regeneration":  # SCP-999
            # Grant 20% HP regeneration per turn for 3 turns to all allies
            for team_unit in self.battle_state["team"]:
                if team_unit["battle_hp"] > 0:
                    # Remove existing joyful regen if present
                    team_unit["effects"] = [e for e in team_unit["effects"] if e.get("type") != "joyful_regen"]
                    # Add new joyful regeneration
                    regen_effect = {
                        "type": "joyful_regen",
                        "turns": 3,
                        "heal_percent": 20,
                        "source": name
                    }
                    # At skill level 5, add 50% increased healing effect
                    if skill_level >= 5:
                        team_unit["effects"] = [e for e in team_unit["effects"] if e.get("type") != "heal_boost"]
                        team_unit["effects"].append({
                            "type": "heal_boost",
                            "turns": 3,
                            "boost_percent": 50,
                            "source": name
                        })
                        regen_effect["enhanced"] = True
                    team_unit["effects"].append(regen_effect)
            
            heal_text = f"💚 {name} grants joyful regeneration to all allies!"
            if skill_level >= 5:
                heal_text += " Enhanced healing effects active!"
            self.add_battle_log(heal_text)
            
        elif skill == "killer_burst":  # Jeff the Killer
            # High damage attack - allow target selection
            alive_enemies = [e for e in self.battle_state["enemies"] if e["hp"] > 0]
            if alive_enemies and target:
                damage, _ = self.calculate_damage(unit, target, force_crit=True)
                damage = int(damage * 1.5)
                target["hp"] = max(0, target["hp"] - damage)
                # Gain 1 ghost stack after using skill
                ghost_effect = None
                for effect in unit["effects"]:
                    if effect.get("type") == "ghost":
                        ghost_effect = effect
                        break
                if ghost_effect:
                    ghost_effect["stacks"] = min(ghost_effect["stacks"] + 1, 5)
                else:
                    unit["effects"].append({"type": "ghost", "turns": 99, "stacks": 1, "source": "Go to Sleep"})
                self.add_battle_log(f"👻 {name} unleashes Killer Burst for {damage} damage and gains Ghost!")
            elif alive_enemies:
                # Fallback for auto-battle
                target = random.choice(alive_enemies)
                damage, _ = self.calculate_damage(unit, target, force_crit=True)
                damage = int(damage * 1.5)
                target["hp"] = max(0, target["hp"] - damage)
                ghost_effect = None
                for effect in unit["effects"]:
                    if effect.get("type") == "ghost":
                        ghost_effect = effect
                        break
                if ghost_effect:
                    ghost_effect["stacks"] = min(ghost_effect["stacks"] + 1, 5)
                else:
                    unit["effects"].append({"type": "ghost", "turns": 99, "stacks": 1, "source": "Go to Sleep"})
                self.add_battle_log(f"👻 {name} unleashes Killer Burst for {damage} damage and gains Ghost!")
                
        elif skill == "analog_distortion":  # Iris
            # Reality distortion - damage and debuff all enemies
            for enemy in self.battle_state["enemies"]:
                if enemy["hp"] > 0:
                    damage = int(unit["entity"]["attack"] * 0.8)
                    enemy["hp"] = max(0, enemy["hp"] - damage)
                    enemy["effects"].append({"type": "debuff", "stat": "defense", "amount": int(enemy["defense"] * 0.3), "turns": 4, "source": name})
            self.add_battle_log(f"📺 {name} distorts reality, damaging and debuffing all enemies!")
            
        elif skill == "indestructible_regeneration":  # SCP-682
            # Heal and taunt
            max_hp = unit.get("battle_stats", {}).get("hp", unit["entity"]["hp"])
            heal = int(max_hp * 0.4)
            unit["battle_hp"] = min(unit["battle_hp"] + heal, max_hp)
            
            # Add regeneration effect (different from SCP-999's joyful_regen)
            unit["effects"].append({"type": "scp_regen", "turns": 3, "heal_percent": 10, "source": name})
            unit["effects"].append({"type": "taunt", "turns": 3, "source": name})
            self.add_battle_log(f"🦎 {name} regenerates {heal} HP and taunts enemies!")
            
        elif skill == "faceless_terror":  # Slender - 8 Pages effect
            # Slender's 8 Pages skill implementation - allow target selection
            alive_enemies = [e for e in self.battle_state["enemies"] if e["hp"] > 0]
            if alive_enemies and target:
                # Guaranteed hit with no defense calculation
                damage = unit["entity"]["attack"]
                target["hp"] = max(0, target["hp"] - damage)
                
                # Add Eight Pages stack
                eight_pages_effect = None
                for effect in target["effects"]:
                    if effect.get("type") == "eight_pages":
                        eight_pages_effect = effect
                        break
                        
                if eight_pages_effect:
                    eight_pages_effect["stacks"] = min(eight_pages_effect["stacks"] + 1, 8)
                else:
                    target["effects"].append({"type": "eight_pages", "turns": 99, "stacks": 1, "source": name})
                    eight_pages_effect = target["effects"][-1]
                    
                # Apply defense reduction based on stacks
                defense_reduction = eight_pages_effect["stacks"] * 5
                target["effects"] = [e for e in target["effects"] if not (e.get("type") == "debuff" and e.get("source") == "Eight Pages")]
                target["effects"].append({"type": "debuff", "stat": "defense", "amount": defense_reduction, "turns": 99, "source": "Eight Pages"})
                
                # Check for 8 stacks at max skill level
                if skill_level == 5 and eight_pages_effect["stacks"] >= 8:
                    target["effects"].append({"type": "stun", "turns": 2, "source": name})
                    target["effects"].append({"type": "fear", "turns": 3, "source": name})
                    eight_pages_effect["stacks"] = 0
                    self.add_battle_log(f"📄 {name} completes the 8 Pages ritual! {target['name']} is stunned and feared!")
                else:
                    self.add_battle_log(f"📄 {name} uses Faceless Terror for {damage} damage! {target['name']} has {eight_pages_effect['stacks']} Pages.")
            elif alive_enemies:
                # Fallback for auto-battle
                target = random.choice(alive_enemies)
                damage = unit["entity"]["attack"]
                target["hp"] = max(0, target["hp"] - damage)
                eight_pages_effect = None
                for effect in target["effects"]:
                    if effect.get("type") == "eight_pages":
                        eight_pages_effect = effect
                        break
                if eight_pages_effect:
                    eight_pages_effect["stacks"] = min(eight_pages_effect["stacks"] + 1, 8)
                else:
                    target["effects"].append({"type": "eight_pages", "turns": 99, "stacks": 1, "source": name})
                    eight_pages_effect = target["effects"][-1]
                defense_reduction = eight_pages_effect["stacks"] * 5
                target["effects"] = [e for e in target["effects"] if not (e.get("type") == "debuff" and e.get("source") == "Eight Pages")]
                target["effects"].append({"type": "debuff", "stat": "defense", "amount": defense_reduction, "turns": 99, "source": "Eight Pages"})
                if skill_level == 5 and eight_pages_effect["stacks"] >= 8:
                    target["effects"].append({"type": "stun", "turns": 2, "source": name})
                    target["effects"].append({"type": "fear", "turns": 3, "source": name})
                    eight_pages_effect["stacks"] = 0
                    self.add_battle_log(f"📄 {name} completes the 8 Pages ritual! {target['name']} is stunned and feared!")
                else:
                    self.add_battle_log(f"📄 {name} uses Faceless Terror for {damage} damage! {target['name']} has {eight_pages_effect['stacks']} Pages.")
                    
        elif skill == "bloody_smile":  # Kuchisake-onna
            # High crit chance attack with bleed
            alive_enemies = [e for e in self.battle_state["enemies"] if e["hp"] > 0]
            if alive_enemies:
                target = random.choice(alive_enemies)
                damage, _ = self.calculate_damage(unit, target, force_crit=True)
                target["hp"] = max(0, target["hp"] - damage)
                target["effects"].append({"type": "bleed", "turns": 4, "damage": damage // 4, "source": name})
                self.add_battle_log(f"💋 {name} inflicts a Bloody Smile for {damage} damage and bleeding!")
                
        elif skill == "night_ambush":  # The Rake
            # Multi-hit attack with increased damage in darkness
            alive_enemies = [e for e in self.battle_state["enemies"] if e["hp"] > 0]
            if alive_enemies:
                hits = random.randint(2, 4)
                total_damage = 0
                for _ in range(hits):
                    target = random.choice(alive_enemies)
                    if target["hp"] > 0:
                        damage, _ = self.calculate_damage(unit, target)
                        damage = int(damage * 1.3)  # Night bonus
                        target["hp"] = max(0, target["hp"] - damage)
                        total_damage += damage
                self.add_battle_log(f"🌙 {name} performs Night Ambush with {hits} hits for {total_damage} total damage!")
                
        elif skill == "mothmans_omen":  # Mothman
            # Accuracy debuff and damage all enemies
            for enemy in self.battle_state["enemies"]:
                if enemy["hp"] > 0:
                    damage = int(unit["entity"]["attack"] * 0.6)
                    enemy["hp"] = max(0, enemy["hp"] - damage)
                    enemy["effects"].append({"type": "debuff", "stat": "accuracy", "amount": 30, "turns": 3, "source": name})
            self.add_battle_log(f"🦋 {name} brings an ill omen, reducing all enemies' accuracy!")
            
        elif skill == "mirror_curse":  # Bloody Mary
            # Damage and curse reflection
            alive_enemies = [e for e in self.battle_state["enemies"] if e["hp"] > 0]
            if alive_enemies:
                target = random.choice(alive_enemies)
                damage, _ = self.calculate_damage(unit, target)
                target["hp"] = max(0, target["hp"] - damage)
                # Curse that reflects damage
                target["effects"].append({"type": "mirror_curse", "turns": 5, "reflect_percent": 50, "source": name})
                self.add_battle_log(f"🪞 {name} casts Mirror Curse for {damage} damage and curse reflection!")
                
        # Add other skills as needed...
        
    def calculate_damage(self, attacker, defender, force_crit=False):
        """Calculate damage between attacker and defender using battle stats"""
        # Get battle stats if available, otherwise fall back to base stats
        if "battle_stats" in attacker:
            atk = attacker["battle_stats"]["attack"]
            crit_rate = min(attacker["battle_stats"]["crit_rate"], 100)  # Cap at 100%
            crit_damage = attacker["battle_stats"]["crit_damage"]
        elif "entity" in attacker:
            atk = attacker["entity"]["attack"]
            crit_rate = min(attacker["entity"]["crit_rate"], 100)
            crit_damage = attacker["entity"]["crit_damage"]
        else:
            atk = attacker["attack"]
            crit_rate = min(attacker["crit_rate"], 100)
            crit_damage = attacker["crit_damage"]
            
        if "battle_stats" in defender:
            defense = defender["battle_stats"]["defense"]
        elif "entity" in defender:
            defense = defender["entity"]["defense"]
        else:
            defense = defender["defense"]
            
        # Calculate base damage
        base_damage = max(1, atk - defense)
        
        # Check for crit
        is_crit = force_crit or (random.randint(1, 100) <= crit_rate)
        
        if is_crit:
            damage = int(base_damage * (crit_damage / 100))
        else:
            damage = base_damage
            
        # Add some randomness
        damage = int(damage * random.uniform(0.85, 1.15))
        
        return max(1, damage), is_crit
        
    def apply_slender_eight_pages_passive(self, attacker, target):
        """Apply Slender's Eight Pages passive effect - only when Slender is involved"""
        # Only apply if Slender is the attacker or target
        slender_involved = False
        
        # Check if attacker is Slender
        attacker_name = attacker.get('entity', {}).get('name', attacker.get('name', ''))
        target_name = target.get('entity', {}).get('name', target.get('name', ''))
        
        if attacker_name == 'Slender' or target_name == 'Slender':
            slender_involved = True
            
        if not slender_involved:
            return
            
        # Apply Eight Pages stack to the non-Slender participant
        stack_target = target if attacker_name == 'Slender' else attacker
        stack_target_name = target_name if attacker_name == 'Slender' else attacker_name
        
        if stack_target_name == 'Slender':  # Don't apply to Slender itself
            return
            
        # Apply Eight Pages stack
        eight_pages_effect = None
        for effect in stack_target.get('effects', []):
            if effect.get('type') == 'eight_pages':
                eight_pages_effect = effect
                break
                
        if eight_pages_effect:
            eight_pages_effect['stacks'] = min(eight_pages_effect['stacks'] + 1, 8)
        else:
            if 'effects' not in stack_target:
                stack_target['effects'] = []
            stack_target['effects'].append({
                'type': 'eight_pages', 
                'turns': 99, 
                'stacks': 1, 
                'source': 'Slender'
            })
            eight_pages_effect = stack_target['effects'][-1]
            
        # Apply defense reduction (5% per stack)
        defense_reduction = eight_pages_effect['stacks'] * 5
        
        # Remove old defense debuff from Eight Pages if exists
        stack_target['effects'] = [e for e in stack_target.get('effects', []) 
                              if not (e.get('type') == 'debuff' and e.get('source') == 'Eight Pages')]
                              
        # Apply new defense debuff
        stack_target['effects'].append({
            'type': 'debuff',
            'stat': 'defense',
            'amount': defense_reduction,
            'turns': 99,
            'source': 'Eight Pages'
        })
        
        # Log the effect
        self.add_battle_log(f"📄 {stack_target_name} gains Eight Pages stack ({eight_pages_effect['stacks']}/8) - Defense reduced by {defense_reduction}%!")
        
        # Check for 8 stacks - stun effect
        if eight_pages_effect['stacks'] >= 8:
            stack_target['effects'].append({'type': 'stun', 'turns': 2, 'source': 'Slender'})
            stack_target['effects'].append({'type': 'fear', 'turns': 3, 'source': 'Slender'})
            eight_pages_effect['stacks'] = 0  # Reset stacks after triggering
            self.add_battle_log(f"📄 {stack_target_name} is overwhelmed by the Eight Pages! Stunned and feared!")
        
    def process_auto_player_turn(self, unit):
        """Process an automatic player turn (AI)"""
        # Simple AI: attack random enemy
        alive_enemies = [e for e in self.battle_state["enemies"] if e["hp"] > 0]
        if alive_enemies:
            target = random.choice(alive_enemies)
            
            # Use skill if available and SP is sufficient
            if (unit["entity"]["skill"] and 
                unit["sp"] >= self.skill_costs.get(unit["entity"]["skill"], 999) and
                random.randint(1, 100) <= 30):  # 30% chance to use skill
                self.use_skill(unit, target)
                unit["sp"] -= self.skill_costs[unit["entity"]["skill"]]
                self.add_battle_log(f"🤖 {unit['entity']['name']} uses skill!")
            else:
                # Normal attack
                damage, is_crit = self.calculate_damage(unit, target)
                target["hp"] = max(0, target["hp"] - damage)
                
                # Apply Slender's Eight Pages passive (only when Slender is involved)
                self.apply_slender_eight_pages_passive(unit, target)
                
                # Apply Jeff's Go to Sleep passive on crit
                if is_crit and unit["entity"]["name"] == "Jeff the Killer":
                    ghost_effect = None
                    for effect in unit["effects"]:
                        if effect.get("type") == "ghost":
                            ghost_effect = effect
                            break
                    if ghost_effect:
                        ghost_effect["stacks"] = min(ghost_effect["stacks"] + 1, 5)
                    else:
                        unit["effects"].append({"type": "ghost", "turns": 99, "stacks": 1, "source": "Go to Sleep"})
                    self.add_battle_log(f"👻 {unit['entity']['name']} gains Ghost stack on critical hit!")
                
                crit_text = " [CRIT]" if is_crit else ""
                self.add_battle_log(f"🤖 {unit['entity']['name']} attacks {target['name']} for {damage} damage!{crit_text}")
                
                unit["sp"] = min(unit["sp"] + 5, 150)
                
        self.finish_turn(unit)
        
    def start_next_wave(self):
        """Start the next wave in multi-wave battles"""
        if not hasattr(self.battle_state, 'current_wave') or not hasattr(self.battle_state, 'total_waves'):
            # If not a multi-wave battle, just proceed to victory
            self.battle_victory()
            return
            
        # Increment wave counter
        self.battle_state['current_wave'] += 1
        
        # Generate new enemies for this wave
        if self.battle_state.get("type") == "campaign":
            # Campaign battles: use the enhanced wave generation
            new_enemies = self.generate_enemies(
                self.battle_state['world_idx'], 
                self.battle_state['stage_idx'], 
                wave=self.battle_state['current_wave']
            )
        elif self.battle_state.get("type") == "rune_boss":
            # Rune boss: generate minions leading up to the boss
            if self.battle_state['current_wave'] < self.battle_state['total_waves']:
                # Generate minions for waves 1-4
                new_enemies = self.generate_boss_minions(self.battle_state['boss_data'], self.battle_state['current_wave'])
            else:
                # Final wave: the actual boss
                new_enemies = [self.battle_state['original_boss']]
        else:
            # Default: generate enemies with wave scaling
            new_enemies = self.generate_enemies(0, 0, wave=self.battle_state['current_wave'])
            
        # Replace enemies in battle state
        self.battle_state['enemies'] = new_enemies
        
        # Reset turn order for new wave
        self.battle_state['turn_order'] = []
        
        # Heal team members between waves
        heal_percentage = 0.3 if self.battle_state.get('is_boss_stage') else 0.25  # More healing for boss stages
        sp_recovery = 40 if self.battle_state.get('is_boss_stage') else 30  # More SP for boss stages
        
        for unit in self.battle_state['team']:
            if unit['battle_hp'] > 0:  # Only heal living units
                max_hp = unit.get('battle_stats', {}).get('hp', unit.get('max_hp', 100))
                heal_amount = int(max_hp * heal_percentage)
                unit['battle_hp'] = min(unit['battle_hp'] + heal_amount, max_hp)
                # Also restore SP
                unit['sp'] = min(unit['sp'] + sp_recovery, 150)
        
        # Special message for boss waves
        if self.battle_state.get('is_boss_stage') and self.battle_state['current_wave'] == self.battle_state['total_waves']:
            self.add_battle_log(f"👑 FINAL WAVE! The boss emerges! Team healed for the ultimate challenge!")
        elif self.battle_state.get('is_boss_stage'):
            self.add_battle_log(f"🌊 Boss Stage Wave {self.battle_state['current_wave']}/{self.battle_state['total_waves']} - Team healed, prepare for escalating difficulty!")
        else:
            self.add_battle_log(f"🌊 Wave {self.battle_state['current_wave']}/{self.battle_state['total_waves']} begins! Team partially healed.")
        
        # Update battle display and start new turn
        self.update_battle_display()
        self.start_battle_turn()
    
    def generate_boss_minions(self, boss_data, wave):
        """Generate minions for rune boss waves"""
        minions = []
        num_minions = min(wave + 1, 4)  # 2-5 minions depending on wave
        
        for _ in range(num_minions):
            # Create minions based on boss type
            minion_names = {
                "The Forge Master": ["Animated Hammer", "Fire Spirit", "Molten Guardian"],
                "Guardian Goliath": ["Stone Sentinel", "Crystal Defender", "Armored Wraith"],
                "Mystic Oracle": ["Ethereal Wisp", "Vision Seeker", "Mystic Echo"],
                "Nightmare Sovereign": ["Shadow Minion", "Terror Spawn", "Dread Walker"]
            }
            
            boss_name = boss_data.get('name', 'Unknown Boss')
            minion_pool = minion_names.get(boss_name, ["Minion", "Servant", "Guardian"])
            
            base_stats = {
                "hp": 80 + (wave * 40),
                "attack": 15 + (wave * 8),
                "defense": 8 + (wave * 4),
                "speed": 20 + (wave * 3)
            }
            
            minion = {
                "name": f"{random.choice(minion_pool)} [W{wave}]",
                "rarity": "Rare",
                "hp": base_stats["hp"],
                "max_hp": base_stats["hp"],
                "attack": base_stats["attack"],
                "defense": base_stats["defense"],
                "speed": base_stats["speed"],
                "skill": None,
                "crit_rate": 5,
                "crit_damage": 150,
                "accuracy": 85,
                "evasion": 10,
                "sp": 80,
                "effects": []
            }
            minions.append(minion)
            
        return minions
        
    def show_post_battle_options(self):
        """Show post-battle options after victory"""
        self.clear_content()
        
        # Title
        title_label = tk.Label(
            self.content_frame,
            text="🎉 VICTORY! 🎉",
            font=self.title_font,
            bg='black',
            fg='#66FF66'
        )
        title_label.pack(pady=30)
        
        # Victory message with battle info
        battle_info = self.get_battle_info_text()
        message_label = tk.Label(
            self.content_frame,
            text=f"You have successfully completed:\n{battle_info}\n\nWhat would you like to do next?",
            font=self.header_font,
            bg='black',
            fg='white',
            justify='center'
        )
        message_label.pack(pady=20)
        
        # Options frame
        options_frame = tk.Frame(self.content_frame, bg='black')
        options_frame.pack(pady=30)
        
        # Repeat battle
        repeat_btn = tk.Button(
            options_frame,
            text="🔄 Repeat Battle\n(Same Team)",
            command=self.repeat_last_battle,
            font=self.header_font,
            bg='#006600',
            fg='white',
            width=15,
            height=3
        )
        repeat_btn.pack(side='left', padx=10)
        
        # Multi-Battle mode
        multi_btn = tk.Button(
            options_frame,
            text="⚡ Multi-Battle\n(Auto Repeat)",
            command=self.start_multi_battle,
            font=self.header_font,
            bg='#0066CC',
            fg='white',
            width=15,
            height=3
        )
        multi_btn.pack(side='left', padx=10)
        
        # Change team and retry
        change_team_btn = tk.Button(
            options_frame,
            text="⚔️ Change Team\n& Repeat",
            command=self.change_team_and_retry,
            font=self.header_font,
            bg='#CC6600',
            fg='white',
            width=15,
            height=3
        )
        change_team_btn.pack(side='left', padx=10)
        
        # Continue/Exit
        exit_btn = tk.Button(
            options_frame,
            text="🚪 Continue\n(Return)",
            command=self.exit_post_battle,
            font=self.header_font,
            bg='#666666',
            fg='white',
            width=15,
            height=3
        )
        exit_btn.pack(side='left', padx=10)
    
    def get_battle_info_text(self):
        """Get descriptive text about the last battle"""
        if not hasattr(self, 'last_completed_battle') or not self.last_completed_battle:
            return "Unknown Battle"
            
        battle = self.last_completed_battle
        battle_type = battle.get('type')
        
        if battle_type == 'campaign':
            world_idx = battle.get('world_idx', 0)
            stage_idx = battle.get('stage_idx', 0)
            return f"World {world_idx + 1}-{stage_idx + 1}: {self.worlds[world_idx]['name']}"
        elif battle_type == 'delve':
            floor = battle.get('floor', 1)
            return f"Endless Delve Floor {floor}"
        elif battle_type == 'rune_boss':
            boss_data = battle.get('boss_data', {})
            stage = battle.get('stage', 1)
            return f"{boss_data.get('name', 'Unknown Boss')} - Stage {stage}"
        elif battle_type == 'xp_trainer':
            trainer_data = battle.get('trainer_data', {})
            return f"XP Training vs {trainer_data.get('name', 'Unknown Trainer')}"
        else:
            return "Unknown Battle Type"
    
    def repeat_last_battle(self):
        """Repeat the last completed battle with same team"""
        if not hasattr(self, 'last_completed_battle') or not self.last_completed_battle:
            self.show_notification("❌ No previous battle to repeat!")
            return
            
        battle = self.last_completed_battle
        team = battle.get('team', [])
        
        if not team:
            self.show_notification("❌ No team data found for repeat battle!")
            return
            
        self.show_notification("🔄 Repeating last battle with same team...")
        self.launch_battle_from_data(battle, team)
    
    def retry_last_battle(self):
        """Retry the last battle (for defeats) with same team"""
        if not hasattr(self, 'last_completed_battle') or not self.last_completed_battle:
            self.show_notification("❌ No previous battle to retry!")
            return
            
        battle = self.last_completed_battle
        team = battle.get('team', [])
        
        if not team:
            self.show_notification("❌ No team data found for retry!")
            return
            
        self.show_notification("🔄 Retrying battle with same team...")
        self.launch_battle_from_data(battle, team)
    
    def change_team_and_retry(self):
        """Change team and retry the last battle"""
        if not hasattr(self, 'last_completed_battle') or not self.last_completed_battle:
            self.show_notification("❌ No previous battle to retry!")
            return
            
        battle = self.last_completed_battle
        
        self.show_notification("⚔️ Select new team for battle...")
        self.show_team_selection_inline(lambda team: self.launch_battle_from_data(battle, team) if team else None)
    
    def start_multi_battle(self):
        """Start multi-battle mode"""
        if not hasattr(self, 'last_completed_battle') or not self.last_completed_battle:
            self.show_notification("❌ No battle to repeat in multi-battle mode!")
            return
            
        # Show multi-battle configuration interface
        self.show_multi_battle_config()
    
    def show_multi_battle_config(self):
        """Show multi-battle configuration interface"""
        self.clear_content()
        
        title_label = tk.Label(
            self.content_frame,
            text="⚡ MULTI-BATTLE CONFIGURATION ⚡",
            font=self.title_font,
            bg='black',
            fg='#66CCFF'
        )
        title_label.pack(pady=20)
        
        # Battle info
        battle_info = self.get_battle_info_text()
        info_label = tk.Label(
            self.content_frame,
            text=f"Battle: {battle_info}",
            font=self.header_font,
            bg='black',
            fg='#FFCC66'
        )
        info_label.pack(pady=10)
        
        # Configuration options
        config_frame = tk.LabelFrame(
            self.content_frame,
            text="Multi-Battle Settings",
            font=self.header_font,
            bg='black',
            fg='#CCCCCC'
        )
        config_frame.pack(fill='x', padx=50, pady=20)
        
        # Number of battles
        battles_frame = tk.Frame(config_frame, bg='black')
        battles_frame.pack(pady=10)
        
        battles_label = tk.Label(
            battles_frame,
            text="Number of battles to run:",
            font=self.body_font,
            bg='black',
            fg='white'
        )
        battles_label.pack(side='left', padx=10)
        
        self.multi_battle_count = tk.StringVar(value="5")
        battles_entry = tk.Entry(
            battles_frame,
            textvariable=self.multi_battle_count,
            font=self.body_font,
            bg='#1a1a1a',
            fg='white',
            width=10,
            justify='center'
        )
        battles_entry.pack(side='left', padx=10)
        
        # Stop conditions
        conditions_frame = tk.LabelFrame(
            config_frame,
            text="Stop Conditions",
            font=self.body_font,
            bg='black',
            fg='#FFCC66'
        )
        conditions_frame.pack(fill='x', padx=20, pady=10)
        
        self.stop_on_defeat = tk.BooleanVar(value=True)
        stop_defeat_check = tk.Checkbutton(
            conditions_frame,
            text="Stop on defeat",
            variable=self.stop_on_defeat,
            font=self.body_font,
            bg='black',
            fg='white',
            selectcolor='#333333'
        )
        stop_defeat_check.pack(anchor='w', padx=10, pady=5)
        
        self.stop_on_level_up = tk.BooleanVar(value=False)
        stop_levelup_check = tk.Checkbutton(
            conditions_frame,
            text="Stop when any unit levels up",
            variable=self.stop_on_level_up,
            font=self.body_font,
            bg='black',
            fg='white',
            selectcolor='#333333'
        )
        stop_levelup_check.pack(anchor='w', padx=10, pady=5)
        
        # Start multi-battle button
        start_btn = tk.Button(
            self.content_frame,
            text="⚡ Start Multi-Battle",
            command=self.execute_multi_battle,
            font=self.header_font,
            bg='#006600',
            fg='white',
            width=20,
            height=2
        )
        start_btn.pack(pady=20)
        
        # Back button
        back_btn = tk.Button(
            self.content_frame,
            text="🔙 Back to Post-Battle Options",
            command=self.show_post_battle_options,
            font=self.body_font,
            bg='#666666',
            fg='white'
        )
        back_btn.pack(pady=10)
    
    def execute_multi_battle(self):
        """Execute multi-battle sequence"""
        try:
            battle_count = int(self.multi_battle_count.get())
            if battle_count <= 0 or battle_count > 100:
                self.show_notification("❌ Please enter a valid number between 1 and 100!")
                return
        except ValueError:
            self.show_notification("❌ Please enter a valid number!")
            return
        
        # Initialize multi-battle state
        self.multi_battle_active = True
        self.multi_battle_config = {
            'total_battles': battle_count,
            'completed_battles': 0,
            'stop_on_defeat': self.stop_on_defeat.get(),
            'stop_on_level_up': self.stop_on_level_up.get(),
            'victories': 0,
            'defeats': 0
        }
        
        self.show_notification(f"⚡ Starting multi-battle sequence: {battle_count} battles")
        
        # Start first battle
        self.continue_multi_battle()
    
    def continue_multi_battle(self):
        """Continue multi-battle sequence"""
        if not self.multi_battle_active:
            return
            
        config = self.multi_battle_config
        
        # Check if we should continue
        if config['completed_battles'] >= config['total_battles']:
            self.finish_multi_battle("All battles completed!")
            return
        
        # Launch next battle
        battle = self.last_completed_battle
        team = battle.get('team', [])
        
        if not team:
            self.finish_multi_battle("No team data available!")
            return
        
        config['completed_battles'] += 1
        self.show_notification(f"⚡ Multi-Battle: Starting battle {config['completed_battles']}/{config['total_battles']}")
        
        # Launch battle with auto-battle enabled
        self.launch_battle_from_data(battle, team, auto_battle=True)
    
    def handle_multi_battle_continuation(self):
        """Handle continuation of multi-battle after victory"""
        if not self.multi_battle_active:
            return
            
        self.multi_battle_config['victories'] += 1
        
        # Check stop conditions here if needed
        # For now, just continue to next battle after brief delay
        self.show_notification(f"✅ Victory! Continuing multi-battle... ({self.multi_battle_config['victories']} wins)")
        self.root.after(2000, self.continue_multi_battle)
    
    def finish_multi_battle(self, reason):
        """Finish multi-battle sequence"""
        self.multi_battle_active = False
        config = self.multi_battle_config
        
        # Show results
        results_text = f"⚡ Multi-Battle Complete!\n\n"
        results_text += f"Reason: {reason}\n"
        results_text += f"Battles Completed: {config['completed_battles']}/{config['total_battles']}\n"
        results_text += f"Victories: {config['victories']}\n"
        results_text += f"Defeats: {config['defeats']}"
        
        messagebox.showinfo("Multi-Battle Results", results_text)
        
        # Return to post-battle options
        self.show_post_battle_options()
    
    def launch_battle_from_data(self, battle_data, team, auto_battle=False):
        """Launch a battle from saved battle data"""
        battle_type = battle_data.get('type')
        
        if battle_type == 'campaign':
            world_idx = battle_data.get('world_idx', 0)
            stage_idx = battle_data.get('stage_idx', 0)
            self.launch_battle(world_idx, stage_idx, team)
        elif battle_type == 'delve':
            floor = battle_data.get('floor', 1)
            self.launch_delve_battle(floor, team)
        elif battle_type == 'rune_boss':
            boss_data = battle_data.get('boss_data', {})
            stage = battle_data.get('stage', 1)
            self.launch_rune_boss_battle(boss_data, team, stage)
        elif battle_type == 'xp_trainer':
            trainer_data = battle_data.get('trainer_data', {})
            self.launch_xp_trainer_battle(trainer_data, team)
        else:
            self.show_notification("❌ Unknown battle type!")
            return
        
        # Enable auto-battle if requested (for multi-battle)
        if auto_battle:
            # Wait a moment for battle to initialize, then enable auto-battle
            self.root.after(1000, lambda: setattr(self.battle_state, 'auto_battle', True) if hasattr(self, 'battle_state') else None)
    
    def exit_post_battle(self):
        """Exit post-battle options and return to appropriate screen"""
        if not hasattr(self, 'last_completed_battle') or not self.last_completed_battle:
            self.go_home()
            return
            
        battle_type = self.last_completed_battle.get('type')
        
        if battle_type == 'campaign':
            world_idx = self.last_completed_battle.get('world_idx', 0)
            self.enter_world(world_idx)
        elif battle_type == 'delve':
            self.show_endless_delve()
        elif battle_type == 'rune_boss':
            self.show_rune_sanctums()
        elif battle_type == 'xp_trainer':
            self.show_xp_training()
        else:
            self.go_home()
        
    def process_enemy_turn(self, enemy):
        """Process an enemy's turn"""
        # Enemy AI: attack random player
        alive_team = [u for u in self.battle_state["team"] if u["battle_hp"] > 0]
        if alive_team:
            target = random.choice(alive_team)
            
            damage, is_crit = self.calculate_damage(enemy, target)
            
            # Apply defending reduction
            if target.get("defending"):
                damage = damage // 2
                
            target["battle_hp"] = max(0, target["battle_hp"] - damage)
            
            # Apply Slender's Eight Pages passive (only when Slender is involved)
            self.apply_slender_eight_pages_passive(enemy, target)
            
            crit_text = " [CRIT]" if is_crit else ""
            self.add_battle_log(f"👹 {enemy['name']} attacks {target['entity']['name']} for {damage} damage!{crit_text}")
            
        self.finish_turn(enemy)
        
    def finish_turn(self, unit):
        """Finish the current turn and continue battle"""
        # Reset defending status
        if "entity" in unit:  # Player unit
            unit["defending"] = False
        
        # Apply turn-based effects (DoT, HoT, etc.) and update display
        self.apply_turn_effects(unit)
        
        # Update display immediately to show any changes
        self.update_battle_display()
        
        # Check for battle end
        if not self.check_battle_end():
            # Continue to next turn with speed-adjusted delay
            delay = int(1500 / self.battle_speed) if hasattr(self, 'battle_speed') else 1500
            delay = max(250, delay)  # Minimum delay for readability
            self.root.after(delay, self.process_next_turn)
    
    def apply_turn_effects(self, unit):
        """Apply turn-based effects like DoT, HoT, buffs, debuffs with proper stacking"""
        effects_to_remove = []
        
        # Group effects by type and source for proper stacking
        effect_groups = {}
        for effect in unit.get("effects", []):
            effect_type = effect.get("type")
            effect_source = effect.get("source", "unknown")
            key = f"{effect_type}_{effect_source}"
            
            if key not in effect_groups:
                effect_groups[key] = []
            effect_groups[key].append(effect)
        
        # Process each effect group
        for group_key, effects_list in effect_groups.items():
            effect_type = effects_list[0].get("type")
            effect_source = effects_list[0].get("source", "unknown")
            
            # Apply healing over time effects (these stack from different sources)
            if effect_type == "joyful_regen":
                for effect in effects_list:
                    heal_percent = effect.get("heal_percent", 20)
                    max_hp = unit.get("battle_stats", {}).get("hp", unit.get("max_hp", unit.get("entity", {}).get("hp", 1)))
                    heal_amount = int(max_hp * heal_percent / 100)
                    
                    if "entity" in unit:  # Player unit
                        unit["battle_hp"] = min(unit["battle_hp"] + heal_amount, max_hp)
                    else:  # Enemy unit
                        unit["hp"] = min(unit["hp"] + heal_amount, max_hp)
                        
                    self.add_battle_log(f"💚 {self.get_unit_name(unit)} heals {heal_amount} HP from {effect_source}'s regeneration!")
            
            elif effect_type == "scp_regen":  # SCP-682's regeneration (different from joyful_regen)
                for effect in effects_list:
                    heal_percent = effect.get("heal_percent", 10)
                    max_hp = unit.get("battle_stats", {}).get("hp", unit.get("max_hp", unit.get("entity", {}).get("hp", 1)))
                    heal_amount = int(max_hp * heal_percent / 100)
                    
                    if "entity" in unit:  # Player unit
                        unit["battle_hp"] = min(unit["battle_hp"] + heal_amount, max_hp)
                    else:  # Enemy unit
                        unit["hp"] = min(unit["hp"] + heal_amount, max_hp)
                        
                    self.add_battle_log(f"🦎 {self.get_unit_name(unit)} regenerates {heal_amount} HP from SCP-682's ability!")
            
            # Apply damage over time effects (these also stack from different sources)
            elif effect_type == "bleed":
                for effect in effects_list:
                    damage = effect.get("damage", 10)
                    if "entity" in unit:
                        unit["battle_hp"] = max(0, unit["battle_hp"] - damage)
                    else:
                        unit["hp"] = max(0, unit["hp"] - damage)
                    self.add_battle_log(f"🩸 {self.get_unit_name(unit)} takes {damage} bleed damage from {effect_source}!")
            
            elif effect_type == "burn":
                for effect in effects_list:
                    damage = effect.get("damage", 15)
                    if "entity" in unit:
                        unit["battle_hp"] = max(0, unit["battle_hp"] - damage)
                    else:
                        unit["hp"] = max(0, unit["hp"] - damage)
                    self.add_battle_log(f"🔥 {self.get_unit_name(unit)} takes {damage} burn damage from {effect_source}!")
            
            elif effect_type == "poison":
                for effect in effects_list:
                    damage = effect.get("damage", 20)
                    if "entity" in unit:
                        unit["battle_hp"] = max(0, unit["battle_hp"] - damage)
                    else:
                        unit["hp"] = max(0, unit["hp"] - damage)
                    self.add_battle_log(f"☠️ {self.get_unit_name(unit)} takes {damage} poison damage from {effect_source}!")
            
            # Reduce turn counters for all effects in this group
            for effect in effects_list:
                if "turns" in effect and effect["turns"] > 0:
                    effect["turns"] -= 1
                    if effect["turns"] <= 0:
                        effects_to_remove.append(effect)
        
        # Remove expired effects
        if effects_to_remove:
            for effect in effects_to_remove:
                if effect in unit.get("effects", []):
                    unit["effects"].remove(effect)
                    effect_name = effect.get("type", "unknown").replace("_", " ").title()
                    effect_source = effect.get("source", "unknown")
                    self.add_battle_log(f"⏰ {effect_name} from {effect_source} expired on {self.get_unit_name(unit)}")
    
    def get_unit_name(self, unit):
        """Get the display name of a unit"""
        if "entity" in unit:
            return unit["entity"]["name"]
        else:
            return unit.get("name", "Unknown")
            
    def toggle_auto_battle(self):
        """Toggle auto battle mode with enhanced feedback and save preference"""
        self.battle_state["auto_battle"] = not self.battle_state.get("auto_battle", False)
        
        # Save auto battle preference
        self.auto_battle_preference = self.battle_state["auto_battle"]
        
        if self.battle_state["auto_battle"]:
            self.auto_btn.config(text="🖐️ Manual", bg='#CC6600')
            self.add_battle_log("🤖 Auto battle enabled - AI taking control")
            # Clear action buttons when switching to auto
            for widget in self.actions_frame.winfo_children():
                widget.destroy()
            # Show auto battle status
            auto_status = tk.Label(
                self.actions_frame,
                text="🤖 AUTO BATTLE ACTIVE\nAI is controlling your units",
                font=self.body_font,
                bg='black',
                fg='#FFAA00',
                justify='center'
            )
            auto_status.pack(pady=20)
            # Continue with auto battle
            if not self.check_battle_end():
                delay = int(500 / self.battle_speed) if hasattr(self, 'battle_speed') else 500
                self.root.after(max(200, delay), self.process_next_turn)
        else:
            self.auto_btn.config(text="🤖 Auto", bg='#006600')
            self.add_battle_log("🖐️ Manual control enabled - You're back in command")
            # Clear auto status
            for widget in self.actions_frame.winfo_children():
                widget.destroy()
            # Resume manual control - process current turn if it's a player turn
            if (self.battle_state.get("turn_order") and 
                len(self.battle_state["turn_order"]) > 0 and
                self.battle_state["turn_order"][0]["type"] == "player"):
                current_unit = self.battle_state["turn_order"][0]["unit"]
                if current_unit["battle_hp"] > 0:
                    self.process_player_turn(current_unit)
                
    def battle_victory(self):
        """Handle battle victory with enhanced progression rewards and rune farming incentives"""
        self.show_notification("🎉 VICTORY! Battle completed successfully!")
        
        # Store last completed battle data for repeat functionality
        self.last_completed_battle = {
            "type": self.battle_state.get("type"),
            "world_idx": self.battle_state.get("world_idx"),
            "stage_idx": self.battle_state.get("stage_idx"),
            "floor": self.battle_state.get("floor"),
            "boss_data": self.battle_state.get("boss_data"),
            "stage": self.battle_state.get("stage"),
            "trainer_data": self.battle_state.get("trainer_data"),
            "team": self.battle_state["team"].copy()
        }
        
        # Handle different battle types with enhanced rewards
        if self.battle_state.get("type") == "delve":
            # Enhanced delve rewards for progression
            floor = self.battle_state["floor"]
            exp_gain = 75 + (floor * 25)  # Increased from 50 + (floor * 15)
            cash_gain = 200 + (floor * 100)  # Increased from 100 + (floor * 50)
            
            # Delve rune drops - better rewards for higher floors
            if floor >= 5:
                rune_rarity = "Epic" if floor < 15 else "Legendary"
                delve_rune = self.generate_rune(rarity=rune_rarity)
                delve_rune['level'] = min(floor // 3, 15)  # Higher level runes
                self.player_runes.append(delve_rune)
                self.show_notification(f"🎰 Floor {floor} Reward: {delve_rune['name']} ({rune_rarity})!")
            
            # Unlock next floor
            if floor >= self.player_progress.get('dungeon_highest', 1):
                self.player_progress['dungeon_highest'] = floor + 1
                self.show_notification(f"🔓 Delve Floor {floor + 1} unlocked!")
                
        elif self.battle_state.get("type") == "rune_boss":
            # Enhanced rune boss rewards
            boss_data = self.battle_state["boss_data"]
            stage = self.battle_state.get("stage", 1)
            
            exp_gain = (30 + stage * 8) * 15  # Increased rewards
            cash_gain = (30 + stage * 8) * 75
            
            # Enhanced rune generation with guaranteed high-quality drops
            rune_count = 2 + (stage // 3)  # More runes for higher stages
            rune_rarities = []
            
            if stage <= 3:  # Easy stages
                rune_rarities = ["Rare", "Epic"]  # Upgraded from Common/Rare
            elif stage <= 6:  # Medium stages
                rune_rarities = ["Epic", "Epic"]  # Guaranteed Epic
            elif stage <= 9:  # Hard stages
                rune_rarities = ["Epic", "Legendary"]  # Epic + Legendary
            else:  # Nightmare stage 10
                rune_rarities = ["Legendary", "Legendary"]  # Double Legendary
            
            # Add extra runes for higher stages
            while len(rune_rarities) < rune_count:
                if stage <= 6:
                    rune_rarities.append("Epic")
                else:
                    rune_rarities.append("Legendary")
            
            boss_sets = boss_data.get('sets', ['Nightmare', 'Terror'])
            
            for i, rarity in enumerate(rune_rarities):
                chosen_set = boss_sets[i % 2]
                rune_type = random.choice(list(self.rune_types.keys()))
                
                rune = self.generate_rune(rarity, rune_type)
                rune['set'] = chosen_set
                rune['level'] = min(2 + stage, 12)  # Higher starting levels
                
                # Enhanced stat boosts for higher stages
                if stage >= 5:
                    rune['main_value'] = int(rune['main_value'] * 1.4)
                    for substat in rune['substats']:
                        rune['substats'][substat] = int(rune['substats'][substat] * 1.2)
                if stage >= 8:
                    rune['main_value'] = int(rune['main_value'] * 1.2)
                    for substat in rune['substats']:
                        rune['substats'][substat] = int(rune['substats'][substat] * 1.1)
                
                self.player_runes.append(rune)
                
            set_names = " & ".join(boss_sets)
            self.show_notification(f"🎰 Stage {stage} Complete! Obtained {len(rune_rarities)} {set_names} Set Runes!")
            
        elif self.battle_state.get("type") == "xp_trainer":
            # Enhanced XP trainer rewards
            trainer_data = self.battle_state["trainer_data"]
            exp_gain = trainer_data['level'] * 25  # Increased from 15
            cash_gain = trainer_data['level'] * 120  # Increased from 80
            
            # Enhanced XP potion rewards
            if "Novice" in trainer_data['name']:
                self.player_items["Small XP Pot"] += 5  # Increased from 3
                self.show_notification("⭐ Earned 5x Small XP Potions!")
            elif "Veteran" in trainer_data['name']:
                self.player_items["Medium XP Pot"] += 4  # Increased from 2
                self.show_notification("⭐ Earned 4x Medium XP Potions!")
            elif "Elite" in trainer_data['name']:
                self.player_items["Large XP Pot"] += 2  # Increased from 1
                self.show_notification("⭐ Earned 2x Large XP Potions!")
            elif "Grandmaster" in trainer_data['name']:
                self.player_items["Large XP Pot"] += 2
                self.player_items["Medium XP Pot"] += 2
                self.show_notification("⭐ Earned 2x Large + 2x Medium XP Potions!")
                
        else:
            # Enhanced campaign rewards with progression-gated rune drops
            world_idx = self.battle_state["world_idx"]
            stage_idx = self.battle_state["stage_idx"]
            is_boss_stage = (stage_idx + 1) % 10 == 0
            
            # Scaling rewards based on difficulty
            base_exp = 60 + (world_idx * 15) + (stage_idx * 8)  # Increased base rewards
            base_cash = 150 + (world_idx * 30) + (stage_idx * 15)
            
            # Boss stage bonuses
            if is_boss_stage:
                base_exp = int(base_exp * 1.5)
                base_cash = int(base_cash * 1.5)
                
            exp_gain = base_exp
            cash_gain = base_cash
            
            # Rune drops from campaign stages (progression incentive)
            rune_drop_chance = 0.3 + (world_idx * 0.1) + (0.1 if is_boss_stage else 0)  # 30-80% chance
            
            if random.random() < rune_drop_chance:
                # Determine rune rarity based on world progression
                if world_idx == 0:
                    rune_rarity = random.choices(["Common", "Rare"], weights=[60, 40])[0]
                elif world_idx == 1:
                    rune_rarity = random.choices(["Common", "Rare", "Epic"], weights=[40, 50, 10])[0]
                elif world_idx == 2:
                    rune_rarity = random.choices(["Rare", "Epic"], weights=[60, 40])[0]
                elif world_idx == 3:
                    rune_rarity = random.choices(["Rare", "Epic", "Legendary"], weights=[40, 50, 10])[0]
                else:  # World 5
                    rune_rarity = random.choices(["Epic", "Legendary"], weights=[60, 40])[0]
                
                # Boss stages guarantee higher rarity
                if is_boss_stage and world_idx >= 1:
                    if rune_rarity in ["Common", "Rare"]:
                        rune_rarity = "Epic"
                    elif rune_rarity == "Epic" and world_idx >= 3:
                        if random.random() < 0.3:  # 30% chance to upgrade Epic to Legendary
                            rune_rarity = "Legendary"
                
                campaign_rune = self.generate_rune(rarity=rune_rarity)
                campaign_rune['level'] = max(1, world_idx)  # Higher level runes in later worlds
                
                # Slight stat boost for boss stage runes
                if is_boss_stage:
                    campaign_rune['main_value'] = int(campaign_rune['main_value'] * 1.1)
                    for substat in campaign_rune['substats']:
                        campaign_rune['substats'][substat] = int(campaign_rune['substats'][substat] * 1.05)
                
                self.player_runes.append(campaign_rune)
                self.show_notification(f"🎰 Stage Drop: {campaign_rune['name']} ({rune_rarity})!")
            
            # First-time clear gem rewards
            stage_key = f"world_{world_idx}_stage_{stage_idx}"
            cleared_stages = self.player_progress.get("cleared_stages", [])
            if stage_key not in cleared_stages:
                # First time clearing this stage
                if "cleared_stages" not in self.player_progress:
                    self.player_progress["cleared_stages"] = []
                self.player_progress["cleared_stages"].append(stage_key)
                
                # Gem rewards based on difficulty
                gem_reward = 5 + (world_idx * 3) + (stage_idx // 5)  # 5-25 gems based on world/stage
                if is_boss_stage:
                    gem_reward *= 2  # Double gems for boss stages
                
                self.player_gems += gem_reward
                self.show_notification(f"🎉 FIRST CLEAR BONUS: +{gem_reward} gems!")
            
            # Unlock next stage progression
            if stage_idx + 1 < self.STAGES_PER_WORLD:
                self.player_progress["unlocked"][world_idx][stage_idx + 1] = 1
                self.show_notification(f"🔓 Stage {stage_idx + 2} unlocked!")
            elif world_idx + 1 < self.NUM_WORLDS:
                self.player_progress["unlocked"][world_idx + 1][0] = 1
                self.show_notification(f"🔓 World {world_idx + 2} unlocked! New challenges await!")
        
        # Enhanced EXP and cash rewards with improved level-up detection
        level_ups = []
        for unit in self.battle_state["team"]:
            old_level = unit["level"]
            
            # Apply battle efficiency research bonus
            exp_multiplier = 1.25 if self.player_research.get('battle_efficiency', False) else 1.0
            final_exp_gain = int(exp_gain * exp_multiplier)
            unit["exp"] += final_exp_gain
            
            # Enhanced level up calculation
            levels_gained = 0
            while unit["exp"] >= (unit["level"] * 100):
                unit["exp"] -= (unit["level"] * 100)
                unit["level"] += 1
                levels_gained += 1
                
            if levels_gained > 0:
                level_ups.append(f"{unit['entity']['name']}: Lv.{old_level} → Lv.{unit['level']} (+{levels_gained})")
            
        self.player_cash += cash_gain
        
        # Show enhanced reward notifications
        if self.player_research.get('battle_efficiency', False):
            self.show_notification(f"💰 Earned {cash_gain} cash and {int(exp_gain * 1.25)} EXP per unit! (Battle Efficiency +25%)")
        else:
            self.show_notification(f"💰 Earned {cash_gain} cash and {exp_gain} EXP per unit!")
        
        # Show level-up notifications
        if level_ups:
            for level_up in level_ups:
                self.show_notification(f"⭐ {level_up}")
        
        # Update stats
        self.update_stats_display()
        
        # Check if multi-battle is active
        if self.multi_battle_active:
            self.handle_multi_battle_continuation()
        else:
            # Show post-battle options for single battles
            self.show_post_battle_options()
        
    def battle_defeat(self):
        """Handle battle defeat with multi-battle support and post-battle options"""
        self.show_notification("💀 DEFEAT! Your team was defeated...")
        
        # Check if multi-battle is active
        if self.multi_battle_active:
            self.handle_multi_battle_defeat()
        else:
            # Show post-battle options for single battles
            self.show_post_battle_defeat_options()
    
    def handle_multi_battle_defeat(self):
        """Handle defeat in multi-battle mode"""
        self.multi_battle_active = False
        self.add_battle_log("💀 Multi-battle stopped due to defeat. Returning to post-battle options.")
        
        # After a short delay, show defeat options
        self.root.after(3000, self.show_post_battle_defeat_options)
    
    def show_post_battle_defeat_options(self):
        """Show post-battle options after defeat"""
        self.clear_content()
        
        # Title
        title_label = tk.Label(
            self.content_frame,
            text="💀 BATTLE DEFEAT 💀",
            font=self.title_font,
            bg='black',
            fg='#FF6666'
        )
        title_label.pack(pady=30)
        
        # Defeat message
        message_label = tk.Label(
            self.content_frame,
            text="Your team was defeated, but you can try again!\nChoose your next action:",
            font=self.header_font,
            bg='black',
            fg='white',
            justify='center'
        )
        message_label.pack(pady=20)
        
        # Options frame
        options_frame = tk.Frame(self.content_frame, bg='black')
        options_frame.pack(pady=30)
        
        # Retry battle with same team
        retry_btn = tk.Button(
            options_frame,
            text="🔄 Retry Battle\n(Same Team)",
            command=self.retry_last_battle,
            font=self.header_font,
            bg='#CC6600',
            fg='white',
            width=15,
            height=3
        )
        retry_btn.pack(side='left', padx=10)
        
        # Change team and retry
        change_team_btn = tk.Button(
            options_frame,
            text="⚔️ Change Team\n& Retry",
            command=self.change_team_and_retry,
            font=self.header_font,
            bg='#006666',
            fg='white',
            width=15,
            height=3
        )
        change_team_btn.pack(side='left', padx=10)
        
        # Exit to previous screen
        exit_btn = tk.Button(
            options_frame,
            text="🚪 Exit\n(Return)",
            command=self.exit_post_battle,
            font=self.header_font,
            bg='#666666',
            fg='white',
            width=15,
            height=3
        )
        exit_btn.pack(side='left', padx=10)
        
        # Battle info (if available)
        if hasattr(self, 'last_completed_battle') and self.last_completed_battle:
            battle_info = self.get_battle_info_text()
            info_label = tk.Label(
                self.content_frame,
                text=f"📊 Battle: {battle_info}",
                font=self.body_font,
                bg='black',
                fg='#CCCCCC'
            )
            info_label.pack(pady=20)
        
    def retreat_battle(self):
        """Retreat from battle"""
        self.show_notification("🚪 Retreated from battle.")
        self.go_back()
        
    def show_depths_hub(self):
        """Show The Depths hub interface (Grand Summoners style)"""
        self.navigate_to("depths")
        self.clear_content()
        
        # Title
        title_label = tk.Label(
            self.content_frame,
            text="🕳️ THE NIGHTMARE DEPTHS 🕳️",
            font=self.title_font,
            bg='black',
            fg='#CC66FF'
        )
        title_label.pack(pady=20)
        
        # Subtitle
        subtitle_label = tk.Label(
            self.content_frame,
            text="Challenge the depths and claim legendary rewards!",
            font=self.body_font,
            bg='black',
            fg='#CCCCCC'
        )
        subtitle_label.pack(pady=10)
        
        # Depths options
        options_frame = tk.Frame(self.content_frame, bg='black')
        options_frame.pack(pady=30, padx=50, fill='both', expand=True)
        
        for depth_key, depth_info in self.depths_levels.items():
            # Check if unlocked
            unlocked = self.player_level >= depth_info["unlock_level"]
            
            depth_frame = tk.LabelFrame(
                options_frame,
                text=depth_info["name"] + ("" if unlocked else f" [Req: Lv.{depth_info['unlock_level']}]"),
                font=self.header_font,
                bg='#1a1a1a' if unlocked else '#0a0a0a',
                fg=depth_info["color"] if unlocked else '#666666',
                bd=3,
                relief='ridge'
            )
            depth_frame.pack(fill='x', pady=15, padx=20)
            
            # Icon and description
            info_frame = tk.Frame(depth_frame, bg='#1a1a1a' if unlocked else '#0a0a0a')
            info_frame.pack(pady=15, padx=15, fill='x')
            
            icon_label = tk.Label(
                info_frame,
                text=depth_info["icon"],
                font=self.title_font,
                bg='#1a1a1a' if unlocked else '#0a0a0a',
                fg=depth_info["color"] if unlocked else '#666666'
            )
            icon_label.pack(side='left', padx=(0, 15))
            
            desc_frame = tk.Frame(info_frame, bg='#1a1a1a' if unlocked else '#0a0a0a')
            desc_frame.pack(side='left', fill='x', expand=True)
            
            desc_label = tk.Label(
                desc_frame,
                text=depth_info["description"],
                font=self.body_font,
                bg='#1a1a1a' if unlocked else '#0a0a0a',
                fg='white' if unlocked else '#666666',
                justify='left'
            )
            desc_label.pack(anchor='w')
            
            if unlocked:
                # Show current progress/info
                if depth_key == "Endless Delve":
                    progress_text = f"Highest Floor: {self.player_progress.get('dungeon_highest', 1)}"
                elif depth_key == "Rune Sanctums":
                    progress_text = "Boss Battles Available"
                else:
                    progress_text = "Training Available"
                    
                progress_label = tk.Label(
                    desc_frame,
                    text=progress_text,
                    font=self.small_font,
                    bg='#1a1a1a',
                    fg='#CCCCCC',
                    justify='left'
                )
                progress_label.pack(anchor='w', pady=(5, 0))
                
                # Enter button
                enter_btn = tk.Button(
                    depth_frame,
                    text=f"🚪 Enter {depth_info['name']}",
                    command=lambda dk=depth_key: self.enter_depths_area(dk),
                    font=self.body_font,
                    bg='#006666',
                    fg='white',
                    width=20
                )
                enter_btn.pack(pady=10)
            else:
                # Locked message
                locked_label = tk.Label(
                    desc_frame,
                    text=f"Reach Player Level {depth_info['unlock_level']} to unlock",
                    font=self.small_font,
                    bg='#0a0a0a',
                    fg='#666666',
                    justify='left'
                )
                locked_label.pack(anchor='w', pady=(5, 0))
                
    def enter_depths_area(self, depth_key):
        """Enter a specific depths area"""
        if depth_key == "Endless Delve":
            self.show_endless_delve()
        elif depth_key == "Rune Sanctums":
            self.show_rune_sanctums()
        elif depth_key == "XP Training":
            self.show_xp_training()
            
    def show_endless_delve(self):
        """Show Endless Delve interface"""
        self.navigate_to("endless_delve")
        self.clear_content()
        
        # Title
        title_label = tk.Label(
            self.content_frame,
            text="🕳️ ENDLESS DELVE 🕳️",
            font=self.title_font,
            bg='black',
            fg='#FF6666'
        )
        title_label.pack(pady=20)
        
        # Description
        desc_label = tk.Label(
            self.content_frame,
            text="Descend into infinite floors of escalating nightmare...",
            font=self.body_font,
            bg='black',
            fg='#CCCCCC'
        )
        desc_label.pack(pady=10)
        
        # Current progress
        highest = self.player_progress.get('dungeon_highest', 1)
        progress_label = tk.Label(
            self.content_frame,
            text=f"🏆 Highest Floor Cleared: {highest}",
            font=self.header_font,
            bg='black',
            fg='#FFCC66'
        )
        progress_label.pack(pady=10)
        
        # Floor selection
        selection_frame = tk.LabelFrame(
            self.content_frame,
            text="Select Floor",
            font=self.header_font,
            bg='black',
            fg='#66CCFF'
        )
        selection_frame.pack(pady=20, padx=50, fill='x')
        
        floor_var = tk.StringVar(value="1")
        floor_entry = tk.Entry(
            selection_frame,
            textvariable=floor_var,
            font=self.body_font,
            bg='#1a1a1a',
            fg='white',
            width=10,
            justify='center'
        )
        floor_entry.pack(pady=15)
        
        range_label = tk.Label(
            selection_frame,
            text=f"Available floors: 1 - {highest}",
            font=self.small_font,
            bg='black',
            fg='#CCCCCC'
        )
        range_label.pack()
        
        # Start delve button
        start_btn = tk.Button(
            self.content_frame,
            text="⚔️ Start Delve",
            command=lambda: self.start_delve(int(floor_var.get()) if floor_var.get().isdigit() else 1),
            font=self.body_font,
            bg='#006600',
            fg='white',
            width=15
        )
        start_btn.pack(pady=20)
        
    def start_delve(self, floor):
        """Start delve at specified floor"""
        highest = self.player_progress.get('dungeon_highest', 1)
        if floor > highest:
            self.show_notification(f"❌ Floor {floor} is locked! Clear floor {highest} first.")
            return
            
        if floor < 1:
            self.show_notification(f"❌ Invalid floor number. Please enter 1 or higher.")
            return
            
        self.show_notification(f"🕳️ Starting Endless Delve Floor {floor}...")
        # Team selection then launch delve battle
        self.show_team_selection_inline(lambda team: self.launch_delve_battle(floor, team))
        
    def launch_delve_battle(self, floor, team):
        """Launch delve battle"""
        if not team:
            return
            
        # Generate enhanced enemies for delve
        enemies = []
        num_enemies = random.randint(4, 6)
        
        for _ in range(num_enemies):
            base_entity = random.choice(self.entities)
            scale = 1.0 + (floor * 0.15)
            
            enemy = {
                "name": base_entity["name"] + f" [Lv.{floor}]",
                "rarity": base_entity["rarity"],
                "hp": int(base_entity["hp"] * scale),
                "max_hp": int(base_entity["hp"] * scale),
                "attack": int(base_entity["attack"] * scale),
                "defense": int(base_entity["defense"] * scale),
                "speed": int(base_entity["speed"] * scale),
                "skill": base_entity["skill"],
                "crit_rate": base_entity["crit_rate"],
                "crit_damage": base_entity["crit_damage"],
                "accuracy": base_entity["accuracy"],
                "evasion": base_entity["evasion"],
                "sp": 100,
                "effects": []
            }
            enemies.append(enemy)
            
        # Setup battle state for delve
        self.battle_state = {
            "type": "delve",
            "floor": floor,
            "team": team.copy(),
            "enemies": enemies,
            "current_turn": 0,
            "turn_order": [],
            "auto_battle": False
        }
        
        # Initialize units with proper battle stats
        for unit in self.battle_state["team"]:
            final_stats = self.calculate_unit_stats_with_runes(unit)
            unit["battle_stats"] = final_stats
            unit["battle_hp"] = final_stats["hp"]
            unit["max_hp"] = final_stats["hp"]
            unit["sp"] = 100
            unit["effects"] = []
            unit["defending"] = False
            if unit["entity"]["name"] == "Jeff the Killer":
                unit["effects"].append({"type": "ghost", "turns": 99, "stacks": 1, "source": "Go to Sleep"})
                
        # Show battle interface
        self.show_battle_interface()
        
    def show_rune_sanctums(self):
        """Show Rune Sanctums interface with boss stages"""
        self.navigate_to("rune_sanctums")
        self.clear_content()
        
        # Title
        title_label = tk.Label(
            self.content_frame,
            text="🎰 RUNE SANCTUMS 🎰",
            font=self.title_font,
            bg='black',
            fg='#66CCFF'
        )
        title_label.pack(pady=20)
        
        # Description
        desc_label = tk.Label(
            self.content_frame,
            text="Challenge rune bosses across 10 difficulty stages! Higher stages = rarer rune drops!",
            font=self.body_font,
            bg='black',
            fg='#CCCCCC'
        )
        desc_label.pack(pady=10)
        
        # Boss selection
        bosses_frame = tk.Frame(self.content_frame, bg='black')
        bosses_frame.pack(pady=20, padx=20, fill='both', expand=True)
        
        rune_bosses = [
            {
                "name": "The Forge Master",
                "description": "Ancient spirit of weapon crafting",
                "sets": ["Nightmare", "Terror"],
                "set_descriptions": ["4-Set: +25% Attack", "2-Set: +15% Crit Rate"],
                "icon": "⚒️",
                "unlock_level": 10,
                "color": "#FF6666"
            },
            {
                "name": "Guardian Goliath", 
                "description": "Massive armored protector",
                "sets": ["Spectral", "Void"],
                "set_descriptions": ["4-Set: +30% HP", "2-Set: +15% Defense"],
                "icon": "🛡️",
                "unlock_level": 15,
                "color": "#66CCFF"
            },
            {
                "name": "Mystic Oracle",
                "description": "Seer of ancient mysteries",
                "sets": ["Soul", "Destiny"],
                "set_descriptions": ["2-Set: +10% Speed & Accuracy", "4-Set: +20% Crit Damage"],
                "icon": "🔮",
                "unlock_level": 20,
                "color": "#FFCC66"
            },
            {
                "name": "Nightmare Sovereign",
                "description": "Ruler of the deepest horrors",
                "sets": ["Dread", "Chaos"],
                "set_descriptions": ["4-Set: 25% Stun Chance", "2-Set: +20% Debuff Resist"],
                "icon": "👑",
                "unlock_level": 30,
                "color": "#CC66FF"
            }
        ]
        
        for boss in rune_bosses:
            unlocked = self.player_level >= boss['unlock_level']
            
            boss_frame = tk.LabelFrame(
                bosses_frame,
                text=f"{boss['icon']} {boss['name']}" + ("" if unlocked else f" [Req: Lv.{boss['unlock_level']}]"),
                font=self.header_font,
                bg='#1a1a1a' if unlocked else '#0a0a0a',
                fg=boss['color'] if unlocked else '#666666',
                bd=2,
                relief='ridge'
            )
            boss_frame.pack(fill='x', pady=10, padx=10)
            
            # Boss info
            info_frame = tk.Frame(boss_frame, bg='#1a1a1a' if unlocked else '#0a0a0a')
            info_frame.pack(fill='x', padx=10, pady=10)
            
            desc_label = tk.Label(
                info_frame,
                text=boss['description'],
                font=self.body_font,
                bg='#1a1a1a' if unlocked else '#0a0a0a',
                fg='white' if unlocked else '#666666'
            )
            desc_label.pack(anchor='w')
            
            # Set drops info
            sets_text = f"Drops: {boss['sets'][0]} & {boss['sets'][1]} Set Runes\n"
            sets_text += f"• {boss['set_descriptions'][0]}\n"
            sets_text += f"• {boss['set_descriptions'][1]}"
            
            sets_label = tk.Label(
                info_frame,
                text=sets_text,
                font=self.small_font,
                bg='#1a1a1a' if unlocked else '#0a0a0a',
                fg='#FFCC66' if unlocked else '#666666',
                justify='left'
            )
            sets_label.pack(anchor='w', pady=(5, 0))
            
            if unlocked:
                # Stages buttons frame
                stages_frame = tk.Frame(boss_frame, bg='#1a1a1a')
                stages_frame.pack(pady=10)
                
                stages_label = tk.Label(
                    stages_frame,
                    text="Difficulty Stages:",
                    font=self.body_font,
                    bg='#1a1a1a',
                    fg='white'
                )
                stages_label.pack()
                
                # Stage buttons (1-10)
                buttons_frame = tk.Frame(stages_frame, bg='#1a1a1a')
                buttons_frame.pack(pady=5)
                
                for stage in range(1, 11):
                    stage_color = '#006600' if stage <= 3 else '#CC6600' if stage <= 6 else '#CC3300'
                    difficulty = "Easy" if stage <= 3 else "Medium" if stage <= 6 else "Hard" if stage <= 9 else "Nightmare"
                    
                    stage_btn = tk.Button(
                        buttons_frame,
                        text=f"S{stage}",
                        command=lambda b=boss, s=stage: self.challenge_rune_boss_stage(b, s),
                        font=self.small_font,
                        bg=stage_color,
                        fg='white',
                        width=4,
                        height=2
                    )
                    stage_btn.pack(side='left', padx=2)
                    
                    # Tooltip for stage info
                    if stage == 10:
                        stage_btn.config(bg='#660066', text=f"S{stage}★")
                
                # Stage info
                stage_info = tk.Label(
                    stages_frame,
                    text="Stages 1-3: Common/Rare | 4-6: Rare/Epic | 7-9: Epic/Legendary | 10: Legendary Guaranteed",
                    font=('Consolas', 7),
                    bg='#1a1a1a',
                    fg='#CCCCCC'
                )
                stage_info.pack(pady=2)
            else:
                locked_label = tk.Label(
                    boss_frame,
                    text=f"Locked - Reach Player Level {boss['unlock_level']}",
                    font=self.body_font,
                    bg='#0a0a0a',
                    fg='#666666'
                )
                locked_label.pack(pady=15)
        
    def show_xp_training(self):
        """Show XP Training interface"""
        self.navigate_to("xp_training")
        self.clear_content()
        
        # Title
        title_label = tk.Label(
            self.content_frame,
            text="⭐ XP TRAINING GROUNDS ⭐",
            font=self.title_font,
            bg='black',
            fg='#66FF66'
        )
        title_label.pack(pady=20)
        
        # Description
        desc_label = tk.Label(
            self.content_frame,
            text="Battle elite trainers to earn valuable XP potions!",
            font=self.body_font,
            bg='black',
            fg='#CCCCCC'
        )
        desc_label.pack(pady=10)
        
        # Trainer selection
        trainers_frame = tk.Frame(self.content_frame, bg='black')
        trainers_frame.pack(pady=20, padx=50, fill='both', expand=True)
        
        xp_trainers = [
            {
                "name": "Novice Instructor",
                "level": 15,
                "description": "Teaches basic combat techniques",
                "rewards": "3x Small XP Potions",
                "icon": "🥉",
                "unlock_level": 5
            },
            {
                "name": "Veteran Sergeant",
                "level": 25,
                "description": "Experienced military trainer",
                "rewards": "2x Medium XP Potions",
                "icon": "🥈",
                "unlock_level": 10
            },
            {
                "name": "Elite Commander",
                "level": 40,
                "description": "Master of advanced warfare",
                "rewards": "1x Large XP Potion",
                "icon": "🥇",
                "unlock_level": 20
            },
            {
                "name": "Grandmaster Sensei",
                "level": 60,
                "description": "Legendary training master",
                "rewards": "1x Large + 1x Medium XP Potion",
                "icon": "🏆",
                "unlock_level": 35
            }
        ]
        
        for trainer in xp_trainers:
            unlocked = self.player_level >= trainer['unlock_level']
            
            trainer_frame = tk.LabelFrame(
                trainers_frame,
                text=f"{trainer['icon']} {trainer['name']} (Lv.{trainer['level']})" + ("" if unlocked else f" [Req: Lv.{trainer['unlock_level']}]"),
                font=self.header_font,
                bg='#1a1a1a' if unlocked else '#0a0a0a',
                fg='#66FF66' if unlocked else '#666666',
                bd=2,
                relief='ridge'
            )
            trainer_frame.pack(fill='x', pady=10, padx=10)
            
            desc_label = tk.Label(
                trainer_frame,
                text=trainer['description'],
                font=self.body_font,
                bg='#1a1a1a' if unlocked else '#0a0a0a',
                fg='white' if unlocked else '#666666'
            )
            desc_label.pack(pady=5)
            
            rewards_label = tk.Label(
                trainer_frame,
                text=f"Rewards: {trainer['rewards']}",
                font=self.small_font,
                bg='#1a1a1a' if unlocked else '#0a0a0a',
                fg='#FFCC66' if unlocked else '#666666'
            )
            rewards_label.pack(pady=2)
            
            if unlocked:
                battle_btn = tk.Button(
                    trainer_frame,
                    text="⚔️ Battle Trainer",
                    command=lambda t=trainer: self.battle_xp_trainer(t),
                    font=self.body_font,
                    bg='#006600',
                    fg='white'
                )
                battle_btn.pack(pady=10)
            else:
                locked_label = tk.Label(
                    trainer_frame,
                    text=f"Locked - Reach Player Level {trainer['unlock_level']}",
                    font=self.small_font,
                    bg='#0a0a0a',
                    fg='#666666'
                )
                locked_label.pack(pady=10)
        
    def show_facility_hub(self):
        """Show facility hub interface"""
        self.navigate_to("facility_hub")
        self.clear_content()
        
        # Title
        title_label = tk.Label(
            self.content_frame,
            text="🏭 FACILITY HUB 🏭",
            font=self.title_font,
            bg='black',
            fg='#66FFCC'
        )
        title_label.pack(pady=20)
        
        # Subtitle
        subtitle_label = tk.Label(
            self.content_frame,
            text="Manage your base facilities and unlock new features",
            font=self.body_font,
            bg='black',
            fg='#CCCCCC'
        )
        subtitle_label.pack(pady=10)
        
        # Facilities grid
        facilities_frame = tk.Frame(self.content_frame, bg='black')
        facilities_frame.pack(pady=30, padx=50, fill='both', expand=True)
        
        facilities = [
            {
                "name": "Research Lab",
                "icon": "🧪",
                "description": "Research new technologies and unit enhancements",
                "level": self.player_facilities.get('research_lab', 1),
                "max_level": 10,
                "upgrade_cost": 5000 * self.player_facilities.get('research_lab', 1),
                "function": self.show_research_lab
            },
            {
                "name": "Training Grounds",
                "icon": "⚔️",
                "description": "Train units to gain experience and level up",
                "level": self.player_facilities.get('training_grounds', 1),
                "max_level": 15,
                "upgrade_cost": 3000 * self.player_facilities.get('training_grounds', 1),
                "function": self.show_training_grounds
            },
            {
                "name": "Rune Forge",
                "icon": "⚒️",
                "description": "Craft and enhance runes with special materials",
                "level": self.player_facilities.get('rune_forge', 1),
                "max_level": 12,
                "upgrade_cost": 8000 * self.player_facilities.get('rune_forge', 1),
                "function": self.show_rune_forge
            },
            {
                "name": "Nightmare Nexus Core",
                "icon": "🌀",
                "description": "Central power source that boosts all other facilities",
                "level": self.player_facilities.get('nexus_core', 1),
                "max_level": 5,
                "upgrade_cost": 15000 * self.player_facilities.get('nexus_core', 1),
                "function": self.show_nexus_core
            },
            {
                "name": "Bank Vault",
                "icon": "🏦",
                "description": "Generate passive cash income over time",
                "level": self.player_facilities.get('bank_vault', 1),
                "max_level": 8,
                "upgrade_cost": 4000 * self.player_facilities.get('bank_vault', 1),
                "function": self.show_bank_vault
            },
            {
                "name": "Gem Mine",
                "icon": "💎",
                "description": "Generate passive gem income over time",
                "level": self.player_facilities.get('gem_mine', 1),
                "max_level": 6,
                "upgrade_cost": 10000 * self.player_facilities.get('gem_mine', 1),
                "function": self.show_gem_mine
            }
        ]
        
        for i, facility in enumerate(facilities):
            row = i // 2
            col = i % 2
            
            facility_frame = tk.LabelFrame(
                facilities_frame,
                text=f"{facility['icon']} {facility['name']} (Lv.{facility['level']})",
                font=self.header_font,
                bg='#1a1a1a',
                fg='#66CCFF',
                bd=2,
                relief='ridge'
            )
            facility_frame.grid(row=row, column=col, padx=20, pady=15, sticky='nsew')
            
            # Description
            desc_label = tk.Label(
                facility_frame,
                text=facility['description'],
                font=self.body_font,
                bg='#1a1a1a',
                fg='white',
                wraplength=250,
                justify='left'
            )
            desc_label.pack(pady=10, padx=10)
            
            # Level progress
            progress_text = f"Level: {facility['level']}/{facility['max_level']}"
            progress_label = tk.Label(
                facility_frame,
                text=progress_text,
                font=self.small_font,
                bg='#1a1a1a',
                fg='#FFCC66'
            )
            progress_label.pack()
            
            # Buttons frame
            btn_frame = tk.Frame(facility_frame, bg='#1a1a1a')
            btn_frame.pack(pady=15)
            
            # Enter facility button
            enter_btn = tk.Button(
                btn_frame,
                text="🚪 Enter",
                command=facility['function'],
                font=self.body_font,
                bg='#006600',
                fg='white',
                width=8
            )
            enter_btn.pack(side='left', padx=5)
            
            # Upgrade button
            if facility['level'] < facility['max_level']:
                upgrade_btn = tk.Button(
                    btn_frame,
                    text=f"⬆️ Upgrade\n({facility['upgrade_cost']} 🪙)",
                    command=lambda f=facility: self.upgrade_facility(f),
                    font=self.small_font,
                    bg='#CC6600',
                    fg='white',
                    width=10
                )
                upgrade_btn.pack(side='left', padx=5)
            else:
                max_label = tk.Label(
                    btn_frame,
                    text="MAX LEVEL",
                    font=self.small_font,
                    bg='#1a1a1a',
                    fg='#FFD700'
                )
                max_label.pack(side='left', padx=5)
                
        # Configure grid weights
        for col in range(2):
            facilities_frame.grid_columnconfigure(col, weight=1)
            
    def upgrade_facility(self, facility):
        """Upgrade a facility"""
        if self.player_cash < facility['upgrade_cost']:
            self.show_notification(f"❌ Need {facility['upgrade_cost']} cash to upgrade {facility['name']}!", '#FF6666')
            return
            
        if facility['level'] >= facility['max_level']:
            self.show_notification(f"⚠️ {facility['name']} is already at maximum level!", '#FF6666')
            return
            
        self.player_cash -= facility['upgrade_cost']
        facility_key = facility['name'].lower().replace(' ', '_').replace('nightmare_nexus_', '')
        
        if facility_key not in self.player_facilities:
            self.player_facilities[facility_key] = 1
        self.player_facilities[facility_key] += 1
        
        self.show_notification(f"✨ {facility['name']} upgraded to Level {self.player_facilities[facility_key]}!")
        self.update_stats_display()
        self.show_facility_hub()  # Refresh display
        
    def show_research_lab(self):
        """Show research lab interface"""
        self.clear_content()
        
        title_label = tk.Label(
            self.content_frame,
            text="🧪 RESEARCH LAB 🧪",
            font=self.title_font,
            bg='black',
            fg='#66CCFF'
        )
        title_label.pack(pady=20)
        
        level = self.player_facilities.get('research_lab', 1)
        info_label = tk.Label(
            self.content_frame,
            text=f"Research Lab Level {level} - Advanced technological research",
            font=self.body_font,
            bg='black',
            fg='white'
        )
        info_label.pack(pady=10)
        
        # Research projects
        projects_frame = tk.LabelFrame(
            self.content_frame,
            text="Available Research Projects",
            font=self.header_font,
            bg='black',
            fg='#CCCCCC'
        )
        projects_frame.pack(fill='both', expand=True, padx=50, pady=20)
        
        research_projects = [
            {
                "name": "Enhanced Summoning",
                "cost": 10000,
                "description": "Increases legendary summon rates by 2%",
                "completed": self.player_research.get('enhanced_summoning', False),
                "requirement": 3
            },
            {
                "name": "Battle Efficiency",
                "cost": 15000,
                "description": "Units gain 25% more EXP from battles",
                "completed": self.player_research.get('battle_efficiency', False),
                "requirement": 5
            },
            {
                "name": "Rune Mastery",
                "cost": 20000,
                "description": "Rune upgrade costs reduced by 30%",
                "completed": self.player_research.get('rune_mastery', False),
                "requirement": 7
            },
            {
                "name": "Nightmare Amplification",
                "cost": 25000,
                "description": "All units gain +10% to all stats",
                "completed": self.player_research.get('nightmare_amplification', False),
                "requirement": 10
            }
        ]
        
        for project in research_projects:
            can_research = level >= project['requirement'] and not project['completed']
            
            project_frame = tk.LabelFrame(
                projects_frame,
                text=project['name'],
                font=self.body_font,
                bg='#1a1a1a',
                fg='#66FF66' if project['completed'] else '#FFCC66' if can_research else '#666666'
            )
            project_frame.pack(fill='x', padx=20, pady=10)
            
            desc_label = tk.Label(
                project_frame,
                text=project['description'],
                font=self.body_font,
                bg='#1a1a1a',
                fg='white'
            )
            desc_label.pack(pady=5)
            
            if project['completed']:
                status_label = tk.Label(
                    project_frame,
                    text="✅ COMPLETED",
                    font=self.body_font,
                    bg='#1a1a1a',
                    fg='#66FF66'
                )
                status_label.pack(pady=5)
            elif can_research:
                research_btn = tk.Button(
                    project_frame,
                    text=f"🔬 Research ({project['cost']} 🪙)",
                    command=lambda p=project: self.start_research(p),
                    font=self.body_font,
                    bg='#006600',
                    fg='white'
                )
                research_btn.pack(pady=5)
            else:
                req_label = tk.Label(
                    project_frame,
                    text=f"❌ Requires Research Lab Level {project['requirement']}",
                    font=self.body_font,
                    bg='#1a1a1a',
                    fg='#666666'
                )
                req_label.pack(pady=5)
                
    def start_research(self, project):
        """Start a research project"""
        if self.player_cash < project['cost']:
            self.show_notification(f"❌ Need {project['cost']} cash to research {project['name']}!", '#FF6666')
            return
            
        self.player_cash -= project['cost']
        project_key = project['name'].lower().replace(' ', '_')
        self.player_research[project_key] = True
        
        self.show_notification(f"🔬 {project['name']} research completed!")
        self.update_stats_display()
        self.show_research_lab()  # Refresh display
        
    def show_training_grounds(self):
        """Show training grounds interface"""
        self.clear_content()
        
        title_label = tk.Label(
            self.content_frame,
            text="⚔️ TRAINING GROUNDS ⚔️",
            font=self.title_font,
            bg='black',
            fg='#FF6666'
        )
        title_label.pack(pady=20)
        
        level = self.player_facilities.get('training_grounds', 1)
        multiplier = 1 + (level * 0.2)
        
        info_label = tk.Label(
            self.content_frame,
            text=f"Training Grounds Level {level} - EXP Multiplier: {multiplier:.1f}x",
            font=self.body_font,
            bg='black',
            fg='white'
        )
        info_label.pack(pady=10)
        
        # Training options
        training_frame = tk.LabelFrame(
            self.content_frame,
            text="Training Programs",
            font=self.header_font,
            bg='black',
            fg='#CCCCCC'
        )
        training_frame.pack(fill='both', expand=True, padx=50, pady=20)
        
        training_options = [
            {"name": "Basic Training", "cost": 500, "exp": int(100 * multiplier), "time": "Instant"},
            {"name": "Intensive Training", "cost": 1500, "exp": int(350 * multiplier), "time": "Instant"},
            {"name": "Elite Training", "cost": 3000, "exp": int(750 * multiplier), "time": "Instant"},
            {"name": "Nightmare Boot Camp", "cost": 5000, "exp": int(1500 * multiplier), "time": "Instant"},
        ]
        
        for option in training_options:
            option_frame = tk.LabelFrame(
                training_frame,
                text=option['name'],
                font=self.body_font,
                bg='#1a1a1a',
                fg='#FFCC66'
            )
            option_frame.pack(fill='x', padx=20, pady=10)
            
            info_text = f"Cost: {option['cost']} 🪙 | EXP Gain: {option['exp']} | Duration: {option['time']}"
            info_label = tk.Label(
                option_frame,
                text=info_text,
                font=self.body_font,
                bg='#1a1a1a',
                fg='white'
            )
            info_label.pack(pady=5)
            
            train_btn = tk.Button(
                option_frame,
                text="💪 Start Training",
                command=lambda o=option: self.start_training(o),
                font=self.body_font,
                bg='#006600',
                fg='white'
            )
            train_btn.pack(pady=5)
            
    def start_training(self, option):
        """Start training for selected units"""
        if self.player_cash < option['cost']:
            self.show_notification(f"❌ Need {option['cost']} cash for {option['name']}!", '#FF6666')
            return
            
        # Show unit selection for training
        self.show_training_unit_selection(option)
        
    def show_training_unit_selection(self, training_option):
        """Show unit selection for training"""
        self.clear_content()
        
        title_label = tk.Label(
            self.content_frame,
            text=f"💪 {training_option['name'].upper()} 💪",
            font=self.title_font,
            bg='black',
            fg='#FF6666'
        )
        title_label.pack(pady=20)
        
        info_label = tk.Label(
            self.content_frame,
            text=f"Select units to train (Cost: {training_option['cost']} per unit | EXP: {training_option['exp']})",
            font=self.body_font,
            bg='black',
            fg='white'
        )
        info_label.pack(pady=10)
        
        # Selected units display
        selected_frame = tk.LabelFrame(
            self.content_frame,
            text="Selected for Training",
            font=self.header_font,
            bg='black',
            fg='#66FF66'
        )
        selected_frame.pack(fill='x', pady=20, padx=20)
        
        self.training_selected_frame = tk.Frame(selected_frame, bg='black')
        self.training_selected_frame.pack(fill='x', padx=10, pady=10)
        
        self.training_selected_units = []
        
        # Available units
        units_frame = tk.LabelFrame(
            self.content_frame,
            text="Available Units",
            font=self.header_font,
            bg='black',
            fg='#CCCCCC'
        )
        units_frame.pack(fill='both', expand=True, pady=20, padx=20)
        
        # Scrollable units display
        canvas = tk.Canvas(units_frame, bg='black', highlightthickness=0)
        scrollbar = ttk.Scrollbar(units_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='black')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Display units
        for i, unit in enumerate(self.player_inventory):
            row = i // 4
            col = i % 4
            
            unit_btn = tk.Button(
                scrollable_frame,
                text=f"{unit['entity']['name']}\nLv.{unit['level']}",
                command=lambda idx=i: self.toggle_training_unit_selection(idx),
                font=self.body_font,
                bg=self.rarity_colors[unit['entity']['rarity']],
                fg='black' if unit['entity']['rarity'] in ['Common', 'Rare'] else 'white',
                width=15,
                height=3,
                relief='raised',
                bd=3
            )
            unit_btn.grid(row=row, column=col, padx=5, pady=5)
            
        # Configure grid
        for col in range(4):
            scrollable_frame.grid_columnconfigure(col, weight=1)
            
        # Bottom buttons
        btn_frame = tk.Frame(self.content_frame, bg='black')
        btn_frame.pack(pady=20)
        
        self.train_confirm_btn = tk.Button(
            btn_frame,
            text="💪 Start Training",
            command=lambda: self.execute_training(training_option),
            font=self.body_font,
            bg='#006600',
            fg='white',
            state='disabled'
        )
        self.train_confirm_btn.pack(side='left', padx=10)
        
        back_btn = tk.Button(
            btn_frame,
            text="🔙 Back",
            command=self.show_training_grounds,
            font=self.body_font,
            bg='#666666',
            fg='white'
        )
        back_btn.pack(side='left', padx=10)
        
        self.update_training_selection_display()
        
    def toggle_training_unit_selection(self, unit_idx):
        """Toggle unit selection for training"""
        unit = self.player_inventory[unit_idx]
        
        if unit in self.training_selected_units:
            self.training_selected_units.remove(unit)
        else:
            self.training_selected_units.append(unit)
            
        self.update_training_selection_display()
        
    def update_training_selection_display(self):
        """Update the training selection display"""
        # Clear existing display
        for widget in self.training_selected_frame.winfo_children():
            widget.destroy()
            
        if not self.training_selected_units:
            empty_label = tk.Label(
                self.training_selected_frame,
                text="No units selected",
                font=self.body_font,
                bg='black',
                fg='#666666'
            )
            empty_label.pack()
            self.train_confirm_btn.config(state='disabled')
        else:
            for unit in self.training_selected_units:
                unit_label = tk.Label(
                    self.training_selected_frame,
                    text=f"{unit['entity']['name']} (Lv.{unit['level']})",
                    font=self.body_font,
                    bg='black',
                    fg=self.rarity_colors[unit['entity']['rarity']]
                )
                unit_label.pack(side='left', padx=10)
                
            self.train_confirm_btn.config(state='normal')
            
    def execute_training(self, option):
        """Execute the training for selected units"""
        if not self.training_selected_units:
            return
            
        total_cost = option['cost'] * len(self.training_selected_units)
        
        if self.player_cash < total_cost:
            self.show_notification(f"❌ Need {total_cost} cash to train {len(self.training_selected_units)} units!", '#FF6666')
            return
            
        self.player_cash -= total_cost
        
        # Apply training
        for unit in self.training_selected_units:
            unit['exp'] += option['exp']
            # Level up check (simplified)
            while unit['exp'] >= (unit['level'] * 100):
                unit['exp'] -= (unit['level'] * 100)
                unit['level'] += 1
                
        self.show_notification(f"💪 Training completed! {len(self.training_selected_units)} units gained {option['exp']} EXP each!")
        self.update_stats_display()
        self.show_training_grounds()
        
    def show_rune_forge(self):
        """Show rune forge interface"""
        self.clear_content()
        
        title_label = tk.Label(
            self.content_frame,
            text="⚒️ RUNE FORGE ⚒️",
            font=self.title_font,
            bg='black',
            fg='#CC66FF'
        )
        title_label.pack(pady=20)
        
        level = self.player_facilities.get('rune_forge', 1)
        info_label = tk.Label(
            self.content_frame,
            text=f"Rune Forge Level {level} - Craft and enhance magical runes",
            font=self.body_font,
            bg='black',
            fg='white'
        )
        info_label.pack(pady=10)
        
        # Forge options
        forge_frame = tk.LabelFrame(
            self.content_frame,
            text="Forge Services",
            font=self.header_font,
            bg='black',
            fg='#CCCCCC'
        )
        forge_frame.pack(fill='both', expand=True, padx=50, pady=20)
        
        services = [
            {"name": "Craft Common Rune", "cost": 1000, "type": "Common"},
            {"name": "Craft Rare Rune", "cost": 3000, "type": "Rare", "min_level": 3},
            {"name": "Craft Epic Rune", "cost": 8000, "type": "Epic", "min_level": 6},
            {"name": "Craft Legendary Rune", "cost": 20000, "type": "Legendary", "min_level": 10},
        ]
        
        for service in services:
            can_use = level >= service.get('min_level', 1)
            
            service_frame = tk.LabelFrame(
                forge_frame,
                text=service['name'],
                font=self.body_font,
                bg='#1a1a1a',
                fg=self.rarity_colors[service['type']] if can_use else '#666666'
            )
            service_frame.pack(fill='x', padx=20, pady=10)
            
            cost_label = tk.Label(
                service_frame,
                text=f"Cost: {service['cost']} 🪙",
                font=self.body_font,
                bg='#1a1a1a',
                fg='white' if can_use else '#666666'
            )
            cost_label.pack(pady=5)
            
            if can_use:
                craft_btn = tk.Button(
                    service_frame,
                    text="⚒️ Craft Rune",
                    command=lambda s=service: self.craft_rune(s),
                    font=self.body_font,
                    bg='#006600',
                    fg='white'
                )
                craft_btn.pack(pady=5)
            else:
                req_label = tk.Label(
                    service_frame,
                    text=f"❌ Requires Rune Forge Level {service.get('min_level', 1)}",
                    font=self.body_font,
                    bg='#1a1a1a',
                    fg='#666666'
                )
                req_label.pack(pady=5)
                
    def craft_rune(self, service):
        """Craft a rune at the forge"""
        if self.player_cash < service['cost']:
            self.show_notification(f"❌ Need {service['cost']} cash to craft {service['type']} rune!", '#FF6666')
            return
            
        self.player_cash -= service['cost']
        
        # Generate a new rune
        new_rune = self.generate_rune(service['type'])
        self.player_runes.append(new_rune)
        
        self.show_notification(f"⚒️ Crafted {new_rune['name']} ({service['type']})!")
        self.update_stats_display()
        
    def show_nexus_core(self):
        """Show nexus core interface"""
        self.clear_content()
        
        title_label = tk.Label(
            self.content_frame,
            text="🌀 NIGHTMARE NEXUS CORE 🌀",
            font=self.title_font,
            bg='black',
            fg='#FF3333'
        )
        title_label.pack(pady=20)
        
        level = self.player_facilities.get('nexus_core', 1)
        bonus = level * 10
        
        info_label = tk.Label(
            self.content_frame,
            text=f"Core Level {level} - Global Efficiency Bonus: +{bonus}%",
            font=self.body_font,
            bg='black',
            fg='white'
        )
        info_label.pack(pady=10)
        
        # Core effects
        effects_frame = tk.LabelFrame(
            self.content_frame,
            text="Active Core Effects",
            font=self.header_font,
            bg='black',
            fg='#FF3333'
        )
        effects_frame.pack(fill='both', expand=True, padx=50, pady=20)
        
        effects = [
            f"🏭 All facility operations {bonus}% more efficient",
            f"⚔️ Battle rewards increased by {bonus}%",
            f"💎 Summon rates improved by {level * 2}%",
            f"🎰 Rune drop quality increased by {level * 5}%",
            f"💰 Passive income generation increased by {bonus}%"
        ]
        
        for effect in effects:
            effect_label = tk.Label(
                effects_frame,
                text=effect,
                font=self.body_font,
                bg='black',
                fg='#FFCC66',
                justify='left'
            )
            effect_label.pack(anchor='w', padx=20, pady=5)
            
        # Core status
        status_label = tk.Label(
            effects_frame,
            text="🌀 Nexus Core is operating at maximum efficiency",
            font=self.header_font,
            bg='black',
            fg='#66FF66'
        )
        status_label.pack(pady=20)
        
    def show_bank_vault(self):
        """Show bank vault interface"""
        self.clear_content()
        
        title_label = tk.Label(
            self.content_frame,
            text="🏦 BANK VAULT 🏦",
            font=self.title_font,
            bg='black',
            fg='#FFCC66'
        )
        title_label.pack(pady=20)
        
        level = self.player_facilities.get('bank_vault', 1)
        income_rate = level * 100
        
        info_label = tk.Label(
            self.content_frame,
            text=f"Bank Vault Level {level} - Passive Income: {income_rate} 🪙/hour",
            font=self.body_font,
            bg='black',
            fg='white'
        )
        info_label.pack(pady=10)
        
        # Collect earnings
        earnings_frame = tk.LabelFrame(
            self.content_frame,
            text="Earnings Collection",
            font=self.header_font,
            bg='black',
            fg='#FFCC66'
        )
        earnings_frame.pack(fill='x', padx=50, pady=20)
        
        # Calculate available earnings (simplified)
        available_earnings = income_rate * 24  # 24 hours worth
        
        earnings_label = tk.Label(
            earnings_frame,
            text=f"Available Earnings: {available_earnings} 🪙",
            font=self.header_font,
            bg='black',
            fg='#66FF66'
        )
        earnings_label.pack(pady=10)
        
        collect_btn = tk.Button(
            earnings_frame,
            text="💰 Collect All Earnings",
            command=lambda: self.collect_vault_earnings(available_earnings),
            font=self.body_font,
            bg='#006600',
            fg='white'
        )
        collect_btn.pack(pady=10)
        
        # Investment options
        invest_frame = tk.LabelFrame(
            self.content_frame,
            text="Investment Options",
            font=self.header_font,
            bg='black',
            fg='#CCCCCC'
        )
        invest_frame.pack(fill='both', expand=True, padx=50, pady=20)
        
        investments = [
            {"name": "Short Term Bond", "cost": 5000, "return": 6000, "time": "1 day"},
            {"name": "Medium Term Fund", "cost": 15000, "return": 20000, "time": "3 days"},
            {"name": "Long Term Securities", "cost": 50000, "return": 75000, "time": "7 days"},
        ]
        
        for investment in investments:
            invest_frame_item = tk.LabelFrame(
                invest_frame,
                text=investment['name'],
                font=self.body_font,
                bg='#1a1a1a',
                fg='#FFCC66'
            )
            invest_frame_item.pack(fill='x', padx=20, pady=10)
            
            invest_info = tk.Label(
                invest_frame_item,
                text=f"Invest: {investment['cost']} 🪙 → Return: {investment['return']} 🪙 ({investment['time']})",
                font=self.body_font,
                bg='#1a1a1a',
                fg='white'
            )
            invest_info.pack(pady=5)
            
            invest_btn = tk.Button(
                invest_frame_item,
                text="📈 Invest",
                command=lambda i=investment: self.make_investment(i),
                font=self.body_font,
                bg='#006600',
                fg='white'
            )
            invest_btn.pack(pady=5)
            
    def collect_vault_earnings(self, amount):
        """Collect earnings from bank vault"""
        self.player_cash += amount
        self.show_notification(f"💰 Collected {amount} cash from bank vault!")
        self.update_stats_display()
        
    def make_investment(self, investment):
        """Make an investment"""
        if self.player_cash < investment['cost']:
            self.show_notification(f"❌ Need {investment['cost']} cash to invest in {investment['name']}!", '#FF6666')
            return
            
        self.player_cash -= investment['cost']
        # Simplified - immediate return for demo
        self.player_cash += investment['return']
        
        self.show_notification(f"📈 Investment in {investment['name']} completed! Earned {investment['return'] - investment['cost']} profit!")
        self.update_stats_display()
        
    def show_gem_mine(self):
        """Show gem mine interface"""
        self.clear_content()
        
        title_label = tk.Label(
            self.content_frame,
            text="💎 GEM MINE 💎",
            font=self.title_font,
            bg='black',
            fg='#66CCFF'
        )
        title_label.pack(pady=20)
        
        level = self.player_facilities.get('gem_mine', 1)
        income_rate = level * 5
        
        info_label = tk.Label(
            self.content_frame,
            text=f"Gem Mine Level {level} - Passive Income: {income_rate} 💎/hour",
            font=self.body_font,
            bg='black',
            fg='white'
        )
        info_label.pack(pady=10)
        
        # Mining operations
        mining_frame = tk.LabelFrame(
            self.content_frame,
            text="Mining Operations",
            font=self.header_font,
            bg='black',
            fg='#66CCFF'
        )
        mining_frame.pack(fill='both', expand=True, padx=50, pady=20)
        
        # Available gems to collect
        available_gems = income_rate * 12  # 12 hours worth
        
        gems_label = tk.Label(
            mining_frame,
            text=f"💎 Available Gems: {available_gems}",
            font=self.header_font,
            bg='black',
            fg='#66CCFF'
        )
        gems_label.pack(pady=10)
        
        collect_gems_btn = tk.Button(
            mining_frame,
            text="💎 Collect Gems",
            command=lambda: self.collect_gems(available_gems),
            font=self.body_font,
            bg='#006600',
            fg='white'
        )
        collect_gems_btn.pack(pady=10)
        
        # Mining expeditions
        expeditions = [
            {"name": "Surface Mining", "cost": 1000, "gems": 50, "time": "Instant"},
            {"name": "Deep Excavation", "cost": 3000, "gems": 180, "time": "Instant"},
            {"name": "Nightmare Vein Extraction", "cost": 8000, "gems": 500, "time": "Instant"},
        ]
        
        for expedition in expeditions:
            exp_frame = tk.LabelFrame(
                mining_frame,
                text=expedition['name'],
                font=self.body_font,
                bg='#1a1a1a',
                fg='#66CCFF'
            )
            exp_frame.pack(fill='x', padx=20, pady=10)
            
            exp_info = tk.Label(
                exp_frame,
                text=f"Cost: {expedition['cost']} 🪙 | Yield: {expedition['gems']} 💎 | Duration: {expedition['time']}",
                font=self.body_font,
                bg='#1a1a1a',
                fg='white'
            )
            exp_info.pack(pady=5)
            
            exp_btn = tk.Button(
                exp_frame,
                text="⛏️ Start Expedition",
                command=lambda e=expedition: self.start_mining_expedition(e),
                font=self.body_font,
                bg='#006600',
                fg='white'
            )
            exp_btn.pack(pady=5)
            
    def collect_gems(self, amount):
        """Collect gems from mine"""
        self.player_gems += amount
        self.show_notification(f"💎 Collected {amount} gems from mine!")
        self.update_stats_display()
        
    def start_mining_expedition(self, expedition):
        """Start a mining expedition"""
        if self.player_cash < expedition['cost']:
            self.show_notification(f"❌ Need {expedition['cost']} cash for {expedition['name']}!", '#FF6666')
            return
            
        self.player_cash -= expedition['cost']
        self.player_gems += expedition['gems']
        
        self.show_notification(f"⛏️ {expedition['name']} completed! Mined {expedition['gems']} gems!")
        self.update_stats_display()
        
    def show_rune_management(self):
        """Show rune management interface for selling and upgrading"""
        self.navigate_to("rune_management")
        self.clear_content()

        title_label = tk.Label(self.content_frame, text="🎰 RUNE MANAGEMENT 🎰", font=self.title_font, bg='black', fg='#CC66FF')
        title_label.pack(pady=20)

        # Filter and sort controls
        controls_frame = tk.Frame(self.content_frame, bg='black')
        controls_frame.pack(fill='x', padx=20, pady=10)
        
        # Sort dropdown
        sort_label = tk.Label(controls_frame, text="Sort by:", font=self.body_font, bg='black', fg='white')
        sort_label.pack(side='left', padx=5)
        
        self.rune_sort_var = tk.StringVar(value="name")
        sort_menu = ttk.Combobox(controls_frame, textvariable=self.rune_sort_var, 
                                values=["name", "rarity", "type", "level"], state="readonly", width=10)
        sort_menu.pack(side='left', padx=5)
        sort_menu.bind("<<ComboboxSelected>>", lambda e: self.refresh_rune_display())
        
        # Filter by rarity
        filter_label = tk.Label(controls_frame, text="Filter:", font=self.body_font, bg='black', fg='white')
        filter_label.pack(side='left', padx=(20, 5))
        
        self.rune_filter_var = tk.StringVar(value="All")
        filter_menu = ttk.Combobox(controls_frame, textvariable=self.rune_filter_var,
                                  values=["All", "Common", "Rare", "Epic", "Legendary"], state="readonly", width=10)
        filter_menu.pack(side='left', padx=5)
        filter_menu.bind("<<ComboboxSelected>>", lambda e: self.refresh_rune_display())
        
        # Total runes count
        self.rune_count_label = tk.Label(controls_frame, text="", font=self.body_font, bg='black', fg='#CCCCCC')
        self.rune_count_label.pack(side='right', padx=10)

        # Display runes in grid with scrolling
        self.runes_display_frame = tk.Frame(self.content_frame, bg='black')
        self.runes_display_frame.pack(fill='both', expand=True, padx=20, pady=20)

        self.refresh_rune_display()
        
    def refresh_rune_display(self):
        """Refresh the rune display with current filters and sorting"""
        # Clear existing display
        for widget in self.runes_display_frame.winfo_children():
            widget.destroy()
            
        # Get filtered and sorted runes
        filtered_runes = self.get_filtered_runes()
        
        # Update count
        self.rune_count_label.config(text=f"Showing {len(filtered_runes)} runes")
        
        if not filtered_runes:
            no_runes_label = tk.Label(self.runes_display_frame, text="No runes match the current filter", 
                                     font=self.body_font, bg='black', fg='#666666')
            no_runes_label.pack(pady=50)
            return
            
        canvas = tk.Canvas(self.runes_display_frame, bg='black', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.runes_display_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='black')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Display each rune
        for i, rune in enumerate(filtered_runes):
            rune_frame = tk.LabelFrame(scrollable_frame, text=f"{rune['name']} (Lv.{rune['level']})", font=self.body_font,
                                       bg='#1a1a1a', fg=self.rarity_colors[rune['rarity']], bd=2, relief='ridge')
            rune_frame.grid(row=i // 3, column=i % 3, padx=10, pady=10, sticky='nsew')

            info_text = f"Type: {rune['type']} {self.rune_types[rune['type']]['icon']}\nRarity: {rune['rarity']}\nMain Stat: {rune['main_stat']} +{rune['main_value']}\nSubstats:\n"
            for substat, val in rune['substats'].items():
                info_text += f"  • {substat}: +{val}\n"
                
            # Equipment status
            if rune['equipped_unit'] is not None:
                unit_name = self.player_inventory[rune['equipped_unit']]['entity']['name']
                info_text += f"\nEquipped on: {unit_name}"

            info_label = tk.Label(rune_frame, text=info_text, font=self.small_font, bg='#1a1a1a', fg='white', justify='left')
            info_label.pack(padx=5, pady=5)

            # Action buttons
            btn_frame = tk.Frame(rune_frame, bg='#1a1a1a')
            btn_frame.pack(pady=5)
            
            # Upgrade button
            upgrade_btn = tk.Button(btn_frame, text="⬆️ Upgrade", font=self.small_font, bg='#006600', fg='white',
                                   command=lambda r=rune: self.upgrade_rune(r), width=8)
            upgrade_btn.pack(side='left', padx=2)
            
            # Sell button
            sell_btn = tk.Button(btn_frame, text="💰 Sell", font=self.small_font, bg='#CC6600', fg='white',
                                command=lambda r=rune: self.sell_rune(r), width=8)
            sell_btn.pack(side='left', padx=2)

        # Configure grid weights
        for col in range(3):
            scrollable_frame.grid_columnconfigure(col, weight=1)
            
    def get_filtered_runes(self):
        """Get filtered and sorted runes"""
        runes = self.player_runes.copy()
        
        # Apply filter
        if hasattr(self, 'rune_filter_var') and self.rune_filter_var.get() != "All":
            runes = [r for r in runes if r['rarity'] == self.rune_filter_var.get()]
            
        # Apply sort
        if hasattr(self, 'rune_sort_var'):
            sort_by = self.rune_sort_var.get()
            if sort_by == "name":
                runes.sort(key=lambda r: r['name'])
            elif sort_by == "rarity":
                rarity_order = {"Common": 0, "Rare": 1, "Epic": 2, "Legendary": 3}
                runes.sort(key=lambda r: rarity_order.get(r['rarity'], 0), reverse=True)
            elif sort_by == "type":
                runes.sort(key=lambda r: r['type'])
            elif sort_by == "level":
                runes.sort(key=lambda r: r['level'], reverse=True)
                
        return runes
        
    def upgrade_rune(self, rune):
        """Upgrade a rune (placeholder implementation)"""
        if rune['level'] >= 15:
            self.show_notification("⚠️ Rune is already at maximum level!")
            return
            
        upgrade_cost = rune['level'] * 1000
        if self.player_cash < upgrade_cost:
            self.show_notification(f"❌ Need {upgrade_cost} cash to upgrade this rune!")
            return
            
        self.player_cash -= upgrade_cost
        rune['level'] += 1
        
        # Increase main stat
        rune['main_value'] = int(rune['main_value'] * 1.1)
        
        # Chance to upgrade substats
        for substat in rune['substats']:
            if random.randint(1, 100) <= 25:  # 25% chance
                rune['substats'][substat] = int(rune['substats'][substat] * 1.05)
                
        self.show_notification(f"✨ {rune['name']} upgraded to level {rune['level']}!")
        self.update_stats_display()
        self.refresh_rune_display()
        
    def sell_rune(self, rune):
        """Sell a rune"""
        if rune['equipped_unit'] is not None:
            self.show_notification("❌ Cannot sell equipped rune! Unequip it first.")
            return
            
        # Calculate sell price
        rarity_multiplier = {"Common": 100, "Rare": 300, "Epic": 800, "Legendary": 2000}
        sell_price = rarity_multiplier[rune['rarity']] + (rune['level'] * 50)
        
        self.player_cash += sell_price
        self.player_runes.remove(rune)
        
        self.show_notification(f"💰 Sold {rune['name']} for {sell_price} cash!")
        self.update_stats_display()
        self.refresh_rune_display()
        
    def show_account_manager(self):
        """Show account manager interface"""
        self.navigate_to("account_manager")
        self.clear_content()
        
        # Title
        title_label = tk.Label(
            self.content_frame,
            text="👤 ACCOUNT MANAGER 👤",
            font=self.title_font,
            bg='black',
            fg='#66CCFF'
        )
        title_label.pack(pady=20)
        
        # Current account info
        account_frame = tk.LabelFrame(
            self.content_frame,
            text="Current Account",
            font=self.header_font,
            bg='black',
            fg='#66FF66'
        )
        account_frame.pack(fill='x', pady=20, padx=50)
        
        if self.current_user:
            user_info = f"Username: {self.current_user['username']}\n"
            user_info += f"Account Type: {'Developer' if self.current_user.get('is_developer') else 'Standard'}\n"
            user_info += f"Player Level: {self.player_level}\n"
            user_info += f"Total Units: {len(self.player_inventory)}\n"
            user_info += f"Total Runes: {len(self.player_runes)}\n"
            user_info += f"Highest Delve Floor: {self.player_progress.get('dungeon_highest', 1)}\n"
            user_info += f"Worlds Completed: {self.player_progress.get('world', 0) + 1}/{self.NUM_WORLDS}"
        else:
            user_info = "No user logged in"
            
        info_label = tk.Label(
            account_frame,
            text=user_info,
            font=self.body_font,
            bg='black',
            fg='white',
            justify='left'
        )
        info_label.pack(pady=15, padx=15, anchor='w')
        
        # Account actions
        actions_frame = tk.LabelFrame(
            self.content_frame,
            text="Account Actions",
            font=self.header_font,
            bg='black',
            fg='#FFCC66'
        )
        actions_frame.pack(fill='x', pady=20, padx=50)
        
        # Developer tools (if developer account)
        if self.current_user and self.current_user.get('is_developer'):
            dev_frame = tk.LabelFrame(
                actions_frame,
                text="🔧 Developer Tools",
                font=self.body_font,
                bg='#1a1a1a',
                fg='#FF6666'
            )
            dev_frame.pack(fill='x', pady=10, padx=15)
            
            dev_buttons = [
                ("💎 Add 10000 Gems", lambda: self.dev_add_resources(gems=10000)),
                ("🪙 Add 50000 Cash", lambda: self.dev_add_resources(cash=50000)),
                ("⭐ Level Up (+10)", lambda: self.dev_level_up(10)),
                ("🎰 Generate 10 Epic Runes", lambda: self.dev_generate_runes("Epic", 10)),
                ("🌟 Generate 5 Legendary Runes", lambda: self.dev_generate_runes("Legendary", 5)),
                ("🏭 Max All Facilities", self.dev_max_facilities),
                ("⚔️ Re-equip All Units", self.auto_equip_best_runes)
            ]
            
            for i, (text, command) in enumerate(dev_buttons):
                row = i // 2
                col = i % 2
                btn = tk.Button(
                    dev_frame,
                    text=text,
                    command=command,
                    font=self.small_font,
                    bg='#006600',
                    fg='white',
                    width=25
                )
                btn.grid(row=row, column=col, padx=5, pady=5)
                
        # Standard account actions
        standard_frame = tk.LabelFrame(
            actions_frame,
            text="👤 Account Management",
            font=self.body_font,
            bg='#1a1a1a',
            fg='#66CCFF'
        )
        standard_frame.pack(fill='x', pady=10, padx=15)
        
        standard_buttons = [
            ("📊 View Statistics", self.show_player_statistics),
            ("💾 Export Save Data", self.export_save_data),
            ("🚪 Logout", self.logout),
            ("🔄 Reset Account", self.reset_account_warning)
        ]
        
        for text, command in standard_buttons:
            btn = tk.Button(
                standard_frame,
                text=text,
                command=command,
                font=self.body_font,
                bg='#006666',
                fg='white',
                width=20
            )
            btn.pack(side='left', padx=10, pady=10)
        
    def show_help_menu(self):
        """Show help and options menu"""
        self.navigate_to("help_menu")
        self.clear_content()
        
        # Title
        title_label = tk.Label(
            self.content_frame,
            text="❓ HELP & OPTIONS ❓",
            font=self.title_font,
            bg='black',
            fg='#66FFCC'
        )
        title_label.pack(pady=20)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Game Guide Tab
        guide_frame = tk.Frame(notebook, bg='black')
        notebook.add(guide_frame, text='📖 Game Guide')
        
        guide_text = tk.Text(
            guide_frame,
            bg='#1a1a1a',
            fg='white',
            font=self.small_font,
            wrap=tk.WORD,
            padx=10,
            pady=10
        )
        guide_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        guide_content = """NIGHTMARE NEXUS - GAME GUIDE

🌟 SUMMONING:
• Use gems to summon horror entities
• Different banners have boosted rates for specific units
• Higher rarity units are more powerful

⚔️ BATTLE SYSTEM:
• Select up to 4 units for your team
• Turn order is determined by Speed stat
• Use Attack, Skills, or Defend each turn
• Auto Battle available for convenience

🎰 RUNES:
• Equipment that enhances unit stats
• 6 slots per unit: Weapon, Armor, Accessory, 3x Enhancement
• Main stats and substats provide different bonuses
• Upgrade runes to increase their power

🏭 FACILITIES:
• Research Lab: Unlock permanent upgrades
• Training Grounds: Train units for EXP
• Rune Forge: Craft new runes
• Bank Vault: Generate passive cash income
• Gem Mine: Generate passive gem income
• Nexus Core: Boost all facility efficiency

🗺️ CAMPAIGN:
• Progress through 5 worlds with 20 stages each
• Defeat enemies to unlock new content
• Boss stages every 10 levels

🕳️ THE DEPTHS:
• Endless Delve: Infinite floors with scaling difficulty
• Rune Sanctums: Boss battles for rare runes (Coming Soon)
• XP Training: Battle trainers for XP potions (Coming Soon)

💎 RESOURCES:
• Gems: Premium currency for summoning
• Cash: Used for upgrades and training
• XP Potions: Quickly level up units

🎯 SPECIAL MECHANICS:
• Eight Pages (Slender): Attackers gain stacks, reducing defense by 5% each
• Ghost (Jeff): Cannot be targeted unless last unit alive
• Lifesteal (Vampire): Heals for 10% of damage dealt
• Many more unique passive abilities!"""
        
        guide_text.insert('1.0', guide_content)
        guide_text.config(state='disabled')
        
        # Controls Tab
        controls_frame = tk.Frame(notebook, bg='black')
        notebook.add(controls_frame, text='🎮 Controls')
        
        controls_text = tk.Text(
            controls_frame,
            bg='#1a1a1a',
            fg='white',
            font=self.small_font,
            wrap=tk.WORD,
            padx=10,
            pady=10
        )
        controls_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        controls_content = """NIGHTMARE NEXUS - CONTROLS

🖱️ MOUSE CONTROLS:
• Left Click: Select buttons, units, targets
• Scroll Wheel: Scroll through long lists
• Hover: View additional information (where available)

⌨️ NAVIGATION:
• 🏠 Home Button: Return to main menu
• 🔙 Back Button: Go to previous screen
• Window can be resized as needed

⚔️ BATTLE CONTROLS:
• Click unit portraits to view stats
• Select actions: Attack, Skill, Defend
• Target selection: Click enemy to attack
• 🤖 Auto Battle: Let AI control your team
• 🚪 Retreat: Exit battle (no rewards)

📱 INTERFACE TIPS:
• Most lists are scrollable if content exceeds window
• Status effects show as icons with numbers
• Rarity colors: White=Common, Blue=Rare, Purple=Epic, Red=Legendary
• Notification area shows recent actions and results
• Battle log shows detailed combat information

🎯 BATTLE TIPS:
• Check turn order to plan your strategy
• Use Defend to reduce damage and gain SP
• Skills cost SP but are powerful
• Critical hits deal extra damage
• Status effects can turn the tide of battle"""
        
        controls_text.insert('1.0', controls_content)
        controls_text.config(state='disabled')
        
        # Settings Tab
        settings_frame = tk.Frame(notebook, bg='black')
        notebook.add(settings_frame, text='⚙️ Settings')
        
        settings_label = tk.Label(
            settings_frame,
            text="🔧 Game Settings",
            font=self.header_font,
            bg='black',
            fg='#FFCC66'
        )
        settings_label.pack(pady=20)
        
        # Settings options
        settings_options_frame = tk.LabelFrame(
            settings_frame,
            text="Display Options",
            font=self.body_font,
            bg='black',
            fg='#CCCCCC'
        )
        settings_options_frame.pack(fill='x', pady=20, padx=50)
        
        # Window size options
        size_frame = tk.Frame(settings_options_frame, bg='black')
        size_frame.pack(pady=10)
        
        size_label = tk.Label(size_frame, text="Window Size:", font=self.body_font, bg='black', fg='white')
        size_label.pack(side='left', padx=10)
        
        size_buttons = [
            ("1400x900", lambda: self.root.geometry("1400x900")),
            ("1600x1000", lambda: self.root.geometry("1600x1000")),
            ("1800x1100", lambda: self.root.geometry("1800x1100")),
            ("Fullscreen", lambda: self.root.state('zoomed'))
        ]
        
        for text, command in size_buttons:
            btn = tk.Button(size_frame, text=text, command=command, font=self.small_font, 
                           bg='#006666', fg='white', width=12)
            btn.pack(side='left', padx=5)
            
        # About Tab
        about_frame = tk.Frame(notebook, bg='black')
        notebook.add(about_frame, text='ℹ️ About')
        
        about_text = tk.Text(
            about_frame,
            bg='#1a1a1a',
            fg='white',
            font=self.small_font,
            wrap=tk.WORD,
            padx=10,
            pady=10
        )
        about_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        about_content = """NIGHTMARE NEXUS
Horror Gacha Collection Game

🎮 VERSION: 1.0 Enhanced GUI Edition
👨‍💻 DEVELOPER: AI Assistant & User Collaboration
🎨 THEME: Horror, Creepypasta, SCP Foundation, Analogue Horror

📖 DESCRIPTION:
Nightmare Nexus is a horror-themed gacha collection game where players summon terrifying entities from various horror franchises. Build your team of nightmare creatures and battle through increasingly difficult challenges.

🌟 FEATURES:
✓ 20+ Unique Horror Entities
✓ Comprehensive Battle System
✓ Rune Equipment System
✓ Facility Management
✓ Campaign and Endless Modes
✓ Full GUI Interface
✓ Developer Tools

🎯 ENTITIES INCLUDE:
• Creepypasta: Slender, Jeff the Killer, The Rake
• SCP Foundation: SCP-682, SCP-999
• Analogue Horror: Iris
• Classic Monsters: Vampires, Werewolves, Zombies
• Urban Legends: Mothman, Chupacabra
• And many more!

💀 SPECIAL THANKS:
To the horror community and creators of the various entities featured in this game. This is a fan tribute and educational project.

🔧 TECHNICAL:
• Built with Python + Tkinter
• Single-file executable design
• Cross-platform compatibility
• Extensible architecture

❤️ ENJOY THE NIGHTMARE!"""
        
        about_text.insert('1.0', about_content)
        about_text.config(state='disabled')
        
        # Bug Report Tab
        bug_report_frame = tk.Frame(notebook, bg='black')
        notebook.add(bug_report_frame, text='🐛 Bug Report')
        
        # Bug report title
        bug_title = tk.Label(
            bug_report_frame,
            text="🐛 Report a Bug",
            font=self.header_font,
            bg='black',
            fg='#FF6666'
        )
        bug_title.pack(pady=20)
        
        # Bug report description
        bug_desc = tk.Label(
            bug_report_frame,
            text="Found a bug? Help us improve Nightmare Nexus by reporting it!\nAll fields marked with * are required.",
            font=self.body_font,
            bg='black',
            fg='white',
            justify='center'
        )
        bug_desc.pack(pady=10)
        
        # Bug report form frame
        form_frame = tk.Frame(bug_report_frame, bg='black')
        form_frame.pack(fill='both', expand=True, padx=50, pady=20)
        
        # Contact info (optional)
        contact_frame = tk.Frame(form_frame, bg='black')
        contact_frame.pack(fill='x', pady=5)
        
        contact_label = tk.Label(
            contact_frame,
            text="Contact Info (optional):",
            font=self.body_font,
            bg='black',
            fg='white'
        )
        contact_label.pack(anchor='w')
        
        self.bug_contact_entry = tk.Entry(
            contact_frame,
            font=self.body_font,
            bg='#1a1a1a',
            fg='white',
            relief='solid',
            bd=1
        )
        self.bug_contact_entry.pack(fill='x', pady=2)
        
        # Bug summary (required)
        summary_frame = tk.Frame(form_frame, bg='black')
        summary_frame.pack(fill='x', pady=10)
        
        summary_label = tk.Label(
            summary_frame,
            text="Bug Summary* (brief description):",
            font=self.body_font,
            bg='black',
            fg='white'
        )
        summary_label.pack(anchor='w')
        
        self.bug_summary_entry = tk.Entry(
            summary_frame,
            font=self.body_font,
            bg='#1a1a1a',
            fg='white',
            relief='solid',
            bd=1
        )
        self.bug_summary_entry.pack(fill='x', pady=2)
        
        # Bug description (required)
        desc_frame = tk.Frame(form_frame, bg='black')
        desc_frame.pack(fill='both', expand=True, pady=10)
        
        desc_label = tk.Label(
            desc_frame,
            text="Detailed Description* (what happened?):",
            font=self.body_font,
            bg='black',
            fg='white'
        )
        desc_label.pack(anchor='w')
        
        self.bug_description_text = tk.Text(
            desc_frame,
            font=self.body_font,
            bg='#1a1a1a',
            fg='white',
            height=6,
            wrap=tk.WORD,
            relief='solid',
            bd=1
        )
        self.bug_description_text.pack(fill='both', expand=True, pady=2)
        
        # Steps to reproduce
        steps_frame = tk.Frame(form_frame, bg='black')
        steps_frame.pack(fill='both', expand=True, pady=10)
        
        steps_label = tk.Label(
            steps_frame,
            text="Steps to Reproduce (how to recreate the bug):",
            font=self.body_font,
            bg='black',
            fg='white'
        )
        steps_label.pack(anchor='w')
        
        self.bug_steps_text = tk.Text(
            steps_frame,
            font=self.body_font,
            bg='#1a1a1a',
            fg='white',
            height=4,
            wrap=tk.WORD,
            relief='solid',
            bd=1
        )
        self.bug_steps_text.pack(fill='both', expand=True, pady=2)
        
        # Submit button and status
        submit_frame = tk.Frame(form_frame, bg='black')
        submit_frame.pack(fill='x', pady=20)
        
        submit_btn = tk.Button(
            submit_frame,
            text="📝 Submit Bug Report",
            command=self.submit_bug_report,
            font=self.header_font,
            bg='#CC3300',
            fg='white',
            width=20,
            height=2
        )
        submit_btn.pack()
        
        # Clear button
        clear_btn = tk.Button(
            submit_frame,
            text="🗑️ Clear Form",
            command=self.clear_bug_form,
            font=self.body_font,
            bg='#666666',
            fg='white',
            width=15,
            height=1
        )
        clear_btn.pack(pady=5)
        
        # Status message
        self.bug_status_label = tk.Label(
            form_frame,
            text="",
            font=self.body_font,
            bg='black',
            fg='#66FF66'
        )
        self.bug_status_label.pack(pady=10)
        
    def submit_bug_report(self):
        """Submit a bug report"""
        # Get form data
        contact = self.bug_contact_entry.get().strip()
        summary = self.bug_summary_entry.get().strip()
        description = self.bug_description_text.get("1.0", tk.END).strip()
        steps = self.bug_steps_text.get("1.0", tk.END).strip()
        
        # Validate required fields
        if not summary:
            self.bug_status_label.config(text="❌ Please enter a bug summary!", fg='#FF6666')
            return
        
        if not description:
            self.bug_status_label.config(text="❌ Please provide a detailed description!", fg='#FF6666')
            return
        
        # Create bug report data
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        username = self.current_user['username'] if self.current_user else "unknown"
        
        bug_report = {
            "id": f"bug_{timestamp}_{username}",
            "timestamp": timestamp,
            "user_info": {
                "username": username,
                "is_developer": self.current_user.get('is_developer', False) if self.current_user else False
            },
            "contact_info": contact,
            "summary": summary,
            "description": description,
            "steps_to_reproduce": steps,
            "game_state": {
                "level": self.player_level,
                "gems": self.player_gems,
                "cash": self.player_cash,
                "units_count": len(self.player_inventory),
                "runes_count": len(self.player_runes),
                "current_world": self.player_progress.get('world', 0),
                "current_stage": self.player_progress.get('stage', 0)
            },
            "system_info": {
                "platform": os.name,
                "python_version": str(os.sys.version_info[:3])
            }
        }
        
        # Save bug report to file
        try:
            # Ensure bug_reports directory exists
            os.makedirs("bug_reports", exist_ok=True)
            
            filename = f"bug_reports/bug_{username}_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(bug_report, f, indent=2, ensure_ascii=False)
            
            # Clear form and show success
            self.clear_bug_form()
            self.bug_status_label.config(
                text=f"✅ Bug report submitted successfully!\nSaved as: {filename}",
                fg='#66FF66'
            )
            
            # Also show notification in main area
            self.show_notification("📝 Bug report submitted! Thank you for helping improve the game.")
            
        except Exception as e:
            self.bug_status_label.config(
                text=f"❌ Error saving bug report: {str(e)}",
                fg='#FF6666'
            )
    
    def clear_bug_form(self):
        """Clear all bug report form fields"""
        self.bug_contact_entry.delete(0, tk.END)
        self.bug_summary_entry.delete(0, tk.END)
        self.bug_description_text.delete("1.0", tk.END)
        self.bug_steps_text.delete("1.0", tk.END)
        self.bug_status_label.config(text="")
        
    def exit_game(self):
        """Exit the game"""
        if messagebox.askyesno("Exit Game", "Are you sure you want to exit Nightmare Nexus?"):
            self.root.quit()
            
    def dev_add_resources(self, gems=0, cash=0):
        """Developer tool to add resources"""
        if gems > 0:
            self.player_gems += gems
            self.show_notification(f"💎 Added {gems} gems!")
        if cash > 0:
            self.player_cash += cash
            self.show_notification(f"🪙 Added {cash} cash!")
        self.update_stats_display()
        
    def dev_level_up(self, levels):
        """Developer tool to level up player"""
        self.player_level += levels
        self.show_notification(f"⭐ Player leveled up {levels} times! Now level {self.player_level}")
        self.update_stats_display()
        
    def dev_generate_runes(self, rarity, count):
        """Developer tool to generate runes"""
        for _ in range(count):
            rune = self.generate_rune(rarity)
            self.player_runes.append(rune)
        self.show_notification(f"🎰 Generated {count} {rarity} runes!")
        
    def dev_max_facilities(self):
        """Developer tool to max all facilities"""
        max_levels = {
            'research_lab': 10,
            'training_grounds': 15, 
            'rune_forge': 12,
            'nexus_core': 5,
            'bank_vault': 8,
            'gem_mine': 6
        }
        
        for facility, max_level in max_levels.items():
            self.player_facilities[facility] = max_level
            
        self.show_notification("🏭 All facilities maxed out!")
        
    def show_player_statistics(self):
        """Show detailed player statistics"""
        stats = f"""📊 PLAYER STATISTICS

👤 Profile:
Level: {self.player_level}
Experience: {self.player_xp:,}

💰 Resources:
Gems: {self.player_gems:,}
Cash: {self.player_cash:,}
Small XP Pots: {self.player_items.get('Small XP Pot', 0)}
Medium XP Pots: {self.player_items.get('Medium XP Pot', 0)}
Large XP Pots: {self.player_items.get('Large XP Pot', 0)}

👥 Collection:
Total Units: {len(self.player_inventory)}
Total Runes: {len(self.player_runes)}

🗺️ Progress:
Current World: {self.player_progress.get('world', 0) + 1}/{self.NUM_WORLDS}
Current Stage: {self.player_progress.get('stage', 0) + 1}/{self.STAGES_PER_WORLD}
Highest Delve Floor: {self.player_progress.get('dungeon_highest', 1)}

🏭 Facilities:"""
        
        for facility, level in self.player_facilities.items():
            facility_name = facility.replace('_', ' ').title()
            stats += f"\n{facility_name}: Level {level}"
            
        messagebox.showinfo("Player Statistics", stats)
        
    def export_save_data(self):
        """Export save data (placeholder)"""
        self.show_notification("💾 Save data export feature coming soon!")
        
    def reset_account_warning(self):
        """Show warning before account reset"""
        if messagebox.askyesno("Reset Account", 
                              "⚠️ WARNING: This will permanently delete all progress!\n\nAre you absolutely sure you want to reset your account?"):
            if messagebox.askyesno("Final Confirmation", 
                                  "💀 LAST CHANCE: This cannot be undone!\n\nReset account now?"):
                self.reset_account()
                
    def reset_account(self):
        """Reset all account progress"""
        self.player_gems = 100
        self.player_cash = 500
        self.player_level = 1
        self.player_xp = 0
        self.player_inventory = []
        self.player_items = {"Small XP Pot": 0, "Medium XP Pot": 0, "Large XP Pot": 0}
        self.player_runes = []
        self.player_facilities = {}
        self.player_research = {}
        self.player_progress = {
            "world": 0,
            "stage": 0,
            "unlocked": [[1] + [0]*19] + [[0]*20 for _ in range(4)],
            "dungeon_highest": 1
        }
        
        self.show_notification("🔄 Account reset complete! Starting fresh...")
        self.update_stats_display()
        self.go_home()
        
    def start_unit_test(self, unit_idx):
        """Start a unit test battle with practice dummy"""
        if unit_idx >= len(self.player_inventory):
            return
            
        unit = self.player_inventory[unit_idx]
        self.show_notification(f"🧪 Starting practice battle with {unit['entity']['name']}...")
        
        # Create practice dummy
        practice_dummy = {
            "name": "Practice Dummy",
            "rarity": "Common",
            "hp": 999999,  # Infinite HP
            "max_hp": 999999,
            "attack": 1,  # Minimal damage
            "defense": 0,
            "speed": 1,  # Very slow
            "skill": None,
            "crit_rate": 0,
            "crit_damage": 100,
            "accuracy": 100,
            "evasion": 0,
            "sp": 0,
            "effects": []
        }
        
        # Setup practice battle state
        self.battle_state = {
            "type": "practice",
            "team": [unit.copy()],
            "enemies": [practice_dummy],
            "current_turn": 0,
            "turn_order": [],
            "auto_battle": False
        }
        
        # Initialize practice unit with infinite HP
        practice_unit = self.battle_state["team"][0]
        practice_unit["battle_hp"] = 999999  # Infinite HP for testing
        practice_unit["sp"] = 150  # Max SP to test skills
        practice_unit["effects"] = []
        practice_unit["defending"] = False
        
        # Jeff starts with 1 ghost stack even in practice
        if practice_unit["entity"]["name"] == "Jeff the Killer":
            practice_unit["effects"].append({"type": "ghost", "turns": 99, "stacks": 1, "source": "Go to Sleep"})
            
        # Show practice battle interface
        self.show_practice_battle_interface()
        
    def show_practice_battle_interface(self):
        """Show the practice battle interface"""
        self.current_screen = "practice_battle"
        self.clear_content()
        
        unit = self.battle_state["team"][0]
        
        # Battle title
        title_label = tk.Label(
            self.content_frame,
            text=f"🧪 PRACTICE BATTLE - {unit['entity']['name'].upper()}",
            font=self.title_font,
            bg='black',
            fg='#66CCFF'
        )
        title_label.pack(pady=10)
        
        # Practice info
        info_label = tk.Label(
            self.content_frame,
            text="Test your unit's abilities! Both you and the dummy have infinite HP.",
            font=self.body_font,
            bg='black',
            fg='#CCCCCC'
        )
        info_label.pack(pady=5)
        
        # Battle controls
        controls_frame = tk.Frame(self.content_frame, bg='black')
        controls_frame.pack(pady=10)
        
        end_practice_btn = tk.Button(
            controls_frame,
            text="🚪 End Practice",
            command=self.end_practice_battle,
            font=self.body_font,
            bg='#CC6600',
            fg='white',
            width=12
        )
        end_practice_btn.pack(side='left', padx=5)
        
        # Reset SP button
        reset_sp_btn = tk.Button(
            controls_frame,
            text="⚡ Reset SP",
            command=self.reset_practice_sp,
            font=self.body_font,
            bg='#006666',
            fg='white',
            width=12
        )
        reset_sp_btn.pack(side='left', padx=5)
        
        # Battle log
        log_frame = tk.LabelFrame(
            self.content_frame,
            text="Practice Log",
            font=self.header_font,
            bg='black',
            fg='#FF9966'
        )
        log_frame.pack(fill='x', pady=10, padx=20)
        
        self.battle_log_display = tk.Text(
            log_frame,
            bg='#1a1a1a',
            fg='white',
            font=self.small_font,
            height=8,
            state='disabled',
            wrap=tk.WORD
        )
        self.battle_log_display.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Unit display
        unit_frame = tk.LabelFrame(
            self.content_frame,
            text="Your Unit",
            font=self.header_font,
            bg='black',
            fg='#66FF66'
        )
        unit_frame.pack(fill='x', pady=10, padx=20)
        
        self.practice_unit_display = tk.Frame(unit_frame, bg='black')
        self.practice_unit_display.pack(fill='x', padx=10, pady=10)
        
        # Action buttons frame
        self.practice_actions_frame = tk.LabelFrame(
            self.content_frame,
            text="Test Actions",
            font=self.header_font,
            bg='black',
            fg='#FFFF66'
        )
        self.practice_actions_frame.pack(fill='x', pady=10, padx=20)
        
        # Initialize practice display and start
        self.update_practice_display()
        self.add_battle_log(f"🧪 Practice battle started with {unit['entity']['name']}! Test your abilities!")
        self.process_practice_turn()
        
    def update_practice_display(self):
        """Update the practice battle display"""
        # Clear existing display
        for widget in self.practice_unit_display.winfo_children():
            widget.destroy()
            
        unit = self.battle_state["team"][0]
        
        unit_info_frame = tk.Frame(self.practice_unit_display, bg='#1a1a1a', relief='ridge', bd=2)
        unit_info_frame.pack(padx=10, pady=5, fill='x')
        
        # Unit name
        name_label = tk.Label(
            unit_info_frame,
            text=f"{unit['entity']['name']} (Practice Mode)",
            font=self.body_font,
            bg='#1a1a1a',
            fg=self.rarity_colors[unit['entity']['rarity']]
        )
        name_label.pack(pady=2)
        
        # HP (shows as infinite)
        hp_label = tk.Label(
            unit_info_frame,
            text="HP: ∞ (Infinite for testing)",
            font=self.small_font,
            bg='#1a1a1a',
            fg='#66FF66'
        )
        hp_label.pack()
        
        # SP
        sp_label = tk.Label(
            unit_info_frame,
            text=f"SP: {unit['sp']}/150",
            font=self.small_font,
            bg='#1a1a1a',
            fg='#66CCFF'
        )
        sp_label.pack()
        
        # Status effects
        if unit.get("effects"):
            effects_text = " ".join([self.get_effect_icon(eff) for eff in unit["effects"]])
            effects_label = tk.Label(
                unit_info_frame,
                text=f"Effects: {effects_text}",
                font=self.small_font,
                bg='#1a1a1a',
                fg='#FFCC66'
            )
            effects_label.pack()
            
    def process_practice_turn(self):
        """Process practice turn - always player's turn"""
        unit = self.battle_state["team"][0]
        
        # Clear action buttons
        for widget in self.practice_actions_frame.winfo_children():
            widget.destroy()
            
        # Show current unit
        current_label = tk.Label(
            self.practice_actions_frame,
            text=f"🧪 Test {unit['entity']['name']}'s abilities:",
            font=self.header_font,
            bg='black',
            fg='#66CCFF'
        )
        current_label.pack(pady=10)
        
        # Action buttons
        actions_btn_frame = tk.Frame(self.practice_actions_frame, bg='black')
        actions_btn_frame.pack(pady=10)
        
        # Attack button
        attack_btn = tk.Button(
            actions_btn_frame,
            text="⚔️ Test Attack",
            command=lambda: self.practice_attack(unit),
            font=self.body_font,
            bg='#CC3300',
            fg='white',
            width=12
        )
        attack_btn.pack(side='left', padx=5)
        
        # Skill button (always available in practice)
        if unit["entity"]["skill"]:
            skill_btn = tk.Button(
                actions_btn_frame,
                text="✨ Test Skill",
                command=lambda: self.practice_skill(unit),
                font=self.body_font,
                bg='#3366CC',
                fg='white',
                width=12
            )
            skill_btn.pack(side='left', padx=5)
            
        # Defend button
        defend_btn = tk.Button(
            actions_btn_frame,
            text="🛡️ Test Defend",
            command=lambda: self.practice_defend(unit),
            font=self.body_font,
            bg='#669966',
            fg='white',
            width=12
        )
        defend_btn.pack(side='left', padx=5)
        
    def practice_attack(self, unit):
        """Handle practice attack"""
        dummy = self.battle_state["enemies"][0]
        
        # Calculate damage (but dummy won't actually lose HP)
        damage, is_crit = self.calculate_damage(unit, dummy)
        
        crit_text = " [CRITICAL HIT]" if is_crit else ""
        self.add_battle_log(f"⚔️ {unit['entity']['name']} attacks Practice Dummy for {damage} damage!{crit_text}")
        
        # Special unit effects
        if unit["entity"]["name"] == "Iris":
            self.add_battle_log(f"🌟 Iris's passive: Attack hits all enemies (AoE effect)!")
        elif unit["entity"]["name"] == "Vampire":
            heal = int(damage * 0.1)
            self.add_battle_log(f"🩸 Vampire's lifesteal heals for {heal} HP!")
        
        # Gain SP
        unit["sp"] = min(unit["sp"] + 5, 150)
        
        self.finish_practice_turn(unit)
        
    def practice_skill(self, unit):
        """Handle practice skill use"""
        skill = unit["entity"]["skill"]
        skill_cost = self.skill_costs.get(skill, 30)
        
        # In practice, always allow skill use
        if unit["sp"] < skill_cost:
            unit["sp"] = skill_cost  # Give enough SP
            
        self.add_battle_log(f"✨ Testing {unit['entity']['name']}'s skill: {skill.replace('_', ' ').title()}!")
        
        # Use skill on dummy
        dummy = self.battle_state["enemies"][0]
        self.use_skill(unit, dummy)
        unit["sp"] -= skill_cost
        
        self.finish_practice_turn(unit)
        
    def practice_defend(self, unit):
        """Handle practice defend"""
        unit["defending"] = True
        unit["sp"] = min(unit["sp"] + 10, 150)
        self.add_battle_log(f"🛡️ {unit['entity']['name']} is defending! Damage reduced by 50%, +10 SP gained.")
        
        self.finish_practice_turn(unit)
        
    def finish_practice_turn(self, unit):
        """Finish practice turn and continue"""
        unit["defending"] = False
        self.update_practice_display()
        
        # Continue to next turn after brief delay
        self.root.after(1000, self.process_practice_turn)
        
    def reset_practice_sp(self):
        """Reset SP to full for continued testing"""
        unit = self.battle_state["team"][0]
        unit["sp"] = 150
        self.add_battle_log(f"⚡ {unit['entity']['name']}'s SP reset to maximum for testing!")
        self.update_practice_display()
        
    def end_practice_battle(self):
        """End practice battle and return to unit details"""
        self.add_battle_log("🚪 Practice battle ended. Returning to unit details...")
        self.root.after(1000, self.go_back)
        
    def challenge_rune_boss_stage(self, boss, stage):
        """Challenge a rune boss at specific stage"""
        difficulty_names = {
            1: "Easy", 2: "Easy", 3: "Easy",
            4: "Medium", 5: "Medium", 6: "Medium",
            7: "Hard", 8: "Hard", 9: "Hard",
            10: "Nightmare"
        }
        
        difficulty = difficulty_names[stage]
        self.show_notification(f"⚔️ Challenging {boss['name']} - Stage {stage} ({difficulty})!")
        self.show_team_selection_inline(lambda team: self.launch_rune_boss_battle(boss, team, stage))
        
    def launch_rune_boss_battle(self, boss, team, stage):
        """Launch rune boss battle at specific stage with 5-wave system"""
        if not team:
            return
            
        # Calculate boss stats based on stage (1-10)
        base_level = 20 + (stage * 5)  # Level 25-70
        stage_multiplier = 1.0 + (stage * 0.3)  # 1.0x to 4.0x scaling
        
        # Create boss enemy for final wave
        boss_entity = {
            "name": f"{boss['name']} [Stage {stage}]",
            "rarity": "Legendary",
            "hp": int(base_level * 150 * stage_multiplier),
            "max_hp": int(base_level * 150 * stage_multiplier),
            "attack": int(base_level * 8 * stage_multiplier),
            "defense": int(base_level * 5 * stage_multiplier),
            "speed": base_level + (stage * 3),
            "skill": "boss_special",  # Special boss skill
            "crit_rate": min(stage * 2, 20),  # 0-20% crit rate based on stage
            "crit_damage": 150 + (stage * 10),  # 150-250% crit damage
            "accuracy": 80 + (stage * 2),  # 80-100% accuracy
            "evasion": stage,  # 0-10% evasion
            "sp": 150,
            "effects": []
        }
        
        # Start with first wave minions
        first_wave_enemies = self.generate_boss_minions(boss, 1)
        
        # Setup battle state for boss fight with 5-wave system
        self.battle_state = {
            "type": "rune_boss",
            "boss_data": boss,
            "stage": stage,
            "team": team.copy(),
            "enemies": first_wave_enemies,
            "current_turn": 0,
            "turn_order": [],
            "auto_battle": False,
            "current_wave": 1,
            "total_waves": 5,
            "original_boss": boss_entity
        }
        
        self.show_notification(f"🎰 {boss['name']} Boss Battle! Prepare for 5 waves of increasing difficulty!")
        
        # Initialize units with proper battle stats
        for unit in self.battle_state["team"]:
            final_stats = self.calculate_unit_stats_with_runes(unit)
            unit["battle_stats"] = final_stats
            unit["battle_hp"] = final_stats["hp"]
            unit["max_hp"] = final_stats["hp"]
            unit["sp"] = 100
            unit["effects"] = []
            unit["defending"] = False
            if unit["entity"]["name"] == "Jeff the Killer":
                unit["effects"].append({"type": "ghost", "turns": 99, "stacks": 1, "source": "Go to Sleep"})
                
        # Show battle interface
        self.show_battle_interface()
        
    def battle_xp_trainer(self, trainer):
        """Battle an XP trainer"""
        self.show_notification(f"⚔️ Challenging {trainer['name']}! Earn valuable XP potions!")
        self.show_team_selection_inline(lambda team: self.launch_xp_trainer_battle(trainer, team))
        
    def launch_xp_trainer_battle(self, trainer, team):
        """Launch XP trainer battle"""
        if not team:
            return
            
        # Create trainer enemy
        trainer_entity = {
            "name": trainer['name'],
            "rarity": "Epic",
            "hp": trainer['level'] * 80,
            "max_hp": trainer['level'] * 80,
            "attack": trainer['level'] * 4,
            "defense": trainer['level'] * 2,
            "speed": trainer['level'] + 15,
            "skill": "trainer_special",
            "crit_rate": 10,
            "crit_damage": 175,
            "accuracy": 90,
            "evasion": 15,
            "sp": 120,
            "effects": []
        }
        
        # Setup battle state
        self.battle_state = {
            "type": "xp_trainer",
            "trainer_data": trainer,
            "team": team.copy(),
            "enemies": [trainer_entity],
            "current_turn": 0,
            "turn_order": [],
            "auto_battle": False
        }
        
        # Initialize units with proper battle stats
        for unit in self.battle_state["team"]:
            final_stats = self.calculate_unit_stats_with_runes(unit)
            unit["battle_stats"] = final_stats
            unit["battle_hp"] = final_stats["hp"]
            unit["max_hp"] = final_stats["hp"]
            unit["sp"] = 100
            unit["effects"] = []
            unit["defending"] = False
            if unit["entity"]["name"] == "Jeff the Killer":
                unit["effects"].append({"type": "ghost", "turns": 99, "stacks": 1, "source": "Go to Sleep"})
                
        # Show battle interface
        self.show_battle_interface()
        
    def run(self):
        """Start the GUI application"""
        self.root.protocol("WM_DELETE_WINDOW", self.exit_game)
        self.root.mainloop()
        
    def setup_autosave(self):
        """Setup autosave timer"""
        # Save every 2 minutes
        self.root.after(120000, self.autosave_game_data)  # 2 minutes
    
    def autosave_game_data(self):
        """Auto-save game data periodically"""
        try:
            # Only autosave if user is logged in
            if self.current_user:
                self.save_game_data()
                self.show_notification("💾 Game auto-saved")
        except Exception as e:
            self.show_notification(f"❌ Auto-save failed: {str(e)}", '#FF6666')
        
        # Schedule next autosave
        self.root.after(120000, self.autosave_game_data)
    
    def save_game_data(self):
        """Save game data to file with backward compatibility"""
        # Use account-specific saving for players
        if self.current_user and not self.current_user.get('is_developer'):
            self.save_player_account()
            return
            
        # Developer account uses main save file
        save_data = {
            "version": "1.1",
            "player_gems": self.player_gems,
            "player_cash": self.player_cash,
            "player_level": self.player_level,
            "player_xp": self.player_xp,
            "player_inventory": self.player_inventory,
            "player_items": self.player_items,
            "player_runes": self.player_runes,
            "player_progress": self.player_progress,
            "player_facilities": self.player_facilities,
            "player_research": self.player_research,
            "current_user": self.current_user
        }
        
        # Ensure save directory exists
        os.makedirs("saves", exist_ok=True)
        
        # Save to file
        with open("saves/nightmare_nexus_save.json", "w") as f:
            json.dump(save_data, f, indent=2)
    
    def load_game_data(self):
        """Load game data from file with backward compatibility"""
        try:
            if os.path.exists("saves/nightmare_nexus_save.json"):
                with open("saves/nightmare_nexus_save.json", "r") as f:
                    save_data = json.load(f)
                
                # Load data with backward compatibility
                self.player_gems = save_data.get("player_gems", 100)
                self.player_cash = save_data.get("player_cash", 500)
                self.player_level = save_data.get("player_level", 1)
                self.player_xp = save_data.get("player_xp", 0)
                self.player_inventory = save_data.get("player_inventory", [])
                self.player_items = save_data.get("player_items", {"Small XP Pot": 0, "Medium XP Pot": 0, "Large XP Pot": 0})
                self.player_runes = save_data.get("player_runes", [])
                self.player_progress = save_data.get("player_progress", {
                    "world": 0,
                    "stage": 0,
                    "unlocked": [[1] + [0]*19] + [[0]*20 for _ in range(4)],
                    "dungeon_highest": 1
                })
                self.player_facilities = save_data.get("player_facilities", {})
                self.player_research = save_data.get("player_research", {})
                
                # Ensure backward compatibility for new rune format
                for rune in self.player_runes:
                    if "set" not in rune:
                        rune["set"] = random.choice(list(self.rune_sets.keys()))
                
                # Ensure backward compatibility for units with new level scaling
                for unit in self.player_inventory:
                    if "runes" not in unit:
                        unit["runes"] = {}
                
                print(f"✅ Game data loaded from save file")
        except Exception as e:
            print(f"⚠️ Could not load save data: {e}. Starting with default data.")
    
    def add_battle_log_with_turn(self, message, color='white'):
        """Add message to battle log with turn number"""
        if hasattr(self, 'battle_log_display'):
            self.battle_log_display.config(state='normal')
            turn_text = f"[Turn {self.turn_counter}]"
            self.battle_log_display.insert('end', f"{turn_text} {message}\n")
            self.battle_log_display.see('end')
            self.battle_log_display.config(state='disabled')
            
            # Auto-scroll and limit lines
            lines = self.battle_log_display.get('1.0', 'end').count('\n')
            if lines > 50:
                self.battle_log_display.config(state='normal')
                self.battle_log_display.delete('1.0', '2.0')
                self.battle_log_display.config(state='disabled')
    
    def process_turn_end_sp_recovery(self, unit):
        """Process SP recovery at end of turn if no skill was used"""
        # Check if unit didn't use a skill this turn
        if not hasattr(unit, '_used_skill_this_turn') or not unit._used_skill_this_turn:
            max_sp = unit.get('max_sp', 150)
            sp_recovery = int(max_sp * 0.2)  # 20% of max SP
            old_sp = unit.get('sp', 0)
            unit['sp'] = min(old_sp + sp_recovery, max_sp)
            
            if sp_recovery > 0:
                self.add_battle_log_with_turn(f"⚡ {self.get_unit_name(unit)} recovers {sp_recovery} SP ({old_sp} → {unit['sp']})")
        
        # Reset skill usage flag for next turn
        unit._used_skill_this_turn = False
    
    def mark_skill_used(self, unit):
        """Mark that a unit used a skill this turn"""
        unit._used_skill_this_turn = True
    
    def show_status_effects_on_bars(self, unit_frame, unit):
        """Show status effects beneath HP and SP bars"""
        if unit.get("effects"):
            effects_frame = tk.Frame(unit_frame, bg=unit_frame['bg'])
            effects_frame.pack(pady=2)
            
            effects_text = ""
            for effect in unit["effects"]:
                effect_icon = self.get_effect_icon(effect)
                effects_text += effect_icon + " "
            
            if effects_text.strip():
                effects_label = tk.Label(
                    effects_frame,
                    text=effects_text.strip(),
                    font=('Consolas', 8),
                    bg=unit_frame['bg'],
                    fg='#FFCC66'
                )
                effects_label.pack()
    
    def show_enemy_preview(self, world_idx, stage_idx, enemies):
        """Show enemy preview GUI before team selection"""
        self.clear_content()
        
        # Title
        title_label = tk.Label(
            self.content_frame,
            text=f"👹 ENEMY PREVIEW 👹",
            font=self.title_font,
            bg='black',
            fg='#FF6666'
        )
        title_label.pack(pady=20)
        
        # Stage info
        stage_info = tk.Label(
            self.content_frame,
            text=f"World {world_idx+1}-{stage_idx+1}: {self.worlds[world_idx]['name']}",
            font=self.header_font,
            bg='black',
            fg='#FFCC66'
        )
        stage_info.pack(pady=10)
        
        # Enemy list frame
        enemies_frame = tk.LabelFrame(
            self.content_frame,
            text="Enemies You Will Face",
            font=self.header_font,
            bg='black',
            fg='#FF6666'
        )
        enemies_frame.pack(fill='both', expand=True, pady=20, padx=50)
        
        # Scrollable enemies display
        canvas = tk.Canvas(enemies_frame, bg='black', highlightthickness=0)
        scrollbar = ttk.Scrollbar(enemies_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='black')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)
        
        # Display each enemy
        for i, enemy in enumerate(enemies):
            enemy_frame = tk.LabelFrame(
                scrollable_frame,
                text=f"{i+1}. {enemy['name']}",
                font=self.body_font,
                bg='#2a1a1a',
                fg=self.rarity_colors.get(enemy.get('rarity', 'Common'), '#FFFFFF'),
                bd=2,
                relief='ridge'
            )
            enemy_frame.pack(fill='x', padx=10, pady=5)
            
            # Enemy stats
            stats_text = f"❤️ HP: {enemy['hp']:,}\n"
            stats_text += f"⚔️ Attack: {enemy['attack']:,}\n"
            stats_text += f"🛡️ Defense: {enemy['defense']:,}\n"
            stats_text += f"⚡ Speed: {enemy['speed']}\n"
            
            if enemy.get('skill'):
                stats_text += f"✨ Skill: {enemy['skill'].replace('_', ' ').title()}"
            
            stats_label = tk.Label(
                enemy_frame,
                text=stats_text,
                font=self.small_font,
                bg='#2a1a1a',
                fg='white',
                justify='left'
            )
            stats_label.pack(padx=10, pady=10, anchor='w')
            
        # Action buttons
        buttons_frame = tk.Frame(self.content_frame, bg='black')
        buttons_frame.pack(pady=20)
        
        # Proceed to team selection
        proceed_btn = tk.Button(
            buttons_frame,
            text="⚔️ Select Team & Battle",
            command=lambda: self.show_team_selection_inline(lambda team: self.launch_battle(world_idx, stage_idx, team)),
            font=self.header_font,
            bg='#006600',
            fg='white',
            width=20,
            height=2
        )
        proceed_btn.pack(side='left', padx=10)
        
        # Back button
        back_btn = tk.Button(
            buttons_frame,
            text="🔙 Back to Stage Select",
            command=lambda: self.enter_world(world_idx),
            font=self.body_font,
            bg='#666666',
            fg='white',
            width=20
        )
        back_btn.pack(side='left', padx=10)
    
    def show_unit_rune_management(self, unit_idx):
        """Show comprehensive unit rune management interface"""
        if unit_idx >= len(self.player_inventory):
            return
            
        unit = self.player_inventory[unit_idx]
        self.clear_content()
        
        # Title
        title_label = tk.Label(
            self.content_frame,
            text=f"🎰 RUNE MANAGEMENT - {unit['entity']['name'].upper()} 🎰",
            font=self.title_font,
            bg='black',
            fg='#CC66FF'
        )
        title_label.pack(pady=10)
        
        # Main content with left and right sections
        main_frame = tk.Frame(self.content_frame, bg='black')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left section - Unit info and equipped runes
        left_frame = tk.Frame(main_frame, bg='black', width=400)
        left_frame.pack(side='left', fill='both', padx=(0, 10))
        left_frame.pack_propagate(False)
        
        # Unit stats with runes
        stats_frame = tk.LabelFrame(
            left_frame,
            text=f"{unit['entity']['name']} (Lv.{unit['level']})",
            font=self.header_font,
            bg='black',
            fg=self.rarity_colors[unit['entity']['rarity']]
        )
        stats_frame.pack(fill='x', pady=5)
        
        # Calculate stats
        base_stats = self.calculate_unit_level_stats(unit)
        final_stats = self.calculate_unit_stats_with_runes(unit)
        
        stats_display = [
            ("❤️ HP", "hp"),
            ("⚔️ ATK", "attack"),
            ("🛡️ DEF", "defense"),
            ("⚡ SPD", "speed"),
            ("💥 Crit Rate", "crit_rate"),
            ("🎯 Crit Dmg", "crit_damage")
        ]
        
        for stat_name, stat_key in stats_display:
            stat_row = tk.Frame(stats_frame, bg='black')
            stat_row.pack(fill='x', padx=10, pady=2)
            
            base_val = base_stats[stat_key]
            final_val = final_stats[stat_key]
            bonus = final_val - base_val
            
            if bonus > 0:
                stat_text = f"{stat_name}: {base_val} (+{bonus}) = {final_val}"
                color = '#66FF66'
            else:
                stat_text = f"{stat_name}: {base_val}"
                color = 'white'
            
            stat_label = tk.Label(
                stat_row,
                text=stat_text,
                font=self.small_font,
                bg='black',
                fg=color,
                anchor='w'
            )
            stat_label.pack(fill='x')
        
        # Rune slots display with visual grid
        slots_frame = tk.LabelFrame(
            left_frame,
            text="Rune Slots",
            font=self.body_font,
            bg='black',
            fg='#FFCC66'
        )
        slots_frame.pack(fill='both', expand=True, pady=5)
        
        # Grid layout for slots
        slot_names = {
            1: "⚔️ Weapon", 2: "🛡️ Armor", 3: "💎 Accessory",
            4: "✨ Enhance", 5: "✨ Enhance", 6: "✨ Enhance"
        }
        
        slots_grid = tk.Frame(slots_frame, bg='black')
        slots_grid.pack(fill='both', expand=True, padx=10, pady=10)
        
        for slot in range(1, 7):
            row = (slot - 1) // 2
            col = (slot - 1) % 2
            
            equipped_rune = None
            if slot in unit.get('runes', {}):
                rune_id = unit['runes'][slot]
                equipped_rune = next((r for r in self.player_runes if r["id"] == rune_id), None)
                
            slot_frame = tk.LabelFrame(
                slots_grid,
                text=f"Slot {slot}: {slot_names[slot]}",
                font=self.small_font,
                bg='#1a1a1a',
                fg='#CCCCCC'
            )
            slot_frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
            
            if equipped_rune:
                # Show equipped rune
                rune_info = f"{equipped_rune['name']}\nLv.{equipped_rune['level']} {equipped_rune['rarity']}\n{equipped_rune['main_stat']} +{equipped_rune['main_value']}"
                rune_label = tk.Label(
                    slot_frame,
                    text=rune_info,
                    font=('Consolas', 8),
                    bg='#1a1a1a',
                    fg=self.rarity_colors[equipped_rune['rarity']],
                    justify='center'
                )
                rune_label.pack(pady=5)
                
                # Buttons
                btn_frame = tk.Frame(slot_frame, bg='#1a1a1a')
                btn_frame.pack()
                
                manage_btn = tk.Button(
                    btn_frame,
                    text="⚙️",
                    command=lambda s=slot: self.manage_rune_slot_inline(unit_idx, s),
                    font=('Consolas', 8),
                    bg='#006666',
                    fg='white',
                    width=3
                )
                manage_btn.pack(side='left', padx=1)
                
                upgrade_btn = tk.Button(
                    btn_frame,
                    text="⬆️",
                    command=lambda s=slot: self.show_rune_upgrade_interface(unit_idx, s),
                    font=('Consolas', 8),
                    bg='#CC6600',
                    fg='white',
                    width=3
                )
                upgrade_btn.pack(side='left', padx=1)
            else:
                # Empty slot
                empty_label = tk.Label(
                    slot_frame,
                    text="Empty\n\nClick to equip",
                    font=('Consolas', 8),
                    bg='#1a1a1a',
                    fg='#666666',
                    justify='center'
                )
                empty_label.pack(pady=5)
                
                equip_btn = tk.Button(
                    slot_frame,
                    text="➕",
                    command=lambda s=slot: self.manage_rune_slot_inline(unit_idx, s),
                    font=('Consolas', 8),
                    bg='#333333',
                    fg='white',
                    width=6
                )
                equip_btn.pack()
                
        # Configure grid weights
        for row in range(3):
            slots_grid.grid_rowconfigure(row, weight=1)
        for col in range(2):
            slots_grid.grid_columnconfigure(col, weight=1)
        
        # Right section - Set effects and available runes
        right_frame = tk.Frame(main_frame, bg='black')
        right_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Set effects display
        sets_frame = tk.LabelFrame(
            right_frame,
            text="Active Set Effects",
            font=self.body_font,
            bg='black',
            fg='#66FFCC'
        )
        sets_frame.pack(fill='x', pady=5)
        
        equipped_runes = []
        for slot, rune_id in unit.get('runes', {}).items():
            rune = next((r for r in self.player_runes if r["id"] == rune_id), None)
            if rune:
                equipped_runes.append(rune)
        
        if equipped_runes:
            active_sets = self.get_active_set_names(equipped_runes)
            if active_sets:
                for set_name in active_sets:
                    set_info = self.rune_sets.get(set_name, {})
                    effect_desc = set_info.get('effect', 'Unknown effect')
                    pieces_req = set_info.get('pieces', 2)
                    
                    set_label = tk.Label(
                        sets_frame,
                        text=f"🌟 {set_name} ({pieces_req}-Set): {effect_desc}",
                        font=self.small_font,
                        bg='black',
                        fg='#66FFCC',
                        anchor='w'
                    )
                    set_label.pack(anchor='w', padx=10, pady=2)
            else:
                no_sets_label = tk.Label(
                    sets_frame,
                    text="No set effects active",
                    font=self.small_font,
                    bg='black',
                    fg='#666666'
                )
                no_sets_label.pack(padx=10, pady=10)
        else:
            no_runes_label = tk.Label(
                sets_frame,
                text="No runes equipped",
                font=self.small_font,
                bg='black',
                fg='#666666'
            )
            no_runes_label.pack(padx=10, pady=10)
        
        # Quick actions
        actions_frame = tk.LabelFrame(
            right_frame,
            text="Quick Actions",
            font=self.body_font,
            bg='black',
            fg='#FFCC66'
        )
        actions_frame.pack(fill='x', pady=5)
        
        actions_btn_frame = tk.Frame(actions_frame, bg='black')
        actions_btn_frame.pack(pady=10)
        
        # Auto-equip best runes for this unit
        auto_equip_btn = tk.Button(
            actions_btn_frame,
            text="🤖 Auto-Equip Best",
            command=lambda: self.auto_equip_unit_runes(unit_idx),
            font=self.body_font,
            bg='#006600',
            fg='white',
            width=15
        )
        auto_equip_btn.pack(side='left', padx=5)
        
        # Unequip all
        unequip_all_btn = tk.Button(
            actions_btn_frame,
            text="🗑️ Unequip All",
            command=lambda: self.unequip_all_runes(unit_idx),
            font=self.body_font,
            bg='#CC3300',
            fg='white',
            width=15
        )
        unequip_all_btn.pack(side='left', padx=5)
        
        # Back button
        back_btn = tk.Button(
            self.content_frame,
            text="🔙 Back to Unit Details",
            command=lambda: self.show_unit_details_inline(unit_idx),
            font=self.body_font,
            bg='#666666',
            fg='white'
        )
        back_btn.pack(pady=10)
    
    def auto_equip_unit_runes(self, unit_idx):
        """Auto-equip best available runes for a single unit"""
        if unit_idx >= len(self.player_inventory):
            return
            
        unit = self.player_inventory[unit_idx]
        unit_name = unit['entity']['name']
        
        # Define optimal stat priorities for different unit types
        unit_priorities = {
            "Jeff the Killer": ["Crit Rate", "Crit Damage", "Attack%", "Speed", "Attack"],
            "SCP-682": ["HP%", "Defense%", "HP", "Defense", "Attack%"],
            "Slender": ["Speed", "Accuracy", "HP%", "Evasion", "Attack%"],
            "Iris": ["Attack%", "Speed", "Accuracy", "Attack", "HP%"],
            "SCP-999": ["HP%", "Speed", "Defense%", "HP", "Defense"]
        }
        
        priorities = unit_priorities.get(unit_name, ["Attack%", "HP%", "Speed", "Defense%", "Crit Rate"])
        
        equipped_count = 0
        for slot in range(1, 7):
            compatible_runes = self.get_compatible_runes(slot)
            
            if not compatible_runes:
                continue
                
            # Score runes based on unit priorities
            best_rune = None
            best_score = 0
            
            for rune in compatible_runes:
                if rune['equipped_unit'] is not None:
                    continue
                    
                score = 0
                
                # Score main stat
                main_stat = rune['main_stat']
                if main_stat in priorities:
                    score += (10 - priorities.index(main_stat)) * 100
                
                # Score substats
                for substat in rune['substats']:
                    if substat in priorities:
                        score += (10 - priorities.index(substat)) * 10
                        
                # Bonus for higher rarity and level
                rarity_bonus = {"Common": 1, "Rare": 2, "Epic": 4, "Legendary": 8}
                score += rarity_bonus[rune['rarity']] * 5
                score += rune['level'] * 2
                
                if score > best_score:
                    best_score = score
                    best_rune = rune
                    
            # Equip the best rune found
            if best_rune:
                if self.equip_rune(unit_idx, slot, best_rune['id']):
                    equipped_count += 1
        
        if equipped_count > 0:
            self.show_notification(f"🤖 Auto-equipped {equipped_count} optimal runes for {unit_name}!")
            # Refresh the rune management interface
            self.show_unit_rune_management(unit_idx)
        else:
            self.show_notification(f"⚠️ No suitable runes available for {unit_name}")
    
    def unequip_all_runes(self, unit_idx):
        """Unequip all runes from a unit"""
        if unit_idx >= len(self.player_inventory):
            return
            
        unit = self.player_inventory[unit_idx]
        
        if not unit.get('runes'):
            self.show_notification("⚠️ No runes equipped on this unit")
            return
            
        # Confirm action
        if not messagebox.askyesno("Confirm Unequip", 
                                  f"Are you sure you want to unequip all runes from {unit['entity']['name']}?"):
            return
        
        unequipped_count = 0
        slots_to_clear = list(unit['runes'].keys())
        
        for slot in slots_to_clear:
            if self.unequip_rune(unit_idx, slot):
                unequipped_count += 1
        
        if unequipped_count > 0:
            self.show_notification(f"🗑️ Unequipped {unequipped_count} runes from {unit['entity']['name']}")
            # Refresh the rune management interface
            self.show_unit_rune_management(unit_idx)
        else:
            self.show_notification("❌ Failed to unequip runes")
    
    def show_unit_upgrade_interface(self, unit_idx):
        """Show unit upgrade interface with XP potions and fodder selection"""
        if unit_idx >= len(self.player_inventory):
            return
            
        unit = self.player_inventory[unit_idx]
        self.clear_content()
        
        # Title
        title_label = tk.Label(
            self.content_frame,
            text=f"⭐ UPGRADE {unit['entity']['name'].upper()} ⭐",
            font=self.title_font,
            bg='black',
            fg='#FFCC66'
        )
        title_label.pack(pady=20)
        
        # Current unit info
        info_frame = tk.LabelFrame(
            self.content_frame,
            text="Current Stats",
            font=self.header_font,
            bg='black',
            fg='#66FF66'
        )
        info_frame.pack(fill='x', padx=50, pady=10)
        
        current_stats = self.calculate_unit_level_stats(unit)
        info_text = f"Level: {unit['level']} | EXP: {unit['exp']}\n"
        info_text += f"HP: {current_stats['hp']} | ATK: {current_stats['attack']} | DEF: {current_stats['defense']}\n"
        info_text += f"SP Cap: {current_stats['sp_cap']}"
        
        info_label = tk.Label(
            info_frame,
            text=info_text,
            font=self.body_font,
            bg='black',
            fg='white'
        )
        info_label.pack(pady=10)
        
        # XP Potions upgrade section
        xp_frame = tk.LabelFrame(
            self.content_frame,
            text="🧪 XP Potions Upgrade",
            font=self.header_font,
            bg='black',
            fg='#66CCFF'
        )
        xp_frame.pack(fill='x', padx=50, pady=10)
        
        xp_potions = [
            ("Small XP Pot", 100, "Small XP Pot"),
            ("Medium XP Pot", 500, "Medium XP Pot"),
            ("Large XP Pot", 2000, "Large XP Pot")
        ]
        
        for pot_name, exp_value, item_key in xp_potions:
            pot_frame = tk.Frame(xp_frame, bg='black')
            pot_frame.pack(fill='x', padx=20, pady=5)
            
            available = self.player_items.get(item_key, 0)
            pot_label = tk.Label(
                pot_frame,
                text=f"{pot_name}: {available} available (+{exp_value} EXP each)",
                font=self.body_font,
                bg='black',
                fg='white'
            )
            pot_label.pack(side='left')
            
            if available > 0:
                use_btn = tk.Button(
                    pot_frame,
                    text=f"Use 1 {pot_name}",
                    command=lambda p=pot_name, e=exp_value, k=item_key: self.use_xp_potion(unit_idx, p, e, k),
                    font=self.small_font,
                    bg='#006600',
                    fg='white'
                )
                use_btn.pack(side='right', padx=10)
        
        # Fodder upgrade section
        fodder_frame = tk.LabelFrame(
            self.content_frame,
            text="🍖 Fodder Upgrade",
            font=self.header_font,
            bg='black',
            fg='#FFCC66'
        )
        fodder_frame.pack(fill='both', expand=True, padx=50, pady=10)
        
        fodder_info = tk.Label(
            fodder_frame,
            text="Select units to use as fodder (they will be consumed for EXP)",
            font=self.body_font,
            bg='black',
            fg='#CCCCCC'
        )
        fodder_info.pack(pady=5)
        
        # Available units for fodder (exclude the unit being upgraded)
        available_units = [u for i, u in enumerate(self.player_inventory) if i != unit_idx]
        
        if not available_units:
            no_fodder_label = tk.Label(
                fodder_frame,
                text="No units available for fodder",
                font=self.body_font,
                bg='black',
                fg='#666666'
            )
            no_fodder_label.pack(pady=20)
        else:
            # Scrollable fodder selection
            canvas = tk.Canvas(fodder_frame, bg='black', highlightthickness=0, height=200)
            scrollbar = ttk.Scrollbar(fodder_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg='black')
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
            scrollbar.pack(side="right", fill="y", pady=5)
            
            # Display available units
            for i, fodder_unit in enumerate(available_units):
                row = i // 6
                col = i % 6
                
                # Calculate fodder EXP value (based on level and rarity)
                rarity_multiplier = {"Common": 1, "Rare": 2, "Epic": 4, "Legendary": 8}
                fodder_exp = fodder_unit['level'] * 50 * rarity_multiplier.get(fodder_unit['entity']['rarity'], 1)
                
                fodder_btn = tk.Button(
                    scrollable_frame,
                    text=f"{fodder_unit['entity']['name']}\nLv.{fodder_unit['level']} (+{fodder_exp} EXP)",
                    command=lambda f=fodder_unit, e=fodder_exp: self.use_fodder_unit(unit_idx, f, e),
                    font=self.small_font,
                    bg=self.rarity_colors[fodder_unit['entity']['rarity']],
                    fg='black' if fodder_unit['entity']['rarity'] in ['Common', 'Rare'] else 'white',
                    width=15,
                    height=3
                )
                fodder_btn.grid(row=row, column=col, padx=2, pady=2)
            
            # Configure grid
            for col in range(6):
                scrollable_frame.grid_columnconfigure(col, weight=1)
        
        # Back button
        back_btn = tk.Button(
            self.content_frame,
            text="🔙 Back to Unit Details",
            command=lambda: self.show_unit_details_inline(unit_idx),
            font=self.body_font,
            bg='#666666',
            fg='white'
        )
        back_btn.pack(pady=20)
    
    def use_xp_potion(self, unit_idx, potion_name, exp_value, item_key):
        """Use an XP potion on a unit"""
        if self.player_items.get(item_key, 0) <= 0:
            self.show_notification(f"❌ No {potion_name} available!")
            return
        
        unit = self.player_inventory[unit_idx]
        self.player_items[item_key] -= 1
        unit['exp'] += exp_value
        
        # Handle level ups
        levels_gained = 0
        while unit['exp'] >= (unit['level'] * 100):
            unit['exp'] -= (unit['level'] * 100)
            unit['level'] += 1
            levels_gained += 1
        
        if levels_gained > 0:
            self.show_notification(f"✨ {unit['entity']['name']} gained {levels_gained} level(s)! Now level {unit['level']}")
        else:
            self.show_notification(f"⭐ {unit['entity']['name']} gained {exp_value} EXP")
        
        # Refresh the upgrade interface
        self.show_unit_upgrade_interface(unit_idx)
    
    def use_fodder_unit(self, unit_idx, fodder_unit, fodder_exp):
        """Use a unit as fodder"""
        # Confirmation dialog
        if not messagebox.askyesno("Confirm Fodder", 
                                  f"Are you sure you want to use {fodder_unit['entity']['name']} (Lv.{fodder_unit['level']}) as fodder?\n\nThis will permanently remove the unit and grant {fodder_exp} EXP."):
            return
        
        # Get the target unit by reference before removing fodder
        target_unit = self.player_inventory[unit_idx]
        target_unit_name = target_unit['entity']['name']  # Store name for logging
        
        # Find the index of the fodder unit to ensure correct removal
        fodder_idx = None
        for i, inventory_unit in enumerate(self.player_inventory):
            if inventory_unit is fodder_unit:  # Use 'is' for object identity
                fodder_idx = i
                break
        
        if fodder_idx is None:
            self.show_notification("❌ Error: Fodder unit not found in inventory")
            return
        
        # Remove fodder unit using the found index
        removed_unit = self.player_inventory.pop(fodder_idx)
        
        # Recalculate target unit index if necessary
        # If the fodder was before the target unit, the target's index shifts down by 1
        if fodder_idx < unit_idx:
            new_unit_idx = unit_idx - 1
        else:
            new_unit_idx = unit_idx
        
        # Verify we still have the correct target unit
        if new_unit_idx >= len(self.player_inventory) or self.player_inventory[new_unit_idx] is not target_unit:
            # Fallback: find the target unit by searching for the same object
            new_unit_idx = None
            for i, unit in enumerate(self.player_inventory):
                if unit is target_unit:
                    new_unit_idx = i
                    break
            
            if new_unit_idx is None:
                self.show_notification("❌ Error: Target unit lost during fodder process")
                return
        
        # Grant EXP to the target unit
        target_unit['exp'] += fodder_exp
        
        # Handle level ups
        levels_gained = 0
        while target_unit['exp'] >= (target_unit['level'] * 100):
            target_unit['exp'] -= (target_unit['level'] * 100)
            target_unit['level'] += 1
            levels_gained += 1
        
        if levels_gained > 0:
            self.show_notification(f"💀 {removed_unit['entity']['name']} consumed as fodder! {target_unit_name} gained {levels_gained} level(s)!")
        else:
            self.show_notification(f"💀 {removed_unit['entity']['name']} consumed for {fodder_exp} EXP")
        
        self.update_stats_display()
        # Refresh the upgrade interface with the corrected index
        self.show_unit_upgrade_interface(new_unit_idx)
    
    def show_rune_upgrade_interface(self, unit_idx, slot):
        """Show rune upgrade interface in unit details"""
        if unit_idx >= len(self.player_inventory):
            return
        
        unit = self.player_inventory[unit_idx]
        equipped_rune_id = unit.get('runes', {}).get(slot)
        
        if not equipped_rune_id:
            self.show_notification("❌ No rune equipped in this slot!")
            return
        
        rune = next((r for r in self.player_runes if r["id"] == equipped_rune_id), None)
        if not rune:
            self.show_notification("❌ Rune not found!")
            return
        
        # Clear content and show rune upgrade interface
        self.clear_content()
        
        title_label = tk.Label(
            self.content_frame,
            text=f"⬆️ UPGRADE RUNE ⬆️",
            font=self.title_font,
            bg='black',
            fg='#FFCC66'
        )
        title_label.pack(pady=20)
        
        # Current rune info
        rune_frame = tk.LabelFrame(
            self.content_frame,
            text=f"{rune['name']} (Level {rune['level']})",
            font=self.header_font,
            bg='black',
            fg=self.rarity_colors[rune['rarity']]
        )
        rune_frame.pack(fill='x', padx=50, pady=20)
        
        # Rune details
        details_text = f"Type: {rune['type']} {self.rune_types[rune['type']]['icon']}\n"
        details_text += f"Rarity: {rune['rarity']}\n"
        details_text += f"Set: {rune.get('set', 'None')}\n"
        details_text += f"Main Stat: {rune['main_stat']} +{rune['main_value']}\n\n"
        details_text += "Substats:\n"
        for substat, value in rune['substats'].items():
            details_text += f"  • {substat}: +{value}\n"
        
        details_label = tk.Label(
            rune_frame,
            text=details_text,
            font=self.body_font,
            bg='black',
            fg='white',
            justify='left'
        )
        details_label.pack(padx=20, pady=15)
        
        # Upgrade options
        upgrade_frame = tk.LabelFrame(
            self.content_frame,
            text="Upgrade Options",
            font=self.header_font,
            bg='black',
            fg='#66CCFF'
        )
        upgrade_frame.pack(fill='x', padx=50, pady=20)
        
        if rune['level'] >= 15:
            max_label = tk.Label(
                upgrade_frame,
                text="✨ This rune is already at maximum level! ✨",
                font=self.header_font,
                bg='black',
                fg='#FFD700'
            )
            max_label.pack(pady=20)
        else:
            upgrade_cost = rune['level'] * 1000
            cost_label = tk.Label(
                upgrade_frame,
                text=f"Upgrade Cost: {upgrade_cost} 🪙",
                font=self.body_font,
                bg='black',
                fg='#FFCC66'
            )
            cost_label.pack(pady=10)
            
            # Preview next level stats
            preview_text = "After upgrade:\n"
            preview_text += f"Level: {rune['level']} → {rune['level'] + 1}\n"
            preview_text += f"Main Stat: {rune['main_stat']} +{rune['main_value']} → +{int(rune['main_value'] * 1.1)}\n"
            
            preview_label = tk.Label(
                upgrade_frame,
                text=preview_text,
                font=self.body_font,
                bg='black',
                fg='#66FF66'
            )
            preview_label.pack(pady=5)
            
            # Upgrade button
            if self.player_cash >= upgrade_cost:
                upgrade_btn = tk.Button(
                    upgrade_frame,
                    text="⬆️ Upgrade Rune",
                    command=lambda: self.upgrade_rune_inline(rune, unit_idx, slot),
                    font=self.body_font,
                    bg='#006600',
                    fg='white'
                )
                upgrade_btn.pack(pady=10)
            else:
                insufficient_label = tk.Label(
                    upgrade_frame,
                    text="❌ Insufficient cash for upgrade",
                    font=self.body_font,
                    bg='black',
                    fg='#FF6666'
                )
                insufficient_label.pack(pady=10)
        
        # Back button
        back_btn = tk.Button(
            self.content_frame,
            text="🔙 Back to Unit Details",
            command=lambda: self.show_unit_details_inline(unit_idx),
            font=self.body_font,
            bg='#666666',
            fg='white'
        )
        back_btn.pack(pady=20)
    
    def upgrade_rune_inline(self, rune, unit_idx, slot):
        """Upgrade rune in the inline interface"""
        upgrade_cost = rune['level'] * 1000
        
        if self.player_cash < upgrade_cost:
            self.show_notification(f"❌ Need {upgrade_cost} cash to upgrade this rune!")
            return
        
        if rune['level'] >= 15:
            self.show_notification("⚠️ Rune is already at maximum level!")
            return
        
        # Perform upgrade
        self.player_cash -= upgrade_cost
        rune['level'] += 1
        
        # Increase main stat by 10%
        rune['main_value'] = int(rune['main_value'] * 1.1)
        
        # 25% chance to upgrade each substat by 5%
        for substat in rune['substats']:
            if random.randint(1, 100) <= 25:
                rune['substats'][substat] = int(rune['substats'][substat] * 1.05)
        
        self.show_notification(f"✨ {rune['name']} upgraded to level {rune['level']}!")
        self.update_stats_display()
        
        # Refresh the rune upgrade interface
        self.show_rune_upgrade_interface(unit_idx, slot)
    
    def show_set_effects_display(self, unit):
        """Display active rune set effects for a unit"""
        equipped_runes = []
        for slot, rune_id in unit.get('runes', {}).items():
            rune = next((r for r in self.player_runes if r["id"] == rune_id), None)
            if rune:
                equipped_runes.append(rune)
        
        if not equipped_runes:
            return "No set effects active"
        
        active_sets = self.get_active_set_names(equipped_runes)
        
        if not active_sets:
            return "No set effects active"
        
        set_text = "Active Set Effects:\n"
        for set_name in active_sets:
            set_info = self.rune_sets.get(set_name, {})
            effect_desc = set_info.get('effect', 'Unknown effect')
            set_text += f"• {set_name}: {effect_desc}\n"
        
        return set_text.strip()

    def setup_autosave(self):
        """Setup autosave timer"""
        # Save every 2 minutes
        self.root.after(120000, self.autosave_game_data)  # 2 minutes
    
    def autosave_game_data(self):
        """Auto-save game data periodically"""
        try:
            # Only autosave if user is logged in
            if self.current_user:
                self.save_game_data()
                self.show_notification("💾 Game auto-saved")
        except Exception as e:
            self.show_notification(f"❌ Auto-save failed: {str(e)}", '#FF6666')
        
        # Schedule next autosave
        self.root.after(120000, self.autosave_game_data)
    
    def save_game_data(self):
        """Save game data to file with backward compatibility"""
        # Use account-specific saving for players
        if self.current_user and not self.current_user.get('is_developer'):
            self.save_player_account()
            return
            
        # Developer account uses main save file
        save_data = {
            "version": "1.1",
            "player_gems": self.player_gems,
            "player_cash": self.player_cash,
            "player_level": self.player_level,
            "player_xp": self.player_xp,
            "player_inventory": self.player_inventory,
            "player_items": self.player_items,
            "player_runes": self.player_runes,
            "player_progress": self.player_progress,
            "player_facilities": self.player_facilities,
            "player_research": self.player_research,
            "current_user": self.current_user
        }
        
        # Ensure save directory exists
        os.makedirs("saves", exist_ok=True)
        
        # Save to file
        with open("saves/nightmare_nexus_save.json", "w") as f:
            json.dump(save_data, f, indent=2)
    
    def load_game_data(self):
        """Load game data from file with backward compatibility"""
        try:
            if os.path.exists("saves/nightmare_nexus_save.json"):
                with open("saves/nightmare_nexus_save.json", "r") as f:
                    save_data = json.load(f)
                
                # Load data with backward compatibility
                self.player_gems = save_data.get("player_gems", 100)
                self.player_cash = save_data.get("player_cash", 500)
                self.player_level = save_data.get("player_level", 1)
                self.player_xp = save_data.get("player_xp", 0)
                self.player_inventory = save_data.get("player_inventory", [])
                self.player_items = save_data.get("player_items", {"Small XP Pot": 0, "Medium XP Pot": 0, "Large XP Pot": 0})
                self.player_runes = save_data.get("player_runes", [])
                self.player_progress = save_data.get("player_progress", {
                    "world": 0,
                    "stage": 0,
                    "unlocked": [[1] + [0]*19] + [[0]*20 for _ in range(4)],
                    "dungeon_highest": 1
                })
                self.player_facilities = save_data.get("player_facilities", {})
                self.player_research = save_data.get("player_research", {})
                self.current_user = save_data.get("current_user", None)
                
                # Ensure backward compatibility for new rune format
                for rune in self.player_runes:
                    if "set" not in rune:
                        rune["set"] = random.choice(list(self.rune_sets.keys()))
                
                # Ensure backward compatibility for units with new level scaling
                for unit in self.player_inventory:
                    if "runes" not in unit:
                        unit["runes"] = {}
                
                print(f"✅ Game data loaded from save file")
        except Exception as e:
            print(f"⚠️ Could not load save data: {e}. Starting with default data.")

def main():
    """Main entry point"""
    app = NightmareNexusGUI()
    app.run()

if __name__ == "__main__":
    main()
