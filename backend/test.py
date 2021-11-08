import re

x = "{{bonsoir}} je m'appelle {{ name }}"

p = re.findall(r"{{([\s*a-zA-Z\s*]*)}}", x, flags=re.MULTILINE)

for i in p:
    print(i.strip())

