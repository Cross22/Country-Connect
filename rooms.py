#Remote imports

#Local imports
import continents
from game_components import *
from my_gui import *
from pgu import high

class Room(object):

    def __init__(self, screen, ev_manager):
        self.screen = screen
        self.ev_manager = ev_manager
        self.ev_manager.register_listener(self)
        self.board = None
        self.deck = None
        
        self.font = pygame.font.Font(config.font_sans, config.interface_font_size)
        self.debug_text = self.font.render("FPS ", True, WHITE)        
        
    def __del__(self):
        self.deck = None
        self.board = None
        self.screen = None
        self.ev_manager.unregister_listener(self)
        self.ev_manager = None
        
    def notify(self, event):
        if isinstance(event, TickEvent):        
            self.render(self.screen) 
            pygame.display.update()
#        elif isinstance(event, SecondEvent):
#            self.debug_text = self.font.render(str(int(event.fps)), True, WHITE) 
##            pygame.display.set_caption(''.join(['FPS: ', str(int(event.fps))]))              
        elif isinstance(event, EscRequest): 
            self.ev_manager.post(ChangeRoomRequest(config.TITLE_SCREEN))              

    def render(self, surface):
        pass
#        if config.debug:
#        surface.blit(self.debug_text, (10,10))
        
    def get_highs_table(self):
        fname = 'high_scores.txt'
        current_highs = None
        if config.game_mode == config.TIME_CHALLENGE:
            if config.difficulty == config.EASY:
                current_highs = high.Highs(fname)['time_challenge_easy']
            if config.difficulty == config.MED_DIF:
                current_highs = high.Highs(fname)['time_challenge_med']
            if config.difficulty == config.HARD:
                current_highs = high.Highs(fname)['time_challenge_hard']
            if config.difficulty == config.SUPER:
                current_highs = high.Highs(fname)['time_challenge_super']                 
        elif config.game_mode == config.PLAN_AHEAD:
            pass       
        return current_highs

class Credits(Room):

    def __init__(self, screen, ev_manager):    
        Room.__init__(self, screen, ev_manager)
        
        self.background = resources.credits_bg
        
    def notify(self, event):
        Room.notify(self, event)
        if isinstance(event, MouseButtonLeftEvent):
            self.ev_manager.post(ChangeRoomRequest(config.TITLE_SCREEN))   
        elif isinstance(event, EscRequest):
            self.ev_manager.post(ChangeRoomRequest(config.TITLE_SCREEN))
        
    def render(self, surface):
        surface.blit(self.background, (0, 0))
        Room.render(self, surface)

class Help1(Room):

    def __init__(self, screen, ev_manager):    
        Room.__init__(self, screen, ev_manager)
        self.background = resources.help1_bg

        self.gui_app = gui.App(config.gui_theme)
        self.ev_manager.gui_app = self.gui_app
        c = gui.Container(align=-1,valign=-1)        
        
        #Continent Buttons
        #---------------------------------------
        b = NextButton(ev_manager=self.ev_manager)
        c.add(b, 920, 30)                                                
 
        #Initialize
        #---------------------------------------       
        self.gui_app.init(c)  
        
    def notify(self, event):
        Room.notify(self, event)
#        if isinstance(event, MouseButtonLeftEvent):
#            self.ev_manager.post(ChangeRoomRequest(config.HELP2))   
#        elif isinstance(event, EscRequest):
#            self.ev_manager.post(ChangeRoomRequest(config.HELP2))
        
    def render(self, surface):
        surface.blit(self.background, (0, 0))
        #GUI
        self.gui_app.paint(surface)            
        Room.render(self, surface)
    
class Help2(Room):

    def __init__(self, screen, ev_manager):    
        Room.__init__(self, screen, ev_manager)
        self.background = resources.help2_bg
        
    def notify(self, event):
        Room.notify(self, event)
        if isinstance(event, MouseButtonLeftEvent):
            self.ev_manager.post(ChangeRoomRequest(config.TITLE_SCREEN))   
        elif isinstance(event, EscRequest):
            self.ev_manager.post(ChangeRoomRequest(config.TITLE_SCREEN))
        
    def render(self, surface):
        surface.blit(self.background, (0, 0))
        Room.render(self, surface)
        
    
class LoadingScreen(Room):
    def __init__(self, screen, ev_manager):    
        Room.__init__(self, screen, ev_manager)
        resources.title_screen_bg = pygame.image.load('assets/images/interface/title_screen/background.jpg').convert()
        self.background = resources.title_screen_bg
        self.clock = pygame.time.Clock()
        self.fade_out = None
        self.create_gui()
        self.load_resources()

    def create_gui(self):
        self.gui_app = gui.App(config.gui_theme)
        self.ev_manager.gui_app = self.gui_app
        c = gui.Container(align=0,valign=-1)        
        
        #Continent Buttons
        #---------------------------------------
        l = gui.Label("Loading the world...", color=(255,255,255))
        c.add(l, 0, 250)     
        self.progress_bar = gui.ProgressBar(0, 0, 6, width=200)
        c.add(self.progress_bar, 0, 300)                                                  
 
        #Initialize
        #---------------------------------------       
        self.gui_app.init(c)  
        
    def load_resources(self):       
        
        #Continents
        #------------------------------------------
        resources.europe = continents.Europe()  
        self.progress_bar.value += 1
        self.ev_manager.post(TickEvent(self.clock.tick(), self.clock.get_fps()))  
             
        resources.africa = continents.Africa()   
        self.progress_bar.value += 1
        self.ev_manager.post(TickEvent(self.clock.tick(), self.clock.get_fps())) 
        
        resources.usa = continents.USA()    
        self.progress_bar.value += 1
        self.ev_manager.post(TickEvent(self.clock.tick(), self.clock.get_fps()))
        
        resources.east_asia = continents.EastAsia()   
        self.progress_bar.value += 1
        self.ev_manager.post(TickEvent(self.clock.tick(), self.clock.get_fps()))
        
        resources.west_asia = continents.WestAsia()  
        self.progress_bar.value += 1
        self.ev_manager.post(TickEvent(self.clock.tick(), self.clock.get_fps()))  
        
        #Misc
        #------------------------------------------
        resources.high_scores_bg = pygame.image.load('assets/images/interface/high_scores_bg.jpg').convert()
        resources.game_mode_room_bg = pygame.image.load('assets/images/interface/mode_screen/game-mode-background.jpg').convert()
        resources.game_room_bg = pygame.image.load('assets/images/interface/game_screen.jpg').convert() 
        resources.game_room_logo = pygame.image.load('assets/images/interface/logo_small.png').convert_alpha() 
        resources.game_over_text = pygame.image.load('assets/images/interface/text_game_over.png').convert_alpha()
        resources.trip_complete_text = pygame.image.load('assets/images/interface/text_trip_complete.png').convert_alpha()
        resources.card_shadow_large = pygame.image.load('assets/images/interface/card_shadow_large.png').convert_alpha()
        resources.card_shadow_small = pygame.image.load('assets/images/interface/card_shadow_small.png').convert_alpha()    
        resources.credits_bg = pygame.image.load('assets/images/interface/credits.jpg').convert()
        resources.help1_bg = pygame.image.load('assets/images/interface/help_screen01.jpg').convert()
        resources.help2_bg = pygame.image.load('assets/images/interface/help_screen02.jpg').convert()
       
        #Buttons
        resources.credits_button = pygame.image.load('assets/images/interface/title_screen/credits.png').convert_alpha()
        resources.help_button = pygame.image.load('assets/images/interface/title_screen/help.png').convert_alpha()
        resources.help_button_hover = pygame.image.load('assets/images/interface/title_screen/help-hover.png').convert_alpha()
       
        #Plane images       
        for color in config.COLORS:
            color_string = str(color)
            resources.plane_image[color_string] = pygame.image.load('assets/images/transport/plane.png').convert_alpha()
            image_pixel_array = pygame.PixelArray(resources.plane_image[color_string])
            image_pixel_array.replace(config.MAGENTA_OB, color)            
        self.progress_bar.value += 1
        self.ev_manager.post(TickEvent(self.clock.tick(), self.clock.get_fps())) 

        
        #Fade out
        #------------------------------------------
        self.fade_out = FadeOut(self.ev_manager, config.TITLE_SCREEN, 300)  
        self.ev_manager.post(TickEvent(self.clock.tick(), self.clock.get_fps()))              

    def render(self, surface):
        surface.blit(self.background, (0, 0))
        self.gui_app.paint(surface) 
        Room.render(self, surface)   

        if self.fade_out:
            self.fade_out.render(surface)

class TitleScreen(Room):
    
    def __init__(self, screen, ev_manager):
        Room.__init__(self, screen, ev_manager)
        self.background = resources.title_screen_bg      
        self.create_gui()
        self.fade_in = None
        if config.title_screen_first_load:
            config.title_screen_first_load = False
            self.fade_in = FadeIn(self.ev_manager, 1500)

    def create_gui(self):
        #Setup
        #---------------------------------------
        self.gui_form = gui.Form()
        self.gui_app = gui.App(config.gui_theme)
        self.ev_manager.gui_app = self.gui_app
        c = gui.Container(align=-1,valign=-1)        
        
        #Continent Buttons
        #---------------------------------------
        b = PlayEurope(ev_manager=self.ev_manager)
        c.add(b, 307, 133)  
        b = PlayAfrica(ev_manager=self.ev_manager)
        c.add(b, 372, 380)          
        b = PlayUSA(ev_manager=self.ev_manager)
        c.add(b, 20, 183)  
        b = PlayEastAsia(ev_manager=self.ev_manager)
        c.add(b, 740, 100) 
        b = PlayWestAsia(ev_manager=self.ev_manager)
        c.add(b, 575, 240)         
        
        #Other Buttons
        #---------------------------------------
        b = CreditsButton(ev_manager=self.ev_manager)
        c.add(b, 10, 10)    
#        b = OptionsButton(ev_manager=self.ev_manager)
#        c.add(b, 186, 400)
        b = HelpButton(ev_manager=self.ev_manager)
        c.add(b, 100, 445)        
        b = HighScoresButton(ev_manager=self.ev_manager)
        c.add(b, 186, 400)      
        b = QuitButtonTitle(ev_manager=self.ev_manager)
        c.add(b, 150, 489)                                                  
 
        #Initialize
        #---------------------------------------       
        self.gui_app.init(c)     
        
    def render(self, surface):
        surface.blit(self.background, (0, 0))
        #GUI
        self.gui_app.paint(surface)    
        
        Room.render(self, surface)  
        
        if self.fade_in and self.fade_in.visible:
            self.fade_in.render(surface)
                  

class GameModeRoom(Room):
    
    def __init__(self, screen, ev_manager):
        Room.__init__(self, screen, ev_manager)
        self.background = resources.game_mode_room_bg      
        self.create_gui()

    #Create pgu gui elements
    def create_gui(self):
        #Setup
        #---------------------------------------
        self.gui_form = gui.Form()
        self.gui_app = gui.App(config.gui_theme)
        self.ev_manager.gui_app = self.gui_app
        c = gui.Container(align=-1,valign=-1)    
 
        #Back Button
        #---------------------------------------
        b = BackButton(ev_manager=self.ev_manager)
        c.add(b, 10, 10)       
        
        #Mode Select Buttons
        #---------------------------------------
        b = ModeRelaxedButton(ev_manager=self.ev_manager)
        c.add(b, 300, 180)    
        b = ModeTimeButton(ev_manager=self.ev_manager)
        c.add(b, 300, 300)           
        b = ModePlanButton(ev_manager=self.ev_manager)
        c.add(b, 300, 420)       
        
        #Difficulty selector
        ds = DifficultySelector(config.difficulty)   
        c.add(ds, 740, 375)    
        
        #Initialize
        #---------------------------------------       
        self.gui_app.init(c)                  
    
    def render(self, surface):
        surface.blit(self.background, (0, 0))
        #GUI
        self.gui_app.paint(surface)    
        
        #Base class
        Room.render(self, surface) 
        
class GameRoom(Room):
    
    def __init__(self, screen, ev_manager):
        Room.__init__(self, screen, ev_manager)
        
        #Game mode
        #---------------------------------------   
        self.new_board_timer = None        
        self.game_mode = config.game_mode
        self.highs_dialog = None
        self.game_over = False
        self.hs_key = config.get_hs_key(config.game_mode, config.difficulty)
        config.current_highs = config.all_highs[self.hs_key]
        config.new_boards_left = config.new_boards_at_start
        
        #Fill high score table with empty values if it doesn't exist yet
        while config.current_highs.submit(0,'Empty',data='time|0:00,swaps|0') != None:
            pass
 
        #Trackers  
        #---------------------------------------              
        self.game_clock = Chrono(self.ev_manager)
        self.swap_counter = 0
        self.level = 1  
        
        #Images
        #---------------------------------------   
        self.background = resources.game_room_bg 
        self.logo = resources.game_room_logo 
        self.game_over_text = resources.game_over_text
        self.trip_complete_text = resources.trip_complete_text
               
        self.zoom_game_over = None
        self.zoom_trip_complete = None
        self.fade_out = None
        
        #Text
        #---------------------------------------   
        self.font = pygame.font.Font(config.font_sans, config.interface_font_size)
        self.font_big = pygame.font.Font(config.font_logo, config.interface_font_size_big)
        self.timer_text = self.font.render("Time Left: ", True, config.interface_font_color)  
        self.swapper_text = self.font.render("Swaps Left: ", True, config.interface_font_color) 
        self.connection_text = self.font.render("Connections: ", True, config.interface_font_color)
        self.connection_text_nums_width = None
        self.level_text = self.font_big.render("Trips:", True, config.interface_font_color_big)
        self.level_is_text = self.font.render(str(0), True, BLACK)  
        self.level_text_width = self.level_text.get_width() + self.level_is_text.get_width()
        self.record_is_text = None
        if config.game_mode != config.RELAXED:
            self.record = config.current_highs[0].score    
            self.record_text = self.font_big.render("Record:", True, config.interface_font_color_big)
            self.record_is_text = self.font.render(str(self.record), True, BLACK)

        self.mode_text = self.font_big.render("Mode:", True, config.interface_font_color_big)            
        if self.game_mode == config.RELAXED:
            self.mode_is_text = self.font.render("Relaxed", True, BLACK)
        elif self.game_mode == config.TIME_CHALLENGE:
            self.mode_is_text = self.font.render("Time Challenge", True, BLACK)
        elif self.game_mode == config.PLAN_AHEAD:
            self.mode_is_text = self.font.render("Plan Ahead", True, BLACK)
        self.mode_text_width = self.mode_text.get_width() + self.mode_is_text.get_width()
        
        
        #Create game components   
        #---------------------------------------      
        self.continent = self.set_continent()
        self.board = Board(config.board_size, self.ev_manager)
        self.deck = Deck(self.ev_manager, self.continent)
        self.map = Map(self.continent)
        self.longest_trip = 0
  
        #Set pos of game components
        #---------------------------------------  
        if config.screen_size == (1024, 576): 
            board_pos = (SCREEN_MARGIN[0], 103)
        else:
            board_pos = (SCREEN_MARGIN[0], 109)
        self.board.set_pos(board_pos)
        config.map_pos = (config.screen_size[0] - config.map_size[0] - SCREEN_MARGIN[0], 57);
                
        if config.screen_size == (1024, 576): 
            self.map.set_pos((config.map_pos[0], config.map_pos[1] - 5))
        else:
            self.map.set_pos(config.map_pos)
        
        #Create gui
        #---------------------------------------   
        self.create_gui()
        
        #Create initial board
        #---------------------------------------  
        if config.debug:
            for _ in xrange(20): 
                self.ev_manager.post(DealNewBoardRequest())
            exit()
        else:
            self.ev_manager.post(DealNewBoardRequest())
        
        #Debug
        #---------------------------------------   
        self.fps_text = 'FPS: '
        
    def set_continent(self):
        #Set continent based on const
        if config.continent == config.EUROPE:
            return resources.europe
        elif config.continent == config.AFRICA:
            return resources.africa 
        elif config.continent == config.USA:
            return resources.usa 
        elif config.continent == config.EAST_ASIA:
            return resources.east_asia      
        elif config.continent == config.WEST_ASIA:
            return resources.west_asia                               
        else:
            raise Exception('Continent constant not recognized')     
    
    #Create pgu gui elements
    def create_gui(self):
        
        #Setup
        #---------------------------------------
        self.gui_form = gui.Form()
        self.gui_app = gui.App(config.gui_theme)
        self.ev_manager.gui_app = self.gui_app
        self.gui_container = gui.Container(align=-1,valign=-1)        
        
        #Timer Progress bar
        #---------------------------------------
        self.timer_bar = None
        self.time_increase = None
        self.minutes_left = None
        self.seconds_left = None
        self.timer_text_nums = None
        if self.game_mode == config.TIME_CHALLENGE:
            self.time_challenge_start_time = config.longest_trip_needed**1.2 *  2.5
            self.time_increase = self.time_challenge_start_time
            self.min_timer_increase = int(config.longest_trip_needed**1.2 - 5)            
            self.time_multiplier = .8
            self.max_time_bank = int(1.5 * self.time_challenge_start_time)
            self.timer_bar = gui.ProgressBar(self.time_challenge_start_time,0,self.max_time_bank,width=306,cls='progressbar_red')
            self.gui_container.add(self.timer_bar, 172, 57)
            
        #Swapper Progress bar
        #---------------------------------------
        self.swapper_bar = None
        self.swap_increase = None
        self.swaps_left = None
        self.swapper_text_nums = None
        if self.game_mode == config.PLAN_AHEAD:
            self.plan_ahead_start_swaps = int(config.longest_trip_needed) * 1.3
            self.swap_increase = self.plan_ahead_start_swaps
            self.min_swapper_increase = int((config.longest_trip_needed - 1) * 0.75)
            self.swap_multiplier = .9
            self.max_swap_bank = int(1.5 * self.plan_ahead_start_swaps)
            self.swapper_bar = gui.ProgressBar(self.plan_ahead_start_swaps,0,self.max_swap_bank,width=306,cls='progressbar_red')
            self.gui_container.add(self.swapper_bar, 172, 57)            
            
        #Connections Progress bar
        #---------------------------------------
        self.connections_bar = None
        self.connections_bar = gui.ProgressBar(0,0,config.longest_trip_needed,width=306)
        self.gui_container.add(self.connections_bar, 172, 83)            
        
        y = 14
        w = 9
        #Quit Button
        #---------------------------------------
        b = QuitButton(ev_manager=self.ev_manager)
        self.gui_container.add(b, 950 + w, y)
        
        #Pause Button
        #---------------------------------------
        b = PauseButton(ev_manager=self.ev_manager)
        self.gui_container.add(b, 870 + w, y)        
        
        #New Board Button
        #---------------------------------------
        self.new_board_button = GenerateBoardButton(ev_manager=self.ev_manager, room=self)
        if config.game_mode == config.RELAXED:
            x = 750
        else:
            x = 690
        self.gui_container.add(self.new_board_button, x + w, y)        
        
        #Board Size?
        #---------------------------------------
        bs = SetBoardSizeContainer(config.BOARD_LARGE, ev_manager=self.ev_manager, board=self.board)
#        self.gui_container.add(bs, 640, 20)         
        
        #Fill Board?
        #---------------------------------------  
        t = FillBoardCheckbox(config.fill_board, ev_manager=self.ev_manager)
#        self.gui_container.add(t, 740, 20)
        
        #Darkness?
        #---------------------------------------  
        t = UseDarknessCheckbox(config.use_darkness, ev_manager=self.ev_manager) 
#        self.gui_container.add(t, 770, 20)        

        #Initialize
        #---------------------------------------    
        self.gui_app.init(self.gui_container)
        
    def advance_level(self):
        self.level += 1
        
        if self.timer_bar:      
            self.timer_bar.value += self.time_increase
            self.time_increase = max(self.min_timer_increase, int(self.time_increase * self.time_multiplier))             
        if self.swapper_bar:      
            self.swapper_bar.value += self.swap_increase
            self.swap_increase = max(self.min_swapper_increase, int(self.swap_increase * self.swap_multiplier))          
            swapper_text_nums = str(self.swapper_bar.value)
            self.swapper_text_nums = self.font.render(swapper_text_nums, True, config.interface_font_color)  
            self.swapper_text_nums_width = self.swapper_text_nums.get_width()          
        
        self.level_is_text = self.font.render(str(self.level - 1), True, BLACK)  
        self.level_text_width = self.level_text.get_width() + self.level_is_text.get_width()    

        self.zoom_trip_complete = None
 
    def notify(self, event):
        Room.notify(self, event)
        
        #Tick event
        if isinstance(event, TickEvent):        
            #Wait for zoom to advance level
            if self.zoom_trip_complete and self.zoom_trip_complete.finished:
                self.zoom_trip_complete = None            
                self.advance_level()
                self.ev_manager.post(DealNewBoardRequest())
                                
                     
            #Wait for zoom to Game over
            if self.zoom_game_over and self.zoom_game_over.finished and not self.highs_dialog:
                if config.current_highs.check(self.level-1) != None:
                    self.zoom_game_over.visible = False
                    data = ''.join(['time|', str(self.game_clock.minutes_passed), ':', str(self.game_clock.seconds_passed), ',swaps|', str(self.swap_counter)])
                    self.highs_dialog = HighScoreDialog(score=self.level-1, data=data, ev_manager=self.ev_manager)
                    self.highs_dialog.open()
                elif not self.fade_out:
                    self.fade_out = FadeOut(self.ev_manager, config.TITLE_SCREEN)
                    
        #Second event
        elif isinstance(event, SecondEvent):
#            pygame.display.set_caption(''.join(['FPS: ', str(int(event.fps))]))
            #Timer bar              
            if self.timer_bar:
                if not self.game_clock.paused:      
                    self.timer_bar.value -= 1 
                if self.timer_bar.value <= 0 and not self.game_over:
                    self.ev_manager.post(GameOver())
                self.minutes_left = self.timer_bar.value / 60
                self.seconds_left = self.timer_bar.value % 60
                if self.seconds_left < 10:
                    leading_zero = '0'
                else:
                    leading_zero = ''
                timer_text_nums = ''.join([str(self.minutes_left), ':', leading_zero, str(self.seconds_left)])
                self.timer_text_nums = self.font.render(timer_text_nums, True, config.interface_font_color)  
                self.timer_text_nums_width = self.timer_text_nums.get_width()   
                    
        #Game over
        elif isinstance(event, GameOver):
            self.game_over = True
            self.zoom_game_over = ZoomImage(self.ev_manager, self.game_over_text)
            
        #Pause
        elif isinstance(event, Pause):
            self.game_clock.pause()   
            self.ev_manager.post(FreezeCards())
            
        #Unpause
        elif isinstance(event, Unpause):
            self.game_clock.unpause()   
            self.ev_manager.post(UnfreezeCards())                  
                
        #Trip complete event
        elif isinstance(event, TripComplete):      
            if not self.game_over:   
                self.ev_manager.post(Pause())
                self.zoom_trip_complete = ZoomImage(self.ev_manager, self.trip_complete_text)
            
        #New Board Complete
        elif isinstance(event, NewBoardComplete):
            self.connections_bar.value = self.board.longest_trip
            connection_text_nums = ''.join([str(self.board.longest_trip), '/', str(config.longest_trip_needed)])
            self.connection_text_nums = self.font.render(connection_text_nums, True, config.interface_font_color)
            self.connection_text_nums_width = self.connection_text_nums.get_width()  
            self.ev_manager.post(Unpause())
                    
        #CardSwapComplete
        elif isinstance(event, CardSwapComplete):
            self.swap_counter += 1     
               
            #Connections Counter
            self.connections_bar.value = self.board.longest_trip
            connection_text_nums = ''.join([str(self.board.longest_trip), '/', str(config.longest_trip_needed)])
            self.connection_text_nums = self.font.render(connection_text_nums, True, config.interface_font_color)
            self.connection_text_nums_width = self.connection_text_nums.get_width()                 
                
            #Trip complete?
            if self.board.longest_trip >= config.longest_trip_needed:
                self.ev_manager.post(TripComplete())        

            #Swapper bar
            if self.swapper_bar:
                self.swapper_bar.value -= 1
                if self.swapper_bar.value <= 0 and not self.game_over and not self.zoom_trip_complete:
                    self.ev_manager.post(GameOver())
                swapper_text_nums = str(self.swapper_bar.value)
                self.swapper_text_nums = self.font.render(swapper_text_nums, True, config.interface_font_color)  
                self.swapper_text_nums_width = self.swapper_text_nums.get_width()              
 
        #New board request
        elif isinstance(event, DealNewBoardRequest):  
            if config.new_boards_left <= 0:
                try:
                    self.gui_container.remove(self.new_board_button)
                except:
                    pass
            self.deck.deal_new_board(self.board)
            if self.timer_bar:
                #If request came form "new board" button
                if event.button_request == True:      
                    self.timer_bar.value += max(self.min_timer_increase,  self.time_increase / 2)         
            if self.swapper_bar:  
                #If request came form "new board" button
                if event.button_request == True:    
                    self.swapper_bar.value += max(self.min_swapper_increase, self.swap_increase / 2)
                swapper_text_nums = str(self.swapper_bar.value)
                self.swapper_text_nums = self.font.render(swapper_text_nums, True, config.interface_font_color)  
                self.swapper_text_nums_width = self.swapper_text_nums.get_width()  
                          
        elif isinstance(event, ConfigChangeBoardSize): 
            config.board_size = event.new_size
        elif isinstance(event, ConfigChangeCardSize): 
            config.card_size = event.new_size       
        elif isinstance(event, ConfigChangeFillBoard): 
            config.fill_board = event.new_value          
        elif isinstance(event, ConfigChangeDarkness): 
            config.use_darkness = event.new_value                        
            
    def render(self, surface):
        #Background
        surface.blit(self.background, (0, 0))
        
        #Map
        self.map.render(surface)  
        
        #Board      
        self.board.render(surface)
        
        #Logo
        surface.blit(self.logo, (10,10))
        
        #Text
        #---------------------------------------------
        #Connections
        if self.connection_text_nums_width:
            y = 83
            x = 165 - self.connection_text_nums_width
            surface.blit(self.connection_text_nums, (x, y))
            surface.blit(self.connection_text, (12, y))  
            #Timer text      
        if self.timer_text_nums:
            y = 57
            x = 165 - self.timer_text_nums_width
            surface.blit(self.timer_text_nums, (x, y))        
            surface.blit(self.timer_text, (35, y)) 
        #Swap Counter text      
        if self.swapper_text_nums:
            y = 57
            x = 165 - self.swapper_text_nums_width
            surface.blit(self.swapper_text_nums, (x, y))        
            surface.blit(self.swapper_text, (24, y))             
        #Mode text
        x = 260
        y = 17
        surface.blit(self.mode_text, (x, y))
        surface.blit(self.mode_is_text, (x + 67, y-1))   
        #Level text
        if self.level_is_text:
            x += self.mode_text_width    
            x += 30
            surface.blit(self.level_text, (x, y))   
            surface.blit(self.level_is_text, (x + 66, y-1))   
            #Record text
            if self.record_is_text:
                x += self.level_text_width
                x += 32
                surface.blit(self.record_text, (x, y))  
                surface.blit(self.record_is_text, (x + 87, y-1))      
                 
        #GUI
        self.gui_app.paint(surface)   
        if self.zoom_trip_complete:
            self.zoom_trip_complete.render(surface)     
        if self.zoom_game_over:
            self.zoom_game_over.render(surface)
        if self.fade_out:
            self.fade_out.render(surface)
            
        #Base class
        Room.render(self, surface) 

            
class HighScoresRoom(Room):
    
    def __init__(self, screen, ev_manager):
        Room.__init__(self, screen, ev_manager)
        
        self.background = resources.high_scores_bg      
        self.game_mode = config.game_mode
        self.difficulty = config.difficulty
        
        #Setup
        #---------------------------------------
        self.gui_app = gui.App(config.gui_theme)
        self.ev_manager.gui_app = self.gui_app
        c = gui.Container(align=-1,valign=-1)  
        
        #High Scores Table Selector
        #---------------------------------------
        hss = HighScoresSelector(self.game_mode, self.difficulty, ev_manager=self.ev_manager, align=-1)
        c.add(hss, 100, 216)                  
        
        #High Scores Table
        #---------------------------------------
        hst = HighScoresTable(self.game_mode, self.difficulty, ev_manager=self.ev_manager)
        c.add(hst, 350, 183)    

        #Back Button
        #---------------------------------------
        b = BackButton(ev_manager=self.ev_manager)
        c.add(b, 10, 10)          
        
        #Initialize
        #---------------------------------------        
        self.gui_app.init(c)
    
        
    def render(self, surface):
        surface.blit(self.background, (0, 0))
        #GUI
        self.gui_app.paint(surface)    
        
        #Base class
        Room.render(self, surface)           
    