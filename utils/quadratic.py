'''
First made: 2018/02/04
Last update: 2018/09/03
'''

from math import sqrt
from math import gcd


def solve(a, b, c):

    discrim = b**2 - 4*a*c

    output = []

    def factorization(n):  # Generates a list of prime factors
        n = abs(n)
        factors = []
        number = n
        while abs(number) > 1:
            for i in range(2, number + 1):
                # Looking for smallest divisor (guaranteed to be prime)
                # Milo- Optimizing would mean making the code convoluted, or
                # at least with my knowledge of Python tools so deal with it
                if number % i == 0:
                    factors.append(i)
                    number = number // i
                    break
        return factors

    def radical(n):  # Generate a simplified radical a√b in the form of (a, b)
        imaginary = abs(n) != n
        # This checks if n is negative, and puts it at the end of
        # output like [a, b, (True/False)]
        n = abs(n)
        if sqrt(n) == int(sqrt(n)):
            # Just checking if perfect square for s p e e d
            return [int(sqrt(n)), 1, imaginary]
        perfsqrs = 1
        # perfsqrs is gonna be the number on the outside of the radical
        factors = factorization(n)
        for factor in set(factors):
            # looking for repeats of factors in prime factorization
            if factors.count(factor) >= 2:
                perfsqrs *= factor ** (factors.count(factor) // 2)
                # When there's repeat factors we'll multiply one of the repeated
                # factors for each 2 instances of it
        return [perfsqrs, n // perfsqrs**2, imaginary]

    discrimnumbers = radical(discrim)
    # I have to check if the discrim is imaginary here cause sqrt() is a sissy that
    # breaks on negative inputs
    if (discrimnumbers[2] is False and
       (-b + (sqrt(discrim))) / (2*a) == int((-b + sqrt(discrim))) / (2*a)):
        # This part is for WHOLE NUMBER OUTPUTS ONLY
        output.append(str(int((-b + sqrt(discrim)) // (2*a))))
        output.append(str(int((-b - sqrt(discrim)) // (2*a))))

    elif (discrimnumbers[2] is False and
          discrim >= 0 and sqrt(discrim) == int(sqrt(discrim))):
        # This part is for if it's rational, but not whole
        for sign in [1, -1]:  # Two roots per quadratic
            top = str(-b + (sign * int(sqrt(discrim))))  # defining numerator
            spaces = " " * (int(((len(str(top)))
                            - (len(str(a*2))) / 2)))  # spaces center denominator
            output.append(top + "\n" + "-" * len(top) + "\n" + spaces + str(2*a))
    else:  # Okay, so we have a lot more work to do if the answer's irrational
        divisor = gcd(b, gcd(discrimnumbers[0], 2*a))  # Cancels out common factors
        if divisor > 1:
            final_numbs = [b // divisor,
                           discrimnumbers[0] // divisor,
                           2*a // divisor]
        else:
            final_numbs = [b, discrimnumbers[0], 2*a]

        if final_numbs[1] == 1:
            final_numbs[1] = ""
            # This prevents the 1 outside the radical from being shown for
            # simplification

        if discrimnumbers[2] and discrimnumbers[1] == 1:
            # For the number inside the radical, I take from discrimnumbers.  I
            # have to make it not display if it's just 1.
            sqrtsymbol = "i"
            discrimnumbers[1] = ""  # Making 1 inside radical not display.
            # I only have to do this if its complex because
            # if not its taken care of earlier.
        elif discrimnumbers[2]:
            sqrtsymbol = "i√"
        else:
            sqrtsymbol = "√"

        # Okay, time to format all the pieces together for the last time
        for sign in [" - ", " + "]:  # Two roots per quadratic
            top = (str(-final_numbs[0]) + sign + str((final_numbs[1]))
                   + sqrtsymbol + str(discrimnumbers[1]))
            spaces = " " * ((len(str(top)) // 2)
                            - (len(str(final_numbs[2]))) // 2)
            # These spaces center denominator
            if final_numbs[2] == 1:  # Checks if denominator is 1
                output.append(top)
            elif final_numbs[2] == -1:  # Checks if denominator is -1
                output.append(str(-final_numbs[0] * -1) + sign + str((final_numbs[1]))
                            + sqrtsymbol + str(discrimnumbers[1]))
            else:
                output.append(top + "\n" + "-" * len(top) + "\n"
                            + spaces + str(final_numbs[2]))  # Cool

    return output