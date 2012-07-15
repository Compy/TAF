'''
Created on Jul 9, 2012

@author: Compy
'''

import procgame
import procgame.game
import procgame.dmd
from procgame import *

import pygame
from pygame import mixer

import pinproc
import trough
import attract
import greed
import thing

import logging
logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

import locale
locale.setlocale(locale.LC_ALL, "") # This is used to put commas in the score

dmd_path = "dmd/"
sound_path = "sound/"
music_path = "music/"
font_tiny7 = procgame.dmd.font_named("04B-03-7px.dmd")
font_jazz18 = procgame.dmd.font_named("Jazz18-18px.dmd")

class BaseGameMode(procgame.game.Mode):
    """
    This mode runs whenever the game is actually in progress.
    We use it to play music and flash lights while the ball is being
    knocked around.
    """
    def __init__(self, game):
        super(BaseGameMode, self).__init__(game=game, priority=1)
        pass
    
    def mode_started(self):
        self.ball_launched = False
        self.game.sound.play('prelaunch',1)
        self.game.trough.changed_handlers.append(self.trough_changed)
        
    def mode_stopped(self):
        self.game.sound.stop('prelaunch')
        self.game.sound.stop('mainmusic')
        self.game.trough.changed_handlers.remove(self.trough_changed)
        
    def trough_changed(self):
        if self.game.trough.is_full():
            print "Trough full, ball ended"
            self.game.end_ball()
            
    def sw_ballShooter_open_for_50ms(self, sw):
        print "Shooterlane open"
        self.game.coils.swampFlasher.schedule(0x33333333, 1, True)
        self.game.sound.play('launch')
        
    def sw_ballShooter_open_for_2s(self, sw):
        if not self.ball_launched:
            self.game.sound.stop('prelaunch')
            self.game.sound.play('mainmusic', 1)
            self.ball_launched = True
            
    def sw_rightRampExit_active(self, sw):
        self.game.coils.swampFlasher.pulse(80)
        
    def sw_swampLockUpper_closed(self, sw):
        if not self.ball_launched:
            self.game.sound.stop('prelaunch')
            self.game.sound.play('mainmusic', 1)
            self.ball_launched = True
        self.game.score(1000)
        
    def sw_jet1_closed(self, sw):
        self.game.sound.play('bumper')
        self.game.score(700)
    
    def sw_jet2_closed(self, sw):
        self.game.sound.play('bumper')
        self.game.score(700)
    
    def sw_jet3_closed(self, sw):
        self.game.sound.play('bumper')
        self.game.score(700)
    
    def sw_jet4_closed(self, sw):
        self.game.sound.play('bumper')
        self.game.score(700)
    
    def sw_jet5_closed(self, sw):
        self.game.sound.play('bumper')
        self.game.score(700)
        
    def sw_thingEject_active_for_1s(self, sw):
        # If thing mode is active, don't fire this
        # so the hand can grab the ball
        if self.game.thing_mode.is_started():
            return
        self.game.sound.play('thingkickout')
        self.game.coils.thingEject.pulse()
        
    def sw_thingKickout_active_for_500ms(self, sw):
        self.game.coils.thingKickout.pulse()
    
    def sw_swampLockLower_active_for_1s(self, sw):
        self.game.sound.play('primevalooze')
        self.game.coils.swampRelease.pulse()
        
    def sw_lockupKickout_active_for_1s(self, sw):
        self.game.coils.swampFlasher.schedule(0x00002222, 1, True)
        self.game.coils.lockupKickout.pulse()
        self.game.sound.play('swampeject')
        
    def sw_chairKickout_active_for_500ms(self, sw):
        self.game.coils.miniFlipperFlasher.schedule(0x00002222, 1, True)
        self.game.sound.play('chaireject')
        self.game.coils.chairKickout.pulse()
        self.game.score(5000)
        
    def sw_rightRampEnter_active(self, sw):
        self.game.sound.play('beargrowl');
        
    def sw_rightRampTop_active(self, sw):
        self.game.sound.play('bearkick')
        self.game.score(50000)
        
    def sw_leftRampTop_active(self, sw):
        self.game.coils.trainFlasher.pulse(60)
        
    def sw_upperLeftLoop_active(self, sw):
        self.game.coils.trainFlasher.schedule(0x00002222, 1, True)
        self.game.coils.jetBumperFlasher.schedule(0x00220022, 1, True)
        self.game.coils.telephoneFlasher.schedule(0x22220000, 1, True)
        self.game.coils.swampFlasher.schedule(0x02020202, 1, True)
        self.game.coils.thePowerBackboxFlasher.schedule(0x00002222, 1, True)
        self.game.sound.play('throughgraveyard')
        self.game.score(10000)
        
    def sw_slingL_active(self, sw):
        self.game.sound.play('bumper')
        self.game.score(1000)
        
    def sw_slingR_active(self, sw):
        self.game.sound.play('bumper')
        self.game.score(1000)
        
    def sw_rightInlane_active(self, sw):
        self.game.sound.play('inlane')
        self.game.score(500)
        
    def sw_leftInlane_active(self, sw):
        self.game.sound.play('inlane')
        self.game.score(500)
    
    def sw_leftInlane2_active(self, sw):
        self.game.sound.play('inlane')
        self.game.score(500)
        
    def sw_rightOutlane_active(self, sw):
        self.game.sound.play('drain')
        self.game.score(1000)
        
    def sw_leftOutlane_active(self, sw):
        self.game.sound.play('drain')
        self.game.score(1000)
        
    def sw_trainWreck_active(self, sw):
        self.game.coils.trainFlasher.schedule(0x00002222, 1, True)
        self.game.sound.play('train')
        self.game.score(100000)
        
    def sw_leftRampEnter_active(self, sw):
        self.game.coils.rampDiverter.enable()
        self.delay('diverter_close', None, 3, self.game.coils.rampDiverter.disable, None)
        
    def sw_bumperLaneOpto_active(self, sw):
        self.delay('auto_flip', None, 0.25, self.game.coils.flipperUpLMain.pulse, 90)
        self.game.coils.miniFlipperFlasher.schedule(0x22222222, 2, True)
        
    def sw_graveG_active(self, sw):
        self.generalTargetHit()
        
    def sw_graveR_active(self, sw):
        self.generalTargetHit()
    
    def sw_graveA_active(self, sw):
        self.generalTargetHit()
        
    def sw_cousinIt_active(self, sw):
        self.generalTargetHit()
        
    def sw_lowerSwampMillion_active(self, sw):
        self.generalTargetHit()
        
    def sw_centerSwampMillion_active(self, sw):
        self.generalTargetHit()
        
    def sw_upperSwampMillion_active(self, sw):
        self.generalTargetHit()
        
    def generalTargetHit(self):
        self.game.sound.play('target')
        self.game.score(1000)
        
class TAFGame(procgame.game.BasicGame):
    trough = None
    base_game_mode = None
    attract_mode = None
    greed_mode = None
    thing_mode = None
    
    def __init__(self):
        pygame.mixer.pre_init(44100,-16,2,512)
        super(TAFGame, self).__init__(pinproc.MachineTypeWPC)
        self.load_config('taf.yml')
        self.trough = trough.Trough(game=self)
        self.base_game_mode = BaseGameMode(game=self)
        self.attract_mode = attract.Attract(game=self)
        self.sound = procgame.sound.SoundController(self)
        self.greed_mode = greed.Greed(self)
        self.thing_mode = thing.Thing(self)
        self.lampctrl = procgame.lamps.LampController(self)
        self.lampctrl.register_show('attract1', "lampshows/attract.txt")
        
        print pygame.mixer.get_init()
        
        self.lampctrl = procgame.lamps.LampController(self)
        self.setup()
        
        self.reset()
        
    def setup(self):
        self.sound.register_sound('prelaunch', music_path+"prelaunch.wav")
        self.sound.register_sound('mainmusic', music_path+"mainmusic.ogg")
        self.sound.register_sound('skillshot', music_path+"skillshot.ogg")
        self.sound.register_sound('thinglock', music_path+"thinglock.wav")
        self.sound.register_sound('mansionaward', music_path+"mansionaward.wav")
        
        self.sound.register_sound('beargrowl', sound_path + 'beargrowl.ogg')
        self.sound.register_sound('bearkick', sound_path + 'bearkick.ogg')
        self.sound.register_sound('bumper', sound_path + 'bumper1.ogg')
        self.sound.register_sound('bumper', sound_path + 'bumper2.ogg')
        self.sound.register_sound('bumper', sound_path + 'bumper3.ogg')
        self.sound.register_sound('bumper', sound_path + 'bumper4.ogg')
        self.sound.register_sound('drain', sound_path + 'drain1.ogg')
        self.sound.register_sound('drain', sound_path + 'drain2.ogg')
        self.sound.register_sound('inlane', sound_path + 'inlane1.ogg')
        self.sound.register_sound('inlane', sound_path + 'inlane2.ogg')
        self.sound.register_sound('inlane', sound_path + 'inlane3.ogg')
        self.sound.register_sound('launch', sound_path + 'launch.ogg')
        self.sound.register_sound('openbookcase', sound_path + 'openbookcase.ogg')
        self.sound.register_sound('primevalooze', sound_path + 'primevalooze.ogg')
        self.sound.register_sound('swamp', sound_path + 'swamp.ogg')
        self.sound.register_sound('swamp', sound_path + 'swamp2.ogg')
        self.sound.register_sound('thingkickout', sound_path + 'thingkickout.ogg')
        self.sound.register_sound('thingramp', sound_path + 'thingramp.ogg')
        self.sound.register_sound('this_is_lunacy', sound_path + 'this_is_lunacy.ogg')
        self.sound.register_sound('throughgraveyard', sound_path + 'throughgraveyard.ogg')
        self.sound.register_sound('chaireject', sound_path + 'chaireject.wav')
        self.sound.register_sound('swampeject', sound_path + 'swampeject.wav')
        self.sound.register_sound('target', sound_path + 'target.wav')
        self.sound.register_sound('bookcaseslam', sound_path + 'bookcaseslam.wav')
        self.sound.register_sound('it', sound_path + 'it1.ogg')
        self.sound.register_sound('it', sound_path + 'it2.ogg')
        self.sound.register_sound('it', sound_path + 'it3.ogg')
        self.sound.register_sound('it', sound_path + 'it4.ogg')
        self.sound.register_sound('it', sound_path + 'it5.ogg')
        self.sound.register_sound('train', sound_path + 'train_whistle.wav')
        self.sound.register_sound('welcome', sound_path + 'welcome.ogg')
        
    def reset(self):
        super(TAFGame, self).reset();
        self.modes.add(self.trough)
        self.modes.add(self.attract_mode)
        
    def start_ball(self):
        super(TAFGame, self).start_ball()
        
    def game_started(self):
        self.log("GAME STARTED")
        super(TAFGame, self).game_started()
        self.lampctrl.stop_show()
        self.sound.play('welcome')
        self.modes.add(self.greed_mode)
        
    def ball_starting(self):
        self.log("BALL STARTING")
        super(TAFGame, self).ball_starting()
        
        #Kick a ball into the shooter lane
        self.coils.trough.pulse()
        
        # Turn the flippers on
        self.enable_flippers(True)
        
        # Start the base game mode
        self.modes.add(self.base_game_mode)
        
    def ball_ended(self):
        """
        This is called by end_ball(), which is called by the trough_changed handler
        when the trough state changes
        """
        self.log("BALL ENDED")
        
        self.modes.remove(self.base_game_mode)
        self.enable_flippers(False)
        super(TAFGame, self).ball_ended()
        
    def game_ended(self):
        self.log("GAME ENDED")
        super(TAFGame, self).game_ended()
        self.modes.remove(self.base_game_mode)
        self.modes.remove(self.greed_mode)
        self.modes.add(self.attract_mode)
        
    def set_status(self,text):
        self.dmd.set_message(text,3)
        
def main():
    game = None
    try:
        game = TAFGame()
        game.run_loop()
    finally:
        del game
        
if __name__ == '__main__':
    main()