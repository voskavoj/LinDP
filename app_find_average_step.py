import numpy as np
from matplotlib import pyplot as plt

from source import steps
from source.data_processing import OneMeasSteps
from source.files import load_with_pickle, get_all_files_in_directory
from source.plotting import plot_average_step, set_dataset_name
from source.steps import compute_average_step


def find_average_step(data: OneMeasSteps):
    steps, average_step, no_of_steps = data.steps, data.average_step, data.no_of_steps

    # interpolated_steps = []
    # for s in steps:
    #     print(s.df)

        # df = s.df
        # # Set Time as index
        # df = df.set_index("Time")
        #
        # # Create a full 10 ms time index
        # full_time_index = np.arange(
        #     df.index.min(),
        #     df.index.max() + 0.01,
        #     0.01
        # )
        #
        # # Reindex to include missing timestamps
        # df = df.reindex(full_time_index)
        #
        # # Interpolate linearly
        # df_interpolated = df.interpolate(
        #     method="linear",
        #     limit_direction="both"
        # )
        #
        # # Restore Time column
        # df_interpolated = df_interpolated.reset_index().rename(
        #     columns={"index": "Time"}
        # )
        #
        # s.df_rel = df_interpolated
        # s.df = df_interpolated
        # interpolated_steps.append(s)
        # print(s.df_rel)
        # print("xxxxx")


# # FIX AVERAGING FIRST
#     for s in steps:
#         # print(np.diff(s["Time"]))
#         max_gap = np.max(np.diff(s["Time"]))
#         # print(round(max_gap * 1000), "ms", "!!!!!!!!!!!!!!!" if max_gap > 0.1 else "", "yyyyyyyy" if max_gap <= 0.015 else "")
#
#         if max_gap >= 0.15:
#             print("Yo!")

    average_step = compute_average_step(steps, True)
    plot_average_step(steps, average_step)



    return



    # plot_average_step(steps, average_step)

    dropped_steps = list()

# ## drop shortest
#     idx = min(range(len(steps)), key=lambda i: steps[i].df.shape[0])
#     dropped_steps.append(steps[idx])
#     steps.pop(idx)
#     no_of_steps -= 1
# ## /drop shortest

    average_step = compute_average_step(steps, True)
    old_average_step = average_step
    plot_average_step(steps, average_step, dropped_steps)

## start dropping by variation

    def rms_distance_to_average(df, df_avg):
        # Align on Time (inner join keeps only common timestamps)
        merged = df.merge(
            df_avg,
            on="Time",
            suffixes=("", "_avg"),
            how="inner"
        )

        # Compute squared distance at each time step
        sq_dist = (
                (merged["Roll"] - merged["Roll_avg"]) ** 2 +
                (merged["Pitch"] - merged["Pitch_avg"]) ** 2 +
                (merged["Yaw"] - merged["Yaw_avg"]) ** 2
        )

        # RMS distance
        return np.sqrt(sq_dist.mean())

    # JUST ONCE

    rms_values = [rms_distance_to_average(step.df, average_step.df) for step in steps]
    # print("rms_values", sorted(rms_values))

    KEPT_STEPS = min(10, len(rms_values))
    cutoff_rms = sorted(rms_values, reverse=True)[KEPT_STEPS - 1]

    kept_steps = []
    for i, step in enumerate(steps):
        if rms_values[i] < cutoff_rms:

            dropped_steps.append(step)
        else:
            kept_steps.append(step)

    no_of_steps = len(kept_steps)
    average_step = compute_average_step(kept_steps, True)

    plot_average_step(kept_steps, average_step, dropped_steps)

    ## REPEATEDLY
    # average_step = old_average_step
    # dropped_steps = list()
    # no_of_steps = len(steps)
    # while no_of_steps > 6:
    #     rms_values = [rms_distance_to_average(step.df, average_step.df) for step in steps]
    #     print("rms_values", sorted(rms_values))
    #
    #     worst_rms_idx = rms_values.index(min(rms_values))
    #     print("worst_rms_idx", worst_rms_idx)
    #     dropped_steps.append(steps[worst_rms_idx])
    #     steps.pop(worst_rms_idx)
    #     no_of_steps -= 1
    #     print(no_of_steps, len(steps))
    #     average_step = compute_average_step(kept_steps, True)
    #
    # plot_average_step(steps, average_step)

## /start dropping by variation




if __name__ == "__main__":

    data = ["Z_zu_ja_M_pred"]
    data = get_all_files_in_directory("data/processed")

    for name in data:
        set_dataset_name(name)
        d = load_with_pickle("data/processed/", name)
        find_average_step(d)

    plt.show()
