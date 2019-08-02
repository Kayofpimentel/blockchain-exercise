names = []


def add_names(name='Zé'):
    names.append(name)


def check_list(list_to_check):
    for name in list_to_check:
        if (len(name) > 5) or (name.lower().find('n') != -1):
            print(name)
    else:
        print('-' * 20)


add_names()
add_names('Maria')
add_names('Ana Carolina')
add_names('Fernanda')
add_names('Pedro')
add_names('Nathalia ')
check_list(names)

while len(names) > 0:
    print(names.pop(0))

print(names)
