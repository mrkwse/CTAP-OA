#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import math

# 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15
# 4, 0,12, 3, 8,11,10, 9,13,14,  2,  7,  6,  5, 15,  1

s_box = [0x4, 0x0, 0xC, 0x3,
         0x8, 0xB, 0xA, 0x9,
         0xD, 0xE, 0x2, 0x7,
         0x6, 0x5, 0xF, 0x1]

# input [0, 1, 2,  3, 4, 5, 6,  7, 8, 9, 10, 11,12,13, 14, 15]
p_box = [0, 4, 8, 12, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15]

def main(argv=None):

    if argv == None:
        argv = sys.argv

    try:
        with open(argv[1], 'r') as textStream:
            block_in = textStream.read()

    except Exception as e:
        raise

    print "\n*** SUBSTITUTION TESTS ***"
    substitution_test(s_box, [291, 16579])
    substitution_test(s_box, [17767, 35753])
    substitution_test(s_box, [33623, 54201])
    substitution_test(s_box, [30001, 39728])
    substitution_test(s_box, [23130, 45746])

    print "\n*** PERMUTATION TESTS ***"
    permutation_test(p_box, [61440, 34952])
    permutation_test(p_box, [3840, 17476])
    permutation_test(p_box, [240, 8738])
    permutation_test(p_box, [15, 4369])
    permutation_test(p_box, [23130, 23130])

    print "\n*** FOUR ROUND TEST ***"
    four_round([4132, 8165, 14287, 54321, 53124], 12033, s_box, p_box, 4, 20025)
    four_round([4132, 8165, 14287, 54321, 53124], 62153, s_box, p_box, 4, 7495)

    print "\n*** CHALLENGE VECTOR ***"
    four_round([4132, 8165, 14287, 54321, 53124], 13571, s_box, p_box, 4, 0)
    # returns 45858

    differential_cryptanalysis(s_box, p_box)
# def hadamard(s_box, p_box, input)


def substitution_test(s_in, example_in):

    # Divide the 16 bit input into 4 4-bit boxes
    boxes = [((example_in[0]/(16**3)) % 16), ((example_in[0]/(16**2)) % 16),
             ((example_in[0]/(16**1)) % 16), ((example_in[0]/(16**0)) % 16)]


    # Output the combination of the substituted 4-bit boxes
    out = (s_in[boxes[0]] * (16 ** 3)) + (s_in[boxes[1]] * (16 ** 2)) \
        + (s_in[boxes[2]] * (16 ** 1)) + (s_in[boxes[3]] * (16 ** 0))

    print "\n   Input: " + str(example_in[0]) + " " + '{0:b}'.format(example_in[0]).zfill(len(s_in))
    print "Expected: " + str(example_in[1]) + " " + '{0:b}'.format(example_in[1]).zfill(len(s_in))
    print "  Actual: " + str(out) + " " + '{0:b}'.format(out).zfill(len(s_in))

def permutation_test(p_in, example_in):

    ii = 0

    perm_out = 0

    # If bit is '1' set permutation output to 1
    while ii < len(p_in):
        if int('{0:b}'.format(example_in[0]).zfill(len(p_in))[ii]) == 1:
            perm_out = perm_out + ((2 ** (len(p_in) - (p_in[ii] + 1))))

        ii = ii + 1


    print "\n   Input: " + str(example_in[0]) + " " + '{0:b}'.format(example_in[0]).zfill(len(p_in))
    print "Expected: " + str(example_in[1]) + " " + '{0:b}'.format(example_in[1]).zfill(len(p_in))
    print "  Actual: " + str(perm_out) + " " + '{0:b}'.format(perm_out).zfill(len(p_in))

def substitute(s_in, text_in):

    boxes = [((text_in/(16**3)) % 16), ((text_in/(16**2)) % 16),
             ((text_in/(16**1)) % 16), ((text_in/(16**0)) % 16)]

    out = (s_in[boxes[0]] * (16 ** 3)) + (s_in[boxes[1]] * (16 ** 2)) \
        + (s_in[boxes[2]] * (16 ** 1)) + (s_in[boxes[3]] * (16 ** 0))

    return out

def substitute_diff(distribution, text_in):

    boxes = [((text_in/(16**3)) % 16), ((text_in/(16**2)) % 16),
             ((text_in/(16**1)) % 16), ((text_in/(16**0)) % 16)]

    most_likely_out = [find_max_p(distribution[boxes[0]]),
                       find_max_p(distribution[boxes[1]]),
                       find_max_p(distribution[boxes[2]]),
                       find_max_p(distribution[boxes[3]])]

    ii = 0

    multiple_out = False
    uncertain = 0

    while ii < len(most_likely_out):
        if len(most_likely_out[ii]) > 1:
            multiple_out = True
            uncertain = ii
        ii = ii + 1

    if multiple_out:
        out = []
        ii = 0
        while ii < len(most_likely_out[uncertain]):
            out.append(0)
            jj = 0
            while jj < len(most_likely_out):
                if jj == uncertain:
                    out[ii] = out[ii] + (most_likely_out[jj][ii] * (16 ** (3 - jj)))
                else:
                    out[ii] = out[ii] + (most_likely_out[jj][0] * (16 ** (3 - jj)))
                jj = jj + 1
            ii = ii + 1
    else:
        jj = 0
        out = 0
        while jj < len(most_likely_out):
            out = out + (most_likely_out[jj][0] * (16 ** (3 - jj)))
            jj = jj + 1

    return out, multiple_out


def permutate(p_in, text_in):

    ii = 0

    perm_out = 0
    while ii < len(p_in):
        if int('{0:b}'.format(text_in).zfill(len(p_in))[ii]) == 1:
            perm_out = perm_out + ((2 ** (len(p_in) - (p_in[ii] + 1))))

        ii = ii + 1

    return perm_out

# Input array of int subkeys (in sequence), text_in (as int),
# the s_box, the permutation sequence, int number of rounds,
# and the expected int output
def four_round(subkeys, text_in, s_in, p_in, rounds, expected):

    # The updating ciphertext
    current_text = text_in
    ii = 0

    while ii < rounds:
        if ii < (rounds - 1):

            # Subkey bitwise xor
            current_text = current_text ^ subkeys[ii]

            current_text = substitute(s_in, current_text)

            current_text = permutate(p_in, current_text)

        # Final round skips permutation step
        else:
            current_text = current_text ^ subkeys[ii]

            current_text = substitute(s_in, current_text)

            current_text = current_text ^ subkeys[ii + 1]
        ii = ii + 1

    print "\n   Input: " + str(text_in) + " " + '{0:b}'.format(text_in).zfill(len(p_in))
    print "Expected: " + str(expected) + " " + '{0:b}'.format(expected).zfill(len(p_in))
    print "  Actual: " + str(current_text) + " " + '{0:b}'.format(current_text).zfill(len(p_in))

def find_max_p(array):
    ii = 0
    max_p = 0.0
    val = []

    while ii < len(array):
        if array[ii] > max_p:
            max_p = array[ii]
            val = [ii]
        elif array[ii] == max_p:
            val.append(ii)
        ii = ii + 1

    return val

def differential_cryptanalysis(s_in, p_in):

    ii = 0
    jj = 0

    # Table correlating ∆X and ∆Y
    distribution = []

    while jj < len(s_in):
        distribution.append(([0] * len(s_in)))
        jj = jj + 1

    bit_count = int(math.log(len(s_in),2))

    while ii < len(s_in):
        jj = 0
        while jj < len(s_in):
            # delta_y = s_in[((jj + ii) % 16)] ^ s_in[jj]
            delta_y = s_in[(jj ^ ii)] ^ s_in[jj]
            distribution[ii][delta_y] = distribution[ii][delta_y] + 1

            jj = jj + 1
        ii = ii + 1
    print distribution

    start = [0,0]
    max_p = 0.0

    ii = 1
    while ii < len(distribution):
        jj = 1
        while jj < len(distribution):
            if distribution[ii][jj] > max_p:
                max_p = distribution[ii][jj]
                start = [ii,jj]
            jj = jj + 1
        ii = ii + 1

    print start

    current_text = start[0] << 8

    ii = 0
    rounds = 4
    multiple = False
    subs = []
    while ii < rounds:
        if ii < (rounds - 1):
            if multiple:
                print current_text
            else:
                current_text, multiple = substitute_diff(distribution, current_text)

                if multiple:
                    break
                else:
                    current_text = permutate(p_in, current_text)
        else:
            if multiple:
                print current_text
            else:
                current_text, multiple = substitute_diff(distribution, current_text)
        ii = ii + 1


if __name__ == "__main__":
    main()
