import json
import numpy as np
import pandas as pd
import os
import dask.dataframe as dd
from dask.diagnostics import ProgressBar
import itertools
import csv
import ast
import re


# ------------------------------------------ USEFUL CONSTANTS ------------------------------------------

#new_pairs = [[['left_shoulder', 'left_elbow'], ['left_shoulder', 'left_hip']], [['left_shoulder', 'left_elbow'], ['left_hip', 'left_shoulder']], [['left_elbow', 'left_shoulder'], ['left_shoulder', 'left_hip']], [['left_elbow', 'left_shoulder'], ['left_hip', 'left_shoulder']], [['left_shoulder', 'left_elbow'], ['left_elbow', 'left_wrist']], [['left_shoulder', 'left_elbow'], ['left_wrist', 'left_elbow']], [['left_elbow', 'left_shoulder'], ['left_elbow', 'left_wrist']], [['left_elbow', 'left_shoulder'], ['left_wrist', 'left_elbow']], [['left_shoulder', 'left_elbow'], ['right_shoulder', 'right_elbow']], [['left_shoulder', 'left_elbow'], ['right_elbow', 'right_shoulder']], [['left_elbow', 'left_shoulder'], ['right_shoulder', 'right_elbow']], [['left_elbow', 'left_shoulder'], ['right_elbow', 'right_shoulder']], [['left_shoulder', 'left_elbow'], ['right_shoulder', 'right_hip']], [['left_shoulder', 'left_elbow'], ['right_hip', 'right_shoulder']], [['left_elbow', 'left_shoulder'], ['right_shoulder', 'right_hip']], [['left_elbow', 'left_shoulder'], ['right_hip', 'right_shoulder']], [['left_shoulder', 'left_elbow'], ['right_elbow', 'right_wrist']], [['left_shoulder', 'left_elbow'], ['right_wrist', 'right_elbow']], [['left_elbow', 'left_shoulder'], ['right_elbow', 'right_wrist']], [['left_elbow', 'left_shoulder'], ['right_wrist', 'right_elbow']], [['left_shoulder', 'left_elbow'], ['left_hip', 'left_knee']], [['left_shoulder', 'left_elbow'], ['left_knee', 'left_hip']], [['left_elbow', 'left_shoulder'], ['left_hip', 'left_knee']], [['left_elbow', 'left_shoulder'], ['left_knee', 'left_hip']], [['left_shoulder', 'left_elbow'], ['left_knee', 'left_ankle']], [['left_shoulder', 'left_elbow'], ['left_ankle', 'left_knee']], [['left_elbow', 'left_shoulder'], ['left_knee', 'left_ankle']], [['left_elbow', 'left_shoulder'], ['left_ankle', 'left_knee']], [['left_shoulder', 'left_elbow'], ['right_hip', 'right_knee']], [['left_shoulder', 'left_elbow'], ['right_knee', 'right_hip']], [['left_elbow', 'left_shoulder'], ['right_hip', 'right_knee']], [['left_elbow', 'left_shoulder'], ['right_knee', 'right_hip']], [['left_shoulder', 'left_elbow'], ['right_knee', 'right_ankle']], [['left_shoulder', 'left_elbow'], ['right_ankle', 'right_knee']], [['left_elbow', 'left_shoulder'], ['right_knee', 'right_ankle']], [['left_elbow', 'left_shoulder'], ['right_ankle', 'right_knee']], [['left_shoulder', 'left_elbow'], ['mouth_left', 'mouth_right']], [['left_shoulder', 'left_elbow'], ['mouth_right', 'mouth_left']], [['left_elbow', 'left_shoulder'], ['mouth_left', 'mouth_right']], [['left_elbow', 'left_shoulder'], ['mouth_right', 'mouth_left']], [['left_shoulder', 'left_hip'], ['left_elbow', 'left_wrist']], [['left_shoulder', 'left_hip'], ['left_wrist', 'left_elbow']], [['left_hip', 'left_shoulder'], ['left_elbow', 'left_wrist']], [['left_hip', 'left_shoulder'], ['left_wrist', 'left_elbow']], [['left_shoulder', 'left_hip'], ['right_shoulder', 'right_elbow']], [['left_shoulder', 'left_hip'], ['right_elbow', 'right_shoulder']], [['left_hip', 'left_shoulder'], ['right_shoulder', 'right_elbow']], [['left_hip', 'left_shoulder'], ['right_elbow', 'right_shoulder']], [['left_shoulder', 'left_hip'], ['right_shoulder', 'right_hip']], [['left_shoulder', 'left_hip'], ['right_hip', 'right_shoulder']], [['left_hip', 'left_shoulder'], ['right_shoulder', 'right_hip']], [['left_hip', 'left_shoulder'], ['right_hip', 'right_shoulder']], [['left_shoulder', 'left_hip'], ['right_elbow', 'right_wrist']], [['left_shoulder', 'left_hip'], ['right_wrist', 'right_elbow']], [['left_hip', 'left_shoulder'], ['right_elbow', 'right_wrist']], [['left_hip', 'left_shoulder'], ['right_wrist', 'right_elbow']], [['left_shoulder', 'left_hip'], ['left_hip', 'left_knee']], [['left_shoulder', 'left_hip'], ['left_knee', 'left_hip']], [['left_hip', 'left_shoulder'], ['left_hip', 'left_knee']], [['left_hip', 'left_shoulder'], ['left_knee', 'left_hip']], [['left_shoulder', 'left_hip'], ['left_knee', 'left_ankle']], [['left_shoulder', 'left_hip'], ['left_ankle', 'left_knee']], [['left_hip', 'left_shoulder'], ['left_knee', 'left_ankle']], [['left_hip', 'left_shoulder'], ['left_ankle', 'left_knee']], [['left_shoulder', 'left_hip'], ['right_hip', 'right_knee']], [['left_shoulder', 'left_hip'], ['right_knee', 'right_hip']], [['left_hip', 'left_shoulder'], ['right_hip', 'right_knee']], [['left_hip', 'left_shoulder'], ['right_knee', 'right_hip']], [['left_shoulder', 'left_hip'], ['right_knee', 'right_ankle']], [['left_shoulder', 'left_hip'], ['right_ankle', 'right_knee']], [['left_hip', 'left_shoulder'], ['right_knee', 'right_ankle']], [['left_hip', 'left_shoulder'], ['right_ankle', 'right_knee']], [['left_shoulder', 'left_hip'], ['mouth_left', 'mouth_right']], [['left_shoulder', 'left_hip'], ['mouth_right', 'mouth_left']], [['left_hip', 'left_shoulder'], ['mouth_left', 'mouth_right']], [['left_hip', 'left_shoulder'], ['mouth_right', 'mouth_left']], [['left_elbow', 'left_wrist'], ['right_shoulder', 'right_elbow']], [['left_elbow', 'left_wrist'], ['right_elbow', 'right_shoulder']], [['left_wrist', 'left_elbow'], ['right_shoulder', 'right_elbow']], [['left_wrist', 'left_elbow'], ['right_elbow', 'right_shoulder']], [['left_elbow', 'left_wrist'], ['right_shoulder', 'right_hip']], [['left_elbow', 'left_wrist'], ['right_hip', 'right_shoulder']], [['left_wrist', 'left_elbow'], ['right_shoulder', 'right_hip']], [['left_wrist', 'left_elbow'], ['right_hip', 'right_shoulder']], [['left_elbow', 'left_wrist'], ['right_elbow', 'right_wrist']], [['left_elbow', 'left_wrist'], ['right_wrist', 'right_elbow']], [['left_wrist', 'left_elbow'], ['right_elbow', 'right_wrist']], [['left_wrist', 'left_elbow'], ['right_wrist', 'right_elbow']], [['left_elbow', 'left_wrist'], ['left_hip', 'left_knee']], [['left_elbow', 'left_wrist'], ['left_knee', 'left_hip']], [['left_wrist', 'left_elbow'], ['left_hip', 'left_knee']], [['left_wrist', 'left_elbow'], ['left_knee', 'left_hip']], [['left_elbow', 'left_wrist'], ['left_knee', 'left_ankle']], [['left_elbow', 'left_wrist'], ['left_ankle', 'left_knee']], [['left_wrist', 'left_elbow'], ['left_knee', 'left_ankle']], [['left_wrist', 'left_elbow'], ['left_ankle', 'left_knee']], [['left_elbow', 'left_wrist'], ['right_hip', 'right_knee']], [['left_elbow', 'left_wrist'], ['right_knee', 'right_hip']], [['left_wrist', 'left_elbow'], ['right_hip', 'right_knee']], [['left_wrist', 'left_elbow'], ['right_knee', 'right_hip']], [['left_elbow', 'left_wrist'], ['right_knee', 'right_ankle']], [['left_elbow', 'left_wrist'], ['right_ankle', 'right_knee']], [['left_wrist', 'left_elbow'], ['right_knee', 'right_ankle']], [['left_wrist', 'left_elbow'], ['right_ankle', 'right_knee']], [['left_elbow', 'left_wrist'], ['mouth_left', 'mouth_right']], [['left_elbow', 'left_wrist'], ['mouth_right', 'mouth_left']], [['left_wrist', 'left_elbow'], ['mouth_left', 'mouth_right']], [['left_wrist', 'left_elbow'], ['mouth_right', 'mouth_left']], [['right_shoulder', 'right_elbow'], ['right_shoulder', 'right_hip']], [['right_shoulder', 'right_elbow'], ['right_hip', 'right_shoulder']], [['right_elbow', 'right_shoulder'], ['right_shoulder', 'right_hip']], [['right_elbow', 'right_shoulder'], ['right_hip', 'right_shoulder']], [['right_shoulder', 'right_elbow'], ['right_elbow', 'right_wrist']], [['right_shoulder', 'right_elbow'], ['right_wrist', 'right_elbow']], [['right_elbow', 'right_shoulder'], ['right_elbow', 'right_wrist']], [['right_elbow', 'right_shoulder'], ['right_wrist', 'right_elbow']], [['right_shoulder', 'right_elbow'], ['left_hip', 'left_knee']], [['right_shoulder', 'right_elbow'], ['left_knee', 'left_hip']], [['right_elbow', 'right_shoulder'], ['left_hip', 'left_knee']], [['right_elbow', 'right_shoulder'], ['left_knee', 'left_hip']], [['right_shoulder', 'right_elbow'], ['left_knee', 'left_ankle']], [['right_shoulder', 'right_elbow'], ['left_ankle', 'left_knee']], [['right_elbow', 'right_shoulder'], ['left_knee', 'left_ankle']], [['right_elbow', 'right_shoulder'], ['left_ankle', 'left_knee']], [['right_shoulder', 'right_elbow'], ['right_hip', 'right_knee']], [['right_shoulder', 'right_elbow'], ['right_knee', 'right_hip']], [['right_elbow', 'right_shoulder'], ['right_hip', 'right_knee']], [['right_elbow', 'right_shoulder'], ['right_knee', 'right_hip']], [['right_shoulder', 'right_elbow'], ['right_knee', 'right_ankle']], [['right_shoulder', 'right_elbow'], ['right_ankle', 'right_knee']], [['right_elbow', 'right_shoulder'], ['right_knee', 'right_ankle']], [['right_elbow', 'right_shoulder'], ['right_ankle', 'right_knee']], [['right_shoulder', 'right_elbow'], ['mouth_left', 'mouth_right']], [['right_shoulder', 'right_elbow'], ['mouth_right', 'mouth_left']], [['right_elbow', 'right_shoulder'], ['mouth_left', 'mouth_right']], [['right_elbow', 'right_shoulder'], ['mouth_right', 'mouth_left']], [['right_shoulder', 'right_hip'], ['right_elbow', 'right_wrist']], [['right_shoulder', 'right_hip'], ['right_wrist', 'right_elbow']], [['right_hip', 'right_shoulder'], ['right_elbow', 'right_wrist']], [['right_hip', 'right_shoulder'], ['right_wrist', 'right_elbow']], [['right_shoulder', 'right_hip'], ['left_hip', 'left_knee']], [['right_shoulder', 'right_hip'], ['left_knee', 'left_hip']], [['right_hip', 'right_shoulder'], ['left_hip', 'left_knee']], [['right_hip', 'right_shoulder'], ['left_knee', 'left_hip']], [['right_shoulder', 'right_hip'], ['left_knee', 'left_ankle']], [['right_shoulder', 'right_hip'], ['left_ankle', 'left_knee']], [['right_hip', 'right_shoulder'], ['left_knee', 'left_ankle']], [['right_hip', 'right_shoulder'], ['left_ankle', 'left_knee']], [['right_shoulder', 'right_hip'], ['right_hip', 'right_knee']], [['right_shoulder', 'right_hip'], ['right_knee', 'right_hip']], [['right_hip', 'right_shoulder'], ['right_hip', 'right_knee']], [['right_hip', 'right_shoulder'], ['right_knee', 'right_hip']], [['right_shoulder', 'right_hip'], ['right_knee', 'right_ankle']], [['right_shoulder', 'right_hip'], ['right_ankle', 'right_knee']], [['right_hip', 'right_shoulder'], ['right_knee', 'right_ankle']], [['right_hip', 'right_shoulder'], ['right_ankle', 'right_knee']], [['right_shoulder', 'right_hip'], ['mouth_left', 'mouth_right']], [['right_shoulder', 'right_hip'], ['mouth_right', 'mouth_left']], [['right_hip', 'right_shoulder'], ['mouth_left', 'mouth_right']], [['right_hip', 'right_shoulder'], ['mouth_right', 'mouth_left']], [['right_elbow', 'right_wrist'], ['left_hip', 'left_knee']], [['right_elbow', 'right_wrist'], ['left_knee', 'left_hip']], [['right_wrist', 'right_elbow'], ['left_hip', 'left_knee']], [['right_wrist', 'right_elbow'], ['left_knee', 'left_hip']], [['right_elbow', 'right_wrist'], ['left_knee', 'left_ankle']], [['right_elbow', 'right_wrist'], ['left_ankle', 'left_knee']], [['right_wrist', 'right_elbow'], ['left_knee', 'left_ankle']], [['right_wrist', 'right_elbow'], ['left_ankle', 'left_knee']], [['right_elbow', 'right_wrist'], ['right_hip', 'right_knee']], [['right_elbow', 'right_wrist'], ['right_knee', 'right_hip']], [['right_wrist', 'right_elbow'], ['right_hip', 'right_knee']], [['right_wrist', 'right_elbow'], ['right_knee', 'right_hip']], [['right_elbow', 'right_wrist'], ['right_knee', 'right_ankle']], [['right_elbow', 'right_wrist'], ['right_ankle', 'right_knee']], [['right_wrist', 'right_elbow'], ['right_knee', 'right_ankle']], [['right_wrist', 'right_elbow'], ['right_ankle', 'right_knee']], [['right_elbow', 'right_wrist'], ['mouth_left', 'mouth_right']], [['right_elbow', 'right_wrist'], ['mouth_right', 'mouth_left']], [['right_wrist', 'right_elbow'], ['mouth_left', 'mouth_right']], [['right_wrist', 'right_elbow'], ['mouth_right', 'mouth_left']], [['left_hip', 'left_knee'], ['left_knee', 'left_ankle']], [['left_hip', 'left_knee'], ['left_ankle', 'left_knee']], [['left_knee', 'left_hip'], ['left_knee', 'left_ankle']], [['left_knee', 'left_hip'], ['left_ankle', 'left_knee']], [['left_hip', 'left_knee'], ['right_hip', 'right_knee']], [['left_hip', 'left_knee'], ['right_knee', 'right_hip']], [['left_knee', 'left_hip'], ['right_hip', 'right_knee']], [['left_knee', 'left_hip'], ['right_knee', 'right_hip']], [['left_hip', 'left_knee'], ['right_knee', 'right_ankle']], [['left_hip', 'left_knee'], ['right_ankle', 'right_knee']], [['left_knee', 'left_hip'], ['right_knee', 'right_ankle']], [['left_knee', 'left_hip'], ['right_ankle', 'right_knee']], [['left_hip', 'left_knee'], ['mouth_left', 'mouth_right']], [['left_hip', 'left_knee'], ['mouth_right', 'mouth_left']], [['left_knee', 'left_hip'], ['mouth_left', 'mouth_right']], [['left_knee', 'left_hip'], ['mouth_right', 'mouth_left']], [['left_knee', 'left_ankle'], ['right_hip', 'right_knee']], [['left_knee', 'left_ankle'], ['right_knee', 'right_hip']], [['left_ankle', 'left_knee'], ['right_hip', 'right_knee']], [['left_ankle', 'left_knee'], ['right_knee', 'right_hip']], [['left_knee', 'left_ankle'], ['right_knee', 'right_ankle']], [['left_knee', 'left_ankle'], ['right_ankle', 'right_knee']], [['left_ankle', 'left_knee'], ['right_knee', 'right_ankle']], [['left_ankle', 'left_knee'], ['right_ankle', 'right_knee']], [['left_knee', 'left_ankle'], ['mouth_left', 'mouth_right']], [['left_knee', 'left_ankle'], ['mouth_right', 'mouth_left']], [['left_ankle', 'left_knee'], ['mouth_left', 'mouth_right']], [['left_ankle', 'left_knee'], ['mouth_right', 'mouth_left']], [['right_hip', 'right_knee'], ['right_knee', 'right_ankle']], [['right_hip', 'right_knee'], ['right_ankle', 'right_knee']], [['right_knee', 'right_hip'], ['right_knee', 'right_ankle']], [['right_knee', 'right_hip'], ['right_ankle', 'right_knee']], [['right_hip', 'right_knee'], ['mouth_left', 'mouth_right']], [['right_hip', 'right_knee'], ['mouth_right', 'mouth_left']], [['right_knee', 'right_hip'], ['mouth_left', 'mouth_right']], [['right_knee', 'right_hip'], ['mouth_right', 'mouth_left']], [['right_knee', 'right_ankle'], ['mouth_left', 'mouth_right']], [['right_knee', 'right_ankle'], ['mouth_right', 'mouth_left']], [['right_ankle', 'right_knee'], ['mouth_left', 'mouth_right']], [['right_ankle', 'right_knee'], ['mouth_right', 'mouth_left']]]
new_pairs = [[['right_elbow', 'right_shoulder'],['right_shoulder', 'right_hip']],
            [['left_elbow', 'left_shoulder'],['left_shoulder', 'left_hip']],
            [['right_knee', 'left_hip'],['left_hip', 'left_knee']],
            [['right_hip', 'right_knee'],['right_knee', 'right_ankle']],
            [['left_hip', 'left_knee'],['left_knee', 'left_ankle']],
            [['right_wrist', 'right_elbow'],['right_elbow', 'right_shoulder']],
            [['left_wrist', 'left_elbow'],['left_elbow', 'left_shoulder']]]
new_pairs_2 = [[[11, 13], [11, 23]], [[11, 13], [23, 11]], [[13, 11], [11, 23]], [[13, 11], [23, 11]], [[11, 13], [13, 15]], [[11, 13], [15, 13]], [[13, 11], [13, 15]], [[13, 11], [15, 13]], [[11, 13], [12, 14]], [[11, 13], [14, 12]], [[13, 11], [12, 14]], [[13, 11], [14, 12]], [[11, 13], [12, 24]], [[11, 13], [24, 12]], [[13, 11], [12, 24]], [[13, 11], [24, 12]], [[11, 13], [14, 16]], [[11, 13], [16, 14]], [[13, 11], [14, 16]], [[13, 11], [16, 14]], [[11, 13], [23, 25]], [[11, 13], [25, 23]], [[13, 11], [23, 25]], [[13, 11], [25, 23]], [[11, 13], [25, 27]], [[11, 13], [27, 25]], [[13, 11], [25, 27]], [[13, 11], [27, 25]], [[11, 13], [24, 26]], [[11, 13], [26, 24]], [[13, 11], [24, 26]], [[13, 11], [26, 24]], [[11, 13], [26, 28]], [[11, 13], [28, 26]], [[13, 11], [26, 28]], [[13, 11], [28, 26]], [[11, 13], [9, 10]], [[11, 13], [10, 9]], [[13, 11], [9, 10]], [[13, 11], [10, 9]], [[11, 23], [13, 15]], [[11, 23], [15, 13]], [[23, 11], [13, 15]], [[23, 11], [15, 13]], [[11, 23], [12, 14]], [[11, 23], [14, 12]], [[23, 11], [12, 14]], [[23, 11], [14, 12]], [[11, 23], [12, 24]], [[11, 23], [24, 12]], [[23, 11], [12, 24]], [[23, 11], [24, 12]], [[11, 23], [14, 16]], [[11, 23], [16, 14]], [[23, 11], [14, 16]], [[23, 11], [16, 14]], [[11, 23], [23, 25]], [[11, 23], [25, 23]], [[23, 11], [23, 25]], [[23, 11], [25, 23]], [[11, 23], [25, 27]], [[11, 23], [27, 25]], [[23, 11], [25, 27]], [[23, 11], [27, 25]], [[11, 23], [24, 26]], [[11, 23], [26, 24]], [[23, 11], [24, 26]], [[23, 11], [26, 24]], [[11, 23], [26, 28]], [[11, 23], [28, 26]], [[23, 11], [26, 28]], [[23, 11], [28, 26]], [[11, 23], [9, 10]], [[11, 23], [10, 9]], [[23, 11], [9, 10]], [[23, 11], [10, 9]], [[13, 15], [12, 14]], [[13, 15], [14, 12]], [[15, 13], [12, 14]], [[15, 13], [14, 12]], [[13, 15], [12, 24]], [[13, 15], [24, 12]], [[15, 13], [12, 24]], [[15, 13], [24, 12]], [[13, 15], [14, 16]], [[13, 15], [16, 14]], [[15, 13], [14, 16]], [[15, 13], [16, 14]], [[13, 15], [23, 25]], [[13, 15], [25, 23]], [[15, 13], [23, 25]], [[15, 13], [25, 23]], [[13, 15], [25, 27]], [[13, 15], [27, 25]], [[15, 13], [25, 27]], [[15, 13], [27, 25]], [[13, 15], [24, 26]], [[13, 15], [26, 24]], [[15, 13], [24, 26]], [[15, 13], [26, 24]], [[13, 15], [26, 28]], [[13, 15], [28, 26]], [[15, 13], [26, 28]], [[15, 13], [28, 26]], [[13, 15], [9, 10]], [[13, 15], [10, 9]], [[15, 13], [9, 10]], [[15, 13], [10, 9]], [[12, 14], [12, 24]], [[12, 14], [24, 12]], [[14, 12], [12, 24]], [[14, 12], [24, 12]], [[12, 14], [14, 16]], [[12, 14], [16, 14]], [[14, 12], [14, 16]], [[14, 12], [16, 14]], [[12, 14], [23, 25]], [[12, 14], [25, 23]], [[14, 12], [23, 25]], [[14, 12], [25, 23]], [[12, 14], [25, 27]], [[12, 14], [27, 25]], [[14, 12], [25, 27]], [[14, 12], [27, 25]], [[12, 14], [24, 26]], [[12, 14], [26, 24]], [[14, 12], [24, 26]], [[14, 12], [26, 24]], [[12, 14], [26, 28]], [[12, 14], [28, 26]], [[14, 12], [26, 28]], [[14, 12], [28, 26]], [[12, 14], [9, 10]], [[12, 14], [10, 9]], [[14, 12], [9, 10]], [[14, 12], [10, 9]], [[12, 24], [14, 16]], [[12, 24], [16, 14]], [[24, 12], [14, 16]], [[24, 12], [16, 14]], [[12, 24], [23, 25]], [[12, 24], [25, 23]], [[24, 12], [23, 25]], [[24, 12], [25, 23]], [[12, 24], [25, 27]], [[12, 24], [27, 25]], [[24, 12], [25, 27]], [[24, 12], [27, 25]], [[12, 24], [24, 26]], [[12, 24], [26, 24]], [[24, 12], [24, 26]], [[24, 12], [26, 24]], [[12, 24], [26, 28]], [[12, 24], [28, 26]], [[24, 12], [26, 28]], [[24, 12], [28, 26]], [[12, 24], [9, 10]], [[12, 24], [10, 9]], [[24, 12], [9, 10]], [[24, 12], [10, 9]], [[14, 16], [23, 25]], [[14, 16], [25, 23]], [[16, 14], [23, 25]], [[16, 14], [25, 23]], [[14, 16], [25, 27]], [[14, 16], [27, 25]], [[16, 14], [25, 27]], [[16, 14], [27, 25]], [[14, 16], [24, 26]], [[14, 16], [26, 24]], [[16, 14], [24, 26]], [[16, 14], [26, 24]], [[14, 16], [26, 28]], [[14, 16], [28, 26]], [[16, 14], [26, 28]], [[16, 14], [28, 26]], [[14, 16], [9, 10]], [[14, 16], [10, 9]], [[16, 14], [9, 10]], [[16, 14], [10, 9]], [[23, 25], [25, 27]], [[23, 25], [27, 25]], [[25, 23], [25, 27]], [[25, 23], [27, 25]], [[23, 25], [24, 26]], [[23, 25], [26, 24]], [[25, 23], [24, 26]], [[25, 23], [26, 24]], [[23, 25], [26, 28]], [[23, 25], [28, 26]], [[25, 23], [26, 28]], [[25, 23], [28, 26]], [[23, 25], [9, 10]], [[23, 25], [10, 9]], [[25, 23], [9, 10]], [[25, 23], [10, 9]], [[25, 27], [24, 26]], [[25, 27], [26, 24]], [[27, 25], [24, 26]], [[27, 25], [26, 24]], [[25, 27], [26, 28]], [[25, 27], [28, 26]], [[27, 25], [26, 28]], [[27, 25], [28, 26]], [[25, 27], [9, 10]], [[25, 27], [10, 9]], [[27, 25], [9, 10]], [[27, 25], [10, 9]], [[24, 26], [26, 28]], [[24, 26], [28, 26]], [[26, 24], [26, 28]], [[26, 24], [28, 26]], [[24, 26], [9, 10]], [[24, 26], [10, 9]], [[26, 24], [9, 10]], [[26, 24], [10, 9]], [[26, 28], [9, 10]], [[26, 28], [10, 9]], [[28, 26], [9, 10]], [[28, 26], [10, 9]]]
landmark_mapping = {
        0: 'nose',
        1: 'left_eye_inner',
        2: 'left_eye',
        3: 'left_eye_outer',
        4: 'right_eye_inner',
        5: 'right_eye',
        6: 'right_eye_outer',
        7: 'left_ear',
        8: 'right_ear',
        9: 'mouth_left',
        10: 'mouth_right',
        11: 'left_shoulder',
        12: 'right_shoulder',
        13: 'left_elbow',
        14: 'right_elbow',
        15: 'left_wrist',
        16: 'right_wrist',
        17: 'left_pinky_1',
        18: 'right_pinky_1',
        19: 'left_index_1',
        20: 'right_index_1',
        21: 'left_thumb_2',
        22: 'right_thumb_2',
        23: 'left_hip',
        24: 'right_hip',
        25: 'left_knee',
        26: 'right_knee',
        27: 'left_ankle',
        28: 'right_ankle',
        29: 'left_heel',
        30: 'right_heel',
        31: 'left_foot_index',
        32: 'right_foot_index'
    }
y_landmark_mapping = {
        0: 'y_nose',
        1: 'y_left_eye_inner',
        2: 'y_left_eye',
        3: 'y_left_eye_outer',
        4: 'y_right_eye_inner',
        5: 'y_right_eye',
        6: 'y_right_eye_outer',
        7: 'y_left_ear',
        8: 'y_right_ear',
        9: 'y_mouth_left',
        10: 'y_mouth_right',
        11: 'y_left_shoulder',
        12: 'y_right_shoulder',
        13: 'y_left_elbow',
        14: 'y_right_elbow',
        15: 'y_left_wrist',
        16: 'y_right_wrist',
        17: 'y_left_pinky_1',
        18: 'y_right_pinky_1',
        19: 'y_left_index_1',
        20: 'y_right_index_1',
        21: 'y_left_thumb_2',
        22: 'y_right_thumb_2',
        23: 'y_left_hip',
        24: 'y_right_hip',
        25: 'y_left_knee',
        26: 'y_right_knee',
        27: 'y_left_ankle',
        28: 'y_right_ankle',
        29: 'y_left_heel',
        30: 'y_right_heel',
        31: 'y_left_foot_index',
        32: 'y_right_foot_index'
    }
y_landmarks = ['y_nose',
        'y_left_eye_inner',
        'y_left_eye',
        'y_left_eye_outer',
        'y_right_eye_inner',
        'y_right_eye',
        'y_right_eye_outer',
        'y_left_ear',
        'y_right_ear',
        'y_mouth_left',
        'y_mouth_right',
        'y_left_shoulder',
        'y_right_shoulder',
        'y_left_elbow',
        'y_right_elbow',
        'y_left_wrist',
        'y_right_wrist',
        'y_left_pinky_1',
        'y_right_pinky_1',
        'y_left_index_1',
        'y_right_index_1',
        'y_left_thumb_2',
        'y_right_thumb_2',
        'y_left_hip',
        'y_right_hip',
        'y_left_knee',
        'y_right_knee',
        'y_left_ankle',
        'y_right_ankle',
        'y_left_heel',
        'y_right_heel',
        'y_left_foot_index',
        'y_right_foot_index']
reverse_landmark_mapping = {
    'nose': 0,
    'left_eye_inner': 1,
    'left_eye': 2,
    'left_eye_outer': 3,
    'right_eye_inner': 4,
    'right_eye': 5,
    'right_eye_outer': 6,
    'left_ear': 7,
    'right_ear': 8,
    'mouth_left': 9,
    'mouth_right': 10,
    'left_shoulder': 11,
    'right_shoulder': 12,
    'left_elbow': 13,
    'right_elbow': 14,
    'left_wrist': 15,
    'right_wrist': 16,
    'left_pinky_1': 17,
    'right_pinky_1': 18,
    'left_index_1': 19,
    'right_index_1': 20,
    'left_thumb_2': 21,
    'right_thumb_2': 22,
    'left_hip': 23,
    'right_hip': 24,
    'left_knee': 25,
    'right_knee': 26,
    'left_ankle': 27,
    'right_ankle': 28,
    'left_heel': 29,
    'right_heel': 30,
    'left_foot_index': 31,
    'right_foot_index': 32
}
original_list = ['left_shoulder_left_elbow_left_shoulder_left_hip',
       'left_shoulder_left_elbow_left_hip_left_shoulder',
       'left_elbow_left_shoulder_left_shoulder_left_hip',
       'left_elbow_left_shoulder_left_hip_left_shoulder',
       'left_shoulder_left_elbow_right_shoulder_right_hip',
       'left_shoulder_left_elbow_right_hip_right_shoulder',
       'left_elbow_left_shoulder_right_shoulder_right_hip',
       'left_elbow_left_shoulder_right_hip_right_shoulder',
       'left_shoulder_left_elbow_left_knee_left_hip',
       'left_elbow_left_shoulder_left_hip_left_knee',
       'left_shoulder_left_elbow_left_ankle_left_knee',
       'left_elbow_left_shoulder_left_knee_left_ankle',
       'left_shoulder_left_elbow_right_knee_right_hip',
       'left_elbow_left_shoulder_right_hip_right_knee',
       'left_shoulder_left_elbow_right_knee_right_ankle',
       'left_shoulder_left_elbow_right_ankle_right_knee',
       'left_elbow_left_shoulder_right_knee_right_ankle',
       'left_elbow_left_shoulder_right_ankle_right_knee',
       'left_shoulder_left_hip_right_shoulder_right_elbow',
       'left_shoulder_left_hip_right_elbow_right_shoulder',
       'left_hip_left_shoulder_right_shoulder_right_elbow',
       'left_hip_left_shoulder_right_elbow_right_shoulder',
       'left_shoulder_left_hip_left_knee_left_hip',
       'left_hip_left_shoulder_left_hip_left_knee',
       'left_shoulder_left_hip_right_knee_right_hip',
       'left_hip_left_shoulder_right_hip_right_knee',
       'right_shoulder_right_elbow_right_shoulder_right_hip',
       'right_shoulder_right_elbow_right_hip_right_shoulder',
       'right_elbow_right_shoulder_right_shoulder_right_hip',
       'right_elbow_right_shoulder_right_hip_right_shoulder',
       'right_shoulder_right_elbow_left_knee_left_hip',
       'right_elbow_right_shoulder_left_hip_left_knee',
       'right_shoulder_right_elbow_left_ankle_left_knee',
       'right_elbow_right_shoulder_left_knee_left_ankle',
       'right_shoulder_right_elbow_right_knee_right_hip',
       'right_elbow_right_shoulder_right_hip_right_knee',
       'right_shoulder_right_elbow_right_ankle_right_knee',
       'right_elbow_right_shoulder_right_knee_right_ankle',
       'right_shoulder_right_hip_left_knee_left_hip',
       'right_hip_right_shoulder_left_hip_left_knee',
       'right_shoulder_right_hip_right_knee_right_hip',
       'right_hip_right_shoulder_right_hip_right_knee',
       'left_hip_left_knee_left_ankle_left_knee',
       'left_knee_left_hip_left_knee_left_ankle',
       'left_hip_left_knee_right_ankle_right_knee',
       'left_knee_left_hip_right_knee_right_ankle',
       'left_knee_left_ankle_right_knee_right_hip',
       'left_ankle_left_knee_right_hip_right_knee',
       'right_hip_right_knee_right_ankle_right_knee',
       'right_knee_right_hip_right_knee_right_ankle']
new_pairs_50 = [[['left_shoulder', 'left_elbow'], ['left_shoulder', 'left_hip']], 
             [['left_shoulder', 'left_elbow'], ['left_hip', 'left_shoulder']], 
             [['left_elbow', 'left_shoulder'], ['left_shoulder', 'left_hip']], 
             [['left_elbow', 'left_shoulder'], ['left_hip', 'left_shoulder']], 
             [['left_shoulder', 'left_elbow'], ['right_shoulder', 'right_hip']], 
             [['left_shoulder', 'left_elbow'], ['right_hip', 'right_shoulder']], 
             [['left_elbow', 'left_shoulder'], ['right_shoulder', 'right_hip']], 
             [['left_elbow', 'left_shoulder'], ['right_hip', 'right_shoulder']], 
             [['left_shoulder', 'left_elbow'], ['left_knee', 'left_hip']], 
             [['left_elbow', 'left_shoulder'], ['left_hip', 'left_knee']], 
             [['left_shoulder', 'left_elbow'], ['left_ankle', 'left_knee']], 
             [['left_elbow', 'left_shoulder'], ['left_knee', 'left_ankle']], 
             [['left_shoulder', 'left_elbow'], ['right_knee', 'right_hip']], 
             [['left_elbow', 'left_shoulder'], ['right_hip', 'right_knee']], 
             [['left_shoulder', 'left_elbow'], ['right_knee', 'right_ankle']], 
             [['left_shoulder', 'left_elbow'], ['right_ankle', 'right_knee']], 
             [['left_elbow', 'left_shoulder'], ['right_knee', 'right_ankle']], 
             [['left_elbow', 'left_shoulder'], ['right_ankle', 'right_knee']], 
             [['left_shoulder', 'left_hip'], ['right_shoulder', 'right_elbow']], 
             [['left_shoulder', 'left_hip'], ['right_elbow', 'right_shoulder']], 
             [['left_hip', 'left_shoulder'], ['right_shoulder', 'right_elbow']], 
             [['left_hip', 'left_shoulder'], ['right_elbow', 'right_shoulder']], 
             [['left_shoulder', 'left_hip'], ['left_knee', 'left_hip']], 
             [['left_hip', 'left_shoulder'], ['left_hip', 'left_knee']], 
             [['left_shoulder', 'left_hip'], ['right_knee', 'right_hip']], 
             [['left_hip', 'left_shoulder'], ['right_hip', 'right_knee']], 
             [['right_shoulder', 'right_elbow'], ['right_shoulder', 'right_hip']], 
             [['right_shoulder', 'right_elbow'], ['right_hip', 'right_shoulder']], 
             [['right_elbow', 'right_shoulder'], ['right_shoulder', 'right_hip']], 
             [['right_elbow', 'right_shoulder'], ['right_hip', 'right_shoulder']], 
             [['right_shoulder', 'right_elbow'], ['left_knee', 'left_hip']], 
             [['right_elbow', 'right_shoulder'], ['left_hip', 'left_knee']], 
             [['right_shoulder', 'right_elbow'], ['left_ankle', 'left_knee']], 
             [['right_elbow', 'right_shoulder'], ['left_knee', 'left_ankle']], 
             [['right_shoulder', 'right_elbow'], ['right_knee', 'right_hip']], 
             [['right_elbow', 'right_shoulder'], ['right_hip', 'right_knee']],
             [['right_shoulder', 'right_elbow'], ['right_ankle', 'right_knee']], 
             [['right_elbow', 'right_shoulder'], ['right_knee', 'right_ankle']], 
             [['right_shoulder', 'right_hip'], ['left_knee', 'left_hip']], 
             [['right_hip', 'right_shoulder'], ['left_hip', 'left_knee']], 
             [['right_shoulder', 'right_hip'], ['right_knee', 'right_hip']], 
             [['right_hip', 'right_shoulder'], ['right_hip', 'right_knee']], 
             [['left_hip', 'left_knee'], ['left_ankle', 'left_knee']], 
             [['left_knee', 'left_hip'], ['left_knee', 'left_ankle']], 
             [['left_hip', 'left_knee'], ['right_ankle', 'right_knee']], 
             [['left_knee', 'left_hip'], ['right_knee', 'right_ankle']], 
             [['left_knee', 'left_ankle'], ['right_knee', 'right_hip']], 
             [['left_ankle', 'left_knee'], ['right_hip', 'right_knee']], 
             [['right_hip', 'right_knee'], ['right_ankle', 'right_knee']], 
             [['right_knee', 'right_hip'], ['right_knee', 'right_ankle']]]

# ------------------------------------------ JSON HELPER FUNCTIONS ------------------------------------------

def load_json_data():
    # Step 1: Load the data from JSON files
    with open('json_data/standing_2 copy.json', 'r') as f:
        standing_data = json.load(f)

    # with open('mid_squat_2_t3.json', 'r') as f:
    #     mid_squat_data = json.load(f)

    with open('json_data/squatting_2.json', 'r') as f:
        squatting_data = json.load(f)

    return standing_data, squatting_data

def prepare_data_from_json(standing_data, squatting_data):
    # Step 2: Prepare the data
    X = []
    Y = [] # 0: standing, 1: mid_squat, 2: squatting


    # Extract landmark coordinates and labels from the JSON data

    for filename in standing_data:
        # Access the inner objects for each filename
        inner_objects = standing_data[filename]

        #print("Inner Objects:", inner_objects)

    #     # Iterate through the inner objects
        x_temp = []
        y_temp = []
        for index in inner_objects:
            x_temp.append(inner_objects[index])
        x_temp = np.array(x_temp)
        y_temp = np.full((x_temp.shape[0],), 0, dtype=int)
        X.append(x_temp)
        #Y.append(y_temp)
        Y.append(0)

        #print("X:", X)

    # for filename in mid_squat_data:
    #     # Access the inner objects for each filename
    #     inner_objects = mid_squat_data[filename]

    #     #print("Inner Objects:", inner_objects)

    # #     # Iterate through the inner objects
    #     x_temp = []
    #     y_temp = []
    #     for index in inner_objects:
    #         x_temp.append(inner_objects[index])
    #         #y_temp.append(1)
    #     x_temp = np.array(x_temp)
    #     y_temp = np.full((x_temp.shape[0],), 1, dtype=int)
        
    #     X.append(x_temp)
    #     #Y.append(y_temp)
    #     Y.append(1)

        #print("X:", X)

    for filename in squatting_data:
        # Access the inner objects for each filename
        inner_objects = squatting_data[filename]

        #print("Inner Objects:", inner_objects)

    #     # Iterate through the inner objects
        x_temp = []
        y_temp = []
        for index in inner_objects:
            x_temp.append(inner_objects[index])
        x_temp = np.array(x_temp)
        y_temp = np.full((x_temp.shape[0],), 2, dtype=int)
        X.append(x_temp)
        #Y.append(y_temp)
        Y.append(1)

        #print("X:", X)
    
    return X, Y

# ------------------------------------------ CSV HELPER FUNCTIONS ------------------------------------------

def load_csv_data(file_path):
    print("STARTING READING CSV FILE")

    # data = pd.read_csv(file_path)
    # data = pd.read_csv(file_path, low_memory=True)
    file_size = os.path.getsize(file_path)  # Size in bytes

    fraction = 0.01  # Adjust the fraction as needed
    sample_size = int(fraction * file_size)
    data = dd.read_csv(file_path, sample=sample_size)
    # data = dd.read_csv(file_path)
    desired_columns = data.columns[1:]

    #------------------------------NEW NON-VECTORIZED CODE---------------------------------
    

    # Define the desired pose ranges
    pose_ranges = [
        (0, 188),
        (189, 369),
        (370, 523),
        (524, 658),
        (659, 760),
        (761, 904),
        (905, 1006),
        (1007, 1105),
        (1106, 1232),
        (1233, 1371)
    ]

    # Filter the data based on pose ranges and desired columns
    print("STARTING FILTERING DATA")

    filtered_data = data.loc[data['pose_id'].between(0, pose_ranges[-1][1])]
    filtered_data = filtered_data[desired_columns]

    print(filtered_data.columns)


    print("HERE")

    # Create an array of pose_ids
    # pose_ids = filtered_data['pose_id'].values
    # pose_ids = np.arange(1372)
    pose_ids = np.concatenate([np.full(end - start + 1, i) for i, (start, end) in enumerate(pose_ranges)])

    # Create an array of labels for each pose_id
    # labels = np.searchsorted([end for _, end in pose_ranges], pose_ids)
    labels = np.concatenate([np.full(len(pose_data), i) for i, pose_data in enumerate(pose_ranges)])
    

    # Create the X array using values from desired columns
    # X = filtered_data.values
    with ProgressBar():
        X = filtered_data.compute().values


    # Parse the ratios column
    data['ratios'] = data['ratios'].apply(lambda x: np.array(ast.literal_eval(x)))

    # Convert the data to a 2D array
    X = np.stack(data['ratios'].values)
    # last_column = X[:, -1]
    # nested_list = [ast.literal_eval(item) for item in last_column]

    # # Convert the nested list back into a NumPy array and assign it to the last column of X
    # X[:, -1] = np.array(nested_list)
    # for i in range(X.shape[1]):
    #     print(type(X[0, i]))


    # Create the Y array using labels
    # Y = np.concatenate([np.full(len(pose_data), i) for i, pose_data in enumerate(pose_ranges)])
    Y = labels[pose_ids]

    #------------------------------OLD NON-VECTORIZED CODE---------------------------------
    # jj_down = data.loc[(data['pose_id'] >= 0) & (data['pose_id'] <= 188), desired_columns]
    # jj_up = data.loc[(data['pose_id'] >= 189) & (data['pose_id'] <= 369), desired_columns]
    # pull_down = data.loc[(data['pose_id'] >= 370) & (data['pose_id'] <= 523), desired_columns]
    # pull_up = data.loc[(data['pose_id'] >= 524) & (data['pose_id'] <= 658), desired_columns]
    # push_down = data.loc[(data['pose_id'] >= 659) & (data['pose_id'] <= 760), desired_columns]
    # push_up = data.loc[(data['pose_id'] >= 761) & (data['pose_id'] <= 904), desired_columns]
    # sit_down = data.loc[(data['pose_id'] >= 905) & (data['pose_id'] <= 1006), desired_columns]
    # sit_up = data.loc[(data['pose_id'] >= 1007) & (data['pose_id'] <= 1105), desired_columns]
    # squat_down = data.loc[(data['pose_id'] >= 1106) & (data['pose_id'] <= 1232), desired_columns]
    # squat_up = data.loc[(data['pose_id'] >= 1233) & (data['pose_id'] <= 1371), desired_columns]

    # X = np.concatenate([jj_down.values, jj_up.values, pull_down.values, pull_up.values,
    #                 push_down.values, push_up.values, sit_down.values, sit_up.values,
    #                 squat_down.values, squat_up.values], axis=0)
    # # X = np.concatenate([jj_down.values, jj_up.values, pull_down.values, pull_up.values,
    # #                 push_down.values, push_up.values, squat_down.values, squat_up.values], axis=0)
    # # X = np.concatenate([squat_down.values, squat_up.values], axis=0)


    # # Create Y array with corresponding labels using one-hot encoding
    # Y = np.array([0] * len(jj_down) + [1] * len(jj_up) + [2] * len(pull_down) + [3] * len(pull_up) +
    #             [4] * len(push_down) + [5] * len(push_up) + [6] * len(sit_down) + [7] * len(sit_up) +
    #             [8] * len(squat_down) + [9] * len(squat_up))
    
    # # Y = np.array([0] * len(jj_down) + [1] * len(jj_up) + [2] * len(pull_down) + [3] * len(pull_up) +
    # #             [4] * len(push_down) + [5] * len(push_up) + [6] * len(squat_down) + [7] * len(squat_up))
    # # Y = np.array([0] * len(squat_down) + [1] * len(squat_up))

    return X, Y

def convert_angle_csv(file_path, pair, pose_id, landmarks):
    # landmarks = pd.read_csv(file_path)
    # pair = [["right_elbow", "right_shoulder"],["right_shoulder", "right_hip"]]
    # cell_value = landmarks.loc[landmarks['pose_id'] == pose_id, 'x_right_elbow'].values[0]

    point_A1 = np.array([landmarks.loc[landmarks['pose_id'] == pose_id, "x_" + pair[0][0]].values[0],
                        landmarks.loc[landmarks['pose_id'] == pose_id, "y_" + pair[0][0]].values[0],
                        landmarks.loc[landmarks['pose_id'] == pose_id, "z_" + pair[0][0]].values[0]])
    
    point_A2 = np.array([landmarks.loc[landmarks['pose_id'] == pose_id, "x_" + pair[0][1]].values[0],
                        landmarks.loc[landmarks['pose_id'] == pose_id, "y_" + pair[0][1]].values[0],
                        landmarks.loc[landmarks['pose_id'] == pose_id, "z_" + pair[0][1]].values[0]])
    
    point_B1 = np.array([landmarks.loc[landmarks['pose_id'] == pose_id, "x_" + pair[1][0]].values[0],
                        landmarks.loc[landmarks['pose_id'] == pose_id, "y_" + pair[1][0]].values[0],
                        landmarks.loc[landmarks['pose_id'] == pose_id, "z_" + pair[1][0]].values[0]])
    
    point_B2 = np.array([landmarks.loc[landmarks['pose_id'] == pose_id, "x_" + pair[1][1]].values[0],
                        landmarks.loc[landmarks['pose_id'] == pose_id, "y_" + pair[1][1]].values[0],
                        landmarks.loc[landmarks['pose_id'] == pose_id, "z_" + pair[1][1]].values[0]])
    # return cell_value
    # point_A1 = np.array([landmarks[pair[0][0]].x, landmarks[pair[0][0]].y, landmarks[pair[0][0]].z])
    # point_A2 = np.array([landmarks[pair[0][1]].x, landmarks[pair[0][1]].y, landmarks[pair[0][1]].z])

    # point_B1 = np.array([landmarks[pair[1][0]].x, landmarks[pair[1][0]].y, landmarks[pair[1][0]].z])
    # point_B2 = np.array([landmarks[pair[1][1]].x, landmarks[pair[1][1]].y, landmarks[pair[1][1]].z])

    # print("A1:", point_A1)
    # print("A2:", point_A2)
    # print("B1:", point_B1)
    # print("B2:", point_B2)



    # Calculate the vector representations
    vector_A = point_A2 - point_A1
    vector_B = point_B2 - point_B1

    #print("A:", vector_A, " B:", vector_B)

    # Calculate the dot product
    dot_product = np.dot(vector_A, vector_B)

    # Calculate the magnitudes of the vectors
    magnitude_A = np.linalg.norm(vector_A)
    magnitude_B = np.linalg.norm(vector_B)

    # Calculate the angle between the vectors in radians
    angle_rad = np.arccos(dot_product / (magnitude_A * magnitude_B))

    # Convert the angle to degrees
    #print("Sup")
    return 180-np.degrees(angle_rad)

def vectorized_convert_angle_csv(pair, landmarks):
    point_A1 = np.array(landmarks.loc[:, "x_" + pair[0][0]])
    point_A1 = np.vstack((point_A1, landmarks.loc[:, "y_" + pair[0][0]]))
    point_A1 = np.vstack((point_A1, landmarks.loc[:, "z_" + pair[0][0]]))
    point_A1 = np.transpose(point_A1)

    point_A2 = np.array(landmarks.loc[:, "x_" + pair[0][1]])
    point_A2 = np.vstack((point_A2, landmarks.loc[:, "y_" + pair[0][1]]))
    point_A2 = np.vstack((point_A2, landmarks.loc[:, "z_" + pair[0][1]]))
    point_A2 = np.transpose(point_A2)

    point_B1 = np.array(landmarks.loc[:, "x_" + pair[1][0]])
    point_B1 = np.vstack((point_B1, landmarks.loc[:, "y_" + pair[1][0]]))
    point_B1 = np.vstack((point_B1, landmarks.loc[:, "z_" + pair[1][0]]))
    point_B1 = np.transpose(point_B1)

    point_B2 = np.array(landmarks.loc[:, "x_" + pair[1][1]])
    point_B2 = np.vstack((point_B2, landmarks.loc[:, "y_" + pair[1][1]]))
    point_B2 = np.vstack((point_B2, landmarks.loc[:, "z_" + pair[1][1]]))
    point_B2 = np.transpose(point_B2)

     # Calculate the vector representations
    vector_A = point_A2 - point_A1
    vector_B = point_B2 - point_B1


    # Calculate the dot product
    # dot_product = np.dot(vector_A, vector_B)
    dot_product = np.einsum('ij,ij->i', vector_A, vector_B)



    # Calculate the magnitudes of the vectors
    # magnitude_A = np.linalg.norm(vector_A)
    # magnitude_B = np.linalg.norm(vector_B)

    magnitude_A = np.linalg.norm(vector_A, axis=1)
    magnitude_B = np.linalg.norm(vector_B, axis=1)

    # Calculate the angle between the vectors in radians
    angle_rad = np.arccos(dot_product / (magnitude_A * magnitude_B))
    # angle_rad = np.arccos(np.sum(vector_A * vector_B, axis=1) / (magnitude_A * magnitude_B))


    # Convert the angle to degrees
    #print("Sup")
    return 180-np.degrees(angle_rad)

def calculate_angle(pair, landmarks):
    # column_name = pair[0][0] + "_" + pair[0][1] + "_" + pair[1][0] + "_" + pair[1][1]
    # landmarks_subset = landmarks[["x_" + pair[0][0], "y_" + pair[0][0], "z_" + pair[0][0], "x_" + pair[0][1], "y_" + pair[0][1], "z_" + pair[0][1], "x_" + pair[1][0], "y_" + pair[1][0], "z_" + pair[1][0], "x_" + pair[1][1], "y_" + pair[1][1], "z_" + pair[1][1]]]
    # print("LANDMARK SUBSET:", landmarks_subset)
    # vectors = landmarks_subset.values.reshape((-1, 2, 3))
    # print("VECTORS:", vectors, "LENGTH:", vectors.shape)
    # vector_diff = np.diff(vectors, axis=1)
    # angles = np.arctan2(vector_diff[:, :, 1], vector_diff[:, :, 0])
    # angles = np.degrees(angles)
    # angles_diff = np.diff(angles, axis=1)
    # print('ANGLES DIFF:', angles_diff)
    # mean_angles_diff = np.nanmean(angles_diff, axis=1)  # Use nanmean to handle empty slices
    # return column_name, mean_angles_diff

    column_name = pair[0][0] + "_" + pair[0][1] + "_" + pair[1][0] + "_" + pair[1][1]
    pose_ids = landmarks['pose_id'].unique()
    mask = landmarks['pose_id'].isin(pose_ids)
    
    pair_landmarks = landmarks.loc[mask, ["x_" + pair[0][0], "y_" + pair[0][0], "z_" + pair[0][0],
                                          "x_" + pair[0][1], "y_" + pair[0][1], "z_" + pair[0][1],
                                          "x_" + pair[1][0], "y_" + pair[1][0], "z_" + pair[1][0],
                                          "x_" + pair[1][1], "y_" + pair[1][1], "z_" + pair[1][1]]].values

    point_A1 = pair_landmarks[:, 0:3]
    point_A2 = pair_landmarks[:, 3:6]
    point_B1 = pair_landmarks[:, 6:9]
    point_B2 = pair_landmarks[:, 9:12]

    vector_A = point_A2 - point_A1
    vector_B = point_B2 - point_B1

    dot_product = np.einsum('ij,ij->i', vector_A, vector_B)
    magnitude_A = np.linalg.norm(vector_A, axis=1)
    magnitude_B = np.linalg.norm(vector_B, axis=1)

    angle_rad = np.arccos(dot_product / (magnitude_A * magnitude_B))
    angle_deg = np.degrees(angle_rad)
    # global iterations
    # print("Iteration:", iterations)
    # iterations += 1
    return column_name, 180 - angle_deg

def convert_angle(landmarks, pair):
    #print("Here now")
    #print("TEST:", landmarks[pair[0][0]].x, landmarks[pair[0][0]].y, landmarks[pair[0][0]].z)
    point_A1 = np.array([landmarks[pair[0][0]].x, landmarks[pair[0][0]].y, landmarks[pair[0][0]].z])
    point_A2 = np.array([landmarks[pair[0][1]].x, landmarks[pair[0][1]].y, landmarks[pair[0][1]].z])

    point_B1 = np.array([landmarks[pair[1][0]].x, landmarks[pair[1][0]].y, landmarks[pair[1][0]].z])
    point_B2 = np.array([landmarks[pair[1][1]].x, landmarks[pair[1][1]].y, landmarks[pair[1][1]].z])

    #print("A1:", point_A1)

    # Calculate the vector representations
    vector_A = point_A2 - point_A1
    vector_B = point_B2 - point_B1

    #print("A:", vector_A, " B:", vector_B)

    # Calculate the dot product
    dot_product = np.dot(vector_A, vector_B)

    # Calculate the magnitudes of the vectors
    magnitude_A = np.linalg.norm(vector_A)
    magnitude_B = np.linalg.norm(vector_B)

    # Calculate the angle between the vectors in radians
    angle_rad = np.arccos(dot_product / (magnitude_A * magnitude_B))

    # Convert the angle to degrees
    #print("Sup")
    return 180 - np.degrees(angle_rad)

def generate_relative_ratios(file_path, observation):
    # Read from the CSV file
    # file_size = os.path.getsize(file_path)  # Size in bytes

    # fraction = 0.01  # Adjust the fraction as needed
    # sample_size = int(fraction * file_size)
    # landmark_data = dd.read_csv(file_path, sample=sample_size)

    landmark_data = pd.read_csv(file_path) # using pandas instead of dask


    # print("START")


    # y_values = landmark_data[y_landmarks].values
    y_values = landmark_data.loc[observation, y_landmarks].values
    # Perform Min-Max scaling on the y-values using vectorized operations
    min_values = y_values.min(axis=0)
    max_values = y_values.max(axis=0)
    normalized_y_values = (y_values - min_values) / (max_values - min_values)

    # Repeat the y_landmarks list to match the shape of normalized_y_values
    # expanded_landmarks = np.tile(np.array(y_landmarks), (normalized_y_values.shape[0], 1))

    landmark_names = np.array(y_landmarks)
    # Create the normalized 2D array
    # normalized_pose_features_array = np.column_stack((normalized_y_values, expanded_landmarks))
    observation_features = np.column_stack((normalized_y_values, landmark_names))


    # Print the normalized pose features
    print(observation_features)
    print(type(observation_features))

    return observation_features

def correct_csv_format(file_path):
    # Read the CSV file and correct the format of the last column
    corrected_rows = []
    with open(file_path, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            last_column = row[-1]
            print(last_column)  # Debugging print statement
            if last_column == 'ratios':
                continue
            # Parse the string as a JSON array
            corrected_last_column = json.loads(last_column)
            corrected_rows.append(row[:-1] + [corrected_last_column])

    # Write the corrected data back to the CSV file
    with open(file_path, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(corrected_rows)
    
def add_column(landmarks_file_path, angles_file_path):
    angles_data = pd.read_csv(angles_file_path)
    landmarks_data = pd.read_csv(landmarks_file_path)

    result = np.array(landmarks_data['y_nose'])/np.array(landmarks_data['y_left_knee'])
    # ratio_data = pd.DataFrame({'y_nose/y_left_knee': result})
    angles_data['y_nose/y_left_knee'] = result
    angles_data.to_csv('archive_time_series/angles_220.csv', index=False)
    # print(angles_data)

def setup_features_csv(features_file_path):
    pairs = generating_pairs() # generates all 220 pairs using the choice vectors

    # -------------------------------------- CALCULATE ANGLES AND ADD TO CSV --------------------------------------

    landmarks = pd.read_csv('archive_time_series/landmarks.csv')
    angles = pd.read_csv(features_file_path)
    print(angles.shape)
    new_column_data = []
    pair_num = 1

    # ______________________________ NEW CODE WITH FOR LOOP ____________________________________

    for pair in pairs:
        print("_______________Pair_____________:", pair_num)
        new_column_data = vectorized_convert_angle_csv(pair, landmarks)
        new_column_name = pair[0][0] + "_" + pair[0][1] + "_" + pair[1][0] + "_" + pair[1][1]
        new_column = pd.Series(new_column_data, name=new_column_name)
        angles = pd.concat([angles, new_column], axis=1)
        pair_num += 1
    
    result = np.array(landmarks['y_nose']) / np.array(landmarks['y_left_knee'])
    new_column = pd.Series(result, name='y_nose/y_left_knee')
    angles = pd.concat([angles, new_column], axis=1)
    angles.to_csv(features_file_path, index=False)

def add_exercises():
    pass


# ------------------------------------------ PAIR HELPER FUNCTIONS ------------------------------------------

def generating_pairs():

    # all neighboring angles. Take all the joints and compute a joint for 

    landmark_mapping = {
            # 0: 'nose',
            # 1: 'left_eye_inner',
            # 2: 'left_eye',
            # 3: 'left_eye_outer',
            # 4: 'right_eye_inner',
            # 5: 'right_eye',
            # 6: 'right_eye_outer',
            # 7: 'left_ear',
            # 8: 'right_ear',
            9: 'mouth_left',
            10: 'mouth_right',
            11: 'left_shoulder',
            12: 'right_shoulder',
            13: 'left_elbow',
            14: 'right_elbow',
            15: 'left_wrist',
            16: 'right_wrist',
            # 17: 'left_pinky_1',
            # 18: 'right_pinky_1',
            # 19: 'left_index_1',
            # 20: 'right_index_1',
            # 21: 'left_thumb_2',
            # 22: 'right_thumb_2',
            23: 'left_hip',
            24: 'right_hip',
            25: 'left_knee',
            26: 'right_knee',
            27: 'left_ankle',
            28: 'right_ankle',
            # 29: 'left_heel',
            # 30: 'right_heel',
            # 31: 'left_foot_index',
            # 32: 'right_foot_index'
        }

    # Exclude face landmarks
    #excluded_landmarks = ['nose', 'left_eye_inner', 'left_eye', 'left_eye_outer', 'right_eye_inner', 'right_eye', 'right_eye_outer', 'left_ear', 'right_ear', 'mouth_left', 'mouth_right']
    
    vectors = [[['left_shoulder', 'left_elbow'], ['left_elbow', 'left_shoulder']],
               [['left_shoulder', 'left_hip'], ['left_hip', 'left_shoulder']],
               [['left_elbow', 'left_wrist'], ['left_wrist', 'left_elbow']],
               [['right_shoulder', 'right_elbow'], ['right_elbow', 'right_shoulder']],
               [['right_shoulder', 'right_hip'], ['right_hip', 'right_shoulder']],
               [['right_elbow', 'right_wrist'], ['right_wrist', 'right_elbow']],
               [['left_hip', 'left_knee'], ['left_knee', 'left_hip']],
               [['left_knee', 'left_ankle'], ['left_ankle', 'left_knee']],
               [['right_hip', 'right_knee'], ['right_knee', 'right_hip']],
               [['right_knee', 'right_ankle'], ['right_ankle', 'right_knee']],
               [['mouth_left', 'mouth_right'], ['mouth_right', 'mouth_left']]]
    # Generate all possible combinations of non-face landmark pairs
    non_face_pairs = []
    # landmarks = [key for key, value in landmark_mapping.items() if value not in excluded_landmarks]
    landmarks = [key for key, value in landmark_mapping.items()]

    # _____________________________________________COMBINATIONS____________________________________________________
    # for pair in itertools.combinations(landmarks, 4):
    #     p1 = [landmark_mapping[pair[0]], landmark_mapping[pair[1]]]
    #     p2 = [landmark_mapping[pair[2]], landmark_mapping[pair[3]]]
    #     non_face_pairs.append([p1, p2])
    combinations = list(itertools.combinations(vectors, 2))
    for comb in combinations:
        pairs = list(itertools.product(*comb))
        non_face_pairs.extend([list(pair) for pair in pairs])
    # _____________________________________________PERMUTATIONS____________________________________________________
    # for perm in itertools.permutations(landmarks, 4):
    #     p1 = [landmark_mapping[perm[0]], landmark_mapping[perm[1]]]
    #     p2 = [landmark_mapping[perm[2]], landmark_mapping[perm[3]]]
    #     non_face_pairs.append([p1, p2])

    # Return the non-face pairs
    return non_face_pairs

def convert_into_numeric_pairs():
    converted_pairs = [[[reverse_landmark_mapping[point] for point in subpair] for subpair in pair] for pair in new_pairs]
    print(converted_pairs)
    return converted_pairs


# numeric to text conversion
def convert_into_text_pairs():
    landmark_pairs = []
    for pair in default_pairs:
        landmark_pair = [[landmark_mapping[point] for point in subpair] for subpair in pair]
        landmark_pairs.append(landmark_pair)

    return landmark_pairs

# ------------------------------------------ STRING HELPER FUNCTIONS ------------------------------------------
def split_string_by_nth_underscore(string, n):
    parts = string.split("_")
    if len(parts) < n + 1:
        return None
    return ["_".join(parts[:n]), "_".join(parts[n:])]

def split_strings_in_list(strings):
    result = []
    for string in strings:
        first_part, second_part = split_string_by_nth_underscore(string, 4)
        if first_part is not None and second_part is not None:
            sub_list = [split_string_by_nth_underscore(first_part, 2), split_string_by_nth_underscore(second_part, 2)]
            result.append(sub_list)
    return result

def convert_string_representation(original_string):
    cleaned_string = original_string.strip()  # Remove leading/trailing whitespace
    cleaned_string = cleaned_string.replace("[[", "")  # Remove opening double brackets
    cleaned_string = cleaned_string.replace("]]", "")  # Remove closing double brackets
    elements = cleaned_string.split("], [")  # Split the string into individual elements
    updated_list = [list(map(float, elem.replace("'", "").split(", "))) for elem in elements]  # Split each element, remove quotes and convert the values to float
    return updated_list

if __name__ == "__main__":
    # correct_csv_format('archive/angles_trial_220.csv')
    setup_features_csv('archive_time_series/angles_trial.csv')
   