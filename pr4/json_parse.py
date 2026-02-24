import json

# x = '{"name":"Dauren", "age":10, "city":"Almaty"}'

# y = json.loads(x)

# for a, b in y.items():
#     print(a, b)

# z = json.dumps(y, indent=4)

# print(z)

# x = {
#   "name": "John",
#   "age": 30,
#   "married": True,
#   "divorced": False,
#   "children": ("Ann","Billy"),
#   "pets": None,
#   "cars": [
#     {"model": "BMW 230", "mpg": 27.5},
#     {"model": "Ford Edge", "mpg": 24.1}
#   ]
# }

# print(json.dumps(x, indent=4))

def parseData(data):
    imdata = data["imdata"]
    print("DN                                                 Description           Speed    MTU  ")
    for i in imdata[:3]:
        l1PhysIf = i["l1PhysIf"]
        atrs = l1PhysIf["attributes"]
        print(atrs["dn"], 
              atrs["descr"], 
              atrs["speed"],
              atrs["mtu"])

# Open and read JSON file
with open('pr4/sample-data.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

parseData(data) # Outputs the parsed Python object