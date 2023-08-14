#!/usr/bin/python3

import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
from omxplayer.player import OMXPlayer
from time import sleep
from gilligames.Timer import Timer
from gilligames.UIImages import UIImages
from tkinter import *
import pygame as pg
import os

########################################################################################
    
def loadPgSound(name):
    class NoneSound:
        def play(self):
            pass

    if not pg.mixer or not pg.mixer.get_init():
        return NoneSound()

    global appPath

    sound = pg.mixer.Sound("{}/{}".format(appPath, name))

    return sound

################################################################################################

def createPlayer(filePath, layer):
    global screenWidth
    global screenHeight
    
    dbusName = "org.mpris.MediaPlayer2.omxplayer{}".format(layer)
    videoArgs = "--win 0,0,{},{} -o hdmi --layer {}".format(screenWidth, screenHeight, layer)
        
    player = OMXPlayer(
        filePath,
        args=videoArgs,
        dbus_name=dbusName
    )
    player.exitEvent += videoExited
    return player

################################################################################################

def videoExited(player, event):
    global leftPlayer
    global rightPlayer
    global currentVideoPlayer
    
    # Turn the LED's back on when ready to press again.
    GPIO.output(LEFT_LED, 1)
    GPIO.output(RIGHT_LED, 1)
        
    currentVideoPlayer = None
    
################################################################################################

# When a buzzer video is playing, flash the LED of the side that matches.
def flashLED():
    global leftPlayer
    global rightPlayer
    global isFlashOn
    
    if (not flashingLedTimer.isExpired()):
        return
    
    if (currentVideoPlayer == leftPlayer):
        GPIO.output(LEFT_LED, isFlashOn)
    else:
        GPIO.output(RIGHT_LED, isFlashOn)
        
    isFlashOn = not isFlashOn
    flashingLedTimer.reset()
        
################################################################################################

def checkForInput():
    global nextTieWinnerLeft
    global currentVideoPlayer
    global doPlayLeftVideo
    global doPlayRightVideo
    global videoTimer
    global isFlashOn
    
    if (doPlayLeftVideo):
        currentVideoPlayer = playLeftVideo()
    if (doPlayRightVideo):
        currentVideoPlayer = playRightVideo()
    
    if (videoTimer != None and videoTimer.isExpired()):
        # After a video has played for a short bit, reset the background.
        videoTimer = None
        setBackground("buzzer_background_{}x{}.png".format(screenWidth, screenHeight))
    
    if (currentVideoPlayer == None):
        isLeftPressed = not GPIO.input(LEFT_BUTTON_PIN)
        isRightPressed = not GPIO.input(RIGHT_BUTTON_PIN)

        if (isLeftPressed or isRightPressed):
            GPIO.output(LEFT_LED, 0)
            GPIO.output(RIGHT_LED, 0)
            isFlashOn = True
            
            if (isLeftPressed and isRightPressed):
                # Both pressed at the same time, so we need to choose one to be the winner.
                if (nextTieWinnerLeft):
                    isRightPressed = False
                else:
                    isLeftPressed = False
                # Now alternate who wins the next tie.
                nextTieWinnerLeft = not nextTieWinnerLeft
            
            if (isLeftPressed):
                setBackground("buzzer_left_still_{}x{}.png".format(screenWidth, screenHeight))
                doPlayLeftVideo = True
                buzzerSound.play()
            elif (isRightPressed):
                setBackground("buzzer_right_still_{}x{}.png".format(screenWidth, screenHeight))
                doPlayRightVideo = True
                buzzerSound.play()
    else:
        flashLED()
                
    win.after(1, checkForInput)

################################################################################################

def keyPressed(event):
    if (event.keysym == "Escape"):
        cleanup()
        
################################################################################################

def cleanup():
    if (leftPlayer != None):
        leftPlayer.quit()
    if (rightPlayer != None):
        rightPlayer.quit()
    pg.quit()
    GPIO.output(17, 0)
    GPIO.cleanup()
    win.destroy()
    
################################################################################################

def playLeftVideo():
    global leftPlayer
    global doPlayLeftVideo
    global videoTimer
    
    videoTimer = Timer(1)
    
    doPlayLeftVideo = False
    
    if (leftPlayer == None):
        leftPlayer = createPlayer(leftVideoPath, 1)
    else:
        leftPlayer.load(leftVideoPath)
        
    return leftPlayer

################################################################################################

def playRightVideo():
    global rightPlayer
    global doPlayRightVideo
    global videoTimer
    
    videoTimer = Timer(1)

    doPlayRightVideo = False
        
    if (rightPlayer == None):
        rightPlayer = createPlayer(rightVideoPath, 2)
    else:
        rightPlayer.load(rightVideoPath)
        
    return rightPlayer

################################################################################################

def setBackground(path):
    global mainCanvas
    global background

    mainCanvas.itemconfig(background, image=UIImages.get(path))

################################################################################################

LEFT_BUTTON_PIN = 13
LEFT_LED = 17
RIGHT_BUTTON_PIN = 27
RIGHT_LED = 19

flashingLedTimer = Timer(0.1)
isFlashOn = True

win = Tk()
win.title("Buzzer")
win.attributes("-fullscreen", True)
win.configure(bg="black", cursor="none")  # hide the mouse pointer over the window
win.bind("<KeyPress>", keyPressed)

screenWidth = win.winfo_screenwidth()
screenHeight = win.winfo_screenheight()

print("Screen size: {}x{}".format(screenWidth, screenHeight))

# Create the canvas to hold the background image.
mainCanvas = Canvas(win, width=screenWidth, height=screenHeight, highlightthickness=0)
background = mainCanvas.create_image(0, 0, anchor=NW, image=UIImages.get("buzzer_background_{}x{}.png".format(screenWidth, screenHeight)))
mainCanvas.pack(fill="both", expand=True)

leftVideoPath = "./av/buzzer_left.mov"
rightVideoPath = "./av/buzzer_right.mov"

leftPlayer = None
rightPlayer = None
currentVideoPlayer = None

videoTimer = None

# Use these to defer starting videos to the next loop iteration, so the background image can be updated ASAP,
# to avoid the noticeable delay in starting the video. The background image appears quicker.
doPlayLeftVideo = False
doPlayRightVideo = False

# Use pygame for playing standalone sounds, because it's more responsive than omxplayer.
# However, to use pygame sounds, we need to create a pygame window, even if it's positioned offscreen.
pg.init()
pg.display.set_mode((1,1), pg.HIDDEN)

# Set the app path for loading sound using pygame.
appPath = os.path.split(os.path.abspath(__file__))[0]

# Pre-load the buzzer sound so it can play ASAP when a button is pressed, instead of lagging from video loading.
# In order to force pygame sounds to use HDMI instead of the headphone jack, set it in the audio options when running "sudo raspi-config" from command line.
buzzerSound = loadPgSound("av/buzzer.wav")

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BCM)
GPIO.setup(LEFT_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(RIGHT_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.setup(LEFT_LED, GPIO.OUT)
GPIO.setup(RIGHT_LED, GPIO.OUT)

nextTieWinnerLeft = True

GPIO.output(LEFT_LED, 1)
GPIO.output(RIGHT_LED, 1)

# Do other stuff every frame.
win.after(1, checkForInput)

try:
    win.mainloop()

except KeyboardInterrupt:
    cleanup()
