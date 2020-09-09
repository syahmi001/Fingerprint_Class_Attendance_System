import datetime
import time

t =  time.localtime()

current_time = time.strftime("%H:%M:%S", t)

print(current_time)

date = datetime.date.today()
print(date)

datetime_object = datetime.datetime.now()
print(datetime_object)
