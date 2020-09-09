from firebase import firebase

firebase = firebase.FirebaseApplication('https://attendance-36688.firebaseio.com', None)
result= firebase.get('/class', None)
print (result)

