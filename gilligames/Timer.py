import time
import multiprocessing

class Timer(object):    
    def __init__(self, timeSeconds):
        self.startTime = 0               # Time used for starting time.
        self.timeSeconds = timeSeconds  # Duration of timer.
        self.start(timeSeconds)          # Start the timer immediately.
        
    ###########################################################################################
        
    # Called on creation and reset.
    def start(self, timeSeconds):
        self.startTime = Timer.time()
        self.timeSeconds = timeSeconds

    ###########################################################################################

    # Called on creation and reset.
    def startWithCallback(self, timeSeconds, expired_callback):
        self.startTime = Timer.time()
        self.timeSeconds = timeSeconds
        p = multiprocessing.Process(target=self.waitForExpire, args=(timeSeconds, expired_callback))
        p.start()

    def waitForExpire(self, timeSeconds, expired_callback):
        sleep(timeSeconds)
        expired_callback()

    ###########################################################################################
        
    # Restarts the timer for the same amount of time.
    def reset(self):
        self.start(self.timeSeconds)
    
    ###########################################################################################
        
    # Returns the amount of time (in seconds) that has elapsed since starting the timer.
    def timeElapsed(self):
        return Timer.time() - self.startTime
    
    ###########################################################################################

    # Returns 0.0-1.0, where 0.0 is no time elapsed and 1.0 if all time elapsed.
    def timeElapsed_normalized(self):
        return min(1.0, self.timeElapsed() / self.timeSeconds)

    ###########################################################################################
    
    # Returns the amount of time (in seconds) remaining on the timer before it expires.
    def timeRemaining(self):
        time_left = self.timeSeconds - self.timeElapsed()
        return 0.0 if time_left < 0.0 else time_left

    ###########################################################################################
    
    # Returns the amount of time (in seconds) remaining on the timer before it expires.
    def timeRemaining_normalized(self):
        return self.timeRemaining() / self.timeSeconds

    ###########################################################################################
    
    # Add some seconds from the time remaining.
    def addSeconds(self, time_diff):
        self.timeSeconds += time_diff

    ###########################################################################################
        
    # Remove some seconds from the time remaining.
    def removeSeconds(self, time_diff):
        self.timeSeconds -= time_diff

    ###########################################################################################
        
    def forceExpire(self):
        self.startTime = Timer.time() - self.timeSeconds
    
    ###########################################################################################
    
    # Is the timer expired and ready to do something?
    def isExpired(self):
        return self.timeRemaining() <= 0
    
    ###########################################################################################
    
    # A simple wrapper for time.time() so classes that use this don't also need to import time.
    @staticmethod
    def time():
        return time.time()
