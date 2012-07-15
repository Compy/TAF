'''
Created on Jul 9, 2012

@author: Compy
'''

import procgame.game
import procgame.dmd
from procgame.dmd import *

class Greed(procgame.game.Mode):
    """
    The greed mode runs alongside the traditional playing mode so that the player
    can spell "GREED" by hitting the bookcase 5 times to open it.
    """
    
    def __init__(self, game):
        super(Greed, self).__init__(game=game, priority=8)
        
    def mode_started(self):
        self.greed_hits = 0
        self.game.lamps.greedG.disable()
        self.game.lamps.greedR.disable()
        self.game.lamps.greedE1.disable()
        self.game.lamps.greedE2.disable()
        self.game.lamps.greedD.disable()
    
    def mode_stopped(self):
        self.greed_hits = 0
        self.game.lamps.greedG.disable()
        self.game.lamps.greedR.disable()
        self.game.lamps.greedE1.disable()
        self.game.lamps.greedE2.disable()
        self.game.lamps.greedD.disable()
        self.game.lamps.vaultGreen.disable()
        self.game.lamps.thingGreen.disable()
        self.game.modes.remove(self.game.thing_mode)
        
    def sw_bookcase1_active(self, sw):
        self.bookcase_hit()
    
    def sw_bookcase2_active(self, sw):
        self.bookcase_hit()
    
    def sw_bookcase3_active(self, sw):
        self.bookcase_hit()
    
    def sw_bookcase4_active(self, sw):
        self.bookcase_hit()
    
    def bookcase_hit(self):
        if self.greed_hits >= 5: return
        self.game.sound.play('bookcaseslam')
        self.game.score(25000)
        self.game.coils.telephoneFlasher.schedule(0x00002222, 1, True)
        self.greed_hits += 1
        if self.greed_hits == 5:
            # Open the bookcase
            self.open_bookcase()
            self.game.modes.add(self.game.thing_mode)
            self.game.sound.play('openbookcase')
            self.game.lamps.vaultGreen.schedule(0x3f3f3f3f, 0, True)
            self.game.lamps.thingGreen.schedule(0x3f3f3f3f, 0, True)
            
        if (self.greed_hits > 0):
            self.game.lamps.greedG.enable()
        if (self.greed_hits > 1):
            self.game.lamps.greedR.enable()
        if (self.greed_hits > 2):
            self.game.lamps.greedE1.enable()
        if (self.greed_hits > 3):
            self.game.lamps.greedE2.enable()
        if (self.greed_hits > 4):
            self.game.lamps.greedD.enable()
                
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