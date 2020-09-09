import time
import RPi.GPIO as GPIO
import time
import datetime

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

#GPIO setup for lcd
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
GPIO.setup(LCD_E, GPIO.OUT)  # E
GPIO.setup(LCD_RS, GPIO.OUT) # RS
GPIO.setup(LCD_D4, GPIO.OUT) # DB4
GPIO.setup(LCD_D5, GPIO.OUT) # DB5
GPIO.setup(LCD_D6, GPIO.OUT) # DB6
GPIO.setup(LCD_D7, GPIO.OUT) # DB7

#GPIO setup for lcd
GPIO.setup(but1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(but2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(but3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(but4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(but5, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(but6, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def test1(pin):
    print('Button 4 is pressed')
    lcd_string("Button 4",LCD_LINE_1)
    lcd_string("is pressed",LCD_LINE_2)
    time.sleep(3) # 3 second delay
 
    
def main():
  # Main program block
  
  GPIO.add_event_detect(but4, GPIO.FALLING)
  GPIO.add_event_callback(but4,test1)
 
  # Initialise display
  lcd_init()
 
  while True:
    
    t =  time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    print(current_time)
    date = datetime.date.today()
    print(date)
      
    lcd_string("   WELCOME TO",LCD_LINE_1)
    lcd_string("  FINGERPRINT",LCD_LINE_2)
    time.sleep(3) # 3 second delay
      
    lcd_string("   ATTENDANCE",LCD_LINE_1)
    lcd_string("     SYSTEM",LCD_LINE_2)
    time.sleep(3) # 3 second delay
    
    lcd_string("   "+str(date),LCD_LINE_1)
    lcd_string("    "+str(current_time),LCD_LINE_2)
    time.sleep(3) # 3 second delay
    

    if GPIO.input(but2) ==0:
        lcd_string("Button 2",LCD_LINE_1)
        lcd_string("is pressed",LCD_LINE_2)
        time.sleep(3) # 3 second delay
        
    if GPIO.input(but3) ==0:
        lcd_string("Button 3",LCD_LINE_1)
        lcd_string("is pressed",LCD_LINE_2)
        time.sleep(3) # 3 second delay

    if GPIO.input(but4) ==0:
        lcd_string("Button 4",LCD_LINE_1)
        lcd_string("is pressed",LCD_LINE_2)
        time.sleep(3) # 3 second delay

    if GPIO.input(but5) ==0:
        lcd_string("Button 5",LCD_LINE_1)
        lcd_string("is pressed",LCD_LINE_2)
        time.sleep(3) # 3 second delay

    if GPIO.input(but6) ==0:
        lcd_string("Button 6",LCD_LINE_1)
        lcd_string("is pressed",LCD_LINE_2)
        time.sleep(3) # 3 second delay
    
 
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
