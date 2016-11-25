#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import math

s_box = [0x4, 0x0, 0xC, 0x3,
         0x8, 0xB, 0xA, 0x9,
         0xD, 0xE, 0x2, 0x7,
         0x6, 0x5, 0xF, 0x1]

# input [0, 1, 2,  3, 4, 5, 6,  7, 8, 9, 10, 11,12,13, 14, 15]
p_box = [0, 4, 8, 12, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15]

def main(argv=None):

    if argv == None:
        argv = sys.argv

    # Read block.txt and parse to an list block_in of lists of int ['in', 'out']
    try:
        with open(argv[1], 'r') as textStream:
            block_in = textStream.read()

        block_in = block_in.replace("\r","")
        block_in = block_in.replace("  "," ")

        block_in = block_in.split('\n')

        ii = 0
        while ii < len(block_in):
            block_in[ii] = block_in[ii].split(" ")
            jj = 0
            while jj < len(block_in[ii]):
                block_in[ii][jj] = int(block_in[ii][jj])
                jj = jj + 1
            ii = ii + 1
        # print block_in

    except Exception as e:
        raise

    dist, p_table = find_difference_dist(s_box)

    differential_cryptanalysis(s_box, p_box, dist, p_table, 4)

def find_difference_dist(s_in):
    jj = 0

    distribution = []

    # Make 16 x 16 list of lists of zeros to fill with distributions
    while jj < len(s_in):
        distribution.append(([0] * len(s_in)))
        jj = jj + 1

    bit_count = int(math.log(len(s_in), 2))

    probability_table = distribution[:]

    ii = 0

    while ii < len(s_in):

        jj = 0

        while jj < len(s_in):
            delta_y = s_in[(jj ^ ii)] ^ s_in[jj]
            distribution[ii][delta_y] = distribution[ii][delta_y] + 1

            jj = jj + 1

        jj = 0
        while jj < len(s_in):
            probability_table[ii][jj] = float(distribution[ii][jj]) / 16

            jj = jj + 1

        ii = ii + 1
    return distribution, probability_table

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

    return [val, max_p]

def substitute_diff(prob_in, route_in):
    xx = 0
    while xx < len(route_in):
        text_in = route_in[0]

        boxes = [((text_in/(16**3)) % 16), ((text_in/(16**2)) % 16),
                 ((text_in/(16**1)) % 16), ((text_in/(16**0)) % 16)]

        boxes_match = []

        for box in boxes:
            boxes_match.append([])

        ii = 0
        for box in boxes:
            jj = 0
            while jj < len(boxes):
                boxes_match[ii].append(ii)
                if jj == ii:
                    break
                else:
                    if boxes[ii] == boxes[jj]:
                        boxes_match[ii].append(jj)
                jj = jj + 1

            ii = ii + 1



        most_likely_out = [find_max_p(prob_in[boxes[0]]),
                           find_max_p(prob_in[boxes[1]]),
                           find_max_p(prob_in[boxes[2]]),
                           find_max_p(prob_in[boxes[3]])]

        ii = 0

        while ii < len(boxes):
            jj = 0
            route_in[0] = 0
            val = 0
            while jj < len(most_likely_out[ii][0]):
                if jj == 0:
                    val = val + (most_likely_out[ii][0][jj] * 16 ** (3 - ii))
                else:
                    route_in.append(most_likely_out[0][jj], (route_in[1] * most_likely_out[ii][1]))
                    # route_in[1] = route_in[1] * most_likely_out[ii][1]
                jj = jj + 1
            ii = ii + 1

    print most_likely_out
    print route_in



def permutate(p_in, route_in):

    xx = 0

    while xx < len(route_in):
        text_in = route_in[xx][0]

        ii = 0

        perm_out = 0
        while ii < len(p_in):
            if int('{0:b}'.format(text_in).zfill(len(p_in))[ii]) == 1:
                perm_out = perm_out + ((2 ** (len(p_in) - (p_in[ii] + 1))))

            ii = ii + 1
        route_in[xx][0] = perm_out

    return route_in

def differential_cryptanalysis(s_in, p_in, dist, p_table, rounds):

    jj = 0

    probability = []

    # Make 16 x 16 list of lists of zeros to fill with distributions
    while jj < len(s_in):
        probability.append(([0.0] * len(s_in)))
        jj = jj + 1

    ii = 1

    round_pass = 1

    while ii < (2 ** (4 * 4)):
        jj = 0

        linear_route = [[ii, 1.0]]
        # Iterate for R - 1 rounds to find input of final key.
        while jj < (rounds - round_pass):
            kk = 0
            while kk < len(linear_route):
                linear_route[kk] = substitute_diff(p_table,
                                               linear_route[kk])

                linear_route[kk] = permuatate(p_in, linear_route[kk])
                print linear_route
            jj = jj + 1
        ii = ii + 1



if __name__ == "__main__":
    main()
