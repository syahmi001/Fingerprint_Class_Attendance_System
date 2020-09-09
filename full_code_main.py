import time
import RPi.GPIO as GPIO
from pyfingerprint.pyfingerprint import PyFingerprint
from firebase import firebase
import datetime
import json
import hashlib

#setting up link with FireBase
firebase = firebase.FirebaseApplication('https://attendance-36688.firebaseio.com', None)

#define pins gpio for push buttons
but1=19
but2=2
but3=3
but4=26
but5=4
but6=17

HIGH=1
LOW=0


# Define GPIO to LCD mapping
LCD_RS = 7
LCD_E  = 8
LCD_D4 = 25
LCD_D5 = 24
LCD_D6 = 23
LCD_D7 = 18
 
# Define some device constants
LCD_WIDTH = 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False
 
LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
 
# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

#LCD as output
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
GPIO.setup(LCD_E, GPIO.OUT)  # E
GPIO.setup(LCD_RS, GPIO.OUT) # RS
GPIO.setup(LCD_D4, GPIO.OUT) # DB4
GPIO.setup(LCD_D5, GPIO.OUT) # DB5
GPIO.setup(LCD_D6, GPIO.OUT) # DB6
GPIO.setup(LCD_D7, GPIO.OUT) # DB7

#push buttons as input
GPIO.setup(but1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(but2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(but3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(but4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(but5, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(but6, GPIO.IN, pull_up_down=GPIO.PUD_UP)


## Tries to initialize the sensor
try:
    f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

    if ( f.verifyPassword() == False ):
        raise ValueError('The given fingerprint sensor password is wrong!')

except Exception as e:
    print('The fingerprint sensor could not be initialized!')
    print('Exception message: ' + str(e))
    exit(1)

#function to insert/register new finger
def enrollFinger():
    try:
        print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))
        lcd_string("Used space:",LCD_LINE_1)
        lcd_string(str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()),LCD_LINE_2)
        time.sleep(2) # 2 second delay
    
        name=raw_input("Enter Name: ")
        matric=raw_input("Enter Matric No: ")   
        #result= firebase.put('/class/C/', positionNumber, str(name))
        #firebase.put('/class/C/', positionNumber, current_time)
        #print (result)
        print('Waiting for finger...')
        lcd_string("Waiting for",LCD_LINE_1)
        lcd_string("finger",LCD_LINE_2)
    

        ## Wait that finger is read
        while ( f.readImage() == False ):
            pass

        ## Converts read image to characteristics and stores it in charbuffer 1
        f.convertImage(0x01)

        ## Checks if finger is already enrolled
        result = f.searchTemplate()
        positionNumber = result[0]

        if ( positionNumber >= 0 ):
            print('Template already exists at position #' + str(positionNumber))
            lcd_string("Finger already",LCD_LINE_1)
            lcd_string("exists!",LCD_LINE_2)
            return
    
        print('Remove finger...')
        lcd_string("Remove",LCD_LINE_1)
        lcd_string("finger...",LCD_LINE_2)
        time.sleep(2)

        print('Waiting for same finger again...')
        lcd_string("Waiting for",LCD_LINE_1)
        lcd_string("same finger",LCD_LINE_2)

        ## Wait that finger is read again
        while ( f.readImage() == False ):
            pass

        ## Converts read image to characteristics and stores it in charbuffer 2
        f.convertImage(0x02)

        ## Compares the charbuffers
        if ( f.compareCharacteristics() == 0 ):
            raise Exception('Fingers do not match')
            lcd_string("Not same",LCD_LINE_1)
            lcd_string("finger",LCD_LINE_2)

        ## Creates a template
        f.createTemplate()


        ## Saves template at new position number
        positionNumber = f.storeTemplate()
        print('Finger enrolled successfully!')
        print('New template position #' + str(positionNumber))
        lcd_string("Success",LCD_LINE_1)
        lcd_string("register on"+str(positionNumber),LCD_LINE_2)
        time.sleep(2)
        firebase.put('/class',str(positionNumber), {"Name": str(name), "Matric": str(matric)})

    except Exception as e:
        print('Operation failed!')
        print('Exception message: ' + str(e))
        return


#function to find match fingers based on the stored finger
def searchFinger():
    try:
        t =  time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        date = datetime.date.today()
        print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))
        lcd_string("Used space:",LCD_LINE_1)
        lcd_string(str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()),LCD_LINE_2)
        time.sleep(2) # 2 second delay

        print('Waiting for finger...')
        lcd_string("Waiting for",LCD_LINE_1)
        lcd_string("finger",LCD_LINE_2)

        ## Wait that finger is read
        while ( f.readImage() == False ):
            pass

        ## Converts read image to characteristics and stores it in charbuffer 1
        f.convertImage(0x01)

        ## Searchs template
        result = f.searchTemplate()

        positionNumber = result[0]
        accuracyScore = result[1]

        if ( positionNumber == -1 ):
            print('No match found!')
            lcd_string("No match",LCD_LINE_1)
            lcd_string("found!",LCD_LINE_2)
            return
        else:
            print('Found template at position #' + str(positionNumber))
            print('The accuracy score is: ' + str(accuracyScore))

            lcd_string("Found finger",LCD_LINE_1)
            lcd_string("at pos#"+ str(positionNumber),LCD_LINE_2)
            name=firebase.get('/class', positionNumber)
            firebase.put(str(date), str(current_time), name)
            counter=firebase.get('/attendance', positionNumber)+1
            firebase.put('/attendance',positionNumber, counter)

        

        ## OPTIONAL stuff
        ##
        ## Loads the found template to charbuffer 1
        f.loadTemplate(positionNumber, 0x01)

        ## Downloads the characteristics of template loaded in charbuffer 1
        characterics = str(f.downloadCharacteristics(0x01)).encode('utf-8')

        ## Hashes characteristics of template
        print('SHA-2 hash of template: ' + hashlib.sha256(characterics).hexdigest())

    except Exception as e:
        print('Operation failed!')
        print('Exception message: ' + str(e))
        return 


def deleteFinger():
    try:
        positionNumber = 0
        count=0
        lcd_string("Delete finger",LCD_LINE_1)
        lcd_string("Position: "+str(count),LCD_LINE_2)

        while GPIO.input(but5)==True:
            if GPIO.input(but1)==False:
                count=count+1
                if count>1000:
                    count=1000
                lcd_string("Position: "+str(count),LCD_LINE_2)
                time.sleep(0.2)
            
            elif GPIO.input(but4)==False:
                count=count-1
                if count<0:
                    count=0
                lcd_string("Position: "+str(count),LCD_LINE_2)
                time.sleep(0.2)
        positionNumber=count

        if (f.deleteTemplate(positionNumber) == True ):
            print('Template deleted!')
            lcd_string("Fingerprint",LCD_LINE_1)
            lcd_string("deleted!",LCD_LINE_2)
            time.sleep(2)
        

    except Exception as e:
        print('Operation failed!')
        print('Exception message: ' + str(e))
        return



###############################################################################    
def main():
  # Main program block
  # Initialise display
  lcd_init()
 
  while True:

    #defining time and date
    t =  time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    print(current_time)
    date = datetime.date.today()
    print(date)
      
    #lcd_string("   WELCOME TO",LCD_LINE_1)
    #lcd_string("  FINGERPRINT",LCD_LINE_2)
    #time.sleep(2) # 3 second delay
      
    lcd_string("   ATTENDANCE",LCD_LINE_1)
    lcd_string("     SYSTEM",LCD_LINE_2)
    time.sleep(2) # 3 second delay
    
    lcd_string("   "+str(date),LCD_LINE_1)
    lcd_string("    "+str(current_time),LCD_LINE_2)
    time.sleep(2) # 3 second delay

    #GPIO.add_event_detect(but2, GPIO.FALLING)
    #GPIO.add_event_callback(but2,searchFinger)

    #GPIO.add_event_detect(but3, GPIO.FALLING)
    #GPIO.add_event_callback(but3,enrollFinger)

    #GPIO.add_event_detect(but6, GPIO.FALLING)
    #GPIO.add_event_callback(but6,deleteFinger)
    

    #if GPIO.input(but1) ==0:
        #lcd_string("Button 1",LCD_LINE_1)
        #lcd_string("is pressed",LCD_LINE_2)
        #time.sleep(3) # 3 second delay

    if GPIO.input(but2) ==0:
        searchFinger()
        time.sleep(2) # 2 second delay
        
    if GPIO.input(but3) ==0:
        enrollFinger()
        time.sleep(2) # 2 second delay

    #if GPIO.input(but4) ==0:
        #lcd_string("Button 4",LCD_LINE_1)
        #lcd_string("is pressed",LCD_LINE_2)
        #time.sleep(3) # 3 second delay

    #if GPIO.input(but5) ==0:
        #lcd_string("Button 5",LCD_LINE_1)
        #lcd_string("is pressed",LCD_LINE_2)
        #time.sleep(3) # 3 second delay

    if GPIO.input(but6) ==0:
        deleteFinger()
        time.sleep(2) # 2 second delay
    
 
def lcd_init():
  # Initialise display
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)
 
def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = data
  # mode = True  for character
  #        False for command
 
  GPIO.output(LCD_RS, mode) # RS
 
  # High bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x10==0x10:
    GPIO.output(LCD_D4, True)
  if bits&0x20==0x20:
    GPIO.output(LCD_D5, True)
  if bits&0x40==0x40:
    GPIO.output(LCD_D6, True)
  if bits&0x80==0x80:
    GPIO.output(LCD_D7, True)
 
  # Toggle 'Enable' pin
  lcd_toggle_enable()
 
  # Low bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x01==0x01:
    GPIO.output(LCD_D4, True)
  if bits&0x02==0x02:
    GPIO.output(LCD_D5, True)
  if bits&0x04==0x04:
    GPIO.output(LCD_D6, True)
  if bits&0x08==0x08:
    GPIO.output(LCD_D7, True)
 
  # Toggle 'Enable' pin
  lcd_toggle_enable()
 
def lcd_toggle_enable():
  # Toggle enable
  time.sleep(E_DELAY)
  GPIO.output(LCD_E, True)
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)
  time.sleep(E_DELAY)
 
def lcd_string(message,line):
  # Send string to display
 
  message = message.ljust(LCD_WIDTH," ")
 
  lcd_byte(line, LCD_CMD)
 
  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)
 
if __name__ == '__main__':
 
  try:
    main()
  except KeyboardInterrupt:
    pass
  finally:
    lcd_byte(0x01, LCD_CMD)
    lcd_string("Goodbye!",LCD_LINE_1)
    GPIO.cleanup()
