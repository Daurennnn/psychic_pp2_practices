import datetime

x = datetime.datetime.now()
print(x)
print(x.strftime("%A"), x.strftime("%d"), x.strftime("%B"), x.strftime("%Y"), "{0} century".format(x.strftime("%C")))
print()

print(x.strftime("%c"))
print()

y = datetime.datetime(2020, 5, 17)
print(y)
print(y.strftime("%A"))

z = datetime.datetime(1, 1, 1)
print(z)
print(z.strftime("%A"))