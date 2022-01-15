import random

def cuadrados(numero):
    a=numero
    for i in range(10):
        a=a*a
        yield a

if __name__ == "__main__":
    a=cuadrados(random.randint(1,10))
    print(a)
    for i in cuadrados(random.randint(1,10)):
        print(i)