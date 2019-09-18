import math;


#######################################################
#                  helpers                            #


def fib(first=1, second=2, max_value=90):
    """ generator that returns fibonacci numbers """
    last = second;
    second_last = first;
    yield first;
    yield second;
    
    while True:
        n = last + second_last;
        if n > max_value: break;
        yield n;
        last, second_last = n, last;

def is_palindrome(n):
    """ is n the same forwards and backwards """
    return str(n)[::-1] == str(n);

def factorize(n):
    """ return the factors of n """
    factors = [1];
    i = 2;
    while i * i < n:
        if n % i == 0:
            factors += [i, n // i];
        i += 1;
    return sorted(factors);


#######################################################
#                  problems                           #

def problem_1():
    """ multiples of 3 and 5 """
    return sum((i for i in range(1, 1000) if (i%3==0 or i%5==0)));

def problem_2():
    """ even fibonacci numbers """
    return sum((n for n in fib(max_value=4000000) if n%2==0));

def problem_3():
    """ largest prime factor """
    number = 600851475143;
    i = 2;
    while i * i < number:
        while number % i == 0:
            number //= i;
        i += 1;
    return number;

def problem_4():
    """ largest palindrome product """
    largest = 0;
    for i in range(100, 1000):
        for j in range(100, 1000):
            n = i * j;
            if n > largest and is_palindrome(n):
                largest = n;
    return largest;

def problem_5():
    """ smallest multiple """
    pass;
