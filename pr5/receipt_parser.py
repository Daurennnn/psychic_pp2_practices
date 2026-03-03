import re
import json

class Receipt:
    def __init__(self, path):
        with open(path, encoding='utf-8') as f:
            self.receipt = f.read()

    def prices(self):
        price = re.findall(r"(?<=Стоимость\n).+", self.receipt)
        for p in range(len(price)):
            price[p] = float(price[p].replace(",", ".").replace(" ", ""))
        return price
    
    def product_names(self):
        products = re.findall(r'(?<=\d[.]\n).+', self.receipt)
        return products
    
    def total(self):
        total_cost = sum(self.prices())
        return total_cost

    def date(self):
        date_time = re.findall(r"(?<=Время:\W).+", self.receipt)
        date_var = date_time[0].split()[0]
        return date_var
    
    def time(self):
        date_time = re.findall(r"(?<=Время:\W).+", self.receipt)
        time_var = date_time[0].split()[1]
        return time_var
    
    def pay_method(self):
        method = re.findall(r".*(?=.\n.*\nИТОГО:)", self.receipt)[0]
        return method
    
    def get_JSON(self):
        data = {
            'names': self.product_names(),
            'prices': self.prices(),
            'total': self.total(),
            'date': self.date(),
            'time': self.time(),
            'payment_method': self.pay_method()
        }
        return json.dumps(data, indent=4, ensure_ascii=False)


path1 = "pr5/raw.txt"

receipt1 = Receipt(path1)
print(receipt1.get_JSON())
