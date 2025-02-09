"""
Functions for manipulating points on the NIST224p curve, quickly.
"""

# These are the parameters for the NIST224p curve (from the curve database at https://neuromancer.sk/std/nist/P-224)
a = 0xfffffffffffffffffffffffffffffffefffffffffffffffffffffffe
b = 0xb4050a850c04b3abf54132565044b0b7d7bfd8ba270b39432355ffb4
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF000000000000000000000001
n = 0xffffffffffffffffffffffffffff16a2e0b8f03e13dd29455c5c2a3d
G = (0xb70e0cbd6bb4bf7f321390b94a03c1d356c21122343280d6115c1d21, 0xbd376388b5f723fb4c22dfe6cd4375a05a07476444d5819985007e34, 1)
# Curve equation: y^2 = x^3 + ax + b (mod p)

import time

def mod_inv(n):
    """
    Compute modular inverse using Fermat's little theorem.
    Whether this is faster than the Euclidean algorithm depends on whether pow() is optimized or not
    """
    return pow(n, p - 2, p)

def affine_to_jacobian(point):
    """
    Convert affine (x, y) to Jacobian (X, Y, Z).
    """
    x,y = point
    return (x, y, 1)

def jacobian_to_affine(point):
    """
    Convert Jacobian (X, Y, Z) to affine (x, y).
    """
    x,y,z = point
    z_inv = mod_inv(z)
    z_inv2 = (z_inv * z_inv) % p
    z_inv3 = (z_inv2 * z_inv) % p
    x = (x * z_inv2) % p
    y = (y * z_inv3) % p
    return (x, y)

def double(point):
    """
    Point doubling in Jacobian coordinates.
    Uses dbl-1998-cmo-2 (http://www.hyperelliptic.org/EFD/g1p/auto-shortw-jacobian.html#doubling-dbl-1998-cmo-2)
    """
    x,y,z = point
    if y == 0:
        # At y = 0 we are always at the nub of the curve so the tangent is always vertical
        return None  # Point at infinity

    yy = (y * y) % p
    xx = (x * x) % p
    zz = (z * z) % p
    s = (4 * x * yy) % p
    m = (3 * xx + a * zz * zz) % p
    t = (m * m - 2 * s) % p
    x2 = t
    y2 = (m * (s - t) - 8 * yy * yy) % p
    z2 = (2 * y * z) % p
    return (x2, y2, z2)

def add(p1, p2):
    """
    Point addition in Jacobian coordinates.
    Uses add-1998-cmo-2 (http://www.hyperelliptic.org/EFD/g1p/auto-shortw-jacobian.html#addition-add-1998-cmo-2)
    """
    # Handle the identity cases: P1 + 0 = P1, and 0 + P2 = P2
    if (p1 == None):
        return p2
    if (p2 == None):
        return p1

    # Otherwise we can assume that neither point is at infinity so we can destructure into coordinates here
    x1, y1, z1 = p1
    x2, y2, z2 = p2

    z1z1 = (z1 * z1) % p
    z2z2 = (z2 * z2) % p
    u1 = (x1 * z2z2) % p
    u2 = (x2 * z1z1) % p
    # s is the tangent at the two points
    s1 = (y1 * z2 * z2z2) % p
    s2 = (y2 * z1 * z1z1) % p

    # If u1 == u2 then the two points have the same x coordinates (in affine space)
    # In other words, either p1 == p2 or p1 == -p2
    # if s1 == s2 then the points have the same tangent
    if u1 == u2:
        if s1 == s2:
            # Same slope, same x value implies p1 == p2. Just double
            return double(p1)
        else:
            # Different slope, same x value implies p1 == -p2. Sum is infinity.
            return None

    H = (u2 - u1) % p
    R = (s2 - s1) % p
    HH = (H * H) % p
    HHH = (H * HH) % p
    V = u1 * HH
    x3 = (R * R - HHH - 2 * V) % p
    y3 = (R * (V - x3) - s1 * HHH) % p
    z3 = (H * z1 * z2) % p
    return (x3, y3, z3)

def multiply(u, point):
    """
    Scalar multiplication using double-and-add in Jacobian coordinates.
    Simple add-and-double algorithm
    """
    result = None # Point at infinity
    current = point

    while u:
        if u & 1:
            result = add(result, current)
        current = double(current)
        u >>= 1

    return result

def compute_result(u, P, v):
    """
    Compute u * P + v * G using Jacobian coordinates.
    """
    # Convert affine to Jacobian
    Pj = affine_to_jacobian(P)

    # Compute scalar multiplications
    uPj = multiply(u, Pj)
    vG = multiply(v, G)

    # Add results
    R = add(uPj, vG)

    # Convert back to affine
    return jacobian_to_affine(R)

def reduce(s):
    """
    Map any scalar into the finite field
    """
    return (s % (n-1)) + 1

def is_on_curve(point):
    """
    Check if a point is on the curve. Handles both affine and Jacobian coordinates
    """
    if point == None:
        return True
    if len(point) == 2:
        # Affine
        x, y = point
        return (y * y) % p == (x * x * x + a * x + b) % p
    if len(point) == 3:
        x,y,z = point
        return (y * y * z) % p == (x * x * x + a * x * z * z + b * z * z * z) % p
    return False

def performance_test():
    start = time.ticks_us()
    u = reduce(123456789012345678901234567890)
    v = reduce(987654321098765432109876543210)
    P = (0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296 % p, 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162cb3398a3d3e1b16783b2ad3cf2f3b52 % p)
    result = compute_result(u, P, v)
    end = time.ticks_us()

    print(f"Result: {result} time = {end-start}us")

#performance_test()