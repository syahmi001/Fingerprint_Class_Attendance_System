import urllib.request
import urllib.error
import json

from firebase import firebase

firebase = firebase.FirebaseApplication('https://attendance-36688.firebaseio.com', None)

def send_message(message, username):

    my_data = dict()
    my_data ["message"]= message
    my_data ["username"]= username
    my_data ["timestamp"]= {".sv":"timestamp"}

    json_data = json.dumps(my_data).encode()

    try:
        loader = urllib.request.urlopen("https://attendance-36688.firebaseio.com/messages.json", data = json_data)
    except urllib.error.URLError as e:
        message = json.loads(e.read())
        print(message["error"])
    else:
        print(loader.read())
