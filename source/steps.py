import numpy as np
import pandas as pd
from pandas import DataFrame
from scipy.signal import argrelextrema

from source.data_processing import normalize_time


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


def lin_fit(x, a, b, dt):
    return a * (x - dt) + b


def identify_segment_travel_direction(seg: Segment):
    return "forward" if np.polyfit(seg["Time"], seg["X"], 1)[0] >= 0 else "backward"


def identify_segment_step_legs(seg: Segment):
        no_of_half_steps = len(seg.heelstrikes) - 1
        step_legs = []

        for i in range(no_of_half_steps):
            start, end = seg.heelstrikes[i], seg.heelstrikes[i + 1]

            half_step_duration = seg['Time'].iloc[end] - seg['Time'].iloc[start]
            half_step_distance = seg["Y"].iloc[end] - seg["Y"].iloc[start]
            a = half_step_distance / half_step_duration
            b = seg["Y"].iloc[start]
            dt = seg['Time'].iloc[start]

            cnt_above_below = 0
            for j in range(start, end):
                t, y = seg["Time"].iloc[j], seg["Y"].iloc[j]

                if y > lin_fit(t, a, b, dt):
                    cnt_above_below += 1
                else:
                    cnt_above_below -= 1

            confidence = 0.75
            # check if we are confident in the direction
            if abs(cnt_above_below) / (end - start) <= confidence:
                step_leg = "indefinite"
            elif cnt_above_below > 0:  # identify half-step leg by counter and overall direction of travel (Y is not flipped, but legs can be)
                step_leg = "left" if seg.travel_direction == "forward" else "right"
            else:
                step_leg = "right" if seg.travel_direction == "forward" else "left"

            step_legs.append(step_leg)

        step_legs.append("indefinite")
        return step_legs

def extract_steps_from_segments(segments: list[Segment]) -> list[Step]:
    steps, step_cnt = [], 0

    for seg in segments:
        no_of_half_steps = len(seg.heelstrikes) - 1

        i = 0
        while True:  # let's go with RIGHT as the starting foot
            if i >= no_of_half_steps:
                break

            if not seg.step_legs[i] == "right":
                i += 1
                continue
            else:  # we have a right foot
                if seg.step_legs[i + 1] == "left":  # if next step is left, join them together and skip one iteration
                    start, end = seg.heelstrikes[i], seg.heelstrikes[i + 2]
                    step_df = (seg.df.iloc[start:end + 1])
                    step_df = step_df.reset_index(drop=True)  # join the steps together and make a new df

                    step_df_normalized = normalize_time(step_df)

                    steps.append(Step(step_df, step_df_normalized, seg.travel_direction, step_cnt := step_cnt + 1))

                    i += 2
                    continue
                else:  # next step is right again or indefinite
                    i += 1
                    continue

    return steps

def interpolate_df(df: DataFrame):
    # Set Time as index
    df = df.set_index("Time")

    # Create a full 10 ms time index
    full_time_index = np.arange(
        df.index.min(),
        df.index.max() + 0.01,
        0.01
    )

    # Reindex to include missing timestamps
    df = df.reindex(full_time_index)

    # Interpolate linearly
    df_interpolated = df.interpolate(
        method="linear",
        limit_direction="both"
    )

    # Restore Time column
    df_interpolated = df_interpolated.reset_index().rename(
        columns={"index": "Time"}
    )

    return df_interpolated

def compute_average_step(steps: list[Step], crop_to_shortest=False) -> Step:
    # try to compute average
    dfs = [interpolate_df(step.df) for step in steps]  # dataframes

    # Set Time as index
    dfs = [df.set_index("Time") for df in dfs]

    if crop_to_shortest:
        common_index = dfs[0].index
        for df in dfs[1:]:
            common_index = common_index.intersection(df.index)
        dfs = [df.loc[common_index] for df in dfs]

    # Average across rows (ignores missing values automatically)
    avg = pd.concat(dfs).groupby(level=0).mean().reset_index()

    return Step(avg, avg, "", len(steps))


def calculate_average_maximum_derivation(steps:list[Step]) -> list:

    avg_max_derivation = [0.0, 0.0, 0.0]

    for i, axis in enumerate(["Roll", "Pitch", "Yaw"]):
        for step in steps:
            # compute derivation
            dxtx = step.df[axis].diff() / step.df['Time'].diff()
            avg_max_derivation[i] += np.max(dxtx.abs())

        avg_max_derivation[i] = avg_max_derivation[i] / len(steps)

    return avg_max_derivation


def filter_out_steps_by_derivation(steps: list[Step], axis: str, deriv_threshold: float) -> tuple[list[Step], list[Step]]:

    if len(steps) == 0:
        return [], []

    kept_steps, dropped_steps = list(), list()

    for step in steps:
        # compute derivation
        dxtx = step.df[axis].diff() / step.df['Time'].diff()

        if any(dxtx.abs() > deriv_threshold):
            dropped_steps.append(step)
        else:
            kept_steps.append(step)


    return kept_steps, dropped_steps


def filter_out_steps_by_density(steps: list[Step], density_threshold: float) -> tuple[list[Step], list[Step]]:

    if len(steps) == 0:
        return [], []

    kept_steps, dropped_steps = list(), list()

    for step in steps:
        density = step.df.shape[0] / (step.df["Time"].iloc[-1] - step.df["Time"].iloc[0])

        if density >= density_threshold:
            kept_steps.append(step)
        else:
            dropped_steps.append(step)

    return kept_steps, dropped_steps


def auto_filter_steps(steps: list[Step], log_name=""):
    kept_steps, dropped_steps = list(), list()

    threshold_density = 80
    threshold_deriv_r = 80
    threshold_deriv_p = 60
    threshold_deriv_y = 110
    threshold_deriv_as_frac_of_avg = 1.3

    # filter by density
    kept_steps, dropped_steps_d = filter_out_steps_by_density(steps, threshold_density)
    dropped_steps.extend(dropped_steps_d)

    # filter by derivation
    avg_deriv_r, avg_deriv_p, avg_deriv_y = calculate_average_maximum_derivation(steps)

    kept_steps, dropped_steps_r = filter_out_steps_by_derivation(kept_steps, "Roll", max(threshold_deriv_r,
                                                                                         avg_deriv_r * threshold_deriv_as_frac_of_avg))
    kept_steps, dropped_steps_p = filter_out_steps_by_derivation(kept_steps, "Pitch", max(threshold_deriv_p,
                                                                                          avg_deriv_p * threshold_deriv_as_frac_of_avg))
    kept_steps, dropped_steps_y = filter_out_steps_by_derivation(kept_steps, "Yaw", max(threshold_deriv_y,
                                                                                        avg_deriv_y * threshold_deriv_as_frac_of_avg))
    dropped_steps.extend([*dropped_steps_r, *dropped_steps_p, *dropped_steps_y])

    # report statistics
    if log_name:
        d, r, p, y = len(dropped_steps_d), len(dropped_steps_r), len(dropped_steps_p), len(dropped_steps_y)
        col = '\033[93m' if len(kept_steps) / len(steps) < 0.8 else ""  # '\033[92m'
        print(
            col + f"{log_name}:\t{len(kept_steps):02.0f}/{len(steps):02.0f} ({round(100 * len(kept_steps) / len(steps)):03.0f}%) D:{d} R:{r} P:{p} Y:{y} | average r: {round(avg_deriv_r)} p: {round(avg_deriv_p)} y: {round(avg_deriv_y)}" + '\033[0m')

    return kept_steps, dropped_steps

