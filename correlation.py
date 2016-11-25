#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import math
import random

# Combining Function corresponds denary index correlates to binary
# of {x1}{x2}{x3}.
combined = [1,1,0,1,0,0,1,0]

# The manually found correlation between subsets of X={x1x2x3}
x1x2 = [1,-1,0,-1]
x1x3 = [-1,1,-1,0]

# Default length of stream
default_stream_len = 2000

# run with ‘python correlation.py stream.txt’
# Or replace stream.txt with another stream to attempt to break
def main(argv=None):

    if argv == None:
        argv = sys.argv

    try:
        with open(argv[1], 'r') as textStream:
            stream_string_in = textStream.read()
            keystream = int(stream_string_in.replace(" ",""), 2)

    except Exception as e:
        raise


    combine_function_out = [1,1,0,1,0,0,1,0]

    # The tap sequences for each register, along with the size of register
    tapin = [[7,[6,7]],[11,[9,11]],[13,[8,11,12,13]]]

    # Verify passes in the tap sequnce, followed by an array of the initial
    # values to check for each regsiter, then an array of the expected values
    # for each register (as well as the expecte combined value), the length
    # of the stream to check, and finally the combine function.
    verify(tapin,[44,555,616],
           [0b0011010010111011100110010, 0b1101010001010000101000100,
            0b0001011001000101010110111, 0b0000101101010100110001101],
           25, [1,1,0,1,0,0,1,0])

    # This generates the ciphertext for the challenge key.
    verify(tapin, [97,975,6420], [0,0,0,0], 25, combine_function_out)

    # Identify correlation between LSFRs and f(X)
    correlation = generator_correlation(combine_function_out)

    # With the correlations known, attack the cipher
    attack(keystream, tapin, combine_function_out, correlation)


# Returns the correlation between the LSFRs and combining function f(X)
def generator_correlation(combined_result):
    # Calculate number of registers to iterate through
    register_count = int(math.log(len(combined_result), 2))
    ii = 0
    correlation = [0.0] * (register_count)


    # Set starting correlation to equal 110, will shift through later
    # 110 >> 1 = 011; 110 >> 2 = 101; (loops round)
    # Each bit = 1 refers to a register to be examined in combination
    starting_combined_permutation = (2 ** register_count) - 2


    jj = 0

    # Compare each f(X) against against each combination/single value.
    # Iterate through each f(X) (i.e. 8 times), and update correlation array
    # as go along. 16 updates to array each time.
    while jj < len(combined_result):

        xx = 0
        while xx < register_count:

            # Read value of current register in current pass of combination
            # function
            combine_out = combined_result[jj]

            if  combined_result[jj] == (jj / (2 ** (register_count - (xx + 1)))) % 2:
                correlation[xx] = correlation[xx] + 1

            xx = xx + 1


        jj = jj + 1




    ii = 0

    # while ii < (len(correlation) - 1):
    while ii < len(correlation):
        jj = 0

        while jj < 2:

            jj = jj + 1

        correlation[ii] = correlation[ii] / (len(combined_result))

        ii = ii + 1

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
    return [sequence, popped]

# registers contains each register as an array within an array,
# of structure [[]{int register bit-length}, [{tap bits}][], [..., [...]], ...]
def compare_one(stream_in, stream_len, registers, states, reg_to_check):

    # set each state x1..xn to starting sequence and None popped
    init_state_step = 0

    bit_index = 0
    stream_string = "{0:b}".format(stream_in).zfill(stream_len)
    match_count = 0

    if 0:
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
    else:
        if len(reg_to_check) == 1:
            X = 0
            while bit_index < stream_len:
                states[reg_to_check[0]] = LSFR(registers[reg_to_check[0]][0],
                                               registers[reg_to_check[0]][1],
                                               states[reg_to_check[0]][0],
                                               1, True)

                if states[reg_to_check[0]][1] == int(stream_string[bit_index]):
                    match_count = match_count + 1

                bit_index = bit_index + 1

    return match_count

# registers contains each register as an array within an array,
# of structure [[]{int register bit-length}, [{tap bits}][], [..., [...]], ...]
def compare_all(stream_in, check_len, combinator, registers, states):

    # set each state x1..xn to starting sequence and None popped
    init_state_step = 0



    bit_index = 0
    stream_string = "{0:b}".format(stream_in).zfill(check_len)
    match_count = 0

    # Check for required number of bits, 1 bit at a time
    while bit_index < check_len:
        LSFR_index = 0
        X = 0

        # Generate index of X for f(X)
        while LSFR_index < len(states):
            states[LSFR_index] = LSFR(registers[LSFR_index][0],
                                      registers[LSFR_index][1],
                                      states[LSFR_index][0],
                                      1, True)
            X = X + (states[LSFR_index][1] << len(states) - (1 + LSFR_index))
            LSFR_index = LSFR_index + 1

        # Check combined f(X) against cipher stream, incrementing if matching
        if combinator[X] == int(stream_string[bit_index]):
            match_count = match_count + 1
        elif combinator[X] == -1:
            if (random.randint(0,1) == int(stream_string[bit_index])):
                match_count = match_count + 1


        bit_index = bit_index + 1

    return match_count


# Function to verify some set of inputs against an expected output.
# Also used to generate outputs for challenge keys.
def verify(registers, initial, expected_streams, stream_length, combine_fn):
    states = [None] * len(registers)

    init_state_step = 0

    # Set state list to equal input states to check
    while init_state_step < len(states):
        states[init_state_step] = [initial[init_state_step], None]
        init_state_step = init_state_step + 1

    bit_index = 0
    generated_stream = [0] * (len(registers) + 1)

    # Iterate through each bit of stream
    while bit_index < stream_length:
        LSFR_index = 0
        X = 0

        # Iterate through each LSFR
        while LSFR_index < len(states):

            # Get next value from LSFT
            states[LSFR_index] = LSFR(registers[LSFR_index][0],
                                      registers[LSFR_index][1],
                                      states[LSFR_index][0],
                                      1, True)
            # Set X
            X = X + (states[LSFR_index][1] << len(states) - (1 + LSFR_index))

            # Set bit in stream
            generated_stream[LSFR_index] = (generated_stream[LSFR_index] << 1) \
                                            + states[LSFR_index][1]

            LSFR_index = LSFR_index + 1
        bit_index = bit_index + 1
    LSFR_index = 0


    # Output whether or not streams match after comparing values
    while LSFR_index < len(states):
        if generated_stream[LSFR_index] == expected_streams[LSFR_index]:
            print "Streams match. Generated: " + \
                   "{0:b}".format(generated_stream[LSFR_index]).zfill(stream_length) + \
                  " Expected: " + "{0:b}".format(expected_streams[LSFR_index]).zfill(stream_length)
        else:
            print "Streams differ. Generated: " + \
                   "{0:b}".format(generated_stream[LSFR_index]).zfill(stream_length) + \
                  " Expected: " + "{0:b}".format(expected_streams[LSFR_index]).zfill(stream_length)

        LSFR_index = LSFR_index + 1

    bit_index = 0
    while bit_index < stream_length:
        current_X = 0
        LSFR_index = 0
        while LSFR_index < len(states):
            current_X = current_X << 1
            current_X = current_X + int('{0:b}'.format(generated_stream[LSFR_index]).zfill(stream_length)[bit_index])
            LSFR_index = LSFR_index + 1

        generated_stream[len(states)] = (generated_stream[len(states)] << 1) \
                                        + combine_fn[current_X]
        bit_index = bit_index + 1

    if generated_stream[len(states)] == expected_streams[len(states)]:
        print "Streams match. Generated: " + \
               "{0:b}".format(generated_stream[len(states)]).zfill(stream_length) + \
              " Expected: " + "{0:b}".format(expected_streams[len(states)]).zfill(stream_length)
    else:
        print "Streams differ. Generated: " + \
               "{0:b}".format(generated_stream[len(states)]) + \
              " Expected: " + "{0:b}".format(expected_streams[len(states)]).zfill(stream_length)



# Attacks a stream cipher to find initial register values
def attack(stream, tapin, combining, correlation):

    register_count = int(math.log(len(combining), 2))
    vulnerable = correlation

    found_keys = [None] * register_count

    checked = []

    ii = 0

    # Iterate through each correlation probability, finding exploitable register
    while ii < register_count:
        # Check for exploitable register
        if correlation[ii] != 0.5:
            # Ignores array of combined correlations
            if ii < register_count:
                reg_to_check = [ii]
                jj = 0
                states = [None] * int(register_count)
                # Compare matches for sequence of starting values
                while jj < (2 ** tapin[ii][0]):
                    states[ii] = [jj, None]
                    match_count = compare_one(stream, default_stream_len, tapin, states, reg_to_check)

                    # If returned number of matches appropriate to correlation
                    # probability, print current starting value as key for
                    # that register
                    if ((0.8 * correlation[ii]) * default_stream_len) < match_count \
                       < ((1.2 * correlation[ii]) * default_stream_len):
                        print "LSFR" + str(ii + 1) + ", init val: " + str(jj) \
                               + " returned " + str(match_count) + " matches"
                        break
                    jj = jj + 1

                # Note key in array
                found_keys[ii] = jj

                # Note that LSFR(ii+1) key has been found, so that checks with
                # multiple registers fix value of that register
                checked.append(ii)
            else:
                break
            ii = ii + 1
        else:
            ii = ii + 1

    # Extract from correlation[ii]
    corr = 0.75
    ii = 0
    states = []
    to_break = []
    while ii < (register_count - 1):
        if found_keys[ii] != None:
            states.append([found_keys[ii], None])
        else:
            to_break.append(ii)
            # Skip 0 state due to bug
            states.append([1, None])
        ii = ii + 1

    kk = 0

    max_key = [2 ** 12]
    found = False

    best_found = [0,0]
    worst_found = [0,0]

    # Compare combined x1x2 until 75% correlation with stream
    while found != True:

        match_count = compare_all(stream, default_stream_len, x1x2, tapin, states[:])

        # Check if stream matches sufficiently and update best_found
        # if better than previous closest match
        if ((0.98 * corr) * default_stream_len) < match_count:
            if match_count > best_found[1]:
                best_found = [states[to_break[0]][0], match_count]
            if states[to_break[0]][0] < max_key[0]:
                states[to_break[0]][0] = states[to_break[0]][0] + 1
            else:
                found = True
        else:

            if states[to_break[0]][0] < max_key[0]:
                states[to_break[0]][0] = states[to_break[0]][0] + 1
            else:
                found = True


    print "LSFR" + str(to_break[0] + 1) + ", init val: " + str(best_found[0]) \
           + " returned " + str(best_found[1]) + " matches"

    # Note new key.
    found_keys[1] = best_found[0]

    ii = 0
    to_break = []
    states = []
    while ii < register_count:
        if found_keys[ii] != None:
            states.append([found_keys[ii], None])
        else:
            to_break.append(ii)
            states.append([0, None])
        ii = ii + 1

    max_key = [2 ** 12, 2 ** 14]
    found = False
    check_len = default_stream_len
    max_count = 0

    # Search through states of final register
    while found != True:

        match_count = compare_all(stream, check_len, combined, tapin, states[:])
        max_count = max(match_count, max_count)

        # Check for exact match, incrementing through each initial value
        # of final register
        if match_count < check_len:
            if states[to_break[0]][0] < max_key[1]:
                states[to_break[0]][0] = states[to_break[0]][0] + 1
            else:
                states[to_break[0]][0] = 0
                print "Unfindable"
                break

        # Exact match found
        else:
            if check_len == default_stream_len:
                found = True
                print "Found!"


    # Print final values
    print "LSFR1 init: " + str(states[0][0]) +\
        "\nLSFR2 init: " + str(states[1][0]) +\
        "\nLSFR3 init: " + str(states[2][0])



if __name__ == "__main__":
    main()
