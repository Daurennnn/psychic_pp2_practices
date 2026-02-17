even = lambda x: x % 2 == 0
nums = list(range(20))
even_nums = list(filter(even, nums))
print(even_nums)