import requests

api_link = 'https://attendance-36688.firebaseio.com/class.json'

num = 3

data = {"C":num,
        "D":1
        }

response = requests.put(api_link, json=data)
print(data, response.json())
