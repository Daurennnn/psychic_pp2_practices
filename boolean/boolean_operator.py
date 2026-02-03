cases = (True, False)
for i in cases:
    for j in cases:
        st1 = not i or not j
        st2 = not(i and j)
        print(st1 == st2)