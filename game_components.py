#Remote imports
import pygame
from pygame.locals import *
import random
import operator
from copy import copy
from math import sqrt

#Local imports
#import config
import resources
from my_gui import BoardCreationDialog
from events import *
from matrix import Matrix
from textrect import render_textrect, TextRectException
from hyphen import hyphenator
from textwrap2 import TextWrapper

##############################
#CONSTANTS
##############################

SCREEN_MARGIN = (10, 10)

#Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 200, 0)

#Directions
LEFT = -1
RIGHT = 1
UP = 2
DOWN = -2 

#Cards
CARD_MARGIN = (10, 10)
CARD_PADDING = (2, 2)

#Card types
BLANK = 0
COUNTRY = 1
TRANSPORT = 2

#Transport types
PLANE = 0
TRAIN = 1
CAR = 2
SHIP = 3

class Timer(object):
    
    def __init__(self, ev_manager, time_left):
        self.ev_manager = ev_manager
        self.ev_manager.register_listener(self)
        self.time_left = time_left
        self.paused = False
    
    def __repr__(self):
        return str(self.time_left)
    
    def pause(self):
        self.paused = True
    
    def unpause(self):
        self.paused = False
    
    def notify(self, event):
        #Pause Event
        if isinstance(event, Pause):   
            self.pause() 
        #Unpause Event
        elif isinstance(event, Unpause):   
            self.unpause()                
        #Second Event
        elif isinstance(event, SecondEvent):   
            if not self.paused: 
                self.time_left -= 1   
                
class Chrono(object):
    
    def __init__(self, ev_manager, start_time=0):
        self.ev_manager = ev_manager
        self.ev_manager.register_listener(self)
        self.time = start_time
        self.paused = False
        self.minutes_passed = self.time / 60
        self.seconds_passed = self.time % 60
    
    def __repr__(self):
        return str(self.time)
    
    def pause(self):
        self.paused = True
    
    def unpause(self):
        self.paused = False
    
    def notify(self, event):
        if isinstance(event, SecondEvent):   
            if not self.paused: 
                self.time += 1                    
                self.minutes_passed = self.time / 60
                self.seconds_passed = self.time % 60                       

class Blinker(object):
    
    def __init__(self, ev_manager, blink = True, image = None, color = (0,0,0)):
        self.ev_manager = ev_manager
        self.ev_manager.register_listener(self)
        self.size = config.blinker_size
        self.blink = blink
        self.center = (self.size[0]/2, self.size[1]/2)
        if image:
            self.image = pygame.image.load(image).convert_alpha()
            self.image = pygame.transform.smoothscale(self.image, self.size)
        else:
            pygame.draw.circle(self, self.color, self.center, self.size[0]/2)
        self.on = False
        self.visible = True
        self.pos = (0, 0)
        self.on_time = 0
        
    def notify(self, event):
        if isinstance(event, TickEvent):
            if self.on and self.blink:
                self.on_time += event.time_passed
                if self.on_time >= 500:
                    if self.visible:
                        self.visible = False
                    else:
                        self.visible = True
                    self.on_time = 0     
            else:
                self.on_time = 0
                self.visible = True      
                       
    def map_pos(self, pos):
        x = pos[0] + config.map_pos[0] - self.size[0]/2
        y = pos[1] + config.map_pos[1] - self.size[1]/2
        self.pos = (x, y)
    
    def render(self, surface):
        surface.blit(self.image, self.pos)

class Map(object):
    
    def __init__(self, continent):
        self.map_image = continent.map_image
        self.map_text = continent.map_text
        self.pos = (0, 0)
        self.map_image = pygame.transform.smoothscale(self.map_image, config.map_size)
        self.size = config.map_size       
        
    def set_pos(self, pos):
        self.pos = pos          
        
    def render(self, surface):
        background = pygame.Surface(self.size)
        background.fill(WHITE)
        background.set_alpha(150)
        surface.blit(background, (self.pos))
        surface.blit(self.map_image, (self.pos))
        surface.blit(self.map_text, (self.pos)) 
        pygame.draw.rect(surface, config.COLOR5, Rect(self.pos, (self.size[0], self.size[1])), 1)   
        
class Deck(object):
    
    def __init__(self, ev_manager, continent = None):
        self.ev_manager = ev_manager     
        self.ev_manager.register_listener(self)   
        self.stack = []
        self.discard_stack = []        
        self.continent = continent  
        if continent != None:  
            self.rebuild(continent)  
        self.pos = (-5000,-5000)
            
    def clone(self):
        new_deck = Deck(self.ev_manager)
        for card in self.stack:
            new_card = card.clone()
            new_deck.stack.append(new_card)
        for card in self.discard_stack:
            new_card = card.clone()
            new_deck.discard_stack.append(new_card)
        return new_deck
        
        new_deck.stack = self.stack
        new_deck.discard_stack = self.discard_stack
        return new_deck      
    
    def rebuild(self, continent):
        self.stack = []
        self.discard_stack = []
                
        #Add countries  
        for country in continent.countries:
            for _ in xrange(country.number):
                self.stack.append(CountryCard(country, self.ev_manager))
        
        #Add ships
        for ocean in continent.oceans:
            for _ in xrange(ocean.number):
                self.stack.append(ShipCard(ocean, self.ev_manager))
                
        #Add planes
        for color in continent.colors:
            for _ in xrange(1):
                self.stack.append(PlaneCard(color, self.ev_manager))
                
        #Add cars
#        for _ in xrange(5):
#            self.stack.append(CarCard())        
        
    def shuffle(self):
        random.shuffle(self.stack)
            
    def deal_random(self, board):
        for _, r, c in board.matrix:
            old_card = board.get_card((r, c))
            try:
                new_card = self.stack.pop(0)
                new_card.set_pos(old_card.pos)
                board.place_card(new_card, (r,c))
            except IndexError:
                self.merge_discard_stack()
                self.shuffle()
                new_card = self.stack.pop(0)
                new_card.set_pos(old_card.pos)  
                board.place_card(new_card, (r,c))             
            if old_card.type != BLANK:    
                self.discard_stack.append(old_card)       
    
    #Returns the given board with a connection sequence of the specified number of connections   
    def deal_connection_matrix(self, board, number_of_connections, starting_index = None):
        number_of_tries = 0
        try_again = True
        clock = pygame.time.Clock()
        while try_again == True:
            self.ev_manager.post(TickEvent(clock.tick(), clock.get_fps()))
            number_of_tries += 1
#            print 'Connection Matrix Number of tries: ' + str(number_of_tries)          
            if number_of_tries >= 40:
                raise Exception('Was unable to create connection matrix after ' + str(number_of_tries) + ' tries.' )    

            self.merge_board_stack(board)
            self.shuffle    
            if starting_index == None:
                current_row = random.randrange(board.matrix.rows)
                current_col = random.randrange(board.matrix.cols)
            else:
                current_row = starting_index[0]
                current_col = starting_index[1]
            protected_indexes = []                
            
            #Set starting card
            for card in self.stack:
                if card.type == COUNTRY:
                    board.place_card_first_time(card, (current_row, current_col))
                    self.remove(card)
                    protected_indexes.append((current_row, current_col))
                    board.start_card = card
                    card.is_start_card = True
                    last_card = card
                    break       
                
            #Create connections
            test_counter = 0
            for i in xrange(number_of_connections - 1):
                test_counter += 1
                
                #Determine which direction to go for connection
                possible_new_indexes = []    
                adjacent_indexes = last_card.get_adjacent_indexes(board)
                for adjacent_index in adjacent_indexes:
                    if adjacent_index not in protected_indexes:
                        possible_new_indexes.append(adjacent_index)
                if len(possible_new_indexes) == 0:      
#                    print 'possible new index trouble'         
                    try_again = True
                    break               
                random.shuffle(possible_new_indexes)
                current_row, current_col = possible_new_indexes.pop()     
                
                #Find and place card with connection to last card 
                for card in self.stack:
                    found_connection = False
                    card.set_index((current_row, current_col), board)
                    if i == (number_of_connections - 2) and card.type == TRANSPORT:            
                        continue   
                    if card.test_connection(last_card, board):
                        found_connection = True
                        break
                    
                if found_connection == True:
                    try_again = False
                    board.place_card_first_time(card, (current_row, current_col))  
                    self.remove(card)           
                    protected_indexes.append((current_row, current_col))  
                    last_card = card     
                else: 
                    try_again = True
                    break
    
    def deal_to_blank_squares(self, board):
        for card, r, c in board.matrix:
            if card[r][c].type == BLANK:
                try:
                    new_card = self.stack.pop()
                except:
                    self.rebuild(self.continent)
                    new_card = self.stack.pop()
                board.place_card_first_time(new_card, (r, c))         
    
    def deal_new_board(self, board):
        clock = pygame.time.Clock()               
        #Progress meter
        self.board_creation_dialog = BoardCreationDialog(ev_manager=self.ev_manager)  
        self.board_creation_dialog.open()        
        self.ev_manager.post(TickEvent(clock.tick(), clock.get_fps()))         
        
        self.merge_board_stack(board)               
#        self.ev_manager.post(TickEvent(clock.tick(), clock.get_fps()))        
        self.merge_discard_stack()
        self.shuffle()
        board.clear()        
        #Change board size if changed in config
#        if board.matrix_size != config.board_size:
#            if config.board_size == config.BOARD_LARGE:
#                config.longest_trip_to_deal = config.TRIP_LARGE_TO_DEAL
#                config.longest_trip_needed = config.TRIP_LARGE_TO_WIN
#            elif config.board_size == config.BOARD_MED:
#                config.longest_trip_to_deal = config.TRIP_MED_TO_DEAL
#                config.longest_trip_needed = config.TRIP_MED_TO_WIN
#            elif config.board_size == config.BOARD_SMALL:
#                config.longest_trip_to_deal = config.TRIP_SMALL_TO_DEAL
#                config.longest_trip_needed = config.TRIP_SMALL_TO_WIN                   
#            board.change_size()
#            board.change_card_size()  
#            self.change_card_size()   
        self.deal_connection_matrix(board, config.longest_trip_to_deal)          
        board.displace_cards(1, [board.start_card.index])
        if config.fill_board:
            self.deal_to_blank_squares(board)
        board.refresh_trip()
        board.refresh_connections()
        board.refresh_darkness()   
        self.ev_manager.post(NewBoardComplete())       
        self.board_creation_dialog = None  
        
    def discard(self, card):
        self.stack.remove(card)
        self.discard_stack.append(card)   
        
    def remove(self, card):
        self.stack.remove(card)

    def place_card_on_board(self, card, board, index):
        board.place_card(card, index)
        self.stack.remove(card)
        
    def contains(self, card):
        try:
            return self.stack.index(card)
        except ValueError:
            return False
        
    def merge_discard_stack(self):
        for card in self.discard_stack:
            card.in_darkness = True
            self.stack.append(card)
            card.set_pos(self.pos)
        self.discard_stack = []
        
    def merge_board_stack(self, board):
        for card, r, c in board.matrix:
            if card[r][c].type != BLANK:
                card[r][c].is_start_card = False
                card[r][c].in_darkness = True
                self.stack.append(card[r][c])
                card[r][c].set_pos((-500,-500))
                board.remove((r, c))

    def change_card_size(self, new_size = None):
        if new_size == None:
            new_size = config.card_size        
        for card in self.stack:
            card.change_size(new_size)
        
    def notify(self, event):
        pass    
#        #DealNewBoardRequest
#        if isinstance(event, DealNewBoardRequest) and event.deck == self: 
##            count = 0
##            while count < 100:
##                count += 1
##                print 'Count: ' + str(count)
##            event.board.update = False
#            self.deal_new_board(event.board)   
        
        #Debug event
#        if isinstance(event, DebugEvent):
#            old_positions = []
#            for card, r, c in event.board.matrix:
#                old_positions.append(card[r][c].pos)
#            for card in self.stack:
#                old_positions.append(card.pos)
#            for card, r, c in event.board.matrix:
#                if old_positions.count(card[r][c].pos) > 1:
#                    print card[r][c], card[r][c].index, card[r][c].pos        
        
class Board(object):
    
    def __init__(self, size, ev_manager):
        self.update = True
        self.card_size = config.card_size
        self.pos = (0, 0)
        self.matrix_size = size
        self.width = self.matrix_size[1] * (config.card_size[0] + CARD_MARGIN[0])
        self.height = self.matrix_size[0] * (config.card_size[1] + CARD_MARGIN[1])
        self.connections = []
        self.selected_card = None 
        self.start_card = None  
        self.longest_trip = 1
        self.longest_trip_list = None
        self.ev_manager = ev_manager
        self.ev_manager.register_listener(self)
        self.swapping = False
        self.swapping_list = []
        self.completed_swaps = []
        self.blinker_selected = Blinker(self.ev_manager, True, 'assets/images/interface/blinker_red.png')        
        self.blinker_hover = Blinker(self.ev_manager, False, 'assets/images/interface/blinker_green.png')
        
        #Create a matrix to hold the cards, and deal blank cards to start
        self.matrix = Matrix(self.matrix_size[0], self.matrix_size[1])
        self.clear()
    
    def change_size(self, new_size = None):
        if new_size == None:
            new_size = config.card_size
        if self.matrix_size == new_size:
            return
        else:
            self.matrix_size = config.board_size
            self.matrix = Matrix(self.matrix_size[0], self.matrix_size[1])
            self.clear()
            
    def change_card_size(self, new_size = None):
        if new_size == None:
            new_size = config.card_size
        self.card_size = new_size
        for card, r, c in self.matrix:
            card[r][c].change_size(new_size)
                
    def clone(self):
        new_board = Board((self.matrix_size[0], self.matrix_size[1]), self.ev_manager)
        new_board.set_pos(self.pos)
        for card, r, c in self.matrix:
            new_card = card[r][c].clone()
            if card[r][c] == self.start_card:
                new_board.set_start_card(new_card)
            new_board.place_card(new_card, (r, c))
        return new_board
               
    def count_cards(self):
        count = 0
        for card, r, c in self.matrix:
            if card[r][c].type != BLANK:
                count += 1
        return count
     
    def clear(self):
        self.clear_selection()
        for _, r, c in self.matrix:
            blank_card = BlankCard(self.ev_manager)
            blank_card.set_index((r, c), self) 
            self.matrix.setitem(r, c, blank_card)     
        self.set_pos(self.pos)
        self.connections = []
        
    #Replace card at given index with blank card
    def remove(self, index):
        blank_card = BlankCard(self.ev_manager)
        self.matrix.setitem(index[0], index[1], blank_card) 
        blank_card.set_index((index[0], index[1]), self)     
        self.set_pos(self.pos)
        self.connections = self.refresh_connections()
        
    def set_pos(self, pos):
        self.pos = pos    
        self.grid_lines = []
        
        #Set card position
        for card,r,c in self.matrix:
            x = c * (self.card_size[0] + CARD_MARGIN[0]) + self.pos[0]
            x_orig = x
            if  c % 2 == 1:
                x -= CARD_MARGIN[0] / 4
            elif c % 2 == 0:
                x += CARD_MARGIN[0] / 4
            y = r * (self.card_size[1] + CARD_MARGIN[1]) + self.pos[1]
            y_orig = y 
            if  r % 2 == 1:
                y -= CARD_MARGIN[1] / 4
            elif r % 2 == 0:
                y += CARD_MARGIN[1] / 4  
                          
            card[r][c].set_pos((x,y))  
            
            #Set grid line positions
            if c != 0 and c % 2 == 0:
                a = (x_orig - CARD_MARGIN[0] / 2, self.pos[1])
                b = (x_orig - CARD_MARGIN[0] / 2, self.pos[1] + self.height - CARD_MARGIN[1])
                self.grid_lines.append((a, b))
            if r != 0 and r % 2 == 0:
                a = (self.pos[0], y_orig - CARD_MARGIN[1] / 2)
                b = (self.pos[0] + self.width - CARD_MARGIN[0], y_orig - CARD_MARGIN[1] / 2)
                self.grid_lines.append((a, b))                
    
    def set_start_card(self, card):
        self.start_card = card
            
    def place_card(self, card, index):
        self.matrix.setitem(index[0], index[1], card) 
        card.set_index((index[0], index[1]), self)      
        self.set_pos(self.pos) 
        card.destination = card.pos
        
    def place_card_first_time(self, card, index):
        self.place_card(card, index)
        card.set_possible_indexes(self)
            
    #Return the card at the given matrix index (r, c)            
    def get_card(self, index):
        if index[0] < 0 or index[1] < 0:
            raise Exception('Cannot get card from a negative index')
        return self.matrix.getitem(index[0], index[1])            
    
    def test_index_on_board(self, index):
        if index[0] < 0 or index[0] > self.matrix_size[0] - 1:
            return False
        elif index[1] < 0 or index[1] > self.matrix_size[1] - 1:
            return False
        else:
            return True
   
    def clear_selection(self):
        self.blinker_selected.on = False
        if self.selected_card:
            self.selected_card.selected = False
            self.selected_card = None
            for card, r, c in self.matrix:
                card[r][c].possible_swap = False
                card[r][c].update_text_color()
   
    def set_possible_swaps(self, card):
        possible_indexes = card.get_bounding_box(self)
        for index in possible_indexes:
            if index != card.index:
                possible_swap_card = self.get_card(index)
                possible_swap_card.possible_swap = True
            
    def select_card(self, card):
        if self.selected_card:
            self.clear_selection()
        card.selected = True
        self.selected_card = card
        card.update_text_color()       
        self.set_possible_swaps(card)
        if card.type == COUNTRY or (card.type == TRANSPORT and card.transport_type == SHIP):
            self.blinker_selected.map_pos(card.map_coord)
            self.blinker_selected.on = True
            if self.blinker_hover.pos == self.blinker_selected.pos:
                    self.blinker_hover.on = False            
        
    def request_swap(self, card1, card2):
        card1.destination = copy(card2.pos)
        card2.destination = copy(card1.pos)
        card1.future_index = copy(card2.index)
        card2.future_index = copy(card1.index) 
        self.swapping = True 
        self.swapping_list.append(card1)
        self.swapping_list.append(card2)    
        self.clear_selection()
        
    #displace_by = number of cards to displace each card by  
    #cards with indexes in protected_indexes are not displaced
    #returns False if unsuccessful at displacing cards; can try again
    def displace_cards(self, displace_by, protected_indexes):
        clock = pygame.time.Clock()        
        original_setup = {}
        for card, r, c in self.matrix:
            if card[r][c].type != BLANK:
                original_setup[card[r][c]] = card[r][c].index
        #Sort the cards by matrix index, so that they can be displaced more systematically
        #This method attained from http://stackoverflow.com/questions/613183/python-sort-a-dictionary-by-value
        original_setup = sorted(original_setup.items(), key=operator.itemgetter(1))
        
        number_of_tries = 0
        try_again = True
        while try_again == True:   
            self.ev_manager.post(TickEvent(clock.tick(), clock.get_fps()))
            #Throw exception if too many tries
            number_of_tries += 1
#            print 'Number of displacement tries: ' + str(number_of_tries)
            if number_of_tries >= 20:
                raise Exception('Was unable to create displacement board ' + str(number_of_tries) + ' tries.' )     
            
            self.clear()    
            
            #Set up variables    
            new_protected_indexes = copy(protected_indexes)    

            for card, original_index in original_setup:                 
                possible_new_indexes = []
                if original_index in protected_indexes:
                    self.place_card(card, original_index)
                    try_again = False
                else:      
                    #Determine which direction to go for displacement
                    for index in card.get_bounding_box(self):
                        if index not in new_protected_indexes:
#                            if not card.get_connections(self, index):                         
                            connections = card.get_connections(self, index)
                            if connections:
                                number_of_connections = len(card.get_connections(self, index))
                                possible_new_indexes.append((number_of_connections, index))
                            else:
                                possible_new_indexes.append((0, index))
                    possible_new_indexes.sort()
            
                    if len(possible_new_indexes) == 0:
                        try_again = True
                        break 
                    else:
                        try_again = False             
                        new_index = possible_new_indexes.pop(0)[1]
                        self.place_card(card, new_index)
                        new_protected_indexes.append(new_index)   
                    
        self.ev_manager.post(DisplaceCardsComplete())                    
     
    def refresh_trip(self):
        for card, r, c in self.matrix:
            card[r][c].in_trip = False
            card[r][c].in_longest_trip = False
            card[r][c].update_text_color()
        if self.start_card:
            self.start_card.add_to_trip(self)   
            self.longest_trip_list = self.get_longest_trip()
        if self.longest_trip_list:
            self.longest_trip = len(self.longest_trip_list)
            for card, r, c in self.matrix:
                if card[r][c] in self.longest_trip_list:
                    card[r][c].in_longest_trip = True
                    card[r][c].in_darkness = False    
                    card[r][c].update_text_color()
        
    def get_longest_trip(self):
        return self.start_card.get_longest_trip(self, list())    
    
    #refresh all connections on the board - typically done when a card is moved
    #IMPORTANT: refresh_trip needs to be called first for connections' in_trip property to be set correctly
    def refresh_connections(self):
        self.connections = []
        for card, r, c in self.matrix:
            current_card = card[r][c]
            try:
                card_right = card[r][c+1]
                if current_card.test_connection(card_right, self):
                    new_connection = Connection(current_card, card_right, self.ev_manager)
                    self.connections.append(new_connection)
            except:
                pass
            try:
                card_down = card[r+1][c]
                if current_card.test_connection(card_down, self):
                    new_connection = Connection(current_card, card_down, self.ev_manager)
                    self.connections.append(new_connection)
            except:
                pass  
    
    def refresh_darkness(self):
        for card, r, c in self.matrix:
            if card[r][c] == self.start_card:
                card[r][c].in_darkness = False  
            elif card[r][c].test_close_to_trip(self):
                card[r][c].in_darkness = False  
            else:
                card[r][c].in_darkness = True 
    
    def notify(self, event):
        #Tick Event
        if isinstance(event, TickEvent):
            #Swapping
            if self.swapping and not self.swapping_list:
                self.swapping = False
                for card in self.completed_swaps:
                    self.place_card(card, card.future_index)        
                self.refresh_trip()
                self.refresh_connections()
                self.refresh_darkness()       
                self.completed_swaps = []                            
                self.ev_manager.post(CardSwapComplete())   
 
        #MouseMove Event
        elif isinstance(event, MouseMoveEvent):
            #Blinker
            for card, r, c in self.matrix:
                if card[r][c].test_pos_on_card(event.pos):
                    if card[r][c].type == COUNTRY or (card[r][c].type == TRANSPORT and card[r][c].transport_type == SHIP):
                        if not card[r][c].selected and not card[r][c].in_darkness:
                            self.blinker_hover.map_pos(card[r][c].map_coord)
                            self.blinker_hover.on = True 
                        else:
                            self.blinker_hover.on = False
                    break
                else:
                    self.blinker_hover.on = False
            else:
                self.blinker_hover.on = False
          
        #CardSwapComplete Event
        elif isinstance(event, CardSwapComplete):
            #Blinker
            mouse_pos = pygame.mouse.get_pos()
            for card, r, c in self.matrix:
                if card[r][c].test_pos_on_card(mouse_pos):
                    if card[r][c].type == COUNTRY or (card[r][c].type == TRANSPORT and card[r][c].transport_type == SHIP):
                        if not card[r][c].selected and not card[r][c].in_darkness:
                            self.blinker_hover.map_pos(card[r][c].map_coord)
                            self.blinker_hover.on = True 
                        else:
                            self.blinker_hover.on = False
                    break
            else:
                self.blinker_hover.on = False
    
    #Render board components
    def render(self, surface):
        #Render bounding box grid
        for line in self.grid_lines:
            pygame.draw.aaline(surface, config.COLOR5, line[0], line[1])
        
        #Render connections
        if self.connections:
            for connection in self.connections:
                if connection.in_trip:
                    connection.render(surface)            
        #Render cards
        for card,r,c in self.matrix:
            if card[r][c] != 0:
                card[r][c].render(surface)
                
        #Render blinkers
        if self.blinker_selected.on and self.blinker_selected.visible:
            self.blinker_selected.render(surface)
        if self.blinker_hover.on:
            self.blinker_hover.render(surface)
    
class Card(object):
    
    def __init__(self, type, text, image, color, ev_manager):  
        self.in_longest_trip = False        
        self.color = color
        self.text = text
        self.text_rect = None
        self.image = image
        self.board = None
        self.is_start_card = False
        self.size = config.card_size
        self.price = 0
        self.font = pygame.font.Font(config.font_mono, config.card_font_size)
        self.text_color = BLACK
        self.text_bgcolor = WHITE             
        self.pos = [-500, -500]   
        self.destination = self.pos    
        self.type = type     
        self.selected = False  
        self.possible_swap = False
        self.in_trip = False
        self.possible_indexes = ()
        self.ev_manager = ev_manager
        self.ev_manager.register_listener(self)
        self.in_darkness = True     #Cards that are not close to the longest trip are in darkness
        self.index = None
        self.speed = config.card_speed
        self.moving = False
        self.future_index = self.index
        self.frozen = False       
        self.set_text()
        self.set_image(self.image)  
        
        #shadow
        if config.difficulty == config.EASY:
            self.shadow = resources.card_shadow_large
        else:
            self.shadow = resources.card_shadow_small            
            
    def change_size(self, new_size = None):
        if new_size == None:
            new_size = config.card_size        
        self.size = new_size
        self.set_text(self.text)
        self.set_image(self.image)
        self.set_pos(self.pos)

    def clone(self):
        if self.type == BLANK:
            return BlankCard(self.ev_manager)
        elif self.type == COUNTRY:
            return CountryCard(self.country, self.ev_manager)
        elif self.type == TRANSPORT:
            if self.transport_type == PLANE:
                return PlaneCard(self.color, self.ev_manager)
            elif self.transport_type == TRAIN:
                return TrainCard(self.ev_manager)
            elif self.transport_type == CAR:
                return CarCard(self.ev_manager)    
            elif self.transport_type == SHIP:
                return ShipCard(self.ocean, self.ev_manager)                    
        
    def set_text(self):
        self.rendered_text = self.render_text_rec()  
        self.text_size = self.rendered_text.get_size()          
        
    def update_text_color(self):
        try:
            if self.selected:
                text_color = BLACK
                bg_color = pygame.Color('#e9c0b7')            
            elif self.is_start_card:
                text_color = WHITE
                bg_color = config.COLOR3        
            elif self.in_longest_trip:
                text_color = BLACK
                bg_color = pygame.Color('#c3d3b8')
            else:
                text_color = BLACK
                bg_color = WHITE
            self.rendered_text = render_textrect(self.text, self.font, self.text_rect, text_color, bg_color, 1)
        except:
            pass

    #Render some text in a wrapped text rectangle that fits within the card    
    def render_text_rec(self):
        if self.selected:
            text_color = BLACK
            bg_color = pygame.Color('#e9c0b7')            
        elif self.is_start_card:
            text_color = WHITE
            bg_color = config.COLOR3        
        elif self.in_longest_trip:
            text_color = BLACK
            bg_color = pygame.Color('#c3d3b8')
        else:
            text_color = BLACK
            bg_color = WHITE
            
        max_text_width = self.size[0] - 2*CARD_PADDING[0]
        text_size = self.font.size(self.text)
        if text_size[0] <= max_text_width:
            text_lines = 1;
        elif text_size[0] <= max_text_width*2:
            text_lines = 2;
        elif text_size[0] <= max_text_width*3:
            text_lines = 3;
        else:
            text_lines = 4
        try_again = True
        while try_again == True:
            try:
                self.text_rect = pygame.Rect(0, 0, max_text_width + 1, text_lines*text_size[1] + 1)
                return render_textrect(self.text, self.font, self.text_rect, text_color, bg_color, 1)
            except (TextRectException) as exception:
                if exception.problem == 'too long':
                    self.text = self.wrap_text(self.text)
                elif exception.problem == 'too tall':
                    text_lines += 1
    
    def wrap_text(self, text):
        """Wraps text to fit on card--uses hyphenation dictionary. Returns string."""
        
        max_text_width = self.size[0] - 2*CARD_PADDING[0] - 1
        char_size = self.font.size("A")
        max_chars = int(max_text_width/char_size[0])
        
        h_en = hyphenator('en_US', lmin = 3, rmin = 3)
        tw = TextWrapper(width=max_chars, use_hyphenator=h_en)
        
        wrapped_text = tw.fill(unicode(text))
        return wrapped_text

    def set_image(self, image):
        try:
            image = self.image  
            
            #Scale image to card size
            height_ratio = float(image.get_height()) / float(image.get_width())
            max_image_height = int(self.size[1] - self.text_size[1] - 2*CARD_PADDING[1])
            max_image_width = int(self.size[0] - 2*CARD_PADDING[0])
            self.image_size = [0, 0]
            if height_ratio >= float(max_image_height) / float(max_image_width):
                self.image_size[1] = max_image_height
                self.image_size[0] = int(self.image_size[1] / height_ratio) 
            else:
                self.image_size[0] = max_image_width
                self.image_size[1] = int(self.image_size[0] * height_ratio)
                
            #Scale image with scale_factor
            if self.type == COUNTRY:
                scale_factor = self.country_size
            else:
                scale_factor = 0.9                
            self.image_size[0] = int(scale_factor*self.image_size[0])
            self.image_size[1] = int(scale_factor*self.image_size[1])
            
            self.rendered_image = pygame.transform.smoothscale(image, self.image_size)
        except pygame.error, e:
            print e
        
    def set_pos(self, pos):
        #Set card pos
        self.pos[0] = pos[0]
        self.pos[1] = pos[1]
        
        #Set text pos
        self.text_pos = [0, 0]
        self.text_pos[0] = self.pos[0] + CARD_PADDING[0]
        self.text_pos[1] = self.pos[1] + self.size[1] - CARD_PADDING[1] - self.text_size[1] + 1
        
        #Set price pos
        self.price_pos = [0, 0]
        self.price_pos[0] = self.pos[0] + CARD_PADDING[0]
        self.price_pos[1] = self.pos[1] + CARD_PADDING[1]
        
        #Set img pos
        try:
            self.image_pos = [0, 0]
            max_image_height = int(self.size[1] - self.text_size[1] - 2*CARD_PADDING[1])
            self.image_pos[0] = self.get_center()[0] - self.image_size[0]/2
            self.image_pos[1] = self.pos[1] + max_image_height/2 + CARD_PADDING[1] - self.image_size[1]/2
#            self.image_pos[1] = self.get_center()[1] - self.text_size[1] - self.image_size[1]/2 + 2*CARD_PADDING[1]
        except:
            pass     
        
    def move(self, time_passed):
        vec_to_destination = (self.destination[0] - self.pos[0], 
                              self.destination[1] - self.pos[1])
        distance_to_destination = sqrt(vec_to_destination[0]**2 + 
                                       vec_to_destination[1]**2)
        l = sqrt(vec_to_destination[0]*vec_to_destination[0] + 
                 vec_to_destination[1]*vec_to_destination[1])
        heading = [0, 0]
        try:
            heading[0] = vec_to_destination[0] / l
            heading[1] = vec_to_destination[1] / l
        except ZeroDivisionError:
            pass
        travel_distance = min(distance_to_destination, time_passed * self.speed)
        new_x = self.pos[0] + travel_distance * heading[0]
        new_y = self.pos[1] + travel_distance * heading[1] 
        self.set_pos((new_x, new_y))        
        
    #Set card's index in the board matrix    
    def set_index(self, index, board):
        self.board = board            
        self.index = index
        
    def set_possible_indexes(self, board):
        self.possible_indexes = list(self.get_adjacent_indexes(board))
        self.possible_indexes.append(self.index)
 
    #Return the card's center position
    def get_center(self):
        return (self.pos[0] + self.size[0]/2, self.pos[1] + self.size[1]/2) 
        
    #Test to see if a given position (x,y) is covered by this card, used to check if clicked on card, etc.
    def test_pos_on_card(self, pos):
        if pos[0] > self.pos[0] and pos[0] < self.pos[0] + self.size[0]:
            if pos[1] > self.pos[1] and pos[1] < self.pos[1] + self.size[1]:
                return True
        return False         
    
    #Test whether a particular card is next to this one on the board
    def test_next_to(self, card):
        if abs(self.index[0] - card.index[0]) == 1 and self.index[1] == card.index[1]:
            return True
        elif abs(self.index[1] - card.index[1]) == 1 and self.index[0] == card.index[0]:
            return True
        else:
            return False  
    
    def get_next_to(self, board):
        next_to_list = []
        for r in xrange(-1, 2):
            for c in xrange(-1, 2):
                test_index = (r + self.index[0], c + self.index[1])
                if board.test_index_on_board(test_index) and board.get_card(test_index) != self:
                    if self.index[0] == test_index[0] or self.index[1] == test_index[1]:
                        next_to_list.append(board.get_card(test_index))
        return next_to_list
    
    def get_bounding_box(self, board):
        bounding_box_indexes = []
        
        box_row = (self.index[0]) / 2
        box_col  = (self.index[1]) / 2
        
        top_row = box_row * 2
        left_col = box_col * 2
        
        if board.test_index_on_board((top_row + 1, left_col)):
            bottom_row = top_row + 1
        else:
            bottom_row = top_row
            
        if board.test_index_on_board((top_row, left_col + 1)):
            right_col = left_col + 1
        else:
            right_col = left_col
            
        for r in xrange(top_row, bottom_row + 1):
            for c in xrange(left_col, right_col + 1):
                bounding_box_indexes.append((r, c))
        
        return bounding_box_indexes
    
    def test_close_to_trip(self, board):
        for index in self.get_bounding_box(board):
            card = board.get_card(index)
            if card.in_trip:
                return True
            else:
                for second_card in card.get_next_to(board):
                    if second_card.in_trip:
                        return True
            
            
#        for card in self.get_next_to(board):
#            if card.in_longest_trip == True:
#                return True
#            for second_card in card.get_next_to(board):
#                if second_card.in_trip == True:
#                    return True
#        return False
    
    def add_to_trip(self, board):
        self.in_trip = True
        if self.get_connections(board):
            for card in self.get_connections(board):
                if card.in_trip == False:
                    card.add_to_trip(board)  
  
    def get_longest_trip(self, board, processed_cards = list()):
        processed_cards = list(processed_cards)
        processed_cards.append(self)
    
        longest_trip = list()
        if self.get_connections(board):
            possible_trips = list()
            for card in self.get_connections(board):
                if card not in processed_cards:
                    possible_trips.append(card.get_longest_trip(board, 
                                                                processed_cards))
            if possible_trips:
                longest_trip = max(possible_trips, key=len)
                longest_trip.append(self)
    
        if not longest_trip:
            longest_trip.append(self)
        return longest_trip
                                 
    def get_adjacent_indexes(self, board):
        row = self.index[0]
        col = self.index[1]
        adjacent_indexes = []
        if row != 0:
            adjacent_indexes.append((row - 1, col))
        if row != board.matrix.last_row: 
            adjacent_indexes.append((row + 1, col))
        if col != 0:
            adjacent_indexes.append((row, col - 1))
        if col != board.matrix.last_col: 
            adjacent_indexes.append((row, col + 1))
        return adjacent_indexes
                
    #Test whether there is a connection between a particular card and this one    
    #Returns True or False
    def test_connection(self, card, board):
        if self.type == BLANK or card.type == BLANK:
            return False
        if self.type == COUNTRY:
            if card.type == COUNTRY:   
                for country_name in self.borders:
                    if country_name == card.country_name:
                        return True
            elif card.type == TRANSPORT:
                if card.transport_type == SHIP:
                    for ocean_name in self.oceans:
                        if ocean_name == card.ocean_name:
                            return True
                elif card.transport_type == PLANE:
                    if self.color == card.color:
                        return True
                elif card.transport_type == CAR:
                    second_card_indexes = []
                    if card.index[1] > self.index[1]:
                        second_card_indexes.append((card.index[0], card.index[1] + 1))
                        second_card_indexes.append((card.index[0] + 1, card.index[1]))
                        second_card_indexes.append((card.index[0] - 1, card.index[1]))
                    elif card.index[1] < self.index[1]:
                        second_card_indexes.append((card.index[0], card.index[1] - 1))
                        second_card_indexes.append((card.index[0] + 1, card.index[1]))
                        second_card_indexes.append((card.index[0] - 1, card.index[1]))
                    elif card.index[0] > self.index[0]:
                        second_card_indexes.append((card.index[0] + 1, card.index[1]))
                        second_card_indexes.append((card.index[0], card.index[1] + 1))
                        second_card_indexes.append((card.index[0], card.index[1] - 1))
                    else:
                        second_card_indexes.append((card.index[0] + -1, card.index[1]))
                        second_card_indexes.append((card.index[0], card.index[1] + 1))
                        second_card_indexes.append((card.index[0], card.index[1] - 1))
                    for second_card_index in second_card_indexes:
                        if board.test_index_on_board(second_card_index):
                            second_card = board.get_card(second_card_index)
                            if second_card.type == COUNTRY:
                                for country_name in self.borders:
                                    for second_country_name in second_card.borders:
                                        if country_name == second_country_name or country_name == second_card.country_name:
                                            return True
        elif self.type == TRANSPORT:
            if card.type == TRANSPORT:
                return False
            elif card.type == COUNTRY:
                if self.transport_type == SHIP:
                    for ocean_name in card.oceans:
                        if ocean_name == self.ocean_name:
                            return True        
                elif self.transport_type == PLANE:
                    if self.color == card.color:
                        return True       
                elif self.transport_type == CAR:
                    second_card_indexes = []
                    if self.index[1] > card.index[1]:
                        second_card_indexes.append((self.index[0], self.index[1] + 1))
                        second_card_indexes.append((self.index[0] + 1, self.index[1]))
                        second_card_indexes.append((self.index[0] - 1, self.index[1]))
                    elif self.index[1] < card.index[1]:
                        second_card_indexes.append((self.index[0], self.index[1] - 1))
                        second_card_indexes.append((self.index[0] + 1, self.index[1]))
                        second_card_indexes.append((self.index[0] - 1, self.index[1]))
                    elif self.index[0] > card.index[0]:
                        second_card_indexes.append((self.index[0] + 1, self.index[1]))
                        second_card_indexes.append((self.index[0], self.index[1] + 1))
                        second_card_indexes.append((self.index[0], self.index[1] - 1))
                    else:
                        second_card_indexes.append((self.index[0] + -1, self.index[1]))
                        second_card_indexes.append((self.index[0], self.index[1] + 1))
                        second_card_indexes.append((self.index[0], self.index[1] - 1))
                    for second_card_index in second_card_indexes:
                        if board.test_index_on_board(second_card_index):
                            second_card = board.get_card(second_card_index)
                            if second_card.type == COUNTRY:
                                for country_name in card.borders:
                                    for second_country_name in second_card.borders:
                                        if country_name == second_country_name or country_name == second_card.country_name:
                                            return True
                      
        return False         
    
    #Get all cards with immediate connections to this card
    #Returns a list of cards, or None if no connections
    def get_connections(self, board, index = None):
        if index == None:
            index = self.index
        r = index[0]
        c = index[1]
        connections = []
        try: 
            card_right = board.get_card([r, c+1])
            if self.test_connection(card_right, board):
                connections.append(card_right)
        except:
            pass
        try: 
            card_down = board.get_card([r+1, c])
            if self.test_connection(card_down, board):
                connections.append(card_down)
        except:
            pass
        try: 
            card_left = board.get_card([r, c-1])
            if self.test_connection(card_left, board):
                connections.append(card_left)
        except:
            pass  
        try: 
            card_up = board.get_card([r-1, c])
            if self.test_connection(card_up, board):
                connections.append(card_up)
        except:
            pass    
        if len(connections) > 0:
            return connections   
        else:
            return None
    
    #Replace this card with another card
    def replace(self, card):
        card.set_pos(self.pos)
        card.set_index(self.index, self.board)
    
    def __repr__(self):
        return str(self.text)    
    
    def notify(self, event):
        #Tick Event
        if isinstance(event, TickEvent):
            if self.pos != self.destination:
                self.moving = True
                self.move(event.time_passed)
            #If card has reached destination but is still "swapping"
            elif self.board:
                if self in self.board.swapping_list:
                    self.board.swapping_list.remove(self) 
                    self.board.completed_swaps.append(self)
                    self.moving = False
                
        #MouseButton Left Event
        elif isinstance(event, MouseButtonLeftEvent):
            if self.test_pos_on_card(event.pos):
                if (self.frozen or self.in_darkness or self == self.board.start_card or 
                    self.moving or self in self.board.completed_swaps):
                    return
                elif self.board.selected_card:
                    if self.selected:
                        self.board.clear_selection()
                    elif self.possible_swap:
                        self.board.request_swap(self, self.board.selected_card)
                    elif self.type != BLANK:
                        self.board.select_card(self)
                elif self.type != BLANK:
                    self.board.select_card(self)                    
  
        elif isinstance(event, FreezeCards):
            self.frozen = True
        elif isinstance(event, UnfreezeCards):
            self.frozen = False            
    
    def render(self, surface): 
        #Shadow
        if self.type != BLANK:        
            surface.blit(self.shadow, self.pos)
        
        #Background
        background = pygame.Surface(self.size)
        background_color = None         
        background.fill(WHITE)       
        if self.selected:
            background_color = pygame.Surface(self.size)
            background_color.fill(config.COLOR1) 
            background_color.set_alpha(75)        
        elif self.in_longest_trip:
            background_color = pygame.Surface(self.size)
            background_color.fill(config.COLOR3) 
            background_color.set_alpha(75)
        if self.type != BLANK:
            surface.blit(background, self.pos) 
        if background_color:
            surface.blit(background_color, self.pos) 
       
        #Image
        if self.type != BLANK:
            surface.blit(self.rendered_image, self.image_pos, None, 0)
       
        #Outline
        if self.selected:
            pygame.draw.rect(surface, config.COLOR1, Rect(self.pos, (self.size[0], self.size[1])), 1)
        elif self.is_start_card:
            pygame.draw.rect(surface, config.COLOR3, Rect(self.pos, (self.size[0], self.size[1])), 2)
        elif self.possible_swap:
            pygame.draw.rect(surface, config.COLOR1, Rect(self.pos, (self.size[0], self.size[1])), 2)
        elif self.in_longest_trip:
            pygame.draw.rect(surface, config.COLOR3, Rect(self.pos, (self.size[0], self.size[1])), 2)            
        elif self.type != BLANK:
            pygame.draw.rect(surface, BLACK, Rect(self.pos, (self.size[0], self.size[1])), 1)
   
        #Text
        if self.type != BLANK:
            surface.blit(self.rendered_text, self.text_pos)
        
        #Darkness
        if config.use_darkness and self.in_darkness and self.type != BLANK:
            dark_surface = pygame.Surface(self.size)
            dark_surface.fill(BLACK)
            dark_surface.set_alpha(150)
            surface.blit(dark_surface, self.pos)          

                    
class BlankCard(Card):
        
    def __init__(self, ev_manager):
        self.price = 0
        self.borders = None
        image = pygame.image.load("assets/images/blank_card.png")
        # Call the base class constructor
        Card.__init__(self, BLANK, "Blank", image, RED, ev_manager)     
    
class CountryCard(Card):
        
    def __init__(self, country, ev_manager):
        self.country = country
        self.country_name = country.name
        self.borders = country.borders
        self.oceans = country.oceans
        self.country_size = country.size
        self.price = country.price        
        self.map_coord = country.coord
        # Call the base class constructor
        Card.__init__(self, COUNTRY, country.name, country.image, country.color, ev_manager)  
        
class TransportCard(Card):
        
    def __init__(self, transport_type, text, image, color, ev_manager):
        # Call the base class constructor
        Card.__init__(self, TRANSPORT, text, image, color, ev_manager)  
        self.transport_type = transport_type
        
class PlaneCard(TransportCard):
        
    def __init__(self, color, ev_manager):
        
        color_string = str(color)
        plane_image = resources.plane_image[color_string]

        # Call the base class constructor
        TransportCard.__init__(self, PLANE, "Airplane", plane_image, color, ev_manager)    
        
class TrainCard(TransportCard):
        
    def __init__(self, ev_manager):
        train_image = 'assets/images/transport/train.png'
        # Call the base class constructor
        TransportCard.__init__(self, TRAIN, "Railroad", train_image, None, ev_manager)   
        
class CarCard(TransportCard):
        
    def __init__(self, ev_manager):
        car_image = 'assets/images/transport/car.png'
        self.price = 200          
        # Call the base class constructor
        TransportCard.__init__(self, CAR, "Car", car_image, None, ev_manager)     
        
class ShipCard(TransportCard):
        
    def __init__(self, ocean, ev_manager):
        ship_image = ocean.card_image
        self.ocean = ocean
        self.ocean_name = ocean.name       
        self.map_coord = ocean.coord           
        # Call the base class constructor
        TransportCard.__init__(self, SHIP, ocean.name, ship_image, None, ev_manager)                      
    
class Connection(object):    
    
    def __init__(self, card1, card2, ev_manager):
        self.card1 = card1
        self.card2 = card2
        self.point_a = card1.get_center()
        self.point_b = card2.get_center()
        if self.card1.in_trip or self.card2.in_trip:
            self.in_trip = True
        else:
            self.in_trip = False
          
    def __repr__(self):
        return self.card1.name + "--" + self.card2.name         
    
    def render(self, surface):
        pygame.draw.aaline(surface, config.COLOR3, self.point_a, self.point_b, False)