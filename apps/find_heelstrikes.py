import sys

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from apps.source.data_processing import rolling_average, rolling_average_segments
from apps.source.plotting import plot_segments_axis
from apps.source.steps import find_heelstrikes_from_z, fit_step_with_sine
from source.data_processing import clean_data, split_data_into_segments, clean_segments, clean_segment_angles
from source.plotting import plot_segment_data
from source.data_processing import tsv_to_dataframe


def open_and_plot(path):
    df = tsv_to_dataframe(path)
    df = clean_data(df)

    segments = split_data_into_segments(df)
    segments = clean_segments(segments)
    segments = clean_segment_angles(segments)
    segments = rolling_average_segments(segments)

    heelstrikes = find_heelstrikes_from_z(segments)

    # plot_segments_axis(segments, "Z", heelstrikes)
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

    plt.figure()


    # LINEAR FIT
    def lin_fit(x, a, b, dt):
        return a * (x - dt) + b

    seg_step_directions = []
    for seg, heels in zip(segments, heelstrikes):
        no_of_half_steps = len(heels - 1)
        step_directions = []

        # get the Segment direction of travel from X axis trend (positive forward)
        segment_direction = "forward" if np.polyfit(seg["Time"], seg["X"], 1)[0] >= 0 else "backward"

        for i in range(no_of_half_steps - 1):
            start, end = heels[i], heels[i + 1]

            half_step_duration = seg['Time'].iloc[end] - seg['Time'].iloc[start]
            half_step_distance = seg["Y"].iloc[end] - seg["Y"].iloc[start]
            a = half_step_distance / half_step_duration
            b = seg["Y"].iloc[start]
            dt = seg['Time'].iloc[start]

            cnt_above_below = 0

            for i in range(start, end):
                t, y = seg["Time"].iloc[i], seg["Y"].iloc[i]

                # plt.plot(t, y, ".", color="blue")
                # plt.plot(t, lin_fit(t, a, b, dt), ".", color="orange")

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

            colors = {"indefinite": "black", "left": "blue", "right": "green"}
            plt.plot(seg["Time"].iloc[start:end], seg["Y"].iloc[start:end], color=colors[step_leg])

            step_directions.append(step_leg)

        step_directions.append("indefinite")
        seg_step_directions.append(step_directions)

    plot_segment_data(segments, heelstrikes, seg_step_directions)

    # plt.figure()
    # for j, seg in enumerate(segments):
    #     plt.plot(seg['Time'], seg["Y"], ".-")
    #     for k, h in enumerate(heelstrikes[j]):
    #         plt.plot(seg['Time'].iloc[h], seg["Y"].iloc[h], "o", color="red")
    #         plt.text(seg['Time'].iloc[h], seg["Y"].iloc[h], f"  {seg_step_directions[j][k]}")




    # df = segments[0]
    # start, middle, end = heelstrikes[0][1], heelstrikes[0][2], heelstrikes[0][2]
    # plt.figure(figsize=(15, 10))
    # plt.tight_layout(pad=2)
    # plt.suptitle(name)
    #
    # i = 1
    #
    # for y in ["X", "Y", "Z"]:
    #     plt.subplot(3, 2, i)
    #     plt.grid(True, linestyle=':')
    #     plt.plot(df["Time"].iloc[start:end], df[y].iloc[start:end])
    #     plt.plot(df["Time"].iloc[middle], df[y].iloc[middle], "o", color="red")
    #     plt.title(y)
    #     plt.ylabel(f"{y} (mm)")
    #     i += 2
    # plt.xlabel("Čas (s)")
    #
    # i = 2
    # for y in ["Roll", "Pitch", "Yaw"]:
    #     plt.subplot(3, 2, i)
    #     plt.grid(True, linestyle=':')
    #     plt.plot(df["Time"].iloc[start:end], df[y].iloc[start:end])
    #     plt.plot(df["Time"].iloc[middle], df[y].iloc[middle], "o", color="red")
    #     plt.title(y)
    #     plt.ylabel(f"{y} (°)")
    #     i += 2
    # plt.xlabel("Čas (s)")


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


