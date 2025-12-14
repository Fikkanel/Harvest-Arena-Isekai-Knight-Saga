import pygame
import sys
import random
import math
import array
import json
import os
import threading
import google.generativeai as genai

# ==============================================================================
#  HARVEST ARENA: ISEKAI KNIGHT SAGA
#  UAS PEMROGRAMAN BERORIENTASI OBJEK (PBO) - 2025
# ==============================================================================

# --- INTEGRASI GOOGLE GEMINI AI ---
# Dapatkan API Key gratis di: https://aistudio.google.com/app/apikey
GEMINI_API_KEY = "INI-DIISI-API-SEHARUSNYA" 

AI_AVAILABLE = False
try:
    if GEMINI_API_KEY != "ISI_API_KEY_GEMINI_DISINI":
        genai.configure(api_key=GEMINI_API_KEY)
        # Menggunakan model flash agar lebih cepat dan hemat
        AI_MODEL = genai.GenerativeModel('gemini-2.5-flash-lite') 
        AI_AVAILABLE = True
        print("System: Gemini AI Connected.")
    else:
        print("System: API Key not set. Offline Mode.")
except Exception as e:
    print(f"System: AI Init Failed ({e}). Offline Mode.")


# --- KONSTANTA & KONFIGURASI ---
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
pygame.mixer.init()

# Resolusi Logika Game
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600

# Setup Window
WINDOW = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Harvest Arena: Isekai Knight Saga (UAS Final Project)")

# Canvas Virtual
SCREEN = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

# Variabel Global
GLOBAL_SCALE = 1.0
GLOBAL_OFFSET = (0, 0)
MENU_BGM = "ASSETS/menu_theme.mp3" 

# Pengaturan Grid Map
TILE_SIZE = 50
MAP_WIDTH = 60  
MAP_HEIGHT = 40 

# Definisi Warna (RGB)
C_BG_DARK = (20, 20, 30)
C_UI_BG = (30, 35, 45, 240)       
C_UI_BORDER = (200, 180, 100)     
C_ACCENT_GOLD = (255, 215, 0)
C_ACCENT_HOVER = (255, 230, 100)
C_TEXT_WHITE = (240, 240, 240)
C_TEXT_GREY = (180, 180, 180)
C_BTN_NORMAL = (50, 50, 60)
C_BTN_HOVER = (70, 70, 80)
C_BTN_CLICK = (40, 40, 50)
C_BAR_HP = (220, 60, 60)
C_BAR_MANA = (60, 100, 220)
C_BAR_STAMINA = (0, 180, 255) 
C_BAR_HUNGER = (255, 140, 0)
C_BAR_BG = (40, 40, 40)
C_BG_NIGHT_TOP = (10, 15, 30)
C_BG_NIGHT_BOT = (40, 30, 60)
C_MOON = (255, 255, 220)
C_ARENA_TOP = (60, 60, 70)
C_ARENA_SIDE = (40, 40, 50)

# Pengaturan Font
FONT_UI_SMALL = pygame.font.SysFont("Segoe UI", 12)
FONT_UI = pygame.font.SysFont("Segoe UI", 14)
FONT_BOLD = pygame.font.SysFont("Segoe UI", 16, bold=True)
FONT_BIG = pygame.font.SysFont("Segoe UI", 24, bold=True)
FONT_TITLE = pygame.font.SysFont("Gabriola", 60, bold=True) 
FONT_STORY = pygame.font.SysFont("Gabriola", 40, italic=True) 
FONT_DMG = pygame.font.SysFont("Impact", 35)

# Mesin State Game
STATE_MAIN_MENU = 0
STATE_OVERWORLD = 1
STATE_BATTLE = 2
STATE_SHOP = 3
STATE_INVENTORY = 4
STATE_PAUSE = 5
STATE_SETTINGS = 6
STATE_PROLOGUE = 7 
STATE_INPUT_NAME = 8 
STATE_LOAD_MENU = 9 


# --- FUNGSI BANTUAN UI (HELPER) ---
def get_corrected_mouse():
    mx, my = pygame.mouse.get_pos()
    gx = (mx - GLOBAL_OFFSET[0]) / GLOBAL_SCALE
    gy = (my - GLOBAL_OFFSET[1]) / GLOBAL_SCALE
    return gx, gy

def update_scale():
    global GLOBAL_SCALE, GLOBAL_OFFSET
    window_w, window_h = WINDOW.get_size()
    scale_w = window_w / SCREEN_WIDTH
    scale_h = window_h / SCREEN_HEIGHT
    GLOBAL_SCALE = min(scale_w, scale_h)
    new_w = int(SCREEN_WIDTH * GLOBAL_SCALE)
    new_h = int(SCREEN_HEIGHT * GLOBAL_SCALE)
    off_x = (window_w - new_w) // 2
    off_y = (window_h - new_h) // 2
    GLOBAL_OFFSET = (off_x, off_y)

update_scale()


# --- DATABASE ITEM ---
ITEM_DATA = {
    "Hoe": {"sell": 0, "type": "Tool", "eat": 0},
    "Watering Can": {"sell": 0, "type": "Tool", "eat": 0},
    "Grape": {"sell": 60, "type": "Crop", "eat": 25},
    "Mushroom": {"sell": 120, "type": "Crop", "eat": 40},
    "Potato": {"sell": 80, "type": "Crop", "eat": 30},
    "Carrot": {"sell": 120, "type": "Crop", "eat": 40},
    "Grape Seed": {"sell": 20, "type": "Seed", "eat": 0},
    "Mushroom Seed": {"sell": 40, "type": "Seed", "eat": 0},
    "Potato Seed": {"sell": 20, "type": "Seed", "eat": 0},
    "Carrot Seed": {"sell": 25, "type": "Seed", "eat": 0},
    "Slime Gel": {"sell": 30, "type": "Loot", "eat": 0},
    "Wolf Fang": {"sell": 80, "type": "Loot", "eat": 0},
    "Magic Dust": {"sell": 200, "type": "Loot", "eat": 0},
    "Dark Essence": {"sell": 250, "type": "Loot (Rare)", "eat": 0},
    "Gold Nugget": {"sell": 500, "type": "Loot (Ultra)", "eat": 0},
    "Potion": {"sell": 50, "type": "Consumable", "eat": 0}, 
    "Coffee": {"sell": 20, "type": "Consumable", "eat": 0}, 
    "Elixir": {"sell": 150, "type": "Consumable", "eat": 0} 
}

NAME_TO_CODE = {
    "Hoe": "HOE", "Watering Can": "WATER",
    "Grape Seed": "SEED_GRAPE", "Mushroom Seed": "SEED_MUSHROOM",
    "Potato Seed": "SEED_POTATO", "Carrot Seed": "SEED_CARROT",
    "Grape": "CROP_GRAPE", "Mushroom": "CROP_MUSHROOM", 
    "Potato": "CROP_POTATO", "Carrot": "CROP_CARROT",   
    "Potion": "POTION", "Coffee": "COFFEE", "Elixir": "ELIXIR"
}
CODE_TO_NAME = {v: k for k, v in NAME_TO_CODE.items()}

SHOP_INVENTORY = {
    "SEEDS": [("Grape Seed", 20), ("Mushroom Seed", 60), ("Potato Seed", 40), ("Carrot Seed", 50)],
    "ITEMS": [("Potion", 100), ("Coffee", 80), ("Elixir", 300)],
    "LOOT": [("Slime Gel", 100), ("Wolf Fang", 250), ("Magic Dust", 600), ("Dark Essence", 1500), ("Gold Nugget", 5000)],
    "CROPS": [("Grape", 100), ("Mushroom", 300), ("Potato", 160), ("Carrot", 240)]
}


# --- MANAJEMEN ASET ---
ASSETS = {}
def load_assets():
    def load_scale(path, size=None):
        try:
            img = pygame.image.load(path).convert_alpha()
            if size: 
                img = pygame.transform.scale(img, size)
            return img
        except:
            s = pygame.Surface(size if size else (50,50))
            s.fill((255, 0, 255))
            return s

    ASSETS["menu_frames"] = []
    for i in range(21):
        filename = f"ASSETS/home/home-{i:03d}.jpg" 
        try:
            if os.path.exists(filename):
                img = pygame.image.load(filename).convert()
                ASSETS["menu_frames"].append(pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT)))
        except: 
            pass
            
    if not ASSETS["menu_frames"]:
        f = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        f.fill(C_BG_DARK)
        ASSETS["menu_frames"].append(f)

    ASSETS["grass"] = load_scale("ASSETS/tile_grass.png", (TILE_SIZE, TILE_SIZE))
    ASSETS["dirt"] = load_scale("ASSETS/tile_dirt.png", (TILE_SIZE, TILE_SIZE))
    ASSETS["water"] = load_scale("ASSETS/tile_water.png", (TILE_SIZE, TILE_SIZE))
    ASSETS["sand"] = load_scale("ASSETS/tile_sand.png", (TILE_SIZE, TILE_SIZE))
    ASSETS["forest_bg"] = load_scale("ASSETS/tile_forest.png", (TILE_SIZE, TILE_SIZE))
    ASSETS["tilled"] = load_scale("ASSETS/tile_tilled.png", (TILE_SIZE, TILE_SIZE))
    ASSETS["watered"] = load_scale("ASSETS/tile_watered.png", (TILE_SIZE, TILE_SIZE))
    ASSETS["tree"] = load_scale("ASSETS/obj_tree.png", (100, 100)) 
    ASSETS["house"] = load_scale("ASSETS/obj_house.png", (250, 250))
    ASSETS["hero_battle"] = load_scale("ASSETS/hero_battle_idle.png", (200, 200))
    
    if os.path.exists("ASSETS/hero_ow_walk.png"):
        ASSETS["hero_walk"] = pygame.image.load("ASSETS/hero_ow_walk.png").convert_alpha()
    else:
        ASSETS["hero_walk"] = pygame.Surface((40,40))

    ASSETS["crops"] = {}
    def load_custom_strip(filename, frame_w, frame_h, scale_size):
        path = os.path.join("ASSETS", "crops", filename)
        if not os.path.exists(path): path = filename 
        if not os.path.exists(path): return None
        try:
            sheet = pygame.image.load(path).convert_alpha()
            frames = []
            for i in range(4):
                surf = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
                surf.blit(sheet, (0, 0), (i * frame_w, 0, frame_w, frame_h))
                frames.append(pygame.transform.scale(surf, scale_size))
            return frames
        except: return None

    ASSETS["crops"]["Grape"] = load_custom_strip("grape.png", 32, 48, (40, 60))
    ASSETS["crops"]["Mushroom"] = load_custom_strip("mushroom.png", 16, 32, (30, 50))
    ASSETS["crops"]["Carrot"] = load_custom_strip("carrots.png", 16, 32, (30, 50))
    ASSETS["crops"]["Potato"] = load_custom_strip("potato.png", 16, 32, (30, 50))
    
    try:
        slime_sheet = pygame.image.load("ASSETS/enemy/slime.png").convert_alpha()
        frames_battle = [pygame.transform.scale(slime_sheet.subsurface((i*32, 0, 32, 32)), (160, 160)) for i in range(8)]
        frames_ow = [pygame.transform.scale(slime_sheet.subsurface((i*32, 0, 32, 32)), (50, 50)) for i in range(8)]
        ASSETS["Slime_battle"] = frames_battle
        ASSETS["Slime_ow"] = frames_ow
    except: pass
    
    try:
        golem_sheet = pygame.image.load("ASSETS/enemy/golem.png").convert_alpha()
        frames_battle = [pygame.transform.scale(golem_sheet.subsurface((i*64, 0, 64, 64)), (200, 200)) for i in range(18)]
        frames_ow = [pygame.transform.scale(golem_sheet.subsurface((i*64, 0, 64, 64)), (60, 60)) for i in range(18)]
        ASSETS["Golem_battle"] = frames_battle
        ASSETS["Golem_ow"] = frames_ow
    except: pass

load_assets()


# --- SISTEM QUEST ---
class Quest:
    def __init__(self, q_id, desc, target_val, q_type, target_name):
        self.id = q_id
        self.desc = desc
        self.target_val = target_val
        self.current_val = 0
        self.type = q_type 
        self.target_name = target_name
        self.completed = False

    def check_progress(self, p_type, p_name):
        if not self.completed and self.type == p_type and self.target_name == p_name:
            self.current_val += 1
            if self.current_val >= self.target_val:
                self.completed = True
                return True
        return False


# --- DATABASE QUEST OFFLINE (BAHASA INDONESIA) ---
OFFLINE_QUESTS_DB = [
    Quest(1, "Panen 2 Anggur", 2, "harvest", "Grape"),
    Quest(2, "Kalahkan 2 Slime", 2, "kill", "Slime"),
    Quest(3, "Panen 3 Wortel", 3, "harvest", "Carrot"),
    Quest(4, "Kalahkan 1 Golem", 1, "kill", "Golem"),
    Quest(5, "Panen 5 Kentang", 5, "harvest", "Potato"),
]


# --- [PBO: ENKAPSULASI] STATISTIK PEMAIN ---
class PlayerStats:
    def __init__(self):
        self.player_name = "Player"
        self.reset()
        
    def reset(self):
        self._level = 1
        self._xp = 0
        self._xp_next = 100
        self._gold = 500
        self._max_hp = 300
        self._hp = 300
        self._max_mana = 150
        self._mana = 150
        self._stamina = 100
        self._max_stamina = 100
        self._hunger = 100
        self._max_hunger = 100
        self.day = 1
        self.water_current = 20
        self.water_max = 20
        
        self.inventory = {
            "Hoe": 1, "Watering Can": 1, "Grape Seed": 2, "Potion": 1, "Coffee": 1
        }
        
        # --- SISTEM QUEST HYBRID (AI + OFFLINE) ---
        self.current_active_quest = None
        self.offline_quest_index = 0
        self.is_generating_quest = False
        
        # Load quest pertama
        self.load_next_quest()

    # Properties untuk Encapsulation
    @property
    def hp(self): return self._hp
    @hp.setter
    def hp(self, val): self._hp = max(0, min(self._max_hp, val))
        
    @property
    def max_hp(self): return self._max_hp
    @max_hp.setter
    def max_hp(self, val): self._max_hp = val
    
    @property
    def mana(self): return self._mana
    @mana.setter
    def mana(self, val): self._mana = max(0, min(self._max_mana, val))

    @property
    def gold(self): return self._gold
    @gold.setter
    def gold(self, val): self._gold = max(0, val)
    
    @property
    def stamina(self): return self._stamina
    @stamina.setter
    def stamina(self, val): self._stamina = max(0, min(self._max_stamina, val))

    @property
    def hunger(self): return self._hunger
    @hunger.setter
    def hunger(self, val): self._hunger = max(0, min(self._max_hunger, val))
    
    @property
    def level(self): return self._level
    @level.setter
    def level(self, val): self._level = val
    
    @property
    def xp(self): return self._xp
    @xp.setter
    def xp(self, val): self._xp = val
    
    @property
    def xp_next(self): return self._xp_next
    @xp_next.setter
    def xp_next(self, val): self._xp_next = val
    
    @property
    def max_mana(self): return self._max_mana
    @max_mana.setter
    def max_mana(self, val): self._max_mana = val
    
    @property
    def max_stamina(self): return self._max_stamina
    @max_stamina.setter
    def max_stamina(self, val): self._max_stamina = val
    
    @property
    def max_hunger(self): return self._max_hunger
    @max_hunger.setter
    def max_hunger(self, val): self._max_hunger = val

    # --- LOGIKA QUEST BARU ---
    def get_current_quest(self):
        return self.current_active_quest

    def load_next_quest(self):
        """Mencoba load quest baru. Prioritas: AI -> Offline -> Kosong."""
        if self.current_active_quest and not self.current_active_quest.completed:
            return # Masih ada quest aktif

        # Jika AI tersedia dan terhubung internet, coba generate
        if AI_AVAILABLE:
            if not self.is_generating_quest:
                self.is_generating_quest = True
                threading.Thread(target=self._fetch_ai_quest_worker).start()
        else:
            self._load_offline_quest()

    def _load_offline_quest(self):
        """Fallback ke quest offline jika AI mati/error."""
        if self.offline_quest_index < len(OFFLINE_QUESTS_DB):
            q_data = OFFLINE_QUESTS_DB[self.offline_quest_index]
            self.current_active_quest = Quest(900+self.offline_quest_index, q_data.desc, q_data.target_val, q_data.type, q_data.target_name)
            self.offline_quest_index += 1
            print("System: Loaded Offline Quest")
        else:
            self.current_active_quest = None 
            print("System: Offline Quests Exhausted")

    def _fetch_ai_quest_worker(self):
        """Worker thread untuk memanggil Gemini API."""
        try:
            # --- PROMPT AI DIPERKETAT UNTUK FOKUS PANEN DAN KILL ---
            prompt = f"""
            You are a strict quest generator API for a survival RPG.
            
            Game Context: A solitary survival RPG.
            Current Player Level: {self.level}
            
            STRICT INSTRUCTION: Generate a quest ONLY for 'harvest' or 'kill'.
            
            ALLOWED TARGETS (Exact spelling required):
            - For 'harvest': Grape, Mushroom, Potato, Carrot
            - For 'kill': Slime, Golem
            
            Response Format (JSON ONLY):
            {{
                "desc": "Singkat, Padat, Bahasa Indonesia (contoh: Panen 5 Anggur)",
                "target_val": <integer 3-10>,
                "type": "<harvest OR kill>",
                "target_name": "<Must be one of the ALLOWED TARGETS>"
            }}
            
            RULES:
            1. NO story, NO flavor text in JSON, NO other characters.
            2. 'type' MUST be exactly "harvest" or "kill".
            3. 'desc' MUST be in BAHASA INDONESIA.
            4. 'target_name' MUST be one of the allowed targets exactly.
            """
            
            response = AI_MODEL.generate_content(prompt)
            # Bersihkan response jika ada format markdown
            txt = response.text.strip().replace("```json", "").replace("```", "")
            data = json.loads(txt)
            
            new_quest = Quest(random.randint(1000,9999), data['desc'], data['target_val'], data['type'], data['target_name'])
            self.current_active_quest = new_quest
            print(f"System: AI Generated Quest: {data['desc']}")
            
        except Exception as e:
            print(f"System: AI Error ({e}). Switching to offline quest.")
            self._load_offline_quest()
        finally:
            self.is_generating_quest = False

    def update_quest(self, p_type, p_name):
        q = self.current_active_quest
        if q and not q.completed:
            if q.check_progress(p_type, p_name):
                reward_gold = 100 + (self.level * 20)
                reward_xp = 50 + (self.level * 10)
                self.gold += reward_gold
                self.xp += reward_xp
                
                msg = f"Quest Done! +{reward_gold}G +{reward_xp}XP"
                
                self.current_active_quest = None
                self.load_next_quest()
                
                return msg
        return None

    def add_xp(self, amount):
        self.xp += amount
        leveled_up = False
        while self.xp >= self.xp_next:
            self.xp -= self.xp_next
            self.level += 1
            self.xp_next = int(self.xp_next * 1.5)
            self.max_hp += 50
            self.max_mana += 20
            self.max_stamina += 10
            self.hp = self.max_hp
            self.mana = self.max_mana
            self.stamina = self.max_stamina
            leveled_up = True
        return leveled_up
    
    def to_dict(self):
        return {
            "player_name": self.player_name, 
            "level": self.level, "xp": self.xp, "xp_next": self.xp_next, 
            "gold": self.gold, "max_hp": self.max_hp, "hp": self.hp, 
            "max_mana": self.max_mana, "mana": self.mana, 
            "stamina": self.stamina, "max_stamina": self.max_stamina, 
            "hunger": self.hunger, "day": self.day, "inventory": self.inventory,
            "water_current": self.water_current,
            "offline_quest_index": self.offline_quest_index
        }
    
    def load_from_dict(self, data):
        self.player_name = data.get("player_name", "Player")
        self.level = data["level"]
        self.xp = data["xp"]
        self.xp_next = data["xp_next"]
        self.gold = data["gold"]
        self.max_hp = data["max_hp"]
        self.hp = data["hp"]
        self.max_mana = data["max_mana"]
        self.mana = data["mana"]
        self.stamina = data["stamina"]
        self.max_stamina = data["max_stamina"]
        self.hunger = data.get("hunger", 100)
        self.day = data["day"]
        self.water_current = data.get("water_current", 20)
        self.offline_quest_index = data.get("offline_quest_index", 0)
        
        saved_inv = data["inventory"]
        for k, v in saved_inv.items(): 
            self.inventory[k] = v
        
        self.current_active_quest = None
        self.load_next_quest()

GAME_STATS = PlayerStats()


# --- SISTEM SUARA ---
class SoundSynth:
    def __init__(self):
        self.sounds = {}
        self.music_vol = 0.5
        self.sfx_vol = 0.5
        self.generate_sounds()
        
    def generate_sounds(self):
        self.sounds["slash"] = self.make_noise(0.15, decay=True)
        self.sounds["hit"] = self.make_noise(0.2, pitch_shift=0.5)
        self.sounds["magic"] = self.make_tone(0.4, 440, slide=880)
        self.sounds["thunder"] = self.make_noise(0.8, pitch_shift=0.3, volume=0.8)
        self.sounds["heal"] = self.make_tone(0.5, 500, slide=600, tremolo=True)
        self.sounds["eat"] = self.make_noise(0.15, pitch_shift=1.2, volume=0.5) 
        self.sounds["battle_start"] = self.make_tone(1.0, 300, slide=100, tremolo=True)
        self.sounds["levelup"] = self.make_tone(1.5, 400, slide=800, tremolo=True)
        self.sounds["hoe"] = self.make_noise(0.1, pitch_shift=0.8, volume=0.3)
        self.sounds["water"] = self.make_noise(0.3, pitch_shift=1.5, volume=0.3)
        self.sounds["step"] = self.make_noise(0.05, volume=0.1)
        self.sounds["buy"] = self.make_tone(0.2, 1000, slide=1200)
        self.sounds["sell"] = self.make_tone(0.2, 1200, slide=1500)
        self.sounds["error"] = self.make_tone(0.2, 200, slide=150)
        self.sounds["save"] = self.make_tone(0.5, 600, slide=600, tremolo=True)
        self.sounds["select"] = self.make_tone(0.1, 800, slide=900)
        self.sounds["type"] = self.make_noise(0.02, volume=0.2) 
        
        self.set_sfx_volume(self.sfx_vol)
        self.set_music_volume(self.music_vol)
        
    def set_music_volume(self, val):
        self.music_vol = max(0.0, min(1.0, val))
        pygame.mixer.music.set_volume(self.music_vol)
        
    def set_sfx_volume(self, val):
        self.sfx_vol = max(0.0, min(1.0, val))
        for s in self.sounds.values(): 
            s.set_volume(self.sfx_vol)
            
    def make_noise(self, duration, decay=True, pitch_shift=1.0, volume=0.5):
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        buf = array.array('h', [0] * n_samples)
        for i in range(n_samples):
            val = random.randint(-32000, 32000)
            if decay: 
                val = int(val * (1 - (i / n_samples)))
            buf[i] = int(val * volume)
        return pygame.mixer.Sound(buffer=buf)
        
    def make_tone(self, duration, freq, slide=None, tremolo=False):
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        buf = array.array('h', [0] * n_samples)
        for i in range(n_samples):
            t = i / sample_rate
            cf = freq + (slide - freq) * (i / n_samples) if slide else freq
            val = 32000 * math.sin(2 * math.pi * cf * t)
            if tremolo: 
                val *= (0.5 + 0.5 * math.sin(2 * math.pi * 10 * t))
            buf[i] = int(val * 0.3)
        return pygame.mixer.Sound(buffer=buf)
        
    def play(self, name):
        if name in self.sounds: 
            self.sounds[name].play()

AUDIO = SoundSynth()


# --- FUNGSI MENGGAMBAR UI ---
def draw_text_shadow(surface, text, font, x, y, color=C_TEXT_WHITE, center=False):
    s_surf = font.render(text, True, (0, 0, 0))
    t_surf = font.render(text, True, color)
    if center:
        rect_s = s_surf.get_rect(center=(x+2, y+2))
        rect_t = t_surf.get_rect(center=(x, y))
        surface.blit(s_surf, rect_s)
        surface.blit(t_surf, rect_t)
    else:
        surface.blit(s_surf, (x+2, y+2))
        surface.blit(t_surf, (x, y))

# Fungsi untuk memecah teks panjang menjadi beberapa baris
def draw_multiline_text_shadow(surface, text, font, x, y, max_width, color=C_TEXT_WHITE, center=False):
    words = text.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        w, h = font.size(test_line)
        if w < max_width:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    lines.append(' '.join(current_line))
    
    offset_y = 0
    for line in lines:
        draw_text_shadow(surface, line, font, x, y + offset_y, color, center)
        offset_y += font.get_height()

def draw_panel(surface, rect, border=True):
    s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    s.fill(C_UI_BG)
    surface.blit(s, (rect.x, rect.y))
    if border:
        pygame.draw.rect(surface, C_UI_BORDER, rect, 2, border_radius=10)
        pygame.draw.rect(surface, (0,0,0), rect.inflate(2,2), 1, border_radius=10)

def draw_bar_fancy(surface, x, y, w, h, val, max_val, color, label=""):
    pygame.draw.rect(surface, C_BAR_BG, (x, y, w, h), border_radius=5)
    ratio = max(0, min(1, val/max_val)) if max_val > 0 else 0
    bar_w = int(w * ratio)
    if bar_w > 0:
        pygame.draw.rect(surface, color, (x, y, bar_w, h), border_radius=5)
    pygame.draw.rect(surface, (20, 20, 20), (x, y, w, h), 2, border_radius=5)
    if label:
        txt = FONT_UI_SMALL.render(f"{label}: {int(val)}/{max_val}", True, C_TEXT_WHITE)
        surface.blit(txt, (x + w//2 - txt.get_width()//2, y - 18))

def draw_premium_background(surface, shake_offset=(0,0)):
    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    h = 450
    for y in range(h):
        ratio = y / h
        r = C_BG_NIGHT_TOP[0] * (1 - ratio) + C_BG_NIGHT_BOT[0] * ratio
        g = C_BG_NIGHT_TOP[1] * (1 - ratio) + C_BG_NIGHT_BOT[1] * ratio
        b = C_BG_NIGHT_TOP[2] * (1 - ratio) + C_BG_NIGHT_BOT[2] * ratio
        pygame.draw.line(surf, (int(r), int(g), int(b)), (0, y), (SCREEN_WIDTH, y))
    
    pygame.draw.circle(surf, C_MOON, (800, 100), 60)
    pygame.draw.rect(surf, C_ARENA_TOP, (0, 450, SCREEN_WIDTH, 150))
    surface.blit(surf, shake_offset)


# --- KOMPONEN UI ---
class Button:
    def __init__(self, x, y, width, height, text, font=FONT_BOLD):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.is_hovered = False
        self.is_pressed = False

    def draw(self, surface):
        offset_y = 2 if self.is_pressed else 0
        bg_color = C_BTN_HOVER if self.is_hovered else C_BTN_NORMAL
        if self.is_pressed: 
            bg_color = C_BTN_CLICK
        
        shadow_rect = self.rect.copy()
        shadow_rect.y += 4
        pygame.draw.rect(surface, (0, 0, 0, 100), shadow_rect, border_radius=8)
        
        draw_rect = self.rect.copy()
        draw_rect.y += offset_y
        pygame.draw.rect(surface, bg_color, draw_rect, border_radius=8)
        
        border_col = C_ACCENT_HOVER if self.is_hovered else C_UI_BORDER
        pygame.draw.rect(surface, border_col, draw_rect, 2, border_radius=8)
        
        txt_col = C_ACCENT_GOLD if self.is_hovered else C_TEXT_WHITE
        draw_text_shadow(surface, self.text, self.font, draw_rect.centerx, draw_rect.centery, txt_col, center=True)

    def update(self, events):
        mx, my = get_corrected_mouse()
        self.is_hovered = self.rect.collidepoint((mx, my))
        self.is_pressed = False
        clicked = False
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
                self.is_pressed = True
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.is_hovered:
                AUDIO.play("select")
                clicked = True
        return clicked


# --- ENTITAS & PARTIKEL ---
class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color, size, life=30):
        super().__init__()
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (size//2, size//2), size//2)
        self.rect = self.image.get_rect(center=(x, y))
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.life = life
        self.orig_life = life
        
    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        self.life -= 1
        if self.orig_life > 0: 
            self.image.set_alpha(int((self.life / self.orig_life) * 255))
        if self.life <= 0: 
            self.kill()

class MenuParticle(Particle):
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(SCREEN_HEIGHT, SCREEN_HEIGHT + 100)
        self.speed = random.uniform(0.5, 2.0)
        self.size = random.randint(2, 4)
        self.color = random.choice([(255, 215, 0), (255, 255, 200), (200, 200, 255)])
        self.alpha = 0
        
    def update(self):
        self.y -= self.speed
        if self.alpha < 200 and self.y > SCREEN_HEIGHT - 100: 
            self.alpha += 2
        if self.y < 0: 
            self.reset()
            
    def draw(self, surface):
        s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, self.alpha), (self.size//2, self.size//2), self.size//2)
        surface.blit(s, (self.x, self.y))

class ProjectileWithTrail(pygame.sprite.Sprite):
    def __init__(self, start_pos, target_pos, color, particle_group, type="fire"):
        super().__init__()
        self.type = type
        self.color = color
        self.particle_group = particle_group
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        if self.type == "fire": 
            pygame.draw.circle(self.image, color, (15, 15), 15)
            pygame.draw.circle(self.image, (255, 255, 0), (15, 15), 8) 
        else: 
            pygame.draw.polygon(self.image, color, [(15,0), (5, 15), (12, 15), (10, 30), (25, 10), (18, 10)])
            
        self.rect = self.image.get_rect(center=start_pos)
        self.target = target_pos
        self.speed = 18
        
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        dist = math.hypot(dx, dy)
        
        if dist != 0: 
            self.vx = (dx / dist) * self.speed
            self.vy = (dy / dist) * self.speed
        else: 
            self.vx, self.vy = 0, 0
            
    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        
        if random.random() < 0.8:
            size = random.randint(5, 10)
            p_color = self.color if self.type == "thunder" else (255, 100, 0)
            trail = Particle(self.rect.centerx, self.rect.centery, p_color, size, life=10)
            self.particle_group.add(trail) 
            
        if math.hypot(self.rect.centerx - self.target[0], self.rect.centery - self.target[1]) < 25: 
            self.kill()

class FloatingText(pygame.sprite.Sprite):
    def __init__(self, x, y, text, color, is_crit=False):
        super().__init__()
        font = FONT_DMG if is_crit else FONT_BOLD
        text_str = str(text) + "!" if is_crit else str(text)
        
        base_txt = font.render(text_str, True, color)
        outline = font.render(text_str, True, (0,0,0))
        
        w, h = base_txt.get_size()
        scale = 1.5 if is_crit else 1.0
        
        self.image = pygame.Surface((int(w*scale)+4, int(h*scale)+4), pygame.SRCALPHA)
        self.image.blit(pygame.transform.scale(outline, (int(w*scale), int(h*scale))), (2, 2))
        self.image.blit(pygame.transform.scale(base_txt, (int(w*scale), int(h*scale))), (0, 0))
        
        self.rect = self.image.get_rect(center=(x, y))
        self.timer = 60
        self.vy = -4 if is_crit else -2
        self.vx = random.uniform(-1.5, 1.5)
        self.gravity = 0.15
        
    def update(self):
        self.rect.y += self.vy
        self.rect.x += self.vx
        self.vy += self.gravity
        self.timer -= 1
        
        if self.timer < 15: 
            self.image.set_alpha(int((self.timer/15)*255))
        if self.timer <= 0: 
            self.kill()

# --- [PBO: PEWARISAN] KELAS ENTITY (PARENT) ---
class Entity(pygame.sprite.Sprite):
    def __init__(self, name, hp, max_mana, x, y):
        super().__init__()
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.max_mana = max_mana
        self.mana = max_mana
        self.image = pygame.Surface((160, 160), pygame.SRCALPHA)
        self.image_to_draw = self.image 
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.start_pos = pygame.Vector2(x, y)
        self.is_dead = False
        self.anim_tick = 0
        self.shake_timer = 0
        self.flash_timer = 0
        self.lunge_timer = 0
        self.is_facing_right = True
    
    def draw_bar_premium(self, surface, x, y, val, max_val, color_fill, label):
        draw_bar_fancy(surface, x, y, 150, 10, val, max_val, color_fill, label) 
    
    def take_damage(self, amount, type="phys", is_crit=False):
        self.hp = max(0, min(self.max_hp, self.hp - amount))
        color = (255, 50, 50)
        sound_to_play = "hit"
        
        if type == "magic": 
            color = (200, 100, 255)
        if amount < 0: 
            color = (50, 255, 100)
            amount = abs(amount)
            sound_to_play = None
            
        if sound_to_play: 
            AUDIO.play(sound_to_play)
            
        self.shake_timer = 25 if is_crit else 10
        self.flash_timer = 8 if is_crit else 5
        
        return FloatingText(self.rect.centerx, self.rect.top - 20, str(int(amount)), color, is_crit)
    
    def trigger_lunge(self): 
        self.lunge_timer = 15 
    
    # [PBO: POLIMORFISME]
    def update(self):
        self.anim_tick += 0.05
        offset_x = 0
        
        if self.lunge_timer > 0:
            self.lunge_timer -= 1
            if self.lunge_timer > 10: 
                offset_x = 60 if self.is_facing_right else -60
            elif self.lunge_timer > 0: 
                offset_x = -20 if self.is_facing_right else 20
                
        shake_off = pygame.Vector2(0,0)
        if self.shake_timer > 0: 
            shake_off.x = random.randint(-5, 5)
            shake_off.y = random.randint(-3, 3)
            self.shake_timer -= 1
            
        idle_y = math.sin(self.anim_tick) * 4
        self.rect.midbottom = (self.start_pos.x + offset_x + shake_off.x, self.start_pos.y + idle_y + shake_off.y)
        
        if self.flash_timer > 0: 
            self.flash_timer -= 1
            flash_surf = self.image.copy()
            flash_surf.fill((255, 255, 255, 200), special_flags=pygame.BLEND_RGBA_MULT)
            self.image_to_draw = flash_surf
        else: 
            self.image_to_draw = self.image
            
        if self.hp <= 0 and not self.is_dead: 
            self.is_dead = True

# --- [PBO: PEWARISAN] KELAS HERO (CHILD) ---
class Hero(Entity):
    def __init__(self, stats):
        super().__init__(f"Lv.{stats.level} {stats.player_name}", stats.max_hp, stats.max_mana, 250, 440)
        self.hp = stats.hp
        self.mana = stats.mana 
        self.image = ASSETS["hero_battle"].copy()
        self.image_to_draw = self.image
        self.rect = self.image.get_rect(midbottom=(250, 440))
        self.start_pos = pygame.Vector2(250, 440)
        self.is_facing_right = True
        
    def redraw(self): 
        pass 
        
    def regen_mana(self): 
        self.mana = min(self.max_mana, self.mana + 15)

# --- [PBO: PEWARISAN] KELAS ENEMY (CHILD) ---
class Enemy(Entity):
    def __init__(self, level, enemy_type):
        self.type = enemy_type 
        base_hp = 100 + (level * 40)
        spawn_y = 440
        if self.type == "Golem": 
            spawn_y = 410 
            
        super().__init__(f"Lv.{level} {self.type}", base_hp, 0, 750, spawn_y)
        self.level = level
        self.is_facing_right = False
        
        if self.type == "Slime" and ASSETS.get("Slime_battle"): 
            self.image = ASSETS["Slime_battle"][0]
        elif self.type == "Golem" and ASSETS.get("Golem_battle"): 
            self.image = pygame.transform.flip(ASSETS["Golem_battle"][0], True, False)
        else: 
            self.redraw()
    
    # [PBO: POLIMORFISME]
    def redraw(self):
        self.image.fill((0,0,0,0))
        cx, cy = 80, 80
        if self.type == "Slime": 
            pygame.draw.circle(self.image, (50, 200, 50), (cx, cy), 40)
        elif self.type == "Golem": 
            pygame.draw.rect(self.image, (100, 100, 100), (cx-40, cy-40, 80, 80))
        else: 
            pygame.draw.circle(self.image, (255, 0, 0), (cx, cy), 40)
        
    def update(self): 
        super().update() 


# --- FARM TILE & WORLD ---
class FarmTile:
    def __init__(self, global_x, global_y, biome_type):
        self.global_x = global_x
        self.global_y = global_y
        self.biome = biome_type 
        self.state = "NATURAL"
        self.crop_type = None
        self.growth_stage = 0
        self.growth_timer = 0
        self.soil_decay_timer = 0
        self.rect = pygame.Rect(global_x * TILE_SIZE, global_y * TILE_SIZE, TILE_SIZE, TILE_SIZE)

    def to_dict(self):
        """Menyimpan data tile untuk Save Game."""
        return {
            "biome": self.biome,
            "state": self.state,
            "crop_type": self.crop_type,
            "growth_stage": self.growth_stage,
            "growth_timer": self.growth_timer,
            "soil_decay_timer": self.soil_decay_timer
        }
    
    def load_from_dict(self, data):
        """Memuat data tile dari Save Game."""
        self.biome = data.get("biome", self.biome)
        self.state = data.get("state", "NATURAL")
        self.crop_type = data.get("crop_type", None)
        self.growth_stage = data.get("growth_stage", 0)
        self.growth_timer = data.get("growth_timer", 0)
        self.soil_decay_timer = data.get("soil_decay_timer", 0)

    def interact(self, tool):
        # Logika Panen
        if self.crop_type and self.growth_stage == 3:
            GAME_STATS.inventory[self.crop_type] = GAME_STATS.inventory.get(self.crop_type, 0) + 1
            
            msg = GAME_STATS.update_quest("harvest", self.crop_type)
            name = self.crop_type
            self.crop_type = None
            self.growth_stage = 0
            self.state = "TILLED"
            AUDIO.play("buy")
            
            base_msg = f"Harvested {name}!"
            return True, f"{base_msg} | {msg}" if msg else base_msg
        
        # Logika Isi Air
        if tool == "WATER" and self.biome == "WATER":
            GAME_STATS.water_current = GAME_STATS.water_max
            AUDIO.play("water")
            return True, "Water Refilled!"
        
        # Validasi Biome
        if self.biome == "WATER" or self.biome == "FOREST": 
            return False, "Can't farm here!"
        
        # Logika Cangkul
        if tool == "HOE":
            if self.state == "NATURAL":
                if self.biome in ["GRASS", "DIRT"]:
                    if GAME_STATS.stamina >= 5: 
                        GAME_STATS.stamina -= 5
                        self.state = "TILLED"
                        self.soil_decay_timer = 0
                        AUDIO.play("hoe")
                        return True, "Soil Tilled!"
                    else: 
                        return False, "Out of Stamina!"
                else: 
                    return False, "Ground too hard!" 
            elif self.state == "TILLED": 
                return False, "Already Tilled!"
            
        # Logika Tanam Bibit
        elif "SEED" in tool:
            if self.state == "NATURAL": 
                return False, "Till soil first!"
            elif self.crop_type is not None: 
                return False, "Crop already planted!"
                
            seed_name, crop_name = "", ""
            if "GRAPE" in tool: seed_name, crop_name = "Grape Seed", "Grape"
            elif "MUSHROOM" in tool: seed_name, crop_name = "Mushroom Seed", "Mushroom"
            elif "POTATO" in tool: seed_name, crop_name = "Potato Seed", "Potato"
            elif "CARROT" in tool: seed_name, crop_name = "Carrot Seed", "Carrot"
            
            if seed_name and GAME_STATS.inventory.get(seed_name, 0) > 0:
                GAME_STATS.inventory[seed_name] -= 1
                self.crop_type = crop_name
                self.growth_stage = 0
                self.growth_timer = 0
                AUDIO.play("step")
                return True, f"Planted {crop_name}!"
            else: 
                AUDIO.play("error")
                return False, "Out of Seeds!"
            
        # Logika Siram
        elif tool == "WATER":
            if self.state == "TILLED" or (self.crop_type and self.state != "WATERED"):
                if GAME_STATS.water_current > 0:
                    if GAME_STATS.stamina >= 3: 
                        GAME_STATS.stamina -= 3
                        self.state = "WATERED"
                        GAME_STATS.water_current -= 1
                        self.soil_decay_timer = 0
                        AUDIO.play("water")
                        return True, "Watered!"
                    else: 
                        return False, "Out of Stamina!"
                else: 
                    return False, "Empty! Refill at water."
        return False, "" 

    def update(self):
        if self.crop_type and self.state == "WATERED":
            if self.growth_stage < 3:
                self.growth_timer += 1
                if self.growth_timer >= 600: 
                    self.growth_stage += 1
                    self.growth_timer = 0
                    self.state = "TILLED" 
                    
        if self.state == "TILLED" and self.crop_type is None:
            self.soil_decay_timer += 1
            if self.soil_decay_timer >= 1200: 
                self.state = "NATURAL"
                self.soil_decay_timer = 0
        else: 
            self.soil_decay_timer = 0

    def draw(self, surface, camera_x, camera_y):
        screen_x = (self.global_x * TILE_SIZE) - camera_x
        screen_y = (self.global_y * TILE_SIZE) - camera_y
        
        # Optimasi: Culling
        if screen_x < -TILE_SIZE - 100 or screen_x > SCREEN_WIDTH + 100 or screen_y < -TILE_SIZE - 100 or screen_y > SCREEN_HEIGHT + 100: 
            return None

        img = ASSETS["grass"]
        if self.biome == "WATER": img = ASSETS["water"]
        elif self.biome == "SAND": img = ASSETS["sand"]
        elif self.biome == "DIRT": img = ASSETS["dirt"]
        elif self.biome == "FOREST": img = ASSETS["forest_bg"]
        
        if self.state == "TILLED": img = ASSETS["tilled"]
        if self.state == "WATERED": img = ASSETS["watered"]
        
        surface.blit(img, (screen_x, screen_y))

        if self.crop_type:
            if ASSETS.get("crops") and self.crop_type in ASSETS["crops"]:
                stage_idx = min(self.growth_stage, 3) 
                crop_img = ASSETS["crops"][self.crop_type][stage_idx]
                c_x = screen_x + (TILE_SIZE - crop_img.get_width()) // 2
                c_y = screen_y + (TILE_SIZE - crop_img.get_height()) - 5
                surface.blit(crop_img, (c_x, c_y))
            else:
                size = (self.growth_stage + 1) * 6
                col = (255, 255, 200)
                if self.crop_type == "Mushroom": col = (255, 140, 0)
                elif self.crop_type == "Potato": col = (200, 180, 100)
                elif self.crop_type == "Carrot": col = (255, 100, 0)
                
                cx, cy = screen_x + TILE_SIZE//2, screen_y + TILE_SIZE//2
                if self.growth_stage < 3: 
                    pygame.draw.circle(surface, (50, 200, 50), (cx, cy+5), size)
                else: 
                    pygame.draw.circle(surface, col, (cx, cy-5), 12)
            
            if self.growth_stage == 3:
                bounce = math.sin(pygame.time.get_ticks() * 0.015) * 4
                ind_x = screen_x + TILE_SIZE // 2
                ind_y = screen_y - 15 + bounce
                pygame.draw.circle(surface, (255, 255, 255), (int(ind_x), int(ind_y)), 10)
                pygame.draw.circle(surface, (200, 50, 50), (int(ind_x), int(ind_y)), 10, 2)
                draw_text_shadow(surface, "!", FONT_BOLD, ind_x, ind_y, (220, 0, 0), center=True)

        overlay_data = None
        if self.biome == "FOREST":
            overlay_data = {
                "type": "TREE",
                "img": ASSETS["tree"],
                "pos": (screen_x - 25, screen_y - 50),
                "sort_y": (self.global_y * TILE_SIZE) + TILE_SIZE - 10
            }
        return overlay_data

class WorldSystem:
    def __init__(self):
        self.tiles = {}
        self.seed = 999
        self.generate_fixed_map()
        
    def generate_fixed_map(self):
        center_x = MAP_WIDTH // 2
        center_y = MAP_HEIGHT // 2
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                biome = "GRASS"
                if x == 0 or x == MAP_WIDTH - 1 or y == 0 or y == MAP_HEIGHT - 1: 
                    biome = "WATER"
                elif abs(x - center_x) < 5 and abs(y - center_y) < 5: 
                    biome = "GRASS"
                else:
                    val = math.sin(x * 0.15 + self.seed) + math.cos(y * 0.15 + self.seed)
                    if val > 1.4: biome = "FOREST"
                    elif val > 1.0: biome = "DIRT"
                    elif val < -1.4: biome = "SAND" 
                    elif val < -1.6: biome = "WATER"
                self.tiles[(x, y)] = FarmTile(x, y, biome)
                
    def reset_world(self):
        for tile in self.tiles.values(): 
            tile.state = "NATURAL"
            tile.crop_type = None
            tile.growth_stage = 0
            tile.growth_timer = 0
            tile.soil_decay_timer = 0
            
    def get_tile_at(self, global_x, global_y): 
        return self.tiles.get((int(global_x), int(global_y)))
        
    def get_all_tiles(self): 
        return self.tiles.values()
    
    def to_dict(self):
        # Convert tuple keys to string for JSON serialization
        return {f"{x},{y}": tile.to_dict() for (x, y), tile in self.tiles.items()}

    def load_from_dict(self, data):
        for key_str, tile_data in data.items():
            x, y = map(int, key_str.split(","))
            if (x, y) in self.tiles:
                self.tiles[(x, y)].load_from_dict(tile_data)

class PlayerOverworld(pygame.sprite.Sprite):
    def __init__(self, hotbar):
        super().__init__()
        self.hotbar = hotbar
        self.global_x = (MAP_WIDTH // 2) * TILE_SIZE
        self.global_y = ((MAP_HEIGHT // 2) * TILE_SIZE) + 150 
        self.rect = pygame.Rect(0, 0, 40, 40)
        self.speed = 5
        self.facing_right = True
        self.facing_dir = "DOWN"  
        self.sheet = ASSETS["hero_walk"]
        self.frame_index = 0
        self.animation_speed = 0.15
        self.is_moving = False
        self.sheet_w, self.sheet_h = self.sheet.get_size()
        self.frame_width = self.sheet_w // 6
        self.frame_height = self.sheet_h // 8 
        self.image = pygame.Surface((40, 40)) 
        
    def get_frame(self, col, row, flip=False):
        rect = pygame.Rect(col * self.frame_width, row * self.frame_height, self.frame_width, self.frame_height)
        frame_surf = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
        frame_surf.blit(self.sheet, (0, 0), rect)
        scaled_img = pygame.transform.scale(frame_surf, (100, 100))
        if flip: 
            scaled_img = pygame.transform.flip(scaled_img, True, False)
        return scaled_img
        
    def update_animation(self):
        target_row = 0 
        if self.is_moving: 
            target_row = 1
        self.frame_index += self.animation_speed
        if self.frame_index >= 6: 
            self.frame_index = 0
        self.image = self.get_frame(int(self.frame_index), target_row, flip=not self.facing_right)
        
    def update(self, keys, obstacles):
        dx, dy = 0, 0
        self.is_moving = False
        
        if keys[pygame.K_a]: 
            dx = -self.speed; self.facing_right = False; self.facing_dir = "LEFT"; self.is_moving = True
        if keys[pygame.K_d]: 
            dx = self.speed; self.facing_right = True; self.facing_dir = "RIGHT"; self.is_moving = True
        if keys[pygame.K_w]: 
            dy = -self.speed; self.facing_dir = "UP"; self.is_moving = True
        if keys[pygame.K_s]: 
            dy = self.speed; self.facing_dir = "DOWN"; self.is_moving = True
            
        if dx != 0 or dy != 0:
            next_x = self.global_x + dx
            temp_rect = pygame.Rect(0, 0, 40, 40)
            temp_rect.center = (next_x, self.global_y)
            collision_x = False
            for obs in obstacles:
                if temp_rect.colliderect(obs): 
                    collision_x = True; break
                    
            if 0 <= next_x <= (MAP_WIDTH * TILE_SIZE) - 40 and not collision_x: 
                self.global_x = next_x
                
            next_y = self.global_y + dy
            temp_rect.center = (self.global_x, next_y)
            collision_y = False
            for obs in obstacles:
                if temp_rect.colliderect(obs): 
                    collision_y = True; break
                    
            if 0 <= next_y <= (MAP_HEIGHT * TILE_SIZE) - 40 and not collision_y: 
                self.global_y = next_y
                
            if random.random() < 0.05: 
                AUDIO.play("step")
                
        self.update_animation()
        self.rect.center = (self.global_x, self.global_y - 10)

class OverworldEnemy(pygame.sprite.Sprite):
    def __init__(self, global_x, global_y, level, enemy_type):
        super().__init__()
        self.global_x = global_x
        self.global_y = global_y
        self.level = level
        self.type = enemy_type
        self.image = pygame.Surface((60, 60), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(self.global_x, self.global_y))
        self.move_timer = 0
        self.vx = random.choice([-1, 1])
        self.vy = 0
        self.facing_right = True
        self.anim_frames = None
        self.anim_idx = 0
        self.anim_speed = 0.2
        
        if self.type == "Slime": 
            self.anim_frames = ASSETS.get("Slime_ow")
        elif self.type == "Golem": 
            self.anim_frames = ASSETS.get("Golem_ow")
            
    def update(self, safe_zone_rect):
        if self.anim_frames:
            self.anim_idx += self.anim_speed
            if self.anim_idx >= len(self.anim_frames): 
                self.anim_idx = 0
                
        self.move_timer -= 1
        if self.move_timer <= 0: 
            self.move_timer = random.randint(60, 180)
            self.vx = random.uniform(-2, 2)
            self.vy = random.uniform(-2, 2)
            
        if self.vx > 0: self.facing_right = True
        elif self.vx < 0: self.facing_right = False
        
        new_x = self.global_x + self.vx
        new_y = self.global_y + self.vy
        temp_rect = self.image.get_rect(center=(new_x, new_y))
        
        if safe_zone_rect.colliderect(temp_rect): 
            self.vx *= -1
            self.vy *= -1 
        else:
            if 50 < new_x < (MAP_WIDTH * TILE_SIZE) - 50: 
                self.global_x = new_x
            else: 
                self.vx *= -1
            if 50 < new_y < (MAP_HEIGHT * TILE_SIZE) - 50: 
                self.global_y = new_y
            else: 
                self.vy *= -1
                
        self.rect.center = (self.global_x, self.global_y)
        
        if self.anim_frames:
            current_frame = self.anim_frames[int(self.anim_idx)].copy()
            if not self.facing_right: 
                current_frame = pygame.transform.flip(current_frame, True, False)
            self.image = pygame.Surface((60, 60), pygame.SRCALPHA)
            cx, cy = 30, 30
            sl_w = current_frame.get_width()
            sl_h = current_frame.get_height()
            self.image.blit(current_frame, (cx - sl_w//2, cy - sl_h//2))
            
            lvl_surf = FONT_UI.render(f"Lv{self.level}", True, C_ACCENT_GOLD)
            self.image.blit(lvl_surf, lvl_surf.get_rect(center=(cx, cy - 25)))
        else: 
            self.image.fill((0,0,0,0))
            pygame.draw.circle(self.image, (150, 0, 0), (30, 30), 18)


# --- MESIN PERTARUNGAN ---
class BattleScene:
    def __init__(self):
        self.active = False
        self.won = False
        self.all_sprites = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()
        self.texts = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
    
    def start(self, enemy_level, enemy_type):
        self.active = True
        self.won = False
        self.hero = Hero(GAME_STATS)
        self.enemy = Enemy(enemy_level, enemy_type)
        self.all_sprites.empty()
        self.particles.empty()
        self.texts.empty()
        self.projectiles.empty()
        self.all_sprites.add(self.hero, self.enemy)
        self.turn = "PLAYER"
        self.log_text = f"BATTLE START! Vs {self.enemy.name}"
        self.turn_timer = 0
        self.temp_dmg = (0, False)
        self.temp_enemy_dmg = (0, False)
        self.screen_shake_intensity = 0
        AUDIO.play("battle_start")
    
    def deal_damage_w_effect(self, target, amount, type, is_crit=False):
        txt = target.take_damage(amount, type, is_crit)
        self.texts.add(txt)
        color = (255, 50, 50) if type == "phys" else (200, 50, 255)
        self.spawn_particles(target.rect.centerx, target.rect.centery, color, 25 if is_crit else 15, 2 if is_crit else 1)
        if is_crit: 
            self.screen_shake_intensity = 15 
    
    def spawn_particles(self, x, y, color, count=15, speed_mult=1):
        for _ in range(count):
            p = Particle(x, y, color, random.randint(5, 10))
            p.vx *= speed_mult
            p.vy *= speed_mult
            self.particles.add(p)
    
    def handle_input(self, event):
        if self.turn != "PLAYER": return
        action_idx = -1 
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1: action_idx = 0
            elif event.key == pygame.K_2: action_idx = 1
            elif event.key == pygame.K_3: action_idx = 2
            elif event.key == pygame.K_4: action_idx = 3
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for i in range(4):
                bx = 240 + (i * 150)
                rect = pygame.Rect(bx, 515, 140, 70)
                if rect.collidepoint(mx, my): 
                    action_idx = i
                    AUDIO.play("select")
                    break
                    
        if action_idx != -1:
            cost, dmg, skill = 0, 0, ""
            lvl_bonus = GAME_STATS.level * 5
            
            if action_idx == 0: 
                cost, dmg, skill = 0, random.randint(30, 45) + lvl_bonus, "Slash"
                self.hero.trigger_lunge()
                AUDIO.play("slash")
            elif action_idx == 1: 
                cost = 30
                if self.hero.mana >= cost:
                    self.hero.mana -= cost
                    heal = random.randint(60, 100) + lvl_bonus
                    self.texts.add(self.hero.take_damage(-heal, "heal"))
                    self.spawn_particles(self.hero.rect.centerx, self.hero.rect.centery, (50, 255, 100), 30)
                    AUDIO.play("heal")
                    self.log_text = "Hero recovered HP!"
                    self.end_player_turn()
                return 
            elif action_idx == 2: 
                cost, dmg, skill = 40, random.randint(70, 110) + lvl_bonus, "Fireball"
                if self.hero.mana >= cost and self.enemy: 
                    AUDIO.play("magic")
                    proj = ProjectileWithTrail(self.hero.rect.center, self.enemy.rect.center, (255, 100, 0), self.particles, "fire")
                    self.projectiles.add(proj)
            elif action_idx == 3: 
                cost, dmg, skill = 90, random.randint(150, 220) + lvl_bonus, "Thunder"
                if self.hero.mana >= cost and self.enemy: 
                    AUDIO.play("thunder")
                    proj = ProjectileWithTrail(self.hero.rect.center, self.enemy.rect.center, (100, 200, 255), self.particles, "thunder")
                    self.projectiles.add(proj)
                    
            if skill and self.hero.mana >= cost:
                self.hero.mana -= cost
                is_crit = random.random() < (0.2 + (GAME_STATS.level * 0.01))
                dmg = int(dmg * 1.5) if is_crit else dmg
                
                if skill == "Slash": 
                    pygame.time.set_timer(pygame.USEREVENT + 2, 250, 1)
                    self.temp_dmg = (dmg, is_crit)
                else: 
                    self.temp_dmg = (dmg, is_crit) 
                
                self.log_text = f"Hero used {skill}!"
                self.end_player_turn()
            elif skill: 
                self.log_text = "Not Enough Mana!"

    def handle_timers(self, event):
        if event.type == pygame.USEREVENT + 2:
            dmg, is_crit = self.temp_dmg
            if self.enemy and not self.enemy.is_dead:
                self.deal_damage_w_effect(self.enemy, dmg, "phys", is_crit)
        elif event.type == pygame.USEREVENT + 3:
            dmg, is_crit = self.temp_enemy_dmg
            if not self.hero.is_dead:
                self.deal_damage_w_effect(self.hero, dmg, "phys", is_crit)

    def end_player_turn(self): 
        self.turn = "ENEMY_WAIT"
        self.turn_timer = 60 
        
    def enemy_attack(self):
        if not self.enemy or self.enemy.is_dead: return
        self.enemy.trigger_lunge()
        AUDIO.play("slash")
        
        delay = 200 
        if self.enemy.type in ["Golem", "Knight"]: 
            delay = 350
            
        is_crit = random.random() < 0.2
        dmg = random.randint(20, 30 + self.enemy.level * 6)
        dmg = int(dmg * 1.5) if is_crit else dmg
        
        pygame.time.set_timer(pygame.USEREVENT + 3, delay, 1)
        self.temp_enemy_dmg = (dmg, is_crit)
        self.log_text = f"{self.enemy.name} Attacks!"
        self.hero.regen_mana()
        self.turn = "PLAYER"
        
    def update(self):
        self.all_sprites.update()
        self.particles.update()
        self.texts.update()
        self.projectiles.update()
        
        shake_off = (0,0)
        if self.screen_shake_intensity > 0:
            shake_off = (random.randint(-self.screen_shake_intensity, self.screen_shake_intensity), 
                         random.randint(-self.screen_shake_intensity, self.screen_shake_intensity))
            self.screen_shake_intensity -= 1
        self.shake_offset = shake_off
        
        if self.enemy:
            hits = pygame.sprite.spritecollide(self.enemy, self.projectiles, True)
            for proj in hits: 
                dmg, is_crit = self.temp_dmg
                self.deal_damage_w_effect(self.enemy, dmg, "magic", is_crit)
                
        if self.turn == "ENEMY_WAIT":
            self.turn_timer -= 1
            if self.turn_timer <= 0: 
                self.enemy_attack()
            
        if self.enemy and self.enemy.is_dead and self.turn != "WIN_WAIT":
             xp = 50 + (self.enemy.level * 10)
             drops = {"Slime": "Slime Gel", "Golem": "Gold Nugget"}
             drop_item = drops.get(self.enemy.type, "Slime Gel")
             
             if random.random() < 0.05: 
                 drop_item = "Dark Essence"
             
             GAME_STATS.inventory[drop_item] = GAME_STATS.inventory.get(drop_item, 0) + 1
             
             msg_quest = GAME_STATS.update_quest("kill", self.enemy.type)
             
             msg = f"Got {drop_item} +{xp}XP"
             if GAME_STATS.add_xp(xp): 
                 AUDIO.play("levelup")
                 msg = "LEVEL UP! " + msg
             if msg_quest: 
                 msg = "Quest Completed!"
             
             self.log_text = msg
             self.turn = "WIN_WAIT"
             self.win_timer = 120
             self.won = True
             
        if self.hero.hp <= 0 and self.turn != "WIN_WAIT": 
            self.log_text = "DEFEATED! Running away..."
            self.win_timer = 120
            self.turn = "WIN_WAIT"
            self.won = False 
            
        if self.turn == "WIN_WAIT":
            self.win_timer -= 1
            if self.win_timer <= 0: 
                self.active = False
                if self.won: 
                    GAME_STATS.hp = self.hero.hp
                    GAME_STATS.mana = self.hero.mana
                    
    def draw(self, surface):
        offset = getattr(self, 'shake_offset', (0,0))
        draw_premium_background(surface, offset)
        
        for entity in [self.hero, self.enemy]:
            if entity and not entity.is_dead:
                 s_x = entity.rect.centerx - 40 + offset[0]
                 s_y = entity.rect.bottom - 15 + offset[1]
                 pygame.draw.ellipse(surface, (0,0,0,100), (s_x, s_y, 80, 25))
                 
        for sprite in self.all_sprites: 
            img = getattr(sprite, 'image_to_draw', sprite.image)
            surface.blit(img, sprite.rect.move(offset))
            
        for p in self.particles: 
            surface.blit(p.image, p.rect.move(offset))
        for p in self.projectiles: 
            surface.blit(p.image, p.rect.move(offset))
            
        self.texts.draw(surface)
        
        pygame.draw.rect(surface, (30, 30, 40), (0, 500, SCREEN_WIDTH, 100))
        pygame.draw.line(surface, C_ACCENT_GOLD, (0, 500), (SCREEN_WIDTH, 500), 3)
        
        bx = 240
        skills = [("1. Slash", "0 MP", (200,200,200)), ("2. Heal", "30 MP", (50,255,100)), ("3. Fire", "40 MP", (255,100,50)), ("4. Thunder", "90 MP", (100,200,255))]
        
        for name, cost, col in skills:
            bg = (60, 60, 80) if self.turn == "PLAYER" else (30, 30, 40)
            pygame.draw.rect(surface, bg, (bx, 515, 140, 70), border_radius=8)
            pygame.draw.rect(surface, (70, 70, 80), (bx, 515, 140, 70), 2, border_radius=8)
            surface.blit(FONT_BOLD.render(name, True, col), (bx+10, 525))
            surface.blit(FONT_UI.render(cost, True, (150,150,150)), (bx+10, 550))
            bx += 150
            
        self.hero.draw_bar_premium(surface, 20, 540, self.hero.hp, self.hero.max_hp, (220, 60, 60), "HP")
        self.hero.draw_bar_premium(surface, 20, 580, self.hero.mana, self.hero.max_mana, (60, 100, 220), "MP")
        
        if self.enemy and not self.enemy.is_dead: 
            self.enemy.draw_bar_premium(surface, SCREEN_WIDTH-170, 540, self.enemy.hp, self.enemy.max_hp, (220, 60, 60), "HP")
            
        log_bg = pygame.Surface((600, 50), pygame.SRCALPHA)
        pygame.draw.rect(log_bg, (0,0,0,180), log_bg.get_rect(), border_radius=10)
        surface.blit(log_bg, (200, 10))
        txt = FONT_BOLD.render(self.log_text, True, C_ACCENT_GOLD)
        surface.blit(txt, txt.get_rect(center=(SCREEN_WIDTH//2, 35)))


# --- HOTBAR & UI ---
class Hotbar:
    def __init__(self):
        self.slots = ["HOE", "WATER", "SEED_GRAPE", "SEED_MUSHROOM", "POTION"]
        self.selected = 0
        self.slot_size = 50
        
    def draw(self, surface, x_pos=None, y_pos=None):
        total_width = len(self.slots) * (self.slot_size + 5)
        start_x = x_pos if x_pos is not None else (SCREEN_WIDTH - total_width) // 2
        y = y_pos if y_pos is not None else SCREEN_HEIGHT - 70 
        rects = []
        
        for i, slot in enumerate(self.slots):
            x = start_x + (i * (self.slot_size + 5))
            rect = pygame.Rect(x, y, self.slot_size, self.slot_size)
            
            # Slot Styling
            pygame.draw.rect(surface, (30, 30, 30, 220), rect, border_radius=8)
            if i == self.selected: 
                pygame.draw.rect(surface, C_ACCENT_GOLD, rect, 3, border_radius=8)
            else: 
                pygame.draw.rect(surface, (80, 80, 80), rect, 1, border_radius=8)
            
            txt = ""
            if slot == "HOE": txt = "HOE"
            elif slot == "WATER": txt = "WTR"
            elif "SEED" in slot: txt = slot.split("_")[1][0]
            elif slot == "POTION": txt = "POT"
            elif "COFFEE" in slot: txt = "COF"
            elif "ELIXIR" in slot: txt = "ELX"
            elif "CROP" in slot: txt = slot.split("_")[1][0:3]
            
            t_surf = FONT_BOLD.render(txt, True, C_TEXT_WHITE)
            surface.blit(t_surf, t_surf.get_rect(center=rect.center))
            
            if slot in CODE_TO_NAME:
                real_name = CODE_TO_NAME[slot]
                count_val = GAME_STATS.inventory.get(real_name, 0)
                if count_val > 0 and real_name not in ["Hoe", "Watering Can"]:
                     surface.blit(FONT_UI_SMALL.render(str(count_val), True, C_ACCENT_GOLD), (x + 30, y + 35))
            
            if slot == "WATER":
                w_ratio = GAME_STATS.water_current / GAME_STATS.water_max
                pygame.draw.rect(surface, (30, 30, 30), (x+5, y+40, 40, 5))
                if w_ratio > 0: 
                    pygame.draw.rect(surface, (50, 150, 255), (x+5, y+40, 40 * w_ratio, 5))
                    
            draw_text_shadow(surface, str(i+1), FONT_UI_SMALL, x+3, y+2, (180,180,180))
            rects.append(rect)
        return rects


# --- GAME MASTER (KONTROL UTAMA) ---
class MasterGame:
    def __init__(self):
        self.state = STATE_MAIN_MENU
        self.hotbar = Hotbar()
        self.player = PlayerOverworld(self.hotbar)
        self.world = WorldSystem()
        self.battle = BattleScene()
        self.enemies_ow = pygame.sprite.Group() 
        self.msg_text = ""
        self.msg_timer = 0
        self.shop_tab = "BUY"
        self.shop_category = "SEEDS" 
        self.selected_item_name = None 
        self.game_time = 6 * 60
        self.time_speed = 0.05
        self.hunger_timer = 0
        self.menu_particles = [MenuParticle() for _ in range(50)]
        
        self.input_text = ""
        self.save_files = []
        self.selected_save_idx = 0
        
        # --- STATE PROLOG ---
        self.prologue_lines = [
            "Di sebuah kota yang dingin dan sepi...",
            "Seorang pemuda menghembuskan napas terakhirnya dalam kesendirian.",
            "Namun, takdir berkata lain...",
            "Cahaya terang menyelimuti jiwanya.",
            "Ia terbangun di dunia baru... Harvest Arena.",
            "Kini, ia bangkit sebagai Ksatria, berjuang seorang diri.",
            "Membangun kembali harapan dari puing-puing masa lalu."
        ]
        self.prologue_idx = 0
        self.prologue_char_idx = 0
        self.prologue_timer = 0
        self.prologue_speed = 3 

        # --- ANIMASI MENU ---
        self.menu_frame_index = 0
        self.menu_anim_speed = 0.2 
        self.menu_anim_dir = 1 
        self.light_texture = self.create_light_texture(300) 

        center_x = (MAP_WIDTH // 2) * TILE_SIZE
        center_y = (MAP_HEIGHT // 2) * TILE_SIZE
        self.house_rect = pygame.Rect(center_x - 125, center_y - 200, 200, 150)
        self.safe_zone_rect = self.house_rect.inflate(500, 500)
        self.fade_alpha = 0
        self.fade_state = "IDLE"
        self.pending_pass_out = False
        self.black_screen_timer = 0
        self.pending_menu_action = None 

        # --- ELEMEN UI ---
        self.btn_new = Button(SCREEN_WIDTH//2 - 100, 240, 200, 50, "NEW GAME")
        self.btn_load = Button(SCREEN_WIDTH//2 - 100, 300, 200, 50, "LOAD GAME")
        self.btn_sets = Button(SCREEN_WIDTH//2 - 100, 360, 200, 50, "SETTINGS")
        self.btn_quit = Button(SCREEN_WIDTH//2 - 100, 420, 200, 50, "EXIT")
        
        self.btn_res = Button(SCREEN_WIDTH//2 - 100, 200, 200, 50, "RESUME")
        self.btn_sav = Button(SCREEN_WIDTH//2 - 100, 270, 200, 50, "SAVE GAME")
        self.btn_lod = Button(SCREEN_WIDTH//2 - 100, 340, 200, 50, "LOAD GAME")
        self.btn_men = Button(SCREEN_WIDTH//2 - 100, 410, 200, 50, "MAIN MENU")
        
        self.btn_back = Button(SCREEN_WIDTH//2 - 100, 450, 200, 50, "BACK")
        
        self.play_menu_music()

    def create_light_texture(self, radius):
        texture = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        for r in range(radius, 0, -2):
            alpha = int(255 * (1.0 - (r / radius) ** 0.5)) 
            pygame.draw.circle(texture, (255, 255, 255, alpha), (radius, radius), r)
        return texture

    def play_menu_music(self):
        try:
            if os.path.exists(MENU_BGM):
                if not pygame.mixer.music.get_busy():
                    pygame.mixer.music.load(MENU_BGM)
                    pygame.mixer.music.play(-1, fade_ms=500)
        except: pass

    def stop_menu_music(self): 
        pygame.mixer.music.fadeout(500)

    def trigger_menu_transition(self, action):
        self.pending_menu_action = action
        self.fade_state = "FADE_OUT"
        self.stop_menu_music()
        AUDIO.play("select")

    def try_sleep(self):
        dist = math.hypot(self.player.global_x - self.house_rect.centerx, self.player.global_y - (self.house_rect.bottom - 40))
        if dist < 80: 
            if self.game_time >= 1080: 
                self.trigger_day_transition(passed_out=False)
                return True
            else: 
                self.show_msg("Too early to sleep!")
                return True 
        return False

    def trigger_day_transition(self, passed_out=False):
        if self.fade_state == "IDLE": 
            self.fade_state = "FADE_OUT"
            self.pending_pass_out = passed_out
            AUDIO.play("save") 

    def _perform_day_reset(self):
        GAME_STATS.day += 1
        GAME_STATS.stamina = GAME_STATS.max_stamina
        
        if self.pending_pass_out: 
            GAME_STATS.hp = max(1, GAME_STATS.hp // 2)
            GAME_STATS.gold = max(0, GAME_STATS.gold - 50)
            self.show_msg("Passed out! Lost energy & gold.")
        else: 
            GAME_STATS.hp = min(GAME_STATS.max_hp, GAME_STATS.hp + 50)
            self.show_msg(f"Day {GAME_STATS.day} Started!")
            
        self.game_time = 6 * 60
        self.player.global_x = (MAP_WIDTH // 2) * TILE_SIZE
        self.player.global_y = ((MAP_HEIGHT // 2) * TILE_SIZE) + 150 
        self.spawn_enemies(20)
        AUDIO.play("heal")

    def try_consume_item(self):
        tool_code = self.hotbar.slots[self.hotbar.selected]
        item_name = CODE_TO_NAME.get(tool_code)

        if item_name and GAME_STATS.inventory.get(item_name, 0) > 0:
            item_info = ITEM_DATA.get(item_name)
            did_consume = False
            msg_consume = ""

            # --- LOGIKA KONSUMSI ITEM (CEK STATUS PENUH) ---
            if item_info and item_info["type"] == "Crop" and item_info["eat"] > 0:
                if GAME_STATS.hunger < GAME_STATS.max_hunger:
                    GAME_STATS.hunger = min(GAME_STATS.max_hunger, GAME_STATS.hunger + item_info["eat"])
                    GAME_STATS.hp = min(GAME_STATS.max_hp, GAME_STATS.hp + 5)
                    did_consume = True
                    msg_consume = f"Ate {item_name}! +Hunger"
                else:
                    self.show_msg("Full!")

            elif item_name == "Potion":
                if GAME_STATS.hp < GAME_STATS.max_hp:
                    GAME_STATS.hp = min(GAME_STATS.max_hp, GAME_STATS.hp + 100)
                    did_consume = True
                    msg_consume = "HP Restored!"
                else:
                    self.show_msg("HP Full!")

            elif item_name == "Coffee":
                if GAME_STATS.stamina < GAME_STATS.max_stamina:
                    GAME_STATS.stamina = min(GAME_STATS.max_stamina, GAME_STATS.stamina + 50)
                    did_consume = True
                    msg_consume = "Stamina Boost!"
                else:
                    self.show_msg("Stamina Full!")

            elif item_name == "Elixir":
                if GAME_STATS.hp < GAME_STATS.max_hp or GAME_STATS.mana < GAME_STATS.max_mana:
                    GAME_STATS.hp = GAME_STATS.max_hp
                    GAME_STATS.mana = GAME_STATS.max_mana
                    did_consume = True
                    msg_consume = "Fully Restored!"
                else:
                    self.show_msg("Already at Max!")

            if did_consume:
                GAME_STATS.inventory[item_name] -= 1
                AUDIO.play("eat")
                self.show_msg(msg_consume)
                return True
            
        return False

    def clean_hotbar(self):
        for i in range(len(self.hotbar.slots)):
            slot_code = self.hotbar.slots[i]
            if slot_code in CODE_TO_NAME:
                real_name = CODE_TO_NAME[slot_code]
                if real_name in ["Hoe", "Watering Can"]: 
                    continue
                if GAME_STATS.inventory.get(real_name, 0) <= 0: 
                    self.hotbar.slots[i] = "EMPTY" 

    def spawn_enemies(self, count):
        self.enemies_ow.empty()
        p_gx = self.player.global_x
        p_gy = self.player.global_y
        spawned_count = 0
        attempts = 0
        
        while spawned_count < count and attempts < 1000:
            attempts += 1
            gx = random.randint(2, MAP_WIDTH - 3) * TILE_SIZE
            gy = random.randint(2, MAP_HEIGHT - 3) * TILE_SIZE
            
            enemy_test_rect = pygame.Rect(0, 0, 60, 60)
            enemy_test_rect.center = (gx, gy)
            
            if not self.safe_zone_rect.colliderect(enemy_test_rect) and math.hypot(gx - p_gx, gy - p_gy) > 400:
                tile = self.world.get_tile_at(gx // TILE_SIZE, gy // TILE_SIZE)
                if tile and tile.biome != "WATER":
                    min_level = max(1, GAME_STATS.level - 2)
                    max_level = GAME_STATS.level + 2
                    level = random.randint(min_level, max_level)
                    etype = random.choice(["Slime", "Golem"])
                    self.enemies_ow.add(OverworldEnemy(gx, gy, level, etype))
                    spawned_count += 1

    def start_new_game(self):
        GAME_STATS.reset()
        if self.input_text:
            GAME_STATS.player_name = self.input_text
        self.world.reset_world()
        self.player.global_x = (MAP_WIDTH // 2) * TILE_SIZE
        self.player.global_y = ((MAP_HEIGHT // 2) * TILE_SIZE) + 150 
        self.spawn_enemies(20)
        self.game_time = 6 * 60
        self.state = STATE_OVERWORLD

    def check_encounter(self):
        hits = pygame.sprite.spritecollide(self.player, self.enemies_ow, True, pygame.sprite.collide_rect_ratio(0.9))
        if hits:
            enemy_hit = hits[0]
            self.state = STATE_BATTLE
            self.battle.start(enemy_hit.level, enemy_hit.type)
            self.show_msg(f"Battle: Lv{enemy_hit.level} {self.battle.enemy.type}!")
            AUDIO.play("battle_start")

    def show_msg(self, txt): 
        if txt: 
            self.msg_text = txt
            self.msg_timer = 60
    
    def get_tile_under_mouse(self, camera_x, camera_y):
        mx, my = get_corrected_mouse()
        world_mx = mx + camera_x
        world_my = my + camera_y
        gx = int(world_mx // TILE_SIZE)
        gy = int(world_my // TILE_SIZE)
        return self.world.get_tile_at(gx, gy)

    # --- LOGIKA SAVE / LOAD LENGKAP ---
    def save_game(self):
        try:
            filename = f"save_{GAME_STATS.player_name}.json"
            save_data = {
                "stats": GAME_STATS.to_dict(),
                "world": self.world.to_dict(),
                "hotbar": self.hotbar.slots,
                "player_pos": (self.player.global_x, self.player.global_y),
                "game_time": self.game_time
            }
            
            with open(filename, "w") as f: 
                json.dump(save_data, f)
            AUDIO.play("save")
            self.show_msg(f"Saved as {filename}!")
        except Exception as e:
            print(e)
            self.show_msg("Failed to Save!")

    def get_save_files(self):
        files = []
        try:
            for f in os.listdir("."):
                if f.startswith("save_") and f.endswith(".json"):
                    files.append(f)
        except: pass
        return files

    def load_game(self, filename):
        if not os.path.exists(filename): 
            self.show_msg("Save File Not Found!")
            return
        try:
            with open(filename, "r") as f: 
                data = json.load(f)
            
            GAME_STATS.load_from_dict(data["stats"])
            
            if "world" in data:
                self.world.load_from_dict(data["world"])
            else:
                self.world.reset_world()
            
            if "hotbar" in data:
                self.hotbar.slots = data["hotbar"]
            
            if "player_pos" in data:
                self.player.global_x, self.player.global_y = data["player_pos"]
            else:
                self.player.global_x = (MAP_WIDTH // 2) * TILE_SIZE
                self.player.global_y = ((MAP_HEIGHT // 2) * TILE_SIZE) + 150
                
            self.game_time = data.get("game_time", 6 * 60)

            self.stop_menu_music() 
            AUDIO.play("heal")
            self.show_msg(f"Loaded {GAME_STATS.player_name}!")
            self.state = STATE_OVERWORLD
            self.spawn_enemies(20)
        except Exception as e:
            print(e)
            self.show_msg("Failed to Load!")

    def draw_time_filter(self):
        alpha = 0
        hour = (self.game_time // 60) % 24
        
        if 18 <= hour < 20: alpha = 100 
        elif 20 <= hour or hour < 5: alpha = 180 
        elif 5 <= hour < 7: alpha = 80 
        
        if alpha > 0: 
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(alpha)
            overlay.fill((10, 10, 30))
            SCREEN.blit(overlay, (0,0))

    def draw_hud(self):
        # --- KONFIGURASI LAYOUT (Variable biar mudah di-tweak) ---
        panel_x, panel_y = 10, 10
        panel_w, panel_h = 240, 150  # Tinggi panel ditambah jadi 150 biar lega
        
        # Batas untuk Rata Kanan (Right Anchor)
        right_anchor_x = panel_x + panel_w - 15 
        left_anchor_x = panel_x + 15
        
        # Gambar Panel Background
        draw_panel(SCREEN, pygame.Rect(panel_x, panel_y, panel_w, panel_h), border=True)
        
        hour = int((self.game_time // 60) % 24)
        minute = int(self.game_time % 60)
        
        # --- LOGIKA RATA KANAN (RIGHT ALIGN) ---
        # Kita hitung lebar teks agar posisi X menyesuaikan panjang angka
        
        txt_day = f"Day {GAME_STATS.day}"
        w_day, h_day = FONT_BOLD.size(txt_day)
        
        txt_gold = f"{GAME_STATS.gold}G"
        w_gold, h_gold = FONT_BOLD.size(txt_gold) # Hitung lebar teks gold
        
        # --- BARIS 1: WAKTU & DAY ---
        # Waktu (Kiri)
        draw_text_shadow(SCREEN, f"{hour:02}:{minute:02}", FONT_BIG, left_anchor_x, panel_y + 10, C_ACCENT_GOLD)
        
        # Day (Kanan - Koordinat X dikurangi lebar teks)
        draw_text_shadow(SCREEN, txt_day, FONT_BOLD, right_anchor_x - w_day, panel_y + 18, C_TEXT_WHITE)

        # --- BARIS 2: LEVEL & GOLD ---
        # Level (Kiri)
        draw_text_shadow(SCREEN, f"Lv.{GAME_STATS.level}", FONT_BOLD, left_anchor_x, panel_y + 45, (100, 255, 255))
        
        # Gold (Kanan - Koordinat X dikurangi lebar teks)
        draw_text_shadow(SCREEN, txt_gold, FONT_BOLD, right_anchor_x - w_gold, panel_y + 45, C_ACCENT_GOLD)
        
        # --- BARIS 3: STAT BARS (TURUNKAN LAGI) ---
        # Sebelumnya mungkin di y+60 atau y+70, sekarang kita set ke y+85
        # Ini memberikan ruang agar teks Gold tidak menabrak teks HP
        bar_start_y = panel_y + 85 
        gap = 20 # Jarak antar bar lebih rapat sedikit biar muat
        
        draw_bar_fancy(SCREEN, left_anchor_x, bar_start_y, 210, 12, GAME_STATS.hp, GAME_STATS.max_hp, C_BAR_HP, "HP")
        draw_bar_fancy(SCREEN, left_anchor_x, bar_start_y + gap, 210, 12, GAME_STATS.stamina, GAME_STATS.max_stamina, C_BAR_STAMINA, "STM")
        draw_bar_fancy(SCREEN, left_anchor_x, bar_start_y + (gap*2), 210, 12, GAME_STATS.hunger, GAME_STATS.max_hunger, C_BAR_HUNGER, "HGR")

        # --- UPDATE TAMPILAN QUEST ---
        quest_panel_y = panel_y + panel_h + 8 
        draw_panel(SCREEN, pygame.Rect(panel_x, quest_panel_y, panel_w, 80), border=True)
        
        # Header Quest
        draw_text_shadow(SCREEN, "ACTIVE QUEST", FONT_BOLD, panel_x + (panel_w//2), quest_panel_y + 5, C_ACCENT_GOLD, center=True)
        
        quest = GAME_STATS.get_current_quest()
        text_center_x = panel_x + (panel_w//2)
        text_y = quest_panel_y + 30
        
        if quest:
            q_txt = f"{quest.desc} ({quest.current_val}/{quest.target_val})"
            draw_multiline_text_shadow(SCREEN, q_txt, FONT_UI_SMALL, text_center_x, text_y, 220, C_TEXT_WHITE, center=True)
        elif GAME_STATS.is_generating_quest:
            draw_text_shadow(SCREEN, "Mencari quest baru...", FONT_UI_SMALL, text_center_x, text_y + 10, (100, 255, 255), center=True)
        else:
            draw_text_shadow(SCREEN, "Kosong (Tidak ada Quest)", FONT_UI_SMALL, text_center_x, text_y + 10, C_TEXT_GREY, center=True)

    def draw_control_guide(self, surface):
        w, h = 180, 140
        x = SCREEN_WIDTH - w - 10
        y = 10 
        draw_panel(surface, pygame.Rect(x, y, w, h), border=True)
        draw_text_shadow(surface, "CONTROLS", FONT_BOLD, x + 50, y + 10, C_ACCENT_GOLD)
        
        controls = [("WASD", "Move"), ("SPACE", "Act/Sleep"), ("Q", "Shop"), ("E", "Inventory")]
        curr_y = y + 40
        for k, a in controls:
            surface.blit(FONT_UI_SMALL.render(f"[{k}]", True, C_ACCENT_GOLD), (x + 15, curr_y))
            surface.blit(FONT_UI_SMALL.render(a, True, C_TEXT_WHITE), (x + 70, curr_y))
            curr_y += 20

    def draw_main_menu(self):
        if ASSETS["menu_frames"]:
            self.menu_frame_index += self.menu_anim_speed * self.menu_anim_dir
            if self.menu_frame_index >= len(ASSETS["menu_frames"]) - 1:
                self.menu_frame_index = len(ASSETS["menu_frames"]) - 1
                self.menu_anim_dir = -1 
            elif self.menu_frame_index <= 0:
                self.menu_frame_index = 0
                self.menu_anim_dir = 1 
            frame_to_draw = ASSETS["menu_frames"][int(self.menu_frame_index)]
            SCREEN.blit(frame_to_draw, (0, 0))
        else: 
            SCREEN.fill(C_BG_DARK)

        dark_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dark_overlay.fill((0, 0, 0, 230)) 
        
        mx, my = get_corrected_mouse()
        light_rect = self.light_texture.get_rect(center=(mx, my))
        dark_overlay.blit(self.light_texture, light_rect, special_flags=pygame.BLEND_RGBA_SUB)
        SCREEN.blit(dark_overlay, (0, 0))

        for p in self.menu_particles: 
            p.update()
            p.draw(SCREEN)

        scale = 1.0 + 0.05 * math.sin(pygame.time.get_ticks() * 0.003)
        title_surf = FONT_TITLE.render("HARVEST ARENA", True, C_ACCENT_GOLD)
        w = int(title_surf.get_width() * scale)
        h = int(title_surf.get_height() * scale)
        scaled_title = pygame.transform.smoothscale(title_surf, (w, h))
        rect = scaled_title.get_rect(center=(SCREEN_WIDTH//2, 120))
        
        glow_surf = pygame.transform.smoothscale(title_surf, (w+20, h+20))
        glow_surf.fill((255, 200, 0, 50), special_flags=pygame.BLEND_RGBA_MULT)
        SCREEN.blit(glow_surf, glow_surf.get_rect(center=(SCREEN_WIDTH//2, 120)))
        SCREEN.blit(scaled_title, rect)

        self.btn_new.draw(SCREEN)
        self.btn_load.draw(SCREEN)
        self.btn_sets.draw(SCREEN)
        self.btn_quit.draw(SCREEN)

    def draw_settings_menu(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        SCREEN.blit(overlay, (0, 0))
        
        panel_rect = pygame.Rect(SCREEN_WIDTH//2 - 250, 100, 500, 400)
        draw_panel(SCREEN, panel_rect)
        draw_text_shadow(SCREEN, "SETTINGS", FONT_TITLE, SCREEN_WIDTH//2, 140, C_ACCENT_GOLD, center=True)
        
        y_start = 220
        for label, vol, setter in [("Music", AUDIO.music_vol, AUDIO.set_music_volume), ("SFX", AUDIO.sfx_vol, AUDIO.set_sfx_volume)]:
            draw_text_shadow(SCREEN, f"{label} Volume: {int(vol*100)}%", FONT_BIG, SCREEN_WIDTH//2, y_start, center=True)
            
            pygame.draw.rect(SCREEN, (50, 50, 50), (SCREEN_WIDTH//2 - 150, y_start + 40, 300, 15), border_radius=5)
            pygame.draw.rect(SCREEN, C_ACCENT_GOLD, (SCREEN_WIDTH//2 - 150, y_start + 40, 300 * vol, 15), border_radius=5)
            
            min_rect = pygame.Rect(SCREEN_WIDTH//2 - 200, y_start + 30, 30, 30)
            plus_rect = pygame.Rect(SCREEN_WIDTH//2 + 170, y_start + 30, 30, 30)
            
            pygame.draw.rect(SCREEN, C_BTN_NORMAL, min_rect, border_radius=5)
            draw_text_shadow(SCREEN, "-", FONT_BOLD, min_rect.centerx, min_rect.centery, center=True)
            
            pygame.draw.rect(SCREEN, C_BTN_NORMAL, plus_rect, border_radius=5)
            draw_text_shadow(SCREEN, "+", FONT_BOLD, plus_rect.centerx, plus_rect.centery, center=True)
            
            y_start += 100
        self.btn_back.draw(SCREEN)

    def draw_pause_menu(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        SCREEN.blit(overlay, (0, 0))
        
        panel_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, 130, 300, 380)
        draw_panel(SCREEN, panel_rect)
        draw_text_shadow(SCREEN, "PAUSED", FONT_TITLE, SCREEN_WIDTH//2, 160, C_ACCENT_GOLD, center=True)
        
        self.btn_res.draw(SCREEN)
        self.btn_sav.draw(SCREEN)
        self.btn_lod.draw(SCREEN)
        self.btn_men.draw(SCREEN)

    def draw_shop(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0,0,0,180))
        SCREEN.blit(overlay, (0,0))
        
        panel_rect = pygame.Rect(50, 50, 900, 500)
        draw_panel(SCREEN, panel_rect)
        draw_text_shadow(SCREEN, "PIERRE'S SHOP", FONT_TITLE, SCREEN_WIDTH//2, 80, C_ACCENT_GOLD, center=True)
        draw_text_shadow(SCREEN, f"Gold: {GAME_STATS.gold} G", FONT_BIG, 800, 80, C_ACCENT_GOLD)
        
        cat_rects = []
        categories = ["SEEDS", "ITEMS", "LOOT", "CROPS"]
        start_x = 100
        
        for cat in categories:
            r = pygame.Rect(start_x, 140, 180, 40)
            is_active = (self.shop_category == cat)
            col = C_ACCENT_GOLD if is_active else C_BTN_NORMAL
            txt_col = (0,0,0) if is_active else C_TEXT_WHITE
            
            pygame.draw.rect(SCREEN, col, r, border_radius=8)
            draw_text_shadow(SCREEN, cat, FONT_BOLD, r.centerx, r.centery, txt_col, center=True)
            cat_rects.append((r, cat))
            start_x += 200
            
        items_to_show = SHOP_INVENTORY[self.shop_category]
        y_pos = 220
        x_pos = 100
        
        for name, buy_price in items_to_show:
            item_rect = pygame.Rect(x_pos, y_pos, 380, 60)
            mx, my = get_corrected_mouse()
            is_hover = item_rect.collidepoint((mx, my))
            box_col = (60, 60, 70) if is_hover else (50, 50, 50)
            
            pygame.draw.rect(SCREEN, box_col, item_rect, border_radius=5)
            pygame.draw.rect(SCREEN, (80, 80, 80), item_rect, 1, border_radius=5)
            
            player_has = GAME_STATS.inventory.get(name, 0)
            item_data = ITEM_DATA.get(name, {"sell": 0})
            sell_price = item_data["sell"]
            
            draw_text_shadow(SCREEN, name, FONT_BOLD, x_pos + 10, y_pos + 5, C_ACCENT_GOLD)
            draw_text_shadow(SCREEN, f"Owned: {player_has}", FONT_UI_SMALL, x_pos + 10, y_pos + 35, C_TEXT_GREY)
            
            buy_col = C_TEXT_WHITE if GAME_STATS.gold >= buy_price else (255, 100, 100)
            draw_text_shadow(SCREEN, f"Buy: {buy_price}G", FONT_UI, x_pos + 200, y_pos + 20, buy_col)
            draw_text_shadow(SCREEN, f"Sell: {sell_price}G", FONT_UI, x_pos + 300, y_pos + 20, (100, 255, 100))
            
            y_pos += 70
            if y_pos > 480: 
                y_pos = 220
                x_pos += 400
                
        info = FONT_UI.render("[Left Click] Buy | [Right Click] Sell | [Q] Close", True, C_TEXT_GREY)
        SCREEN.blit(info, (SCREEN_WIDTH//2 - info.get_width()//2, 520))
        return cat_rects, items_to_show 

    def draw_inventory_menu(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0,0,0,180))
        SCREEN.blit(overlay, (0,0))
        
        panel_rect = pygame.Rect(50, 50, 900, 500)
        draw_panel(SCREEN, panel_rect)
        draw_text_shadow(SCREEN, "INVENTORY", FONT_TITLE, SCREEN_WIDTH//2, 80, C_ACCENT_GOLD, center=True)
        
        equipped_items = set()
        for slot_code in self.hotbar.slots:
            if slot_code in CODE_TO_NAME: 
                equipped_items.add(CODE_TO_NAME[slot_code])
                
        y_pos = 150
        x_pos = 100
        mx, my = get_corrected_mouse()
        
        for item, count in GAME_STATS.inventory.items():
            if item in equipped_items or count <= 0: 
                continue
                
            item_rect = pygame.Rect(x_pos, y_pos, 250, 60)
            is_hover = item_rect.collidepoint((mx, my))
            is_selected = (self.selected_item_name == item)
            
            bg_col = (70, 70, 90) if is_selected else ((60, 60, 70) if is_hover else (50, 50, 50))
            border_col = C_ACCENT_GOLD if is_selected else (80, 80, 80)
            
            pygame.draw.rect(SCREEN, bg_col, item_rect, border_radius=5)
            pygame.draw.rect(SCREEN, border_col, item_rect, 2 if is_selected else 1, border_radius=5)
            
            data = ITEM_DATA.get(item, {"type": "Misc"})
            draw_text_shadow(SCREEN, f"{item} (x{count})", FONT_BOLD, x_pos + 10, y_pos + 5)
            draw_text_shadow(SCREEN, f"{data['type']}", FONT_UI_SMALL, x_pos + 10, y_pos + 35, C_TEXT_GREY)
            
            y_pos += 70
            if y_pos > 400: 
                y_pos = 150
                x_pos += 260
                
        draw_text_shadow(SCREEN, "Select item above, then [Left Click] Hotbar to Equip, [Right Click] to Unequip", FONT_UI, SCREEN_WIDTH//2, 460, C_ACCENT_GOLD, center=True)
        return self.hotbar.draw(SCREEN, y_pos=500)

    # --- MENU INPUT NAMA ---
    def draw_input_name_menu(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        SCREEN.blit(overlay, (0, 0))
        
        panel_rect = pygame.Rect(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 100, 400, 200)
        draw_panel(SCREEN, panel_rect)
        
        draw_text_shadow(SCREEN, "ENTER YOUR NAME", FONT_BIG, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 70, C_ACCENT_GOLD, center=True)
        
        # Kotak Input
        box_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 20, 300, 40)
        pygame.draw.rect(SCREEN, (20, 20, 30), box_rect)
        pygame.draw.rect(SCREEN, C_ACCENT_GOLD, box_rect, 2)
        
        # Teks
        txt_surf = FONT_BOLD.render(self.input_text + "|", True, C_TEXT_WHITE)
        SCREEN.blit(txt_surf, (box_rect.x + 10, box_rect.y + 10))
        
        draw_text_shadow(SCREEN, "[ENTER] Start  [ESC] Back", FONT_UI, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50, C_TEXT_GREY, center=True)

    # --- MENU PILIH LOAD GAME ---
    def draw_load_select_menu(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        SCREEN.blit(overlay, (0, 0))
        
        panel_rect = pygame.Rect(SCREEN_WIDTH//2 - 200, 100, 400, 400)
        draw_panel(SCREEN, panel_rect)
        
        draw_text_shadow(SCREEN, "SELECT SAVE FILE", FONT_BIG, SCREEN_WIDTH//2, 130, C_ACCENT_GOLD, center=True)
        
        if not self.save_files:
            draw_text_shadow(SCREEN, "No Save Files.", FONT_BOLD, SCREEN_WIDTH//2, 250, C_TEXT_GREY, center=True)
        else:
            y = 180
            for i, filename in enumerate(self.save_files):
                col = C_ACCENT_GOLD if i == self.selected_save_idx else C_TEXT_WHITE
                prefix = "> " if i == self.selected_save_idx else "  "
                disp_name = filename.replace("save_", "").replace(".json", "")
                draw_text_shadow(SCREEN, f"{prefix}{disp_name}", FONT_BOLD, SCREEN_WIDTH//2 - 100, y, col)
                y += 40
        
        draw_text_shadow(SCREEN, "[UP/DOWN] Select  [ENTER] Load  [ESC] Back", FONT_UI, SCREEN_WIDTH//2, 460, C_TEXT_GREY, center=True)

    # --- SISTEM PROLOG ---
    def update_prologue(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.prologue_char_idx = 0
            self.prologue_idx += 1
            if self.prologue_idx >= len(self.prologue_lines):
                # Selesai Prolog
                self.start_new_game()

    def draw_prologue(self):
        SCREEN.fill((0, 0, 0)) # Latar Hitam
        
        if self.prologue_idx < len(self.prologue_lines):
            line = self.prologue_lines[self.prologue_idx]
            
            self.prologue_timer += 1
            if self.prologue_timer >= self.prologue_speed:
                if self.prologue_char_idx < len(line):
                    self.prologue_char_idx += 1
                    AUDIO.play("type")
                self.prologue_timer = 0
            
            visible_text = line[:self.prologue_char_idx]
            draw_text_shadow(SCREEN, visible_text, FONT_STORY, SCREEN_WIDTH//2, SCREEN_HEIGHT//2, C_TEXT_WHITE, center=True)
            
            if self.prologue_char_idx >= len(line):
                if (pygame.time.get_ticks() // 500) % 2 == 0:
                    draw_text_shadow(SCREEN, "[SPACE] Continue...", FONT_UI_SMALL, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 50, C_TEXT_GREY)

    # --- LOOP UPDATE ---
    def update_main_menu(self, event):
        events = [event] 
        if self.btn_new.update(events): 
            self.state = STATE_INPUT_NAME
            self.input_text = ""
            AUDIO.play("select")
        elif self.btn_load.update(events): 
            self.state = STATE_LOAD_MENU
            self.save_files = self.get_save_files()
            self.selected_save_idx = 0
            AUDIO.play("select")
        elif self.btn_sets.update(events): 
            self.state = STATE_SETTINGS
        elif self.btn_quit.update(events): 
            pygame.quit()
            sys.exit()

    def update_settings_menu(self, event):
        mx, my = get_corrected_mouse()
        events = [event]
        if self.btn_back.update(events): 
            self.state = STATE_MAIN_MENU
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if mx < SCREEN_WIDTH//2: 
                if 250 < my < 280: 
                    AUDIO.set_music_volume(AUDIO.music_vol - 0.1)
                elif 350 < my < 380: 
                    AUDIO.set_sfx_volume(AUDIO.sfx_vol - 0.1)
            else: 
                if 250 < my < 280: 
                    AUDIO.set_music_volume(AUDIO.music_vol + 0.1)
                elif 350 < my < 380: 
                    AUDIO.set_sfx_volume(AUDIO.sfx_vol + 0.1)

    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            clock.tick(60)
            self.clean_hotbar()
            
            # --- LOGIKA FADE ---
            if self.fade_state == "FADE_OUT":
                self.fade_alpha += 15 
                if self.fade_alpha >= 255: 
                    self.fade_alpha = 255
                    self.fade_state = "BLACK"
                    self.black_screen_timer = 30 
                    
                    if self.pending_menu_action is None:
                        self._perform_day_reset() 
            
            elif self.fade_state == "BLACK":
                self.black_screen_timer -= 1
                if self.black_screen_timer <= 0:
                    if self.pending_menu_action == "NEW":
                        GAME_STATS.reset()
                        self.world.reset_world()
                        self.state = STATE_PROLOGUE 
                        self.prologue_idx = 0
                        self.pending_menu_action = None
                    elif self.pending_menu_action == "LOAD":
                        self.pending_menu_action = None
                    self.fade_state = "FADE_IN"

            elif self.fade_state == "FADE_IN":
                self.fade_alpha -= 10
                if self.fade_alpha <= 0: 
                    self.fade_alpha = 0
                    self.fade_state = "IDLE"

            # --- LOGIKA GAME ---
            if self.state == STATE_OVERWORLD and self.fade_state == "IDLE":
                self.game_time += self.time_speed
                if self.game_time >= 26 * 60: 
                    self.trigger_day_transition(passed_out=True) 
                    
                self.hunger_timer += 1
                if self.hunger_timer >= 200: 
                    self.hunger_timer = 0
                    GAME_STATS.hunger = max(0, GAME_STATS.hunger - 1)
                    if GAME_STATS.hunger <= 0: 
                        GAME_STATS.hp = max(0, GAME_STATS.hp - 1)
                    if GAME_STATS.hp <= 0: 
                        self.trigger_day_transition(passed_out=True) 

            target_cam_x = self.player.global_x - SCREEN_WIDTH // 2
            target_cam_y = self.player.global_y - SCREEN_HEIGHT // 2
            camera_x = max(0, min(target_cam_x, (MAP_WIDTH * TILE_SIZE) - SCREEN_WIDTH))
            camera_y = max(0, min(target_cam_y, (MAP_HEIGHT * TILE_SIZE) - SCREEN_HEIGHT))
            
            if self.state == STATE_OVERWORLD:
                for t in self.world.get_all_tiles(): 
                    t.update()

            mouse_click = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    running = False
                
                if event.type == pygame.VIDEORESIZE:
                    update_scale()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: 
                    mouse_click = True
                
                if self.state == STATE_MAIN_MENU: 
                    self.update_main_menu(event)
                elif self.state == STATE_SETTINGS: 
                    self.update_settings_menu(event)
                elif self.state == STATE_PROLOGUE: 
                    self.update_prologue(event) 
                
                elif self.state == STATE_INPUT_NAME:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            if len(self.input_text) > 0:
                                self.trigger_menu_transition("NEW")
                            else:
                                AUDIO.play("error")
                        elif event.key == pygame.K_BACKSPACE:
                            self.input_text = self.input_text[:-1]
                        elif event.key == pygame.K_ESCAPE:
                            self.state = STATE_MAIN_MENU
                        else:
                            if len(self.input_text) < 12: 
                                self.input_text += event.unicode

                elif self.state == STATE_LOAD_MENU:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.state = STATE_MAIN_MENU
                        elif event.key == pygame.K_UP:
                            self.selected_save_idx = max(0, self.selected_save_idx - 1)
                            AUDIO.play("select")
                        elif event.key == pygame.K_DOWN:
                            self.selected_save_idx = min(len(self.save_files) - 1, self.selected_save_idx + 1)
                            AUDIO.play("select")
                        elif event.key == pygame.K_RETURN:
                            if self.save_files:
                                target_file = self.save_files[self.selected_save_idx]
                                self.load_game(target_file)
                            else:
                                AUDIO.play("error")

                elif self.state == STATE_PAUSE:
                    events = [event]
                    if self.btn_res.update(events): 
                        self.state = STATE_OVERWORLD
                    elif self.btn_sav.update(events): 
                        self.save_game()
                    elif self.btn_lod.update(events): 
                        self.state = STATE_LOAD_MENU
                        self.save_files = self.get_save_files()
                        self.selected_save_idx = 0
                    elif self.btn_men.update(events): 
                        self.state = STATE_MAIN_MENU
                        self.play_menu_music()
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: 
                        self.state = STATE_OVERWORLD

                elif self.state == STATE_OVERWORLD and self.fade_state == "IDLE":
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: 
                        self.state = STATE_PAUSE
                        
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 4: 
                            self.hotbar.selected = (self.hotbar.selected - 1) % len(self.hotbar.slots)
                            AUDIO.play("select")
                        elif event.button == 5: 
                            self.hotbar.selected = (self.hotbar.selected + 1) % len(self.hotbar.slots)
                            AUDIO.play("select")
                        
                        # --- [FITUR UNEQUIP] KLIK KANAN UNTUK KEMBALIKAN KE INVENTORY ---
                        elif event.button == 3:
                             mx, my = get_corrected_mouse()
                             total_width = len(self.hotbar.slots) * (self.hotbar.slot_size + 5)
                             start_x = (SCREEN_WIDTH - total_width) // 2
                             for i in range(len(self.hotbar.slots)):
                                r = pygame.Rect(start_x + (i * 55), SCREEN_HEIGHT - 70, 50, 50)
                                if r.collidepoint((mx, my)):
                                    self.hotbar.slots[i] = "EMPTY" # Kosongkan slot
                                    AUDIO.play("sell") 
                                    break
                                    
                        elif event.button == 1:
                            mx, my = get_corrected_mouse()
                            clicked_hotbar = False
                            total_width = len(self.hotbar.slots) * (self.hotbar.slot_size + 5)
                            start_x = (SCREEN_WIDTH - total_width) // 2
                            
                            for i in range(len(self.hotbar.slots)):
                                r = pygame.Rect(start_x + (i * 55), SCREEN_HEIGHT - 70, 50, 50)
                                if r.collidepoint((mx, my)):
                                    self.hotbar.selected = i
                                    AUDIO.play("select")
                                    clicked_hotbar = True
                                    break
                            
                            if not clicked_hotbar:
                                if not self.try_sleep():
                                    tool = self.hotbar.slots[self.hotbar.selected]
                                    t = self.get_tile_under_mouse(camera_x, camera_y)
                                    
                                    # --- INTERAKSI TILE & CONSUME ---
                                    action_done = False
                                    
                                    # 1. Coba Interaksi Tanah
                                    if t and math.hypot(t.global_x*TILE_SIZE - self.player.global_x, t.global_y*TILE_SIZE - self.player.global_y) < 150:
                                        success, m = t.interact(tool)
                                        if success: 
                                            if m: self.show_msg(m)
                                            action_done = True
                                    
                                    # 2. Jika Gagal, Coba Consume Item
                                    if not action_done:
                                        self.try_consume_item()

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_1: self.hotbar.selected = 0
                        elif event.key == pygame.K_2: self.hotbar.selected = 1
                        elif event.key == pygame.K_3: self.hotbar.selected = 2
                        elif event.key == pygame.K_4: self.hotbar.selected = 3
                        elif event.key == pygame.K_5: self.hotbar.selected = 4
                        elif event.key == pygame.K_q: 
                            self.state = STATE_SHOP
                            AUDIO.play("select")
                        elif event.key == pygame.K_e: 
                            self.state = STATE_INVENTORY
                            AUDIO.play("select")
                        elif event.key == pygame.K_SPACE:
                            if not self.try_sleep():
                                tool = self.hotbar.slots[self.hotbar.selected]
                                t = self.get_tile_under_mouse(camera_x, camera_y)
                                
                                action_done = False
                                if t and math.hypot(t.global_x*TILE_SIZE - self.player.global_x, t.global_y*TILE_SIZE - self.player.global_y) < 150:
                                    success, m = t.interact(tool)
                                    if success:
                                        if m: self.show_msg(m)
                                        action_done = True
                                
                                if not action_done:
                                    self.try_consume_item()

                elif self.state == STATE_SHOP:
                    if event.type == pygame.KEYDOWN and (event.key == pygame.K_q or event.key == pygame.K_ESCAPE): 
                        self.state = STATE_OVERWORLD
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mx, my = get_corrected_mouse()
                        start_x = 100
                        for cat in ["SEEDS", "ITEMS", "LOOT", "CROPS"]:
                            if pygame.Rect(start_x, 140, 180, 40).collidepoint((mx, my)): 
                                self.shop_category = cat
                                AUDIO.play("select")
                            start_x += 200
                        items = SHOP_INVENTORY[self.shop_category]
                        y_p = 220
                        x_p = 100
                        for name, price in items:
                            r = pygame.Rect(x_p, y_p, 380, 60)
                            if r.collidepoint((mx, my)):
                                if event.button == 1: # Beli
                                    if GAME_STATS.gold >= price: 
                                        GAME_STATS.gold -= price
                                        GAME_STATS.inventory[name] = GAME_STATS.inventory.get(name,0)+1
                                        AUDIO.play("buy")
                                    else: 
                                        AUDIO.play("error")
                                elif event.button == 3: # Jual
                                    if GAME_STATS.inventory.get(name, 0) > 0:
                                        sv = ITEM_DATA.get(name, {}).get("sell", 0)
                                        if sv > 0: 
                                            GAME_STATS.inventory[name] -= 1
                                            GAME_STATS.gold += sv
                                            AUDIO.play("sell")
                                    else: 
                                        AUDIO.play("error")
                            y_p += 70
                            if y_p > 480: 
                                y_p = 220
                                x_p += 400

                elif self.state == STATE_INVENTORY:
                    if event.type == pygame.KEYDOWN and (event.key == pygame.K_e or event.key == pygame.K_ESCAPE): 
                        self.state = STATE_OVERWORLD
                    
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mx, my = get_corrected_mouse()
                        
                        # --- KLIK KANAN: UNEQUIP DI MENU INVENTORY ---
                        if event.button == 3: 
                            total_width = len(self.hotbar.slots) * (self.hotbar.slot_size + 5)
                            start_x = (SCREEN_WIDTH - total_width) // 2
                            for i in range(len(self.hotbar.slots)):
                                r = pygame.Rect(start_x + (i * 55), 500, 50, 50) 
                                if r.collidepoint((mx, my)):
                                    self.hotbar.slots[i] = "EMPTY"
                                    AUDIO.play("sell")
                                    break
                                    
                        elif mouse_click:
                            it_y = 150
                            it_x = 100
                            equipped = {CODE_TO_NAME[s] for s in self.hotbar.slots if s in CODE_TO_NAME}
                            for item, count in GAME_STATS.inventory.items():
                                if item in equipped or count <= 0: continue
                                if pygame.Rect(it_x, it_y, 250, 60).collidepoint((mx, my)):
                                    if item in NAME_TO_CODE: 
                                        self.selected_item_name = item
                                        AUDIO.play("select")
                                it_y += 70
                                if it_y > 400: 
                                    it_y = 150
                                    it_x += 260
                            if self.selected_item_name:
                                total_width = len(self.hotbar.slots) * (self.hotbar.slot_size + 5)
                                start_x = (SCREEN_WIDTH - total_width) // 2
                                for i in range(len(self.hotbar.slots)):
                                    r = pygame.Rect(start_x + (i * 55), 500, 50, 50)
                                    if r.collidepoint((mx, my)):
                                        self.hotbar.slots[i] = NAME_TO_CODE[self.selected_item_name]
                                        self.selected_item_name = None
                                        AUDIO.play("buy")

                elif self.state == STATE_BATTLE:
                    if event.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]: 
                        self.battle.handle_input(event)
                    elif event.type in [pygame.USEREVENT + 2, pygame.USEREVENT + 3]:
                        self.battle.handle_timers(event)

            # --- MENGGAMBAR ---
            if self.state == STATE_MAIN_MENU: 
                self.draw_main_menu()
            elif self.state == STATE_SETTINGS: 
                self.draw_settings_menu()
            elif self.state == STATE_PROLOGUE: 
                self.draw_prologue()
            elif self.state == STATE_INPUT_NAME: 
                self.draw_input_name_menu() 
            elif self.state == STATE_LOAD_MENU: 
                self.draw_load_select_menu() 
            
            elif self.state == STATE_OVERWORLD or self.state == STATE_PAUSE:
                self.player.update(pygame.key.get_pressed(), [self.house_rect]) 
                self.check_encounter()
                self.enemies_ow.update(self.safe_zone_rect) 
                
                SCREEN.fill((20, 20, 20))
                
                # --- SISTEM RENDERING LAYER (Y-SORT) ---
                render_list = []

                for t in self.world.get_all_tiles(): 
                    overlay = t.draw(SCREEN, camera_x, camera_y) 
                    if overlay:
                        render_list.append(overlay)

                render_list.append({
                    "type": "PLAYER",
                    "img": self.player.image,
                    "pos": (self.player.global_x - camera_x - 20, self.player.global_y - camera_y - 20),
                    "sort_y": self.player.rect.bottom 
                })

                for e in self.enemies_ow:
                    esx = e.global_x - camera_x - 20
                    esy = e.global_y - camera_y - 20
                    if -50 < esx < SCREEN_WIDTH+50 and -50 < esy < SCREEN_HEIGHT+50:
                        render_list.append({
                            "type": "ENEMY",
                            "img": e.image,
                            "pos": (esx, esy),
                            "sort_y": e.rect.bottom 
                        })

                sx = self.house_rect.x - camera_x
                sy = self.house_rect.y - camera_y
                render_list.append({
                    "type": "HOUSE",
                    "img": ASSETS["house"],
                    "pos": (sx, sy),
                    "sort_y": self.house_rect.bottom 
                })

                render_list.sort(key=lambda x: x["sort_y"])

                for item in render_list:
                    SCREEN.blit(item["img"], item["pos"])

                if math.hypot(self.player.global_x - self.house_rect.centerx, self.player.global_y - (self.house_rect.bottom-40)) < 80:
                    sx_center = self.house_rect.centerx - camera_x
                    sy_top = self.house_rect.top - camera_y - 20
                    pygame.draw.circle(SCREEN, (255, 255, 0, 100), (sx + 125, sy + 210), 20, 2)
                    txt = "SLEEP [SPACE]" if self.game_time >= 1080 else "Too early..."
                    col = C_ACCENT_GOLD if self.game_time >= 1080 else C_TEXT_GREY
                    draw_text_shadow(SCREEN, txt, FONT_BOLD, sx_center, sy_top, col, center=True)

                t_t = self.get_tile_under_mouse(camera_x, camera_y)
                if t_t: 
                    pygame.draw.rect(SCREEN, (255, 255, 255), (t_t.rect.x-camera_x, t_t.rect.y-camera_y, TILE_SIZE, TILE_SIZE), 2)
                
                self.draw_time_filter()
                self.hotbar.draw(SCREEN)
                self.draw_hud()
                self.draw_control_guide(SCREEN)
                
                if self.msg_timer > 0:
                    self.msg_timer -= 1 
                    msg_surf = FONT_BOLD.render(self.msg_text, True, C_ACCENT_GOLD)
                    bg_msg = pygame.Surface((msg_surf.get_width()+40, 50), pygame.SRCALPHA)
                    pygame.draw.rect(bg_msg, (0,0,0,200), bg_msg.get_rect(), border_radius=20)
                    bg_msg.blit(msg_surf, (20, 15))
                    SCREEN.blit(bg_msg, (SCREEN_WIDTH//2 - bg_msg.get_width()//2, 100))

                if self.state == STATE_PAUSE: 
                    self.draw_pause_menu()
            
            elif self.state == STATE_SHOP: 
                self.draw_shop()
            
            elif self.state == STATE_INVENTORY: 
                hb_rects = self.draw_inventory_menu()

            elif self.state == STATE_BATTLE:
                self.battle.update()
                self.battle.draw(SCREEN)
                if not self.battle.active:
                    if self.battle.won: 
                        self.state = STATE_OVERWORLD
                    else:
                        GAME_STATS.gold = max(0, GAME_STATS.gold // 2)
                        GAME_STATS.hp = 10
                        self.show_msg("Defeated...")
                        self.player.global_x = (MAP_WIDTH//2)*TILE_SIZE
                        self.player.global_y = ((MAP_HEIGHT//2)*TILE_SIZE)+150
                        self.state = STATE_OVERWORLD
                    self.spawn_enemies(20)

            if self.fade_state != "IDLE":
                fs = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                fs.fill((0,0,0))
                fs.set_alpha(self.fade_alpha)
                SCREEN.blit(fs, (0,0))
                if self.fade_state == "BLACK":
                    if self.pending_menu_action is None:
                        draw_text_shadow(SCREEN, f"DAY {GAME_STATS.day}", FONT_TITLE, SCREEN_WIDTH//2, SCREEN_HEIGHT//2, center=True)
            
            scaled_surf = pygame.transform.scale(SCREEN, (int(SCREEN_WIDTH * GLOBAL_SCALE), int(SCREEN_HEIGHT * GLOBAL_SCALE)))
            WINDOW.fill((0, 0, 0))
            WINDOW.blit(scaled_surf, GLOBAL_OFFSET)
            
            pygame.display.flip()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = MasterGame()
    game.run()

