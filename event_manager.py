#Remote imports
import pygame
from pygame.locals import *

#Local imports
import rooms
from events import *

def debug( msg ):
    print "Debug Message: " + str(msg)

class EventManager:
    
    #This object is responsible for coordinating most communication
    #between the Model, View, and Controller.
    def __init__(self):
        from weakref import WeakKeyDictionary
        self.last_listeners = {}
        self.listeners = WeakKeyDictionary()
        self.eventQueue= []
        self.gui_app = None
 
    #----------------------------------------------------------------------
    def clear(self):
#        print 'Before clear: '
#        print '*******************'
#        for listener in list(self.listeners):        
#            print listener
#        print '*******************'        
        for listener in list(self.listeners):
            if not isinstance(listener, CPUSpinnerController):  
                if not isinstance(listener, RoomController):  
                    if not isinstance(listener, PyGameEventController):  
                        self.unregister_listener(listener)
#        print 'After clear: '
#        print '*******************'
#        for listener in list(self.listeners):        
#            print listener
#        print '*******************'
 
    #----------------------------------------------------------------------
    def register_listener(self, listener):
        self.listeners[listener] = 1
 
    #----------------------------------------------------------------------
    def unregister_listener(self, listener):
        if listener in self.listeners:
            del self.listeners[listener]
 
    #----------------------------------------------------------------------
    def post(self, event):
#        if  isinstance(event, MouseButtonLeftEvent):
#            debug(event.name)
        #NOTE: copying the list like this before iterating over it, EVERY tick, is highly inefficient,
        #but currently has to be done because of how new listeners are added to the queue while it is running
        #(eg when popping cards from a deck). Should be changed. See: http://dr0id.homepage.bluewin.ch/pygame_tutorial08.html
        #and search for "Watch the iteration"
        
#        print 'Number of listeners: ' + str(len(self.listeners))
        
#        room_count = 0
#        deck_count = 0
#        board_count = 0
#        card_count = 0

        for listener in list(self.listeners):                               
            #NOTE: If the weakref has died, it will be 
            #automatically removed, so we don't have 
            #to worry about it.
            listener.notify(event)

#            if listener not in self.last_listeners:
#                print 'New listener:'
#                print listener
                
#            if isinstance(listener, rooms.Room):
#                room_count += 1            
#            if isinstance(listener, game_components.Board):
#                board_count += 1
#            if isinstance(listener, game_components.Card):
#                card_count += 1       
#            if isinstance(listener, game_components.Deck):
#                deck_count += 1     
                
#        self.last_listeners = list(self.listeners)    
#        print 'Number of room listeners: ' + str(room_count)              
#        print 'Number of deck listeners: ' + str(deck_count)                 
#        print 'Number of board listeners: ' + str(board_count)
#        print 'Number of card listeners: ' + str(card_count)               
#        
    def notify(self, event):
        pass
 
#------------------------------------------------------------------------------
class PyGameEventController:
    """..."""
    def __init__(self, ev_manager):
        self.ev_manager = ev_manager
        self.ev_manager.register_listener(self) 
        self.input_freeze = False
        
    #----------------------------------------------------------------------
    def notify(self, incoming_event):

        if isinstance(incoming_event, UserInputFreeze):
            self.input_freeze = True
            
        elif isinstance(incoming_event, UserInputUnFreeze):
            self.input_freeze = False        
        
        elif isinstance(incoming_event, TickEvent) or isinstance(incoming_event, BoardCreationTick):
            
            #Share some time with other processes, so we don't hog the cpu
            pygame.time.wait(5)
            
            #Handle Pygame Events
            for event in pygame.event.get():
                #If this event manager has an associated PGU GUI app, notify it of the event
                if self.ev_manager.gui_app:
                    self.ev_manager.gui_app.event(event)
                #Standard event handling for everything else
                ev = None
                if event.type == QUIT:
                    ev = QuitEvent()
                    
                #Mouse
                #-----------------------------------
                elif event.type == pygame.MOUSEBUTTONDOWN and not self.input_freeze:
                    if event.button == 1:    #Button 1
                        pos = event.pos
                        ev = MouseButtonLeftEvent(pos)
                elif event.type == pygame.MOUSEBUTTONDOWN and not self.input_freeze:
                    if event.button == 2:    #Button 2
                        pos = event.pos
                        ev = MouseButtonRightEvent(pos)   
                elif event.type == pygame.MOUSEBUTTONUP and not self.input_freeze:
                    if event.button == 2:    #Button 2 Release
                        pos = event.pos
                        ev = MouseButtonRightReleaseEvent(pos)                                              
                elif event.type == pygame.MOUSEMOTION:
                    pos = event.pos
                    ev = MouseMoveEvent(pos)
                    
                #Keyboard
                #-----------------------------------                    
                elif event.type == pygame.KEYDOWN:
                    if event.key == K_ESCAPE:
                        ev = EscRequest()
                        
                #Post event to event manager
                if ev:
                    self.ev_manager.post(ev)        
                    
#        elif isinstance(event, BoardCreationTick):
#            #Share some time with other processes, so we don't hog the cpu
#            pygame.time.wait(5)               
#                           
#            #If this event manager has an associated PGU GUI app, notify it of the event
#            if self.ev_manager.gui_app:
#                self.ev_manager.gui_app.event(event)
                    
#------------------------------------------------------------------------------            
class CPUSpinnerController:
    
    def __init__(self, ev_manager):
        self.ev_manager = ev_manager
        self.ev_manager.register_listener(self)
        self.clock = pygame.time.Clock()
        self.cumu_time = 0
        self.keep_going = True
        
    #----------------------------------------------------------------------
    def run(self):
        if not self.keep_going:
            raise Exception('dead spinner')        
        while self.keep_going: 
            time_passed = self.clock.tick()
            fps = self.clock.get_fps()
            self.cumu_time += time_passed
            self.ev_manager.post(TickEvent(time_passed, fps))
            
            if self.cumu_time >= 1000:
                self.cumu_time = 0
                self.ev_manager.post(SecondEvent(fps=fps))
        
        pygame.quit()
 
    #----------------------------------------------------------------------
    def notify(self, event):
        if isinstance(event, QuitEvent):
            config.save_settings()
            self.keep_going = False            
        
class RoomController(object):
    """Controls which room is currently active (eg Title Screen)"""

    def __init__(self, screen, ev_manager):
        self.room = None
        self.screen = screen
        self.ev_manager = ev_manager
        self.ev_manager.register_listener(self)
        self.room = self.set_room(config.room)
        
    def set_room(self, room_const):
        if room_const == config.LOADING_SCREEN:
            return rooms.LoadingScreen(self.screen, self.ev_manager)
        if room_const == config.TITLE_SCREEN:
            return rooms.TitleScreen(self.screen, self.ev_manager)
        elif room_const == config.GAME_MODE_ROOM:
            return rooms.GameModeRoom(self.screen, self.ev_manager)        
        elif room_const == config.GAME_ROOM:
            return rooms.GameRoom(self.screen, self.ev_manager)
        elif room_const == config.HIGH_SCORES_ROOM:
            return rooms.HighScoresRoom(self.screen, self.ev_manager)
        elif room_const == config.CREDITS:
            return rooms.Credits(self.screen, self.ev_manager)
        elif room_const == config.HELP1:
            return rooms.Help1(self.screen, self.ev_manager)
        elif room_const == config.HELP2:
            return rooms.Help2(self.screen, self.ev_manager)                
                
    def notify(self, event):       
        if isinstance(event, ChangeRoomRequest):
            self.ev_manager.clear()
            self.room = self.set_room(event.new_room)