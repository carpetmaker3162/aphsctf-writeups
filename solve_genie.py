import z3
import struct
from math import *
import requests


# may 403 with ctx.cl website
URL = 'http://localhost:3000'


# credit https://github.com/PwnFunction/v8-randomness-predictor
def setup_solver(solver: z3.Solver, sequence: list[float]):
    state0, state1 = z3.BitVecs("state0 state1", 64)
    
    for i in range(len(sequence)):
        """
        XorShift128+

        use LShR (logical shift) instead of arithmetic shfit
        """
        se_s1 = state0
        se_s0 = state1
        state0 = se_s0
        se_s1 ^= (se_s1 << 23) & ((1 << 64) - 1)
        se_s1 ^= z3.LShR(se_s1, 17) & ((1 << 64) - 1)
        se_s1 ^= se_s0
        se_s1 ^= z3.LShR(se_s0, 26) & ((1 << 64) - 1)
        state1 = se_s1

        float_64 = struct.pack("d", sequence[i] + 1)
        u_long_long_64 = struct.unpack("<Q", float_64)[0]

        # Get the lower 52 bits (mantissa)
        mantissa = u_long_long_64 & 0xFFFFFFFFFFFFF

        # state0 is the output (V8 implementation)
        # create constraint by comparing mantissas
        solver.add(int(mantissa) == z3.LShR(state0, 12))


def to_float(state0) -> float:
    '''convert a 64-bit unsigned integer (IEEE 754) representation of a float into an actual python float'''
    u_long_long_64 = (state0 >> 12) | 0x3FF0000000000000
    float_64 = struct.pack("<Q", u_long_long_64)
    next_in_sequence = struct.unpack("d", float_64)[0]
    next_in_sequence -= 1
    
    return next_in_sequence


def solve(sequence):
    sequence = sequence[::-1]
    
    solver = z3.Solver()
    setup_solver(solver, sequence)

    status = solver.check()
    if status == z3.sat:
        model = solver.model()

        result = {}
        for state in model.decls():
            result[str(state)] = model[state]

        state0 = result['state0'].as_long()

        next_rand = to_float(state0)
        
        return next_rand

    else:
        return status


def main():
    session = requests.Session()

    r = session.post(f'{URL}/api/session')
    if r.status_code == 403:
        print('Forbidden')
        return

    random_outputs = []
    for _ in range(4):
        output = session.get(f'{URL}/api/random').json()['num']
        random_outputs.append(output)

    try:
        for _ in range(5):
            next_rand = solve(random_outputs)
            assert type(next_rand) == float
            random_outputs.append(next_rand)
            guess = floor(next_rand * 100) + 1

            response = session.post(f'{URL}/api/guess', json={'guess': guess})
            print(response.json())

            if (flag := response.json().get('flag')):
                return flag

            # skip every other prng output
            next_rand = solve(random_outputs)
            assert type(next_rand) == float
            random_outputs.append(next_rand)

    finally:
        session.delete(f'{URL}/api/session')

    print('Failed')


if __name__ == '__main__':
    if (flag := main()):
        print(flag)
