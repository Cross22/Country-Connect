#Remote imports
#import cProfile
#from pygame.locals import *

#Local imports
from event_manager import *
#from events import *
    
def create_display():   
    current_display = pygame.display.Info()
    w = current_display.current_w
    h = current_display.current_h
    
    #Screensize
    if w == 1024:
        if h < 600 and h >= 570:
            config.screen_size = (1024, h)
    else:
        config.screen_size = (1024, 600)        
    
    #Fullscreen
    modes = pygame.display.list_modes()
    if (1024, 600) in modes:
        config.fullscreen = True
    else:
        config.fullscreen = False
    
    if config.fullscreen:
        return pygame.display.set_mode(config.screen_size, FULLSCREEN)
    else:
        return pygame.display.set_mode(config.screen_size)    
    
def main():
    pygame.init()
    
    screen = create_display()
    pygame.display.set_caption("Country Connect!")      
    ev_manager = EventManager()
    spinner = CPUSpinnerController(ev_manager)
    room_controller = RoomController(screen, ev_manager)    
    pygame_event_controller = PyGameEventController(ev_manager)

    spinner.run()
    

# this runs the main function if this script is called to run.
#  If it is imported as a module, we don't run the main function.
if __name__ == "__main__": 
#    cProfile.run('main()', 'cprofile')
#    config.debug = True
    main()

#    config.debug = True
#    cProfile.run('main()', 'cprofile')


    