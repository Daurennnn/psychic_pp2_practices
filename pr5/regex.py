import re

txt = "abc aC bebrak_abbABCdefg"
match1 = re.findall(r'\bab*', txt)
match2 = re.findall(r'ab{1,3}', txt)
match3 = re.findall(r'[a-z]+_[a-z]+', txt)
match4 = re.findall(r'[A-Z]+[a-z]+', txt)

txt2 = "jflasjflaskalkjasdjfab"
match5 = re.findall(r"(a.*b$)", txt2)

camel = "avgVelocity"
match6 = re.findall(r'')

print(match5)