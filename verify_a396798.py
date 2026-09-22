#!/usr/bin/env python3
"""Exact checks for the A396798 congruence proof. Python 3, no dependencies.

Rational-function checks are identities, not finite series sampling.
The additional coefficient checks reconstruct the defining fixed point.
"""

from math import comb


def trim(a):
    a = list(a)
    while len(a) > 1 and a[-1] == 0:
        a.pop()
    return a


def add(a, b, modulus=None):
    c = [0] * max(len(a), len(b))
    for i, v in enumerate(a):
        c[i] += v
    for i, v in enumerate(b):
        c[i] += v
    if modulus is not None:
        c = [v % modulus for v in c]
    return trim(c)


def scale(a, c, modulus=None):
    return trim([c * v if modulus is None else c * v % modulus for v in a])


def mul(a, b, modulus=None, degree=None):
    size = len(a) + len(b) - 1
    if degree is not None:
        size = min(size, degree + 1)
    c = [0] * size
    for i, u in enumerate(a):
        if not u or i >= size:
            continue
        for j in range(min(len(b), size - i)):
            c[i + j] += u * b[j]
    if modulus is not None:
        c = [v % modulus for v in c]
    return trim(c)


def power(a, n, modulus=None):
    out = [1]
    for _ in range(n):
        out = mul(out, a, modulus)
    return out


def rat_add(a, b):
    an, ad = a
    bn, bd = b
    return add(mul(an, bd, 8), mul(bn, ad, 8), 8), mul(ad, bd, 8)


def rat_mul(a, b):
    return mul(a[0], b[0], 8), mul(a[1], b[1], 8)


def rat_equal(a, b):
    assert a[1][0] % 2 == 1 and b[1][0] % 2 == 1
    return add(mul(a[0], b[1], 8), scale(mul(b[0], a[1], 8), -1), 8) == [0]


X = [0, 1]
IDENTITY = (X, [1])
H4 = ([0, 0, 0, 0, 4], power([1, -1], 3, 8))


def mobius(k):
    return X, [1, -k % 8]


def proposed(k):
    return rat_add(mobius(k), H4) if k % 2 else mobius(k)


def apply_f(y):
    """Exact rational substitution F(y), F(x)=x/(1-x)+4*x^4/(1-x)^3."""
    n, d = y
    delta = add(d, scale(n, -1), 8)
    first = mul(mul(n, d, 8), power(delta, 2, 8), 8)
    numerator = add(first, scale(power(n, 4, 8), 4, 8), 8)
    denominator = mul(d, power(delta, 3, 8), 8)
    return numerator, denominator


def compose(a, b, degree, modulus=None):
    """Truncated ordinary formal composition, with b[0]=0."""
    assert b[0] == 0
    out = [0]
    for coefficient in reversed(a[:degree + 1]):
        out = mul(out, b, modulus, degree)
        out = add(out, [coefficient], modulus)
    return out


def fixed_point(degree, modulus=None):
    """Construct each coefficient from A = x + A^{o4} A^{o5}."""
    a = X[:]
    for d in range(2, degree + 1):
        it = X[:]
        for _ in range(4):
            it = compose(a, it, d, modulus)
        it5 = compose(a, it, d, modulus)
        a = add(X, mul(it, it5, modulus, d), modulus)
    return a + [0] * (degree + 1 - len(a))


def coefficient_formula(k, n):
    if n == 1:
        return 1
    correction = 4 * (k % 2) * (comb(n - 2, 2) if n >= 4 else 0)
    return (pow(k, n - 1, 8) + correction) % 8


def main():
    f = proposed(1)
    assert rat_equal(apply_f(f), mobius(2))
    print("PASS: exact rational identity F(F(x)) = x/(1-2x) modulo 8")
    for k in range(8):
        assert rat_equal(apply_f(proposed(k)), proposed(k + 1))
    print("PASS: all eight exact rational transition identities modulo 8")
    rhs = rat_add(IDENTITY, rat_mul(proposed(4), proposed(5)))
    assert rat_equal(f, rhs)
    print("PASS: exact rational defining identity F = x + F^{o4} F^{o5}")

    known = [1, 1, 9, 133, 2517, 55609, 1370321, 36691293,
             1050059709, 31765811601, 1007855339033, 33345188250965,
             1145460034412005, 40717411279314345, 1493765745364063009,
             56436741663524300685, 2192115902521507267021,
             87410192361668819113985, 3573820557441516192963049,
             149667971123475023087339525]
    exact = fixed_point(len(known))
    assert exact[1:] == known
    print("PASS: 20 independently reconstructed integer coefficients match OEIS")

    degree = 64
    a = fixed_point(degree, 8)
    assert a[1:] == [coefficient_formula(1, n) for n in range(1, degree + 1)]
    current = X[:]
    for k in range(17):
        padded = current + [0] * (degree + 1 - len(current))
        assert padded[1:] == [coefficient_formula(k, n) for n in range(1, degree + 1)]
        current = compose(a, current, degree, 8)
    print("PASS: all coefficients through degree 64 for iterates k=0,...,16")
    assert a[2] == 1 and a[3] == 1 and a[4] == 5
    print("PASS: corrected [1,1,5,5] coefficient block starts at n=2")
    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
