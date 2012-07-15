'''
Created on Jul 9, 2012

@author: Compy
'''

import procgame.game
import procgame.dmd
from procgame.dmd import *

font_tiny7 = procgame.dmd.Font("./dmd/04B-03-7px.dmd")
font_jazz18 = procgame.dmd.Font("./dmd/Jazz18-18px.dmd")
font_14x10 = procgame.dmd.Font("./dmd/Font14x10.dmd")
font_18x12 = procgame.dmd.Font("./dmd/Font18x12.dmd")
font_07x4 = procgame.dmd.Font("./dmd/Font07x4.dmd")
font_07x5 = procgame.dmd.Font("./dmd/Font07x5.dmd")
font_09Bx7 = procgame.dmd.Font("./dmd/Font09Bx7.dmd")
font_eurostile = procgame.dmd.font_named("eurostile.dmd")
lampshow_path = "lampshows/"

class PrepareToStart(procgame.game.Mode):
    """
    This class is responsible for checking if the game is ready to begin.
    
    A few things it does:
        Check to see if the trough is full (all balls are drained and off the playfield)
        If the trough is not full, find the remaining balls and kick them out and wait for them to drain
        If the trough is full, kick a ball into the shooter lane and start the game
    """
    def __init__(self, game):
        super(PrepareToStart, self).__init__(game=game, priority=9)
    
    def mode_started(self):
        self.game.trough.changed_handlers.append(self.trough_changed)
        self.pulse_and_delay()
        
    def mode_stopped(self):
        self.game.trough.changed_handlers.remove(self.trough_changed)
        
    def trough_changed(self):
        self.check_ready()
        
    def check_ready(self):
        """
        Check the system state to see if we are ready to start the game.
        """
        return True
        if self.game.trough.is_full():
            self.ready()
            return True
        
        return False
    
    def pulse_and_delay(self):
        ready = self.check_ready()
        
        if not ready:
            self.game.set_status("Looking for pinballs...")
            self.game.coils.thingEject.pulse()
            self.game.coils.chairKickout.pulse()
            self.game.coils.swampRelease.pulse()
            self.delay(name='pulse_and_delay',
                       event_type = None,
                       delay = 5.0,
                       handler = self.pulse_and_delay)
        else:
            self.ready()
            
    def ready(self):
        """
        This is called to indicate that the game is ready to start
        """
        self.game.modes.remove(self)
        # Initialize the game
        self.game.start_game()
        # Add the first player
        self.game.add_player()
        # Start the ball (eject it from the trough into the shooterlane)
        self.game.start_ball()
        
class Attract(procgame.game.Mode):
    """
    The attract mode runs when a game is not in progress. Usually this includes
    a light show and a series of random messages displayed on the dot matrix.
    """
    
    def __init__(self, game):
        super(Attract, self).__init__(game=game, priority=9)
        
        self.press_start = procgame.dmd.TextLayer(128/2, 18, font_09Bx7, "center", opaque=True).set_text("PRESS START")
        self.game_over_layer = procgame.dmd.TextLayer(128/2, 10, font_18x12, "center", opaque=True).set_text("GAME OVER")
       
        self.rpi_logo = procgame.dmd.AnimatedLayer()
        anim = procgame.dmd.Animation().load("./dmd/rpi.dmd")
        self.rpi_logo.frames = anim.frames
       
        self.taf_logo = procgame.dmd.AnimatedLayer()
        anim = procgame.dmd.Animation().load("./dmd/taf.dmd")
        self.taf_logo.frames = anim.frames
        
        gen = procgame.dmd.MarkupFrameGenerator()
        gen.font_plain = font_eurostile
        credits_frame = gen.frame_for_markup("""        
[HELLO]

[I am powered by Raspberry Pi,]
[P-ROC and Python!]

        """)
        
        self.credits_layer = procgame.dmd.PanningLayer(width=128, height=32, frame=credits_frame, origin=(0,0), translate=(0,1), bounce=False)
        self.credits_layer.composite_op = 'blacksrc'
    
    def attract_display(self):
        script = list()
        script.append({'seconds':5.0, 'layer':self.rpi_logo})
        script.append({'seconds':5.0, 'layer':self.taf_logo})
        script.append({'seconds':5.0, 'layer':self.game_over_layer})
        script.append({'seconds':5.0, 'layer':self.press_start})
        script.append({'seconds':17.0, 'layer':self.credits_layer})
        
        self.layer = procgame.dmd.ScriptedLayer(width=128, height=32, script=script)
        
        # Play a lamp show
        self.game.lampctrl.play_show('attract1', repeat=True)
    
    def mode_started(self):
        #self.game.lamps.startButton.schedule(schedule=0xffff0000, cycle_seconds=0, now=False)
        self.attract_display()
        self.game.lamps.gi01.enable()
        self.game.lamps.gi02.enable()
        self.game.lamps.gi03.enable()
        self.game.lamps.gi04.enable()
        self.game.lamps.gi05.enable()
        self.delay('stuck_ball_scanner', None, 2, self.scan_stuck_balls, None)
        self.close_bookcase()
        
    def mode_stopped(self):
        self.game.lamps.startButton.disable()
        
    def sw_startButton_active(self, sw):
        self.game.modes.remove(self)
        
        self.game.modes.add(PrepareToStart(game=self.game))
        
    def scan_stuck_balls(self):
        if self.game.switches.swampLockLower.is_active(): self.sw_swampLockLower_active_for_1s(None)
        if self.game.switches.lockupKickout.is_active(): self.sw_lockupKickout_active_for_1s(None)
        if self.game.switches.thingEject.is_active(): self.sw_thingEject_active_for_1s(None)
        if self.game.switches.thingKickout.is_active(): self.game.coils.thingKickout.pulse()
        
    def sw_thingEject_active_for_1s(self, sw):
        self.game.coils.thingEject.pulse()
    
    def sw_flipperLwR_active(self, sw):
        print "RIGHT FLIPPER"
        
    def sw_flipperLwL_active(self, sw):
        print "LEFT FLIPPER"
    def sw_swampLockLower_active_for_1s(self, sw):
        self.game.coils.swampRelease.pulse()
        
    def sw_lockupKickout_active_for_1s(self, sw):
        self.game.coils.lockupKickout.pulse()
        
    def open_bookcase(self):
        if self.game.switches.bookcaseOpen.is_active(): return;
        self.game.coils.bookcaseMotor.enable();
        self.delay(name='bookcase', 
                   event_type=None, 
                   delay=5,
                   handler=self.game.coils.bookcaseMotor.disable, 
                   param=None)
    
    def sw_bookcaseOpen_active(self, sw):
        print "bookCaseOpen"
        self.game.coils.bookcaseMotor.disable()
        self.cancel_delayed(name='bookcase')
    
    def sw_bookcaseClosed_active(self, sw):
        print "bookCaseClosed"
        self.game.coils.bookcaseMotor.disable()
        self.cancel_delayed(name='bookcase')
    
    def close_bookcase(self):
        if self.game.switches.bookcaseClosed.is_active(): return;
        self.game.coils.bookcaseMotor.enable();
        self.delay(name='bookcase', 
                   event_type=None, 
                   delay=5,
                   handler=self.game.coils.bookcaseMotor.disable, 
                   param=None)