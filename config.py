#Remote imports
import pygame

#Local imports
from pgu import gui, high

#--------------------------------------------------------------------
#Functions
#--------------------------------------------------------------------

def load_settings():
    global difficulty
    settings = {}

    try:
        f = open('settings.txt')
        for line in f.readlines():
            key, value = line.strip().split(":")
            settings[key] = int(value)
        f.close()
        difficulty = settings['difficulty']
    except:
        difficulty = DEFAULT_DIFFICULTY
 
def save_settings():
    try:
        f = open('settings.txt',"w")
        f.write("%s:%d\n"%("difficulty", difficulty))
        f.close()
    except:
        pass   
    

def set_difficulty(difficulty_const):
    global difficulty, board_size, longest_trip_needed, longest_trip_to_deal 
    global fill_board, card_size, high_score_filename, current_highs, current_highs_key 
    global card_speed, card_font_size, new_boards_at_start
    if difficulty_const == EASY:
        card_font_size = CARD_FONT_SIZE_LARGE
        difficulty = EASY
        board_size = BOARD_SMALL
        longest_trip_needed = TRIP_SMALL_TO_WIN 
        longest_trip_to_deal = TRIP_SMALL_TO_DEAL  
        fill_board = False    
        card_size = CARD_LARGE       
        card_speed = CARD_SPEED_FAST
        new_boards_at_start = NEW_BOARDS_EASY
    else: 
        card_font_size = CARD_FONT_SIZE_SMALL 
        board_size = BOARD_LARGE
        card_size = CARD_SMALL 
        card_speed = CARD_SPEED_SLOW
        if difficulty_const == MED_DIF:         
            difficulty = MED_DIF
            longest_trip_needed = TRIP_MED_TO_WIN 
            longest_trip_to_deal = TRIP_MED_TO_DEAL  
            fill_board = False        
            new_boards_at_start = NEW_BOARDS_MED
        elif difficulty_const == HARD:
            difficulty = HARD
            longest_trip_needed = TRIP_LARGE_TO_WIN 
            longest_trip_to_deal = TRIP_LARGE_TO_DEAL      
            fill_board = False   
            new_boards_at_start = NEW_BOARDS_HARD
        elif difficulty_const == SUPER:
            difficulty = SUPER
            longest_trip_needed = TRIP_LARGE_TO_WIN 
            longest_trip_to_deal = TRIP_LARGE_TO_DEAL      
            fill_board = True                            
            new_boards_at_start = NEW_BOARDS_SUPER  

def get_hs_key(mode, difficulty):
    if mode == mode == PLAN_AHEAD:
        f = 'plan_ahead'
    else:
        f = 'time_challenge'
    
    if difficulty == EASY:
        s = 'easy'
    elif difficulty == MED_DIF:
        s = 'med'
    elif difficulty == HARD:
        s = 'hard'
    elif difficulty == SUPER:
        s = 'super'
        
    key = '_'.join([f, s])
    return key

def get_readable_difficulty(dif):
    if dif == EASY:
        return "Easy"
    elif dif == MED_DIF:
        return "Medium"
    elif dif == HARD:
        return "Hard"
    elif dif == SUPER:
        return "Superstar"
    
def get_readable_game_mode(mode):
    if mode == RELAXED:
        return "Relaxed"
    elif mode == TIME_CHALLENGE:
        return "Time Challenge"
    elif mode == PLAN_AHEAD:
        return "Plan Ahead"        

#--------------------------------------------------------------------
#CONSTANTS
#--------------------------------------------------------------------

#Screen
FRAME_RATE = 30
OFFSCREEN = (-500, -500)
hw_surface = 0
fullscreen = True

#Rooms
TITLE_SCREEN = 1
GAME_ROOM = 2
GAME_MODE_ROOM = 3
HIGH_SCORES_ROOM = 4
CREDITS = 5
OPTIONS = 6
LOADING_SCREEN = 7
HELP1 = 8
HELP2 = 9

#Game modes
RELAXED = 1
TIME_CHALLENGE = 2
PLAN_AHEAD = 3

#Difficulties
EASY = 1
MED_DIF = 2
HARD = 3
SUPER = 4

DEFAULT_DIFFICULTY = MED_DIF

#Board
BOARD_SMALL = (4, 4)
BOARD_MED = (6, 4)
BOARD_LARGE = (6, 6)

#Continents
EUROPE = 1
AFRICA = 2
USA = 3
EAST_ASIA = 4
WEST_ASIA = 5

#Trip
TRIP_SMALL_TO_DEAL = 7
TRIP_MED_TO_DEAL = 14
TRIP_LARGE_TO_DEAL = 21

TRIP_SMALL_TO_WIN = 7
TRIP_MED_TO_WIN = 14
TRIP_LARGE_TO_WIN = 21

#Cards
CARD_SMALL = (70, 70)
CARD_MED = (85, 85)
CARD_LARGE = (110, 110)

CARD_SPEED_SLOW = .3
CARD_SPEED_MED = .5
CARD_SPEED_FAST = .5

CARD_FONT_SIZE_SMALL = 10
CARD_FONT_SIZE_LARGE = 14

#Colors
GRAY1 = (72, 72, 72)
GRAY2 = (92, 92, 92)
GRAY3 = (126, 126, 126)
GRAY4 = (155, 155, 155)
GRAY5 = (182, 182, 182)
GRAYS = [GRAY1, GRAY2, GRAY3, GRAY4, GRAY5]
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CREAM_OB = (252, 245, 227)
MAGENTA_OB = (252, 0, 255)
OB_COLOR = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

COLOR1 = pygame.Color('#b42a0b')      #Red
COLOR2 = pygame.Color('#ecb911')      #Yellow  
COLOR3 = pygame.Color('#346b10')       #Green
COLOR4 = pygame.Color('#7aa59b')      #Light Blue
COLOR5 = pygame.Color('#40565c')        #Dark Blue

COLORS = [COLOR1, COLOR2, COLOR3, COLOR4, COLOR5]

NEW_BOARDS_EASY = 3
NEW_BOARDS_MED = 3
NEW_BOARDS_HARD = 3
NEW_BOARDS_SUPER = 3

#--------------------------------------------------------------------
#Variables
#--------------------------------------------------------------------

#Screen
screen_size = (1024, 600)
screen_center = (screen_size[0]/2, screen_size[1]/2)
gui_theme = gui.Theme("assets/images/gui/themes/default")

#Rooms
room = LOADING_SCREEN
all_highs = high.Highs('high_scores.txt')
current_highs = high.Highs('high_scores.txt')['time_challenge_med']

#Game
board_size = BOARD_LARGE
map_size = (520, 520)
fill_board = 0
use_darkness = 1
paused = False

#Game Modes
game_mode = TIME_CHALLENGE
time_challenge_start_time = 2
min_advance_time = 20
max_time_bank = 200
new_boards_left = 0
new_boards_at_start = 0

plan_ahead_start_swaps = 5
min_advance_swaps = 4
max_swap_bank = 20

#Continent
continent = AFRICA

#Trip
longest_trip_needed = TRIP_LARGE_TO_WIN              #How many cards in a trip
longest_trip_to_deal = TRIP_LARGE_TO_DEAL

#Cards
card_size = CARD_SMALL
card_speed = .3

#Options
card_font_size = 0
interface_font_size = 16
interface_font_size_big = 20
interface_font_color = BLACK
interface_font_color_big = COLOR5

#Fonts
font_mono = 'assets/fonts/liberation/LiberationMono-Bold.ttf'
font_sans = 'assets/fonts/vera/Vera.ttf'
font_logo = 'assets/fonts/sfbigwhiskey/SFBigWhiskey.ttf'

#Misc
default_zoom_time = 300 #Default zoom time for ZoomImage in my_gui.py, in ms
zoom_lifetime = 1500 #How long in ms will the zoom images stay around before zooming back out?
default_fade_time = 2500 #Default fade time for FadeOut in my_gui.py, in ms
high_score_filename = 'high_scores.txt'
title_screen_first_load = True
card_shadow = 0

#Map blinker
blinker_size = (75, 75)
blinker_color_selected = RED
blinker_color_right_click = GREEN
map_pos = (0,0)
  

#--------------------------------------------------------------------
#Init
#--------------------------------------------------------------------
load_settings()
set_difficulty(difficulty)

debug = False


