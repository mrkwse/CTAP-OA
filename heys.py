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

    print "*** SUBSTITUTION TESTS ***"
    substitution_test(s_box, [291, 16579])
    substitution_test(s_box, [17767, 35753])
    substitution_test(s_box, [33623, 54201])
    substitution_test(s_box, [30001, 39728])
    substitution_test(s_box, [23130, 45746])

    print "*** PERMUTATION TESTS ***"
    permutation_test(p_box, [61440, 34952])
    permutation_test(p_box, [3840, 17476])
    permutation_test(p_box, [240, 8738])
    permutation_test(p_box, [15, 4369])
    permutation_test(p_box, [23130, 23130])

    print "*** FOUR ROUND TEST ***"
    four_round([4132, 8165, 14287, 54321, 53124], 12033, s_box, p_box, 20025)
    four_round([4132, 8165, 14287, 54321, 53124], 62153, s_box, p_box, 7495)

    print "*** CHALLENGE VECTOR ***"
    four_round([4132, 8165, 14287, 54321, 53124], 13571, s_box, p_box, 0)
    # returns 45858

# def hadamard(s_box, p_box, input)


def substitution_test(s_in, example_in):

    # Divide the 16 bit input into 4 4-bit boxes
    boxes = [((example_in[0]/(16**3)) % 16), ((example_in[0]/(16**2)) % 16),
             ((example_in[0]/(16**1)) % 16), ((example_in[0]/(16**0)) % 16)]


    print boxes

    # Output the combination of the substituted 4-bit boxes
    out = (s_in[boxes[0]] * (16 ** 3)) + (s_in[boxes[1]] * (16 ** 2)) \
        + (s_in[boxes[2]] * (16 ** 1)) + (s_in[boxes[3]] * (16 ** 0))

    print "   Input: " + str(example_in[0]) + " " + '{0:b}'.format(example_in[0]).zfill(len(s_in))
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

    print perm_out


    print "   Input: " + str(example_in[0]) + " " + '{0:b}'.format(example_in[0]).zfill(len(p_in))
    print "Expected: " + str(example_in[1]) + " " + '{0:b}'.format(example_in[1]).zfill(len(p_in))
    print "  Actual: " + str(perm_out) + " " + '{0:b}'.format(perm_out).zfill(len(p_in))

def substitute(s_in, text_in):

    boxes = [((text_in/(16**3)) % 16), ((text_in/(16**2)) % 16),
             ((text_in/(16**1)) % 16), ((text_in/(16**0)) % 16)]

    out = (s_in[boxes[0]] * (16 ** 3)) + (s_in[boxes[1]] * (16 ** 2)) \
        + (s_in[boxes[2]] * (16 ** 1)) + (s_in[boxes[3]] * (16 ** 0))

    return out

def permutate(p_in, text_in):

    ii = 0

    perm_out = 0
    while ii < len(p_in):
        if int('{0:b}'.format(text_in).zfill(len(p_in))[ii]) == 1:
            perm_out = perm_out + ((2 ** (len(p_in) - (p_in[ii] + 1))))

        ii = ii + 1

    return perm_out

def four_round(subkeys, text_in, s_in, p_in, expected):
    current_text = text_in
    ii = 0

    while ii < 4:
        if ii < 3:
            current_text = current_text ^ subkeys[ii]

            current_text = substitute(s_in, current_text)

            current_text = permutate(p_in, current_text)
        else:
            current_text = current_text ^ subkeys[ii]

            current_text = substitute(s_in, current_text)

            current_text = current_text ^ subkeys[ii + 1]
        ii = ii + 1

    print "\n   Input: " + str(text_in) + " " + '{0:b}'.format(text_in).zfill(len(p_in))
    print "Expected: " + str(expected) + " " + '{0:b}'.format(expected).zfill(len(p_in))
    print "  Actual: " + str(current_text) + " " + '{0:b}'.format(current_text).zfill(len(p_in))


if __name__ == "__main__":
    main()
