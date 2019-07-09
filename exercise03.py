import copy

persons = [
    {'name': 'Kayo',
     'age': 29,
     'hobby': {'type': 'game'}},
    {'name': 'Lucas',
     'age': 28,
     'hobby': {'type': 'dog'}},
    {'name': 'Gleidson',
     'age': 26,
     'hobby': {'type': 'music'}}
    ]

persons_names = [person['name'] for person in persons]

print(persons)
print(persons_names)
print(all(person['age'] > 20 for person in persons))

temp_persons = copy.deepcopy(persons)

print(temp_persons)

temp_persons[0]['name'] = 'Nathalia'
temp_persons[0]['hobby'] = 'walk'

print(persons)
print(temp_persons)

person1, person2, person3 = persons
person1_name, person1_age, person1_hobby = person1.values()
print(person1)
print(person2)
print(person3)
print(person1_name + str(person1_age) + str(person1_hobby['type']))
