from firebase import firebase

firebase = firebase.FirebaseApplication('https://attendance-36688.firebaseio.com', None)

#name=raw_input("Name: ")
#num =5
num=472

while num<=1000:
    result= firebase.put('/attendance',num, 0)
    num=num+1
    #print (result)
    

#result= firebase.put('/class',1, {"Name":str(name),"Pro": "Commended"})
#print (result)

