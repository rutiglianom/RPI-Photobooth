# Matthew Rutigliano
# November 6th, 2019
# Photo Booth
# Description: When button is pressed, rpi takes four photos with a delay between them.
# Time between photos is counted on 4-digit seven segment display. Border of color
# and thickness is placed around photos, with an SU logo in the bottom right corner. Photo
# is then posted to twitter.
# Circuit uses MUX and 7-segment LED driver to drive 4-digit display
# Photos at twitter.com/HungryRedMenace

import sys
import os
import time
import RPi.GPIO as GPIO
from picamera import PiCamera, Color
from PIL import Image
from twython import Twython 

# Constants
X_RES = 500
Y_RES = 500
CAM_ROT = 180

LOGO_SIZE = 100

NUM_PICS = 4
COUNT_TIME = 3

BORDER_WIDTH = 25
BORDER_COLOR = 'red'

LOGO_PIC = 'SUinterlock.png'

X_LENGTH = X_RES * NUM_PICS + BORDER_WIDTH * 2
Y_LENGTH = Y_RES + BORDER_WIDTH * 2

TWEET = True
CAPTION = "Livin' it up in the Bannan labs"

# Initialize Camera
camera = PiCamera()
camera.rotation = CAM_ROT
camera.resolution = (X_RES, Y_RES)

SEL_A = 16
SEL_B = 20
DEC_A = 5
DEC_B = 6
DEC_C = 13
DEC_D = 19
BUT = 12

# Setup GPIO
GPIO.setwarnings(False) # Ignore warnings
GPIO.setmode(GPIO.BCM) # Use BCM Pin numbering
GPIO.setup(SEL_A, GPIO.OUT, initial=GPIO.LOW) # Set Pin 4 to be an output pin and set initial value to low (off)
GPIO.setup(SEL_B, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(DEC_A, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(DEC_B, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(DEC_C, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(DEC_D, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(BUT, GPIO.IN)

def binbits(x, n):
    # Return binary representation of x with at least n bits
    # Source: 
    # https://stackoverflow.com/questions/13676183/python-choose-number-of-bits-to-represent-binary-number
    bits = bin(x).split('b')[1]

    if len(bits) < n:
        return '0b' + '0' * (n - len(bits)) + bits
    else:
        return '0b' + bits

def ledSelect(num):
    binNum = binbits(num, 2)
    GPIO.output(SEL_A, bool(int(binNum[3])))
    GPIO.output(SEL_B, bool(int(binNum[2])))

def ledShow(num):
    binNum = binbits(num, 4)
    GPIO.output(DEC_A, bool(int(binNum[5])))
    GPIO.output(DEC_B, bool(int(binNum[4])))
    GPIO.output(DEC_C, bool(int(binNum[3])))
    GPIO.output(DEC_D, bool(int(binNum[2])))
    
def ledDigits(digits):
    for i in range(4):
        ledSelect(i)
        ledShow(int(digits[i]))
        time.sleep(.001)
        
def button_callback(channel):
    global X_LENGTH
    global Y_LENGTH
    global NUM_PICS
    global X_RES
    global Y_RES
    global COUNT_TIME
    global BORDER_WIDTH
    global LOGO_PIC
    global LOGO_SIZE
    global camera
    global TWEET
    global CAPTION
    
    # Twitter Stuff
    C_key = "itM0X4JiDVHzd8aSI2cFOQbSn" 
    C_secret = "5q53Zhk33AtOq2Dv0gIue05KrRlK5QBKQ0nhlm7w72ShiQnnWo" 
    A_token = "1191470994994515968-f2z1yGfI3LuJFy1w3hwT5Qff9tM2SS" 
    A_secret = "UyUxWpHZSgjj2EcKkxNUFW7tGqmHnkj7wOSSXYxrFzJTj"
    
    # Create Composite image of four photos with border
    newImage = Image.new('RGB', (X_LENGTH, Y_LENGTH), BORDER_COLOR)
    camera.start_preview()
    for i in range(0, X_RES * NUM_PICS, X_RES):
        ledSelect(3)
        # Time Delay
        for j in range(COUNT_TIME):
            ledShow(COUNT_TIME - j - 1)
            time.sleep(1)
        camera.capture('tempPhoto.jpg')
        capturedImage = Image.open('tempPhoto.jpg')
        newImage.paste(capturedImage, (i + BORDER_WIDTH, BORDER_WIDTH))
    camera.stop_preview()

    # Overlay SU Logo
    suLogo = Image.open(LOGO_PIC)
    suLogo = suLogo.resize( (LOGO_SIZE, LOGO_SIZE), Image.ANTIALIAS)
    newImage.paste(suLogo, (X_LENGTH - LOGO_SIZE, Y_LENGTH - LOGO_SIZE), suLogo)

    # Save final image
    newImage.save('photoStrip.jpg')
    
    # Send Tweet
    if (TWEET):
        myTweet = Twython(C_key,C_secret,A_token,A_secret)
        photo = open('photoStrip.jpg', 'rb') 
        response = myTweet.upload_media(media=photo)
        myTweet.update_status(status=CAPTION, media_ids=[response['media_id']])
    
    # Delete placeholder images
    os.remove('tempPhoto.jpg')
    os.remove('photoStrip.jpg')
    
# GPIO Event Detector    
GPIO.add_event_detect(BUT, GPIO.FALLING, callback=button_callback, bouncetime=500)

# Main
try:
    while(1):
        # Wait
        time.sleep(1)
    
except KeyboardInterrupt: 
    # This code runs on a Keyboard Interrupt <CNTRL>+C
    print('\n\n' + 'Program exited on a Keyboard Interrupt' + '\n') 

except: 
    # This code runs on any error
    print('\n' + 'Errors occurred causing your program to exit' + '\n')

finally: 
    # This code runs on every exit and sets any used GPIO pins to input mode.
    GPIO.cleanup()
    
   