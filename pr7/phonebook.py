import psycopg2
from config import load_config
import re

def add_contact(name, number):
    pass

def filter_by_name(name):
    pass

def load_to_csv():
    pass

if __name__ == "__main__":
    while True:
        task = input()
        if re.match(r"\\a .*", task):
            add_contact(*task.split()[1:])
        if re.match(r"\\f .*", task):
            filter_by_name(*task.split()[1])
        if re.match(r"\\ld .*", task):
            load_to_csv()
        if re.match(r"\\q .*", task):
            break
            