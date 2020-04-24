import random

def random_sha256_hexdigest():
    return bytes([ random.randint(0, 255) for _ in range(32) ]).hex()
