import functools

# Follow the instructions explained in the problem video and try to
#  implement a solution on your own. Compare it with my solution (video + downloadable files) thereafter.
# #
# # 1) Write a normal function that accepts another function as
#  an argument. Output the result of that other function in your “normal” function.
# #
# # 2) Call your “normal” function by passing a lambda function
#  – which performs any operation of your choice – as an argument.
# #
# # 3) Tweak your normal function by allowing an infinite amount
#  of arguments on which your lambda function will be executed.
# #
# # 4) Format the output of your “normal” function such that
#  numbers look nice and are centered in a 20 character column.


# Result 1 + 3)

def f1(fn, *args):
    test = fn(*args)
    return f'{test/2:^20.4f}'


def f2(*args):
    return functools.reduce(lambda a, b: a + b, args, 0)


print(f1(f2, 3, 4))
print(f1(f2))

# Result 2)

print(f1(lambda farg1, farg2: farg1 + farg2 if farg1 < farg2 else farg1 - farg2, 9, 8))
print(f1(lambda farg1, farg2: farg1 + farg2 if farg1 < farg2 else farg1 - farg2, 8, 9))
