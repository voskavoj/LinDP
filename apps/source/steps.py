import numpy as np
from pandas import DataFrame
from scipy.signal import argrelextrema


class Segment:
    step_leg_colors = {"indefinite": "black", "left": "blue", "right": "green"}

    def __init__(self, segment_df: DataFrame):
        self.df = segment_df
        self.heelstrikes = None
        self.travel_direction = None
        self.step_legs = None

    # make class subscriptable
    def __getitem__(self, item):
        return self.df[item]


class Step:
    def __init__(self, df_abs: DataFrame, df_rel: DataFrame, direction: str, number: int):
        self.df = df_rel  # normalized
        self.df_rel = self.df  # alias
        self.df_abs = df_abs
        self.travel_direction = direction
        self.step_number = number

    # make class subscriptable
    def __getitem__(self, item):
        return self.df[item]


def find_heelstrikes_from_z(df: DataFrame):
    neighbors = 15

    return argrelextrema(df["Z"].values, np.less, order=neighbors)[0]      # np.less for minima
