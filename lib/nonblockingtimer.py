from time import ticks_ms

class NonBlockingTimer:
   def __init__(self, delay_period_ms):
       """
       delay_period_ms is milliseconds delay between
       each function call
       """
       self.start_time = ticks_ms()
       self.delay_period_ms = delay_period_ms

   def non_blocking_timer(self, func):
       """Takes func reference as argument"""
       if ticks_ms() - self.start_time > self.delay_period_ms:
           func()
           self.start_time = ticks_ms()