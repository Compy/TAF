'''
Created on Jul 9, 2012

@author: Compy
'''

import procgame.game

class Trough(procgame.game.Mode):
    """
    Manages all the balls in the trough at the bottom of the game.
    
    This class allows the rest of the game to determine when a ball has been lost by
    listening for switch events and counting the balls in the trough.
    
    If we currently have a ball in play and the trough suddenly becomes full, we know
    we've lost a ball.
    """
    
    # These are the trough switch names that we listen for open/closed events.
    # We must listen for switch events to be notified where the ball is on the playfield
    trough_switch_names = ['trough1','trough2','trough3']
    
    # This is a list of functions that catch/handle the switch events
    changed_handlers = None
    
    # This is a state tracker variable to keep track of the number of balls in the trough
    ball_count = 0
    
    def __init__(self, game):
        """
        Wire up our event changed handlers for all trough switches so we can be notified
        of when a ball enters the trough so we can count how many are in the trough,
        and thus, not on the playfield.
        """
        super(Trough, self).__init__(game=game, priority=2)
        self.changed_handlers = []
        
        # Wire up the switch events for both the 'open' and 'closed' states
        for name in self.trough_switch_names:
            for event_type in ['open','closed']:
                self.add_switch_handler(name=name, event_type=event_type, delay=None, handler=self._trough_switch_changed)
    
    def mode_started(self):
        """
        This is called when the mode itself is started. When the mode starts, count
        the balls in the trough, and if there is a ball in the outhole that hasn't been
        kicked into the trough, do it then.
        """
        self._update_ball_count()
        if self.game.switches.outhole.is_active():
            self.game.coils.outhole.pulse()
            
    def is_full(self):
        """
        Returns true if the trough is full (has all 3 balls in the trough)
        """
        return self.ball_count == self.game.num_balls_total
    
    def _update_ball_count(self):
        """
        Update the ball count by checking the switch states. If the new ball count
        returned by _count_balls() is different than what we currently have,
        fire an event to our listeners telling them that the trough state has changed.
        
        This is useful for other modes wanting to know when a ball is drained.
        """
        count = self._count_balls()
        if count != self.ball_count:
            self.ball_count = count
            self.game.log('Trough now has %d balls.' % (self.ball_count))
            for handler in self.changed_handlers[:]:
                handler()
                
    def _count_balls(self):
        """
        Count the balls in the trough by looping through all trough switches.
        
        If a trough switch is active, we know we have a ball sitting on the switch.
        """
        
        count = 0
        for name in self.trough_switch_names:
            if (self.game.switches[name].is_active()):
                count += 1
                
        return count
    
    def _trough_switch_changed(self, sw):
        """
        This code segment is fired each time a trough switch changes state. One thing we
        do is set a delay in case the pinballs are rattling around after being kicked into
        the trough. This allows us to cut down on the chances of processing a duplicate
        switch event and counting the balls wrong.
        """
        # Set a delay so that we give the trough time to settle if things rattle, etc
        timer_name = 'trough_switch_change_timer'
        self.cancel_delayed(name=timer_name)
        
        self.delay(name=timer_name,
                   event_type=None,
                   delay=0.2,
                   handler=self._trough_switch_change_timer_expired)
        
    def _trough_switch_change_timer_expired(self):
        """
        After the delay when a trough switch changes state, update the ball count
        so we get an accurate reading.
        """
        self._update_ball_count()
        
    def sw_outhole_active_for_500ms(self, sw):
        """
        Once the outhole (drain) switch is active for 500ms, kick the ball into the
        trough.
        """
        self.game.coils.outhole.pulse()