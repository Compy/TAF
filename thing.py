'''
Created on Jul 9, 2012

@author: Compy
'''

import procgame.game
import procgame.dmd
from procgame.dmd import *

class Thing(procgame.game.Mode):
    """
    The thing mode runs when the bookcase is open and we want to pick any ball
    up that lands in thing's hideout.
    
    To do this we listen for a switch closed event (thingEject_active) and when that
    happens, we run the thing motor until the thingUp opto is open, then we
    activate the magnet to grab the ball and run the thing motor until the thingDown
    opto is open and turn of the magnet, releasing the ball underneath the playfield.
    """
    
    def __init__(self, game):
        super(Thing, self).__init__(game=game, priority=7)
        
    def sw_thingEject_active_for_500ms(self, sw):
        self.game.sound.stop('mainmusic')
        self.game.sound.play('thinglock')
        self.delay(name='thinglock', 
                   event_type=None, 
                   delay=9, 
                   handler=self.resume_play, 
                   param=None)
        # Run the thing motor to pick the ball up
        self.game.coils.thingMotor.enable()
        # Set an 'oh crap' timer to shut the motor off after 10 seconds
        # ... we should never get here, but this keeps the motor from running
        # forever if we have an opto out
        self.delay(name='thing',
                   event_type=None,
                   delay=10, 
                   handler=self.game.coils.thingMotor.disable,
                   param=None)
        
    def resume_play(self):
        self.game.sound.play('mainmusic')
        
    def sw_thingUpOpto_active(self, sw):
        # Turn on the magnet to grab the ball
        self.game.coils.thingMagnet.enable()
        
        # Set another backup timer to shut the magnet off after 10 seconds
        # to prevent things from running too long and blowing a fuse
        self.delay(name='thing_grab',
                   event_type=None,
                   delay=10,
                   handler=self.game.coils.thingMagnet.disable,
                   param=None)
        
    def sw_thingDownOpto_active(self, sw):
        # The hand is down, disable the motor
        self.game.coils.thingMotor.disable()
        
        # Also disable the magnet to drop the ball
        self.game.coils.thingMagnet.disable()
        
        # Cancel our backup delays since we successfully reached the end
        self.cancel_delayed('thing')
        self.cancel_delayed('thing_grab')