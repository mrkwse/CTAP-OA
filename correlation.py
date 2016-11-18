#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import math

# Combining Function corresponds denary index correlates to binary
# of {x1}{x2}{x3}.
combined = [0,1,0,1,0,0,1,1]

def main(argv=None):

    if argv == None:
        argv = sys.argv

    try:
        with open(argv[1], 'r') as textStream:
            stream_string_in = textStream.read()
            keystream = int(stream_string_in.replace(" ",""), 2)
            # print keystream
            # print combined
    # stream = open (argv[1], 'r')
    # keystram = int(stream.read(), 2)
    except Exception as e:
        raise

    # if argv[2] == '-v':

    # compare(keystream, 2000, [[7, [1,7]], [11, [1,10]], [13, [1,10,11,13]]])
    verify([[7,[6,7]],[11,[9,11]],[13,[8,11,12,13]]],[44,555,616],
           [0b0011010010111011100110010, 0b1101010001010000101000100,
            0b0001011001000101010110111], 25)

    generator_correlation([1,1,0,1,0,0,1,0])
    # iterate_all(7, [1,7], 2000)
    # sequence, popped = LSFR(4, [1,4], 6, 1)



# Function to identify any register(s) that correlates with the combining f(X)
def generator_correlation(combined_result):
    # Calculate number of registers to iterate through
    register_count = math.log(len(combined_result), 2)
    ii = 0
    correlation = [0.0] * 3

    # Iterate checks for each LSFR {x1,...,xn}
    while ii < register_count:
        jj = 0

        # Iterate through each output bit for f(X)
        while jj < len(combined_result):

            # If input xn and output f(X) match, increment count
            if combined_result[jj] == (jj / (2 ** ii)) % 2:
                correlation[ii] = correlation[ii] + 1

            jj = jj + 1

        # Change correlation count into probability
        correlation[ii] = correlation[ii] / len(combined_result)

        ii = ii + 1

    print correlation
    return correlation



# Confirmed as working with lecture example.
def LSFR(length, tap, initial, iterations, least_significant_n):

    bits = length
    perms = []
    sequence = initial
    # print(str(sequence))

    it = 0

    while it < iterations:

        binstr = "{0:b}".format(sequence)

        # Current iteration through tap bits = tip
        tip = 0

        if least_significant_n:
            current = (binstr).zfill(bits)[(tap[tip] - 1)]
        else:
            current = (binstr).zfill(bits)[(bits - tap[tip])]
        tip += 1

        while tip < len(tap):

            if least_significant_n:
                nextbit = (binstr).zfill(bits)[(tap[tip] - 1)]
            else:
                nextbit = (binstr).zfill(bits)[(bits - tap[tip])]

            current = int(current) ^ int(nextbit)

            tip += 1

        popped = int(binstr[len(binstr) - 1])
        sequence = sequence >> 1

        # If result of XOR function is 1, append to first bit
        if current == 1:
            sequence += 2**(bits-1)

        perms.append(binstr)
        it += 1

    # print perms
    return (sequence, popped)

# registers contains each register as an array within an array,
# of structure [[]{int register bit-length}, [{tap bits}][], [..., [...]], ...]
def compare(stream_in, stream_len, registers):

    # initialise a list of length equal to number of registers
    states = [None] * len(registers)

    # set each state x1..xn to starting sequence and None popped
    init_state_step = 0

    if 0:
        while init_state_step < len(states):
            states[init_state_step] = (0, None)
            init_state_step = init_state_step + 1
    else:
        states[0] = (39, None)
        states[1] = (365, None)
        states[2] = (7413, None)
    print states

    bit_index = 0
    stream_string = "{0:b}".format(stream_in)
    match_count = 0


    while bit_index < stream_len:
        LSFR_index = 0
        X = 0
        while LSFR_index < len(states):
            states[LSFR_index] = LSFR(registers[LSFR_index][0],
                                      registers[LSFR_index][1],
                                      states[LSFR_index][0],
                                      1, False)
            X = X + (states[LSFR_index][1] << len(states) - (1 + LSFR_index))
            LSFR_index = LSFR_index + 1

        if combined[X] == int(stream_string[bit_index]):
            match_count = match_count + 1
        bit_index = bit_index + 1

    print match_count

def verify(registers, initial, expected_stream, stream_length):
    states = [None] * len(registers)

    init_state_step = 0

    while init_state_step < len(states):
        states[init_state_step] = (initial[init_state_step], None)
        init_state_step = init_state_step + 1

    bit_index = 0
    generated_stream = [0] * len(registers)

    while bit_index < stream_length:
        LSFR_index = 0
        X = 0
        while LSFR_index < len(states):
            states[LSFR_index] = LSFR(registers[LSFR_index][0],
                                      registers[LSFR_index][1],
                                      states[LSFR_index][0],
                                      1, True)
            X = X + (states[LSFR_index][1] << len(states) - (1 + LSFR_index))

            generated_stream[LSFR_index] = (generated_stream[LSFR_index] << 1) \
                                            + states[LSFR_index][1]

            LSFR_index = LSFR_index + 1
        bit_index = bit_index + 1
    LSFR_index = 0

    while LSFR_index < len(states):
        if generated_stream[LSFR_index] == expected_stream[LSFR_index]:
            print "Streams match. Generated: " + \
                   "{0:25b}".format(generated_stream[LSFR_index]) + \
                  " Expected: " + "{0:25b}".format(expected_stream[LSFR_index])
        else:
            print "Streams differ. Generated: " + \
                   "{0:b}".format(generated_stream[LSFR_index]) + \
                  " Expected: " + "{0:b}".format(expected_stream[LSFR_index])

        LSFR_index = LSFR_index + 1

def attack(stream, tapin, combining, correlation):

    register_count = math.log(len(combining), 2)
    vulnerable = []

    ii = 0

    # while ii < 

def iterate_all(bits, tapin, iterations):

    bitsin = 1

    while bitsin < (2^bits):

        LSFR(bits, tapin, bitsin, iterations)

        bitsin += 1




    #1 = 129 = 0b1000001


# def LSFR2():
#     # 1025 = 0b01000000001
#
# def LSFR3():
    # 11265 = 0b1011000000001

if __name__ == "__main__":
    main()
