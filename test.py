# Copyright (c) 2023.
# -*-coding:utf-8 -*-
"""
@file: test.py
@author: Jerry(Ruihuang)Yang
@email: rxy216@case.edu
@time: 4/23/23 17:27
"""
import time

# Set the total number of iterations
total_iterations = 100


for i in range(total_iterations):
    # Do some processing here

    # Print the progress
    print('\r', i, '/100', end='')

    # Sleep for a short time to simulate processing time
    time.sleep(1)