from functools import reduce

numbers = [1, 2, 3, 4, 5]

# reduce applies function arg until there is only 1 item
sum_lambda = reduce(lambda x, y: x + y, numbers)  # function arg takes 2 arguments returns 1
print(sum_lambda)

even = list(filter(lambda x: x%2 == 0, numbers))
print("Even numbers:", *even)

squares = list(map(lambda x: x**2, numbers))
print("Numbers squared:", *squares)
