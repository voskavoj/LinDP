import copy
import sys

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy.signal import dfreqresp

from apps.source import steps
from apps.source.data_processing import rolling_average, rolling_average_segments
from apps.source.plotting import plot_segments_axis
from apps.source.steps import find_heelstrikes_from_z, fit_step_with_sine
from source.data_processing import clean_data, split_data_into_segments, clean_segments, clean_segment_angles
from source.plotting import plot_segment_data
from source.data_processing import tsv_to_dataframe


class Step:
    def __init__(self, df, direction, num=None):
        self.absolute = df
        self.relative = self.normalize_time(self.absolute)
        self.travel_direction = direction
        self.step_number = num

    @staticmethod
    def normalize_time(absolute):
        normalized = copy.deepcopy(absolute)
        normalized["Time"] = normalized["Time"] - normalized["Time"].iloc[0]
        normalized["Time"] = normalized["Time"].round(2)
        return normalized

def open_and_plot(path):
    df = tsv_to_dataframe(path)
    df = clean_data(df)

    segments = split_data_into_segments(df)
    segments = clean_segments(segments)
    segments = clean_segment_angles(segments)
    segments = rolling_average_segments(segments)

    heelstrikes = find_heelstrikes_from_z(segments)

    plot_segments_axis(segments, "Time", heelstrikes)
    # plot_segment_data(segments, heelstrikes)

    i = 0
    # fit_step_with_sine(segments[i], heelstrikes[i])

## identify steps

    # COMPARISON - DOES NOT WORK
    # seg_step_directions = []
    # for seg, heels in zip(segments, heelstrikes):
    #     no_of_half_steps = len(heels - 1)
    #     step_directions = []
    #
    #     for i in range(no_of_half_steps - 1):
    #         start, end = heels[i], heels[i + 1]
    #         if seg["Y"].iloc[start] > seg["Y"].iloc[end]:
    #             step_directions.append(1)
    #         else:
    #             step_directions.append(-1)
    #
    #     step_directions.append(0)
    #     seg_step_directions.append(step_directions)

    # plt.figure()


    # LINEAR FIT
    def lin_fit(x, a, b, dt):
        return a * (x - dt) + b

    seg_step_legs = []
    segment_directions = []
    for seg, heels in zip(segments, heelstrikes):
        no_of_half_steps = len(heels) - 1
        step_legs = []

        # get the Segment direction of travel from X axis trend (positive forward)
        segment_direction = "forward" if np.polyfit(seg["Time"], seg["X"], 1)[0] >= 0 else "backward"
        segment_directions.append(segment_direction)

        for i in range(no_of_half_steps):
            start, end = heels[i], heels[i + 1]

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
                step_leg = "left" if segment_direction == "forward" else "right"
            else:
                step_leg = "right" if segment_direction == "forward" else "left"

            # colors = {"indefinite": "black", "left": "blue", "right": "green"}
            # plt.plot(seg["Time"].iloc[start:end], seg["Y"].iloc[start:end], color=colors[step_leg])

            step_legs.append(step_leg)

        step_legs.append("indefinite")
        seg_step_legs.append(step_legs)

    plot_segment_data(segments, heelstrikes, seg_step_legs)

    steps = []
    for seg, heels, legs, segment_direction in zip(segments, heelstrikes, seg_step_legs, segment_directions):
        no_of_half_steps = len(heels) - 1

        i = 0
        while True:  # let's go with RIGHT as the starting foot
            if i >= no_of_half_steps:
                break

            if not legs[i] == "right":
                i += 1
                continue
            else:  # we have a right foot
                if legs[i + 1] == "left":  # if next step is left, join them together and skip one iteration
                    start, end = heels[i], heels[i + 2]
                    step_df = (seg.iloc[start:end+1])
                    step_df = step_df.reset_index(drop=True)  # join the steps together and make a new df

                    steps.append(Step(step_df, segment_direction))

                    i += 2
                    continue
                else:  # next step is right again or indefinite
                    i += 1
                    continue


    # try to compute average
    dfs = [step.relative for step in steps]  # your dataframes

    # Set Time as index
    dfs = [df.set_index("Time") for df in dfs]

    # Concatenate on Time
    # combined = pd.concat(dfs, axis=1)

    # Average across rows (ignores missing values automatically)
    avg = pd.concat(dfs).groupby(level=0).mean().reset_index()
    print(avg.head())

    # result = avg.reset_index(name="X_avg")

    plt.figure()
    for s in steps:
        plt.plot(s.absolute["Time"], s.absolute["Roll"])


    plt.figure(figsize=(15, 10))
    plt.tight_layout(pad=2)
    i = 1
    for y in ["Roll", "Pitch", "Yaw"]:
        plt.subplot(3, 1, i)
        plt.grid(True, linestyle=':')
        for step in steps:
            plt.plot(step.relative["Time"], step.relative[y], color="gray")
        plt.plot(avg["Time"], avg[y], color="orange")
        plt.title(y)
        plt.ylabel(f"{y} (°)")
        i += 1






if __name__ == "__main__":
    # if len(sys.argv) >= 2:
    #     path = sys.argv[1]
    #     open_and_plot(path)
    # else:
    #     while True:
    #         path = input("Vloz cestu na soubor :)\n")
    #         open_and_plot(path)

    for name in ["eli", "ani", "anna"]:
        open_and_plot(f"../data/{name}_6D.tsv")

    plt.show()


