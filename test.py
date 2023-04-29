# Copyright (c) 2023.
# -*-coding:utf-8 -*-
"""
@file: test.py
@author: Jerry(Ruihuang)Yang
@email: rxy216@case.edu
@time: 4/23/23 17:27
"""
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# Generate some sample text
text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."

# Create the word cloud
wordcloud = WordCloud(width=1600, height=800, background_color='white').generate(text)

# Display the word cloud
plt.figure(figsize=(16,9))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.show()