"""
Functions for manipulating points on the NIST224p curve
"""

# These are the parameters for the NIST224p curve (from the curve database at https://neuromancer.sk/std/nist/P-224)
a = 0xfffffffffffffffffffffffffffffffefffffffffffffffffffffffe
b = 0xb4050a850c04b3abf54132565044b0b7d7bfd8ba270b39432355ffb4
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF000000000000000000000001
n = 0xffffffffffffffffffffffffffff16a2e0b8f03e13dd29455c5c2a3d
G = (0xb70e0cbd6bb4bf7f321390b94a03c1d356c21122343280d6115c1d21, 0xbd376388b5f723fb4c22dfe6cd4375a05a07476444d5819985007e34)
# Curve equation: y^2 = x^3 + ax + b (mod p)

# Now we can check if a point is on the curve:
def is_on_curve(x, y):
    return (y**2) % p == (x**3 + a * x + b) % p

# This function maps a scalar into the finite field
def reduce(s):
    return (s % (n-1)) + 1

# To do the multiplication we need some helper functions
# 1. Modular inverse (using extended Euclidean algorithm) since we need to divide in a finite field
def mod_inv(a, m):
    m0, x0, x1 = m, 0, 1
    while a > 1:
        q = a // m
        m, a = a % m, m
        x0, x1 = x1 - q * x0, x0
    if x1 < 0:
        x1 += m0
    return x1

# 2. Point doubling. This is cheaper than adding points
def double(point):
    x,y = point
    m = ((3 * x**2 + a) * mod_inv(2 * y, p)) % p
    x2 = (m**2 - 2 * x) % p
    y2 = (m * (x - x2) - y) % p
    return (x2, y2)

# 3. Point addition
def add(p1, p2):
    # Handle infinity here
    if p1 == (None, None):
        return p2
    if p2 == (None, None):
        return p1

    # FIXME: This does not hold if p1.x == p2.x (but they have different y positions)
    x1, y1 = p1
    x2, y2 = p2
    if x1 == x2 and y1 == y2:
        return double((x1, y1))
    m = ((y2 - y1) * mod_inv((x2 - x1) % p, p)) % p
    x3 = (m**2 - x1 - x2) % p
    y3 = (m * (x1 - x3) - y1) % p
    return (x3, y3)

# Now we can implement scalar multiplication using the double-and-add approach
def multiply(u, point):
    x, y = point
    result_x, result_y = (None, None) # Infinity
    # Loop from least to most significant bit
    for i in ''.join(reversed(bin(u)[2:])):
        if i == '1':
            result_x, result_y = add((result_x, result_y), (x, y))
        x, y = double((x, y))
    return (result_x, result_y)

def generator(u):
    return multiply(u, G)