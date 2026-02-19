import json

x = '{"name":"Dauren", "age":10, "city":"Almaty"}'

y = json.loads(x)

for a, b in y.items():
    print(a, b)

z = json.dumps(y, indent=4)

print(z)