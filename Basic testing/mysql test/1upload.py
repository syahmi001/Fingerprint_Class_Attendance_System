import serial, time, datetime
import struct           #Convert between strings and binary data
import sys
import os
import binascii
import mysql.connector
cnx=mysql.connector.connect(user='root',password='',host='169.254.196.35',database='fingerdb')       # connect to MySql database
cur=cnx.cursor()

ser = serial.Serial('/dev/ttyUSB0',57600)      # serial communication in Linux
#ser = serial.Serial("COM6", baudrate=9600, timeout=1)   #serial communication in Windows

pack = [0xef01, 0xffffffff, 0x1]        # Header, Address and Package Identifier

def readPacket():       # Function to read the Acknowledge packet
        time.sleep(1)
        w = ser.inWaiting()
        ret = []
        if w >= 9:
                s = ser.read(9)         # Partial read to get length
                ret.extend(struct.unpack('!HIBH', s))
                ln = ret[-1]

                time.sleep(1)
                w = ser.inWaiting()
                if w >= ln:
                        s = ser.read(ln)
                        form = '!' + 'B' * (ln - 2) + 'H'       # Specifying byte size
                        ret.extend(struct.unpack(form, s))
        return ret

def readPacket1():      # Function to read the Acknowledge packet
        time.sleep(1)
        w = ser.inWaiting()
        ret = []
        form = 'B' * 700
        s = ser.read(700)
        t=binascii.hexlify(s)   # convert to hex
        u=t[24:]
        cur.execute("insert into fingertb(name,finger) values('%s','%s')" %(name,u) )     # upadate database
        cnx.commit()
        v=binascii.unhexlify(u)
        form1='B'*688
        ret1=[]
        ret1.extend(struct.unpack(form1, v))
        ret.extend(struct.unpack(form, s))

def writePacket(data):          # Function to write the Command Packet
        pack2 = pack + [(len(data) + 2)]
        a = sum(pack2[-2:] + data)
        pack_str = '!HIBH' + 'B' * len(data) + 'H'
        l = pack2 + data + [a]
        s = struct.pack(pack_str, *l)
        ser.write(s)


def verifyFinger():     # Verify Module?s handshaking password
        data = [0x13, 0x0, 0, 0, 0]
        writePacket(data)
        s = readPacket()
        return s[4]

def genImg():   # Detecting finger and store the detected finger image in ImageBuffer
        data = [0x1]
        writePacket(data)
        s = readPacket()
        return s[4]

def img2Tz(buf):        # Generate character file from the original finger image in ImageBuffer and store the file in CharBuffer1 or CharBuffer2.
        data = [0x2, buf]
        writePacket(data)
        s = readPacket()
        return s[4]

def regModel():         # Combine information of character files from CharBuffer1 and CharBuffer2 and generate a template which is stroed back in both CharBuffer1 and CharBuffer2.
        data = [0x5]
        writePacket(data)
        s = readPacket()
        return s[4]

def UpChar(buf):        # Upload the character file or template of CharBuffer1/CharBuffer2 to upper computer
        data = [0x8,buf]
        writePacket(data)
        s = readPacket1()

print ("Type done to exit")
name=raw_input("Enter name : ")
while (name!='done'):

        if verifyFinger():
                print 'Verification Error'
                sys.exit(0)

        print 'Put finger',
        sys.stdout.flush()

        time.sleep(1)
        while genImg():
                time.sleep(0.1)
                print '.',
                sys.stdout.flush()

        print ''
        sys.stdout.flush()

        if img2Tz(1):
                print 'Conversion Error'
                sys.exit(0)

        print 'Put finger again',
        sys.stdout.flush()

        time.sleep(1)
        while genImg():
                time.sleep(0.1)
                print '.',
                sys.stdout.flush()

        print ''
        sys.stdout.flush()

        if img2Tz(2):
                print 'Conversion Error'
                sys.exit(0)

        if regModel():
                print 'Template Error'
                sys.exit(0)

        if UpChar(2):
                print 'Template Error'
                sys.exit(0)

        name=raw_input("Enter name : ")
