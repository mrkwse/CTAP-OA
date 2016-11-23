#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import math

# Combining Function corresponds denary index correlates to binary
# of {x1}{x2}{x3}.
combined = [0,1,0,1,0,0,1,1]

default_stream_len = 2000

def main(argv=None):

    if argv == None:
        argv = sys.argv

    try:
        with open(argv[1], 'r') as textStream:
            stream_string_in = textStream.read()
            keystream = int(stream_string_in.replace(" ",""), 2)
            print '{0:b}'.format(keystream)
            # print keystream
            # print combined
    # stream = open (argv[1], 'r')
    # keystram = int(stream.read(), 2)
    except Exception as e:
        raise

    combine_function_out = [1,1,0,1,0,0,1,0]
    tapin = [[7,[6,7]],[11,[9,11]],[13,[8,11,12,13]]]

    # if argv[2] == '-v':

    # compare(keystream, 2000, [[7, [1,7]], [11, [1,10]], [13, [1,10,11,13]]])
    verify(tapin,[44,555,616],
           [0b0011010010111011100110010, 0b1101010001010000101000100,
            0b0001011001000101010110111, 0b0000101101010100110001101],
           25, [1,1,0,1,0,0,1,0])

    # generator_correlation([1,1,0,1,0,0,1,0])
    correlation, reg_comb = generator_correlation(combine_function_out)

    attack(keystream, tapin, combine_function_out, correlation, reg_comb)
    # iterate_all(7, [1,7], 2000)
    # sequence, popped = LSFR(4, [1,4], 6, 1)



# Function to identify any register(s) that correlates with the combining f(X)
def generator_correlation(combined_result):
    # Calculate number of registers to iterate through
    register_count = int(math.log(len(combined_result), 2))
    ii = 0
    correlation = [0.0] * (register_count)
    correlation.append([])
    for num in range(0, int(register_count)):
        correlation[register_count].append([0.0] * (2 ** (int(register_count) - 1)))

    reg_comb = [[0,1], [0,2], [1,2]]
    # correlation[register_count] = [permutations] * int(register_count)

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

            # reg_val = int(('{0:b}'.format(combined_result[jj][1])).zfill(register_count)[xx])
            combine_out = combined_result[jj]
            # reg_val = int(('{0:b}'.format(jj).zfill(register_count))[xx])

            if  combined_result[jj] == (jj / (2 ** (register_count - (xx + 1)))) % 2:
                correlation[xx] = correlation[xx] + 1

            xx = xx + 1

        yy = 0
        while yy < len(correlation[register_count]):
            if combined_result[jj] == 1:
                chosen_reg_vals = [((jj / (2 ** reg_comb[yy][0])) % 2), ((jj / (2 ** reg_comb[yy][1])) % 2)]
                correlation[register_count][yy][(chosen_reg_vals[0] << 1) + chosen_reg_vals[1]] += 1
            yy = yy + 1

        print 'jj ' + str(jj)
        jj = jj + 1




    ii = 0

    while ii < (len(correlation) - 1):
        jj = 0

        while jj < 2:
            # correlation[ii][jj] = correlation[ii][jj] / (0.5 * len(combined_result))

            jj = jj + 1

        correlation[ii] = correlation[ii] / (len(combined_result))

        ii = ii + 1


    ii = 0

    while ii < len(correlation[register_count]):

        jj = 0

        while jj < len(correlation[register_count][ii]):

            correlation[register_count][ii][jj] /= 2

            jj = jj + 1

        ii = ii + 1
    # for reg_combination in correlation[register_count]:
    #     for bit in reg_combination:
    #         bit = bit / 2

    if 0:
        # Iterate checks for each LSFR {x1,...,xn}
        while ii < register_count:
            jj = 0

            # Iterate through each output bit for f(X)
            while jj < len(combined_result):

                # If input xn and output f(X) match, increment count
                # (jj / (2*i)) % 2 returns iith bit of 0bjj
                if combined_result[jj][1] == (jj / (2 ** ii)) % 2:
                    correlation[ii][1] = correlation[ii][1] + 1

                jj = jj + 1

            # Change correlation count into probability
            correlation[ii][1] = correlation[ii][1] / len(combined_result)

            ii = ii + 1

    print correlation
    return correlation, reg_comb



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

    # try len(states) == len(registers)
    # initialise a list of length equal to number of registers
    # states = [None] * len(registers)

    # set each state x1..xn to starting sequence and None popped
    init_state_step = 0

    if 0:
        while init_state_step < len(states):
            states[init_state_step] = (0, None)
            init_state_step = init_state_step + 1
    # else:
        # states[0] = (39, None)
        # states[1] = (365, None)
        # states[2] = (7413, None)
    # print states

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
                # X = X + (states[reg_to_check[0]][1] << len(states) - (1 + ))
                # print states
                if states[reg_to_check[0]][1] == int(stream_string[bit_index]):
                    match_count = match_count + 1

                bit_index = bit_index + 1

    # print match_count
    return match_count

# registers contains each register as an array within an array,
# of structure [[]{int register bit-length}, [{tap bits}][], [..., [...]], ...]
def compare_all(stream_in, check_len, registers, states):

    # try len(states) == len(registers)
    # initialise a list of length equal to number of registers
    # states = [None] * len(registers)

    # set each state x1..xn to starting sequence and None popped
    init_state_step = 0



    bit_index = 0
    stream_string = "{0:b}".format(stream_in).zfill(check_len)
    match_count = 0


    while bit_index < check_len:
        LSFR_index = 0
        X = 0
        while LSFR_index < len(states):
            states[LSFR_index] = LSFR(registers[LSFR_index][0],
                                      registers[LSFR_index][1],
                                      states[LSFR_index][0],
                                      1, True)
            X = X + (states[LSFR_index][1] << len(states) - (1 + LSFR_index))
            LSFR_index = LSFR_index + 1

        if combined[X] == int(stream_string[bit_index]):
            match_count = match_count + 1
        bit_index = bit_index + 1

    # print match_count
    return match_count

def verify(registers, initial, expected_streams, stream_length, combine_fn):
    states = [None] * len(registers)

    init_state_step = 0

    while init_state_step < len(states):
        states[init_state_step] = (initial[init_state_step], None)
        init_state_step = init_state_step + 1

    bit_index = 0
    generated_stream = [0] * (len(registers) + 1)

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
        if generated_stream[LSFR_index] == expected_streams[LSFR_index]:
            print "Streams match. Generated: " + \
                   "{0:25b}".format(generated_stream[LSFR_index]) + \
                  " Expected: " + "{0:25b}".format(expected_streams[LSFR_index])
        else:
            print "Streams differ. Generated: " + \
                   "{0:b}".format(generated_stream[LSFR_index]) + \
                  " Expected: " + "{0:b}".format(expected_streams[LSFR_index])

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
               "{0:25b}".format(generated_stream[len(states)]) + \
              " Expected: " + "{0:25b}".format(expected_streams[len(states)])
    else:
        print "Streams differ. Generated: " + \
               "{0:b}".format(generated_stream[len(states)]) + \
              " Expected: " + "{0:b}".format(expected_streams[len(states)])





def attack(stream, tapin, combining, correlation, reg_comb):
    brute = True

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

    print checked

    if brute:
        ii = 0
        to_break = []
        states = []
        while ii < register_count:
            if found_keys[ii] != None:
                states.append([found_keys[ii], None])
                print states
            else:
                to_break.append(ii)
                states.append([0, None])
            ii = ii + 1

        max_key = [2 ** 12, 2 ** 14]
        found = False
        check_len = 25
        max_count = 0
        print states
        while found != True:
            # print states
            match_count = compare_all(stream, check_len, tapin, states[:])
            # print match_count
            max_count = max(match_count, max_count)
            if match_count < check_len:
                check_len = 25
                if states[to_break[0]][0] < max_key[0]:
                    states[to_break[0]][0] = states[to_break[0]][0] + 1
                    # print "inc [0]"
                else:
                    states[to_break[0]][0] = 0
                    if states[to_break[1]][0] < max_key[1]:
                        # print "inc [1]"
                        states[to_break[1]][0] = states[to_break[1]][0] + 1
                        # print max_count
                        # print states
                        # break
                        max_count = 0
                    else:
                        print "Unfindable"
                        break
            else:
                if check_len == default_stream_len:
                    found = True
                    print "Found!"
                    print states
                else:
                    check_len = max((check_len * 2), default_stream_len)
                    print "Promising…"
                    print states


    else:
        # If not all keys found, attack register combinations
        if len(checked) != register_count:

            # Confirm working with array of combined correlations
            if ii == register_count:
                exploitable_combs = []
                for fields in range(0, len(correlation[ii])):
                    exploitable_combs.append([])
                jj = 0

                # Iterate through each combination
                while jj < len(correlation[ii]):

                    kk = 0

                    # Iterate through each probability to check which are exploitable
                    # (if any)
                    while kk < len(correlation[ii][jj]):
                        if correlation[ii][jj][kk] != 0.5:
                            exploitable_combs[jj].append(kk)
                        kk = kk + 1

                    jj = jj + 1

                jj = 0

                i
                while jj < len(exploitable_combs):
                    if exploitable_combs[jj] == []:
                        break
                    else:
                        kk = 0

                        while kk < len(exploitable_combs[jj]):
                            if checked.count(exploitable_combs[jj][kk]) > 0:
                                break
                            else:
                                break



                    jj = jj + 1


        print exploitable_combs




    print found_keys


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
