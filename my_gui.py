#Remote imports
import pygame

#Local imports
#import config
import resources
from events import *
from pgu import gui

#--------------------------------------------------------------------
#New GUI Classes
#--------------------------------------------------------------------
class ImageButton(gui.button._button):
    
    def __init__(self, image, image_hover=None, image_down=None, **params):
        gui.button._button.__init__(self,**params)
        self.ev_manager = params['ev_manager']
        self.style.image = image
        if image_hover == None:
            self.style.image_hover = self.style.image
        else:
            self.style.image_hover = image_hover
        if image_down == None:
            self.style.image_down = self.style.image_hover
        else:
            self.style.image_down = image_down
        widths = [self.style.image.get_width(), self.style.image_hover.get_width(), 
                  self.style.image_down.get_width()]
        heights = [self.style.image.get_height(), self.style.image_hover.get_height(), 
                  self.style.image_down.get_height()]        
        self.style.width = max(widths)
        self.style.height = max(heights)
        
        self.image_pos = self.style.image.get_rect(center=(self.style.width/2, self.style.height/2))
        self.image_hover_pos = self.style.image_hover.get_rect(center=(self.style.width/2, self.style.height/2))
        self.image_down_pos = self.style.image_down.get_rect(center=(self.style.width/2, self.style.height/2))
        
        self.state = 0

    def paint(self,s):
        if self.pcls == "hover":
            s.blit(self.style.image_hover,self.image_hover_pos)
        elif self.pcls == "down":          
            s.blit(self.style.image_down,(self.image_down_pos)) 
        else:        
            s.blit(self.style.image,self.image_pos) 
            
class ZoomImage(pygame.sprite.Sprite):
    
    def __init__(self, ev_manager, image, zoom_time=config.default_zoom_time, pos=None):
        if pos == None:
            self.centered = True
            self.pos = image.get_rect(center=config.screen_center)
        else:
            self.centered = False
            self.pos = pos
        self.ev_manager = ev_manager
        self.ev_manager.register_listener(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.zoomed_image = image
        self.original_size = self.image.get_size()
        self.image_size = (1, 1)
        self.zoom_time = zoom_time
        self.zoom_h_per_ms = float(self.original_size[0]) / float(self.zoom_time)
        self.zoom_v_per_ms = float(self.original_size[1]) / float(self.zoom_time)
        self.finished_zoom_in = False
        self.finished = False
        self.start_zoom_out = False
        self.visible = False
        self.ev_manager.post(FreezeCards())
        self.lifetime = 0
    
    def notify(self, event):
        if isinstance(event, TickEvent):
            if self.image_size < self.original_size and not self.start_zoom_out:
                self.zoom_in(event.time_passed)
            elif self.lifetime < config.zoom_lifetime:
                self.finished_zoom_in = True
                self.lifetime += event.time_passed
            elif not self.finished:
                self.start_zoom_out = True
                self.zoom_out(event.time_passed)
                
    def zoom_in(self, time_passed):
        nh = self.zoom_h_per_ms*time_passed
        nv = self.zoom_v_per_ms*time_passed
        new_image_size_h = min(self.image_size[0] + nh, self.original_size[0])
        new_image_size_v = min(self.image_size[1] + nv, self.original_size[1])
        self.image_size = (int(new_image_size_h), int(new_image_size_v))
        self.zoomed_image = pygame.transform.scale(self.image, self.image_size)
        if self.centered:
            self.pos = self.zoomed_image.get_rect(center=config.screen_center)
        self.visible = True       
        
    def zoom_out(self, time_passed):
        nh = self.zoom_h_per_ms*time_passed
        nv = self.zoom_v_per_ms*time_passed
        new_image_size_h = max(self.image_size[0] - nh, 0)
        if new_image_size_h <= 0:
            self.finished = True
        new_image_size_v = max(self.image_size[1] - nv, 0)
        self.image_size = (int(new_image_size_h), int(new_image_size_v))
        self.zoomed_image = pygame.transform.scale(self.image, self.image_size)
        if self.centered:
            self.pos = self.zoomed_image.get_rect(center=config.screen_center)            
        
    def render(self, surface):
        if self.visible and not self.finished:
            surface.blit(self.zoomed_image, self.pos)

class FadeOut(pygame.Surface):
    
    def __init__(self, ev_manager, goto, fade_time=config.default_fade_time, color=(255,255,255)):
        
        pygame.Surface.__init__(self, config.screen_size)
        self.visible = False
        self.ev_manager = ev_manager
        self.ev_manager.register_listener(self)
        self.goto = goto
        self.fade_per_ms = float(255)/float(fade_time)
        self.fill(color)
        self.alpha = 0
        self.finished = False
        
    def notify(self, event):
        if isinstance(event, TickEvent):
            if self.alpha > 0 and not self.visible:
                self.visible = True
            elif self.alpha >= 255 and not self.finished:
                self.finished = True   
                self.ev_manager.post(ChangeRoomRequest(self.goto))     
            else:
                self.alpha += (self.fade_per_ms * event.time_passed)
                self.set_alpha(self.alpha)
            
    def render(self, surface):
        if self.visible:
            surface.blit(self, (0,0))
            
            
class FadeIn(pygame.Surface):
    
    def __init__(self, ev_manager, fade_time=config.default_fade_time, color=(255,255,255)):
        
        pygame.Surface.__init__(self, config.screen_size)
        self.visible = True
        self.ev_manager = ev_manager
        self.ev_manager.register_listener(self)
        self.fade_per_ms = float(255)/float(fade_time)
        self.fill(color)
        self.alpha = 255
        self.finished = False
        
    def notify(self, event):
        if isinstance(event, TickEvent):
            if self.alpha <= 0 and not self.finished:
                self.finished = True       
                self.ev_manager.unregister_listener(self)
            else:
                self.alpha -= (self.fade_per_ms * event.time_passed)
                self.set_alpha(self.alpha)
            
    def render(self, surface):
        if self.visible:
            surface.blit(self, (0,0))            

#--------------------------------------------------------------------
#Loading Screen GUI
#--------------------------------------------------------------------


#--------------------------------------------------------------------
#Title Screen GUI
#--------------------------------------------------------------------
class PlayEurope(ImageButton):
    def __init__(self, **params):
        image = pygame.image.load('assets/images/interface/title_screen/europe.png').convert_alpha()
        image_hover = pygame.image.load('assets/images/interface/title_screen/europe-hover.png').convert_alpha()
        ImageButton.__init__(self, image, image_hover, **params)
        self.connect(gui.CLICK,self.clicked,None)
        
    def clicked(self, value):
        config.continent = config.EUROPE
        self.ev_manager.post(ChangeRoomRequest(config.GAME_MODE_ROOM))
        
class PlayAfrica(ImageButton):
    def __init__(self, **params):
        image = pygame.image.load('assets/images/interface/title_screen/africa.png').convert_alpha()
        image_hover = pygame.image.load('assets/images/interface/title_screen/africa-hover.png').convert_alpha()
        ImageButton.__init__(self, image, image_hover, **params)
        self.connect(gui.CLICK,self.clicked,None)
        
    def clicked(self, value):
        config.continent = config.AFRICA
        self.ev_manager.post(ChangeRoomRequest(config.GAME_MODE_ROOM))
        
class PlayUSA(ImageButton):
    def __init__(self, **params):
        image = pygame.image.load('assets/images/interface/title_screen/NA.png').convert_alpha()
        image_hover = pygame.image.load('assets/images/interface/title_screen/NA-hover.png').convert_alpha()
        ImageButton.__init__(self, image, image_hover, **params)
        self.connect(gui.CLICK,self.clicked,None)
        
    def clicked(self, value):
        config.continent = config.USA
        self.ev_manager.post(ChangeRoomRequest(config.GAME_MODE_ROOM))    
        
class PlayEastAsia(ImageButton):
    def __init__(self, **params):
        image = pygame.image.load('assets/images/interface/title_screen/east-asia.png').convert_alpha()
        image_hover = pygame.image.load('assets/images/interface/title_screen/east-asia-hover.png').convert_alpha()
        ImageButton.__init__(self, image, image_hover, **params)
        self.connect(gui.CLICK,self.clicked,None)
        
    def clicked(self, value):
        config.continent = config.EAST_ASIA
        self.ev_manager.post(ChangeRoomRequest(config.GAME_MODE_ROOM)) 
        
class PlayWestAsia(ImageButton):
    def __init__(self, **params):
        image = pygame.image.load('assets/images/interface/title_screen/west-asia.png').convert_alpha()
        image_hover = pygame.image.load('assets/images/interface/title_screen/west-asia-hover.png').convert_alpha()
        ImageButton.__init__(self, image, image_hover, **params)
        self.connect(gui.CLICK,self.clicked,None)
        
    def clicked(self, value):
        config.continent = config.WEST_ASIA
        self.ev_manager.post(ChangeRoomRequest(config.GAME_MODE_ROOM))          
        
class CreditsButton(ImageButton):
    def __init__(self, **params):
        image = resources.credits_button
        image_hover = pygame.image.load('assets/images/interface/title_screen/credits-hover.png').convert_alpha()
        ImageButton.__init__(self, image, image_hover, **params)
        self.connect(gui.CLICK,self.clicked,None)
        
    def clicked(self, value):
        self.ev_manager.post(ChangeRoomRequest(config.CREDITS))   
        
class HelpButton(ImageButton):
    def __init__(self, **params):
        image = resources.help_button
        image_hover = resources.help_button_hover
        ImageButton.__init__(self, image, image_hover, **params)
        self.connect(gui.CLICK,self.clicked,None)
        
    def clicked(self, value):
        self.ev_manager.post(ChangeRoomRequest(config.HELP1))         
        
class OptionsButton(ImageButton):
    def __init__(self, **params):
        image = pygame.image.load('assets/images/interface/title_screen/options.png').convert_alpha()
        image_hover = pygame.image.load('assets/images/interface/title_screen/options-hover.png').convert_alpha()
        ImageButton.__init__(self, image, image_hover, **params)
        self.connect(gui.CLICK,self.clicked,None)
        
    def clicked(self, value):
        self.ev_manager.post(ChangeRoomRequest(config.OPTIONS))       
        
class HighScoresButton(ImageButton):
    def __init__(self, **params):
        image = pygame.image.load('assets/images/interface/title_screen/high-scores.png').convert_alpha()
        image_hover = pygame.image.load('assets/images/interface/title_screen/high-scores-hover.png').convert_alpha()
        ImageButton.__init__(self, image, image_hover, **params)
        self.connect(gui.CLICK,self.clicked,None)
        
    def clicked(self, value):
        self.ev_manager.post(ChangeRoomRequest(config.HIGH_SCORES_ROOM))                                             

class QuitButtonTitle(ImageButton):
    def __init__(self, **params):
        image = pygame.image.load('assets/images/interface/title_screen/quit.png').convert_alpha()
        image_hover = pygame.image.load('assets/images/interface/title_screen/quit-hover.png').convert_alpha()
        ImageButton.__init__(self, image, image_hover, **params)
        self.connect(gui.CLICK,self.clicked,None)
        
    def clicked(self, value):
        self.ev_manager.post(QuitEvent())    

#--------------------------------------------------------------------
#Game Mode Screen GUI
#--------------------------------------------------------------------
class BackButton(ImageButton):
    def __init__(self, **params):
        image = pygame.image.load('assets/images/interface/back.png').convert_alpha()
        image_hover = pygame.image.load('assets/images/interface/back-hover.png').convert_alpha()
        ImageButton.__init__(self, image, image_hover, **params)
        self.connect(gui.CLICK,self.clicked,None)
        
    def clicked(self, value):
        self.ev_manager.post(EscRequest())    

class DifficultySelector(gui.Container):
    
    def __init__(self, value, **params):
        gui.Container.__init__(self, **params) 
        self.gui_form = gui.Form()
        
        t = gui.Table(align=-1, valign=-1)
        t.tr()
        g = gui.Group(value=value, name='difficulty')
        t.td(gui.Radio(g,value=config.EASY),width=30,height=22)
        t.td(gui.Label("Easy"), align=-1)      
        t.tr()
        t.td(gui.Radio(g,value=config.MED_DIF),width=30,height=22)
        t.td(gui.Label("Medium"), align=-1)          
        t.tr()
        t.td(gui.Radio(g,value=config.HARD),width=30,height=22)
        t.td(gui.Label("Hard"), align=-1)     
        t.tr()
        t.td(gui.Radio(g,value=config.SUPER),width=30,height=22)
        t.td(gui.Label("Superstar"), align=-1)   
        
        g.connect(gui.CHANGE, self.changed, None)   
        self.add(t, 0, 0)                       
    
    def changed(self, value):
        difficulty = self.gui_form['difficulty'].value 
        config.set_difficulty(difficulty)

class ModeRelaxedButton(ImageButton):
    def __init__(self, **params):
        image = pygame.image.load('assets/images/interface/mode_screen/relaxed.png').convert_alpha()
        image_hover = pygame.image.load('assets/images/interface/mode_screen/relaxed-hover.png').convert_alpha()
        ImageButton.__init__(self, image, image_hover, **params)
        self.connect(gui.CLICK,self.clicked,None)
        
    def clicked(self, value):
        config.game_mode = config.RELAXED
        self.ev_manager.post(ChangeRoomRequest(config.GAME_ROOM))   
                             
class ModeTimeButton(ImageButton):
    def __init__(self, **params):
        image = pygame.image.load('assets/images/interface/mode_screen/time-challenge.png').convert_alpha()
        image_hover = pygame.image.load('assets/images/interface//mode_screen/time-challenge-hover.png').convert_alpha()
        ImageButton.__init__(self, image, image_hover, **params)
        self.connect(gui.CLICK,self.clicked,None)
        
    def clicked(self, value):
        config.game_mode = config.TIME_CHALLENGE
        self.ev_manager.post(ChangeRoomRequest(config.GAME_ROOM)) 
                             
class ModePlanButton(ImageButton):
    def __init__(self, **params):
        image = pygame.image.load('assets/images/interface/mode_screen/plan-ahead.png').convert_alpha()
        image_hover = pygame.image.load('assets/images/interface/mode_screen/plan-ahead-hover.png').convert_alpha()
        ImageButton.__init__(self, image, image_hover, **params)
        self.connect(gui.CLICK,self.clicked,None)
        
    def clicked(self, value):
        config.game_mode = config.PLAN_AHEAD
        self.ev_manager.post(ChangeRoomRequest(config.GAME_ROOM))                                                                              

#--------------------------------------------------------------------
#Game Room GUI
#--------------------------------------------------------------------

class BoardCreationDialog(gui.Dialog):

    def __init__(self, **params):
        self.ev_manager = params['ev_manager']
        self.ev_manager.register_listener(self)    
        title = gui.Label("Board is being generated...")
        main = gui.Table()   
        
        main.tr()
        main.td(gui.Label("Your travel agents are working overtime."))
        main.tr()
        self.progress_bar = gui.ProgressBar(0, 0, 10, width=200)
        main.td(self.progress_bar)
        
        gui.Dialog.__init__(self,title,main) 
        
    def notify(self, event):
        if isinstance(event, TickEvent): 
            self.progress_bar.value += 2
        elif isinstance(event, NewBoardComplete):
            self.ev_manager.unregister_listener(self)
            self.ev_manager = None
            self.close()
        

class HighScoreDialog(gui.Dialog):   
    
    def __init__(self, value="", **params):
        self.ev_manager = params['ev_manager']
        self.ev_manager.register_listener(self)    
        self.highs_table = config.current_highs
        self.score = params['score']
        self.data = params['data']
        title = gui.Label("New High Score!")
        main = gui.Table()   
        
        self.gui_form = gui.Form()
        
        main.tr()
        main.td(gui.Label("Please enter your name:"))
        main.tr()
        self.name_field = gui.Input(value=value, name='player_name')
        main.td(self.name_field)
        main.tr()
        submit_button = gui.Button("Submit")
        main.td(submit_button)
        submit_button.connect(gui.CLICK, self.submit, None)
        submit_button.connect(gui.CLOSE, self.close, None)

        gui.Dialog.__init__(self,title,main)   
        
        self.ev_manager.post(FreezeCards())
#        self.name_field.focus()
        
    def close(self, value):    
        self.ev_manager.post(ChangeRoomRequest(config.TITLE_SCREEN))
        
    def submit(self, value):     
        config.current_highs.submit(self.score, self.gui_form['player_name'].value, self.data)
        config.current_highs.save()
        self.ev_manager.post(ChangeRoomRequest(config.HIGH_SCORES_ROOM))
        
    def notify(self, event):
        pass
     
class QuitButton(gui.Button):
    
    def __init__(self, **params):
        params['value'] = 'Back'
        gui.Button.__init__(self, **params)
        self.connect(gui.CLICK,self.clicked,None)
        self.ev_manager = params['ev_manager']
        
    def clicked(self, value):
        self.ev_manager.post(ChangeRoomRequest(config.TITLE_SCREEN))
        
class NextButton(gui.Button):
    
    def __init__(self, **params):
        params['value'] = 'Next'
        gui.Button.__init__(self, **params)
        self.connect(gui.CLICK,self.clicked,None)
        self.ev_manager = params['ev_manager']
        
    def clicked(self, value):
        self.ev_manager.post(ChangeRoomRequest(config.HELP2))        
        
class PauseButton(gui.Button):
    
    def __init__(self, **params):
        params['value'] = 'Pause'
        self.ev_manager = params['ev_manager']
        self.ev_manager.register_listener(self)
        gui.Button.__init__(self, **params)
        self.connect(gui.CLICK,self.clicked,None)
        
    def clicked(self, value):
        self.ev_manager.post(Pause())
        pause_dialog = PauseDialog(ev_manager=self.ev_manager)
        pause_dialog.connect(gui.CLOSE, self.resume, None)        
        pause_dialog.open()   
 
    def resume(self, value):   
        self.ev_manager.post(Unpause())
        
    def notify(self, event):
        pass
        
class PauseDialog(gui.Dialog):
    
    def __init__(self, **params):
        self.ev_manager = params['ev_manager']
        self.ev_manager.register_listener(self)        
        title = gui.Label("Game Paused")
        main = gui.Table(width=100, height = 50)   
        
        self.gui_form = gui.Form()
        
#        main.tr()
#        main.td(gui.Label("Click to un-pause:"))
        main.tr()
        submit_button = gui.Button("Resume")
        main.td(submit_button)
        submit_button.connect(gui.CLICK, self.resume, None)

        gui.Dialog.__init__(self,title,main)   
        
    def resume(self, value):   
        self.ev_manager.post(Unpause())
        self.ev_manager.unregister_listener(self)
        self.close()
        
    def notify(self, event):
        pass        
        
class GenerateBoardButton(gui.Button):
    
    def __init__(self, **params):
        if config.game_mode != config.RELAXED:
            value = "New Board (%d left)" % config.new_boards_left
        else:
            value = "New Board"
        gui.Button.__init__(self, value, **params)
        self.connect(gui.CLICK,self.clicked,None)
        self.ev_manager = params['ev_manager']     
        
    def clicked(self, value):
        if config.game_mode != config.RELAXED:
            config.new_boards_left -= 1
            self.value = "New Board (%d left)" % config.new_boards_left
        self.ev_manager.post(DealNewBoardRequest(button_request=True))
#        self.room.advance_level()
#        self.room.new_board = self.room.deck.deal_new_board(self.room.board)
#        self.ev_manager.post(NewBoardComplete(self.room.new_board))
        
class SetBoardSizeContainer(gui.Container):
    
    def __init__(self, value, **params):
        gui.Container.__init__(self, **params)
        self.ev_manager = params['ev_manager']
        self.board = params['board']
        
        self.gui_form = gui.Form()
        
        t = gui.Table(background=(255,255,255), align=-1)
        t.tr()
        t.td(gui.Label("Board Size:"), colspan=2)
        t.tr()
        g = gui.Group(value=value, name='board_size')
        t.td(gui.Radio(g,value=config.BOARD_SMALL))
        t.td(gui.Label("Small"), align=-1)
        t.tr()
        t.td(gui.Radio(g,value=config.BOARD_MED))
        t.td(gui.Label("Med"), align=-1)
        t.tr()
        t.td(gui.Radio(g,value=config.BOARD_LARGE))  
        t.td(gui.Label("Large"), align=-1)
        
        g.connect(gui.CHANGE, self.changed, None)
               
        self.add(t, 0, 0)   
        
    def changed(self, value):
        new_board_size = self.gui_form['board_size'].value
        self.ev_manager.post(ConfigChangeBoardSize(new_board_size))
        if new_board_size == config.BOARD_LARGE:
            new_card_size = config.CARD_SMALL
        elif new_board_size == config.BOARD_MED:
            new_card_size = config.CARD_MED
        elif new_board_size == config.BOARD_SMALL:
            new_card_size = config.CARD_LARGE           
        self.ev_manager.post(ConfigChangeCardSize(new_card_size)) 
        
class FillBoardCheckbox(gui.Table):

    def __init__(self, value, **params): 
        gui.Table.__init__(self, **params)
        self.ev_manager = params['ev_manager']        
        self.gui_form = gui.Form()
        g = gui.Group(value=[config.fill_board], name='fill_board')     
        self.td(gui.Checkbox(g, value=1))
        self.td(gui.Label("Fill board"))    
        g.connect(gui.CHANGE, self.changed, None)
        
    def changed(self, value):
        if self.gui_form['fill_board'].value:
            value = 1
        else:
            value = 0
        self.ev_manager.post(ConfigChangeFillBoard(value))    
        
class UseDarknessCheckbox(gui.Table):

    def __init__(self, value, **params): 
        gui.Table.__init__(self, **params)
        self.ev_manager = params['ev_manager']        
        self.gui_form = gui.Form()
        g = gui.Group(value=[config.use_darkness], name='use_darkness')     
        self.td(gui.Checkbox(g, value=1))
        self.td(gui.Label("Darkness"))
        g.connect(gui.CHANGE, self.changed, None)
        
    def changed(self, value):
        if self.gui_form['use_darkness'].value:
            value = 1
        else:
            value = 0
        self.ev_manager.post(ConfigChangeDarkness(value))              
        
#--------------------------------------------------------------------
#High Scores Room GUI
#--------------------------------------------------------------------    

class HighScoresTable(gui.Table):
    
    def __init__(self, mode, difficulty, **params): 
        gui.Table.__init__(self, **params)   
        self.ev_manager = params['ev_manager']
        self.ev_manager.register_listener(self)
        self.mode = mode
        self.difficulty = difficulty
        self.key = config.get_hs_key(self.mode, self.difficulty) 
        self.h1 = pygame.font.Font(config.font_logo, 24)
        
        self.refresh(self.key, self.mode, self.difficulty)
        
        
    def refresh(self, key, game_mode, difficulty):
        #Fill high score table with empty values if it doesn't exist yet
        while config.all_highs[key].submit(0,'Empty',data='time|0:00,swaps|0') != None:
            pass      
        
        self.clear()
#        readable_dif = config.get_readable_difficulty(difficulty)
#        readable_mode = config.get_readable_game_mode(game_mode)        
#        self.tr()       
#        self.td(gui.Label(readable_dif + " " + readable_mode))         
        self.tr()
        self.td(gui.Label("Name", font=self.h1, color=config.COLOR5), align=-1, width=150, height=50)
        self.td(gui.Label("Trips", font=self.h1, color=config.COLOR5), width=100) 
        self.td(gui.Label("Time", font=self.h1, color=config.COLOR5), width=100)      
        self.td(gui.Label("Swaps", font=self.h1, color=config.COLOR5), width=100)      
        
        for hs in config.all_highs[key]:
            self.tr()
            self.td(gui.Label(hs.name), align=-1, height=30)
            self.td(gui.Label(str(hs.score)))  
                
            data_dic = {}
            try:
                for item in hs.data.split(","):
                    key,value = item.split("|")
                    data_dic[key] = value 
            except:
                pass
            
            try:
                self.td(gui.Label(data_dic['time']))
            except:
                self.td(gui.Label('error reading hs file'))
            try:
                self.td(gui.Label(data_dic['swaps']))   
            except:
                self.td(gui.Label('error reading hs file'))
        
    def notify(self, event):
        if isinstance(event, RefreshHighScores):
            self.key = config.get_hs_key(event.mode, event.difficulty)
            self.refresh(self.key, event.mode, event.difficulty)

class HighScoresSelector(gui.Table):
    
    def __init__(self, mode, dif, **params):
        gui.Table.__init__(self, **params)   
        self.ev_manager = params['ev_manager']
        self.ev_manager.register_listener(self)
        self.h1 = pygame.font.Font(config.font_logo, 18)

        self.gui_form = gui.Form()
         
        self.tr()
        self.td(gui.Label("Mode:", font=self.h1, color=config.COLOR5), colspan=2, align=-1, height=50)                   
        g = gui.Group(value=mode, name='mode')
        self.tr()
        self.td(gui.Radio(g,value=config.TIME_CHALLENGE))
        self.td(gui.Label("Time Challenge"), align=-1)      
        self.tr()
        self.td(gui.Radio(g,value=config.PLAN_AHEAD))
        self.td(gui.Label("Plan Ahead"), align=-1)          
        
        
        self.tr()
        self.td(gui.Label("Difficulty:", font=self.h1, color=config.COLOR5), colspan=2, align=-1, height=50)     
        g = gui.Group(value=dif, name='difficulty')
        self.tr()
        self.td(gui.Radio(g,value=config.EASY),width=30)
        self.td(gui.Label("Easy"), align=-1)      
        self.tr()
        self.td(gui.Radio(g,value=config.MED_DIF))
        self.td(gui.Label("Medium"), align=-1)          
        self.tr()
        self.td(gui.Radio(g,value=config.HARD))
        self.td(gui.Label("Hard"), align=-1)     
        self.tr()
        self.td(gui.Radio(g,value=config.SUPER))
        self.td(gui.Label("Superstar"), align=-1)      
      
        self.tr()      
        self.refresh_button = gui.Button("Refresh")
        self.td(self.refresh_button, colspan=2, align=-1, height=50) 
        
        self.refresh_button.connect(gui.CLICK, self.refresh, None)   
                      
    def notify(self, event):
        pass
    
    def refresh(self, value):
        mode = self.gui_form['mode'].value 
        difficulty = self.gui_form['difficulty'].value 
        self.ev_manager.post(RefreshHighScores(mode, difficulty))     