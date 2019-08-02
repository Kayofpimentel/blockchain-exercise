# File to solve the first exercises presented in the Python course.

name = input("Hello there, what's your name?\n ")
age = int(input("And, if I may ask, your age?\n "))

def number_of_decades():
    global age
    return age//10

def print_name_and_age():
    global name
    global age
    decades = number_of_decades()
    print("Hello {}, you're {}, right? You've lived {} decades, wow!\n ".format(name, age, decades))


def print_two_strings(str1="", str2=""):
    print("{} {}".format(str1, str2))


print_name_and_age()
print_two_strings("Hello", "World")
