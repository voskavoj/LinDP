import random

import numpy as np
from matplotlib import pyplot as plt

from source.files import load_with_pickle, get_all_files_in_directory, save_as_txt
from source.plotting import plot_average_step, set_dataset_name

if __name__ == "__main__":
    data = get_all_files_in_directory("data/average_steps")


    export_data = []

    data_z_o, data_z_m, data_n_o, data_n_m = list(), list(), list(), list()

    max_rolls, min_rolls, max_pitches, min_pitches, max_yaws, min_yaws = list(), list(), list(), list(), list(), list()



    all_data = load_with_pickle("data/datasets/", "dataset_dict")
    for h in ("Z", "N"):
        for m in ("M", "O"):
            for b in ("pred", ):
                one_meas_type = all_data[h][m][b]

                export_data.append(f"Data: {h} {m} {b}\tPrumer\t" + "\t".join([d.name for d in one_meas_type]))
                print(export_data[-1])

                max_rolls, min_rolls, max_pitches, min_pitches, max_yaws, min_yaws = list(), list(), list(), list(), list(), list()
                for d in one_meas_type:

                    avg_step = d.average_step
                    no_of_steps = d.from_number_of_steps

                    max_r = max(avg_step.df["Roll"])
                    max_p = max(avg_step.df["Pitch"])
                    max_y = max(avg_step.df["Yaw"])

                    min_r = min(avg_step.df["Roll"])
                    min_p = min(avg_step.df["Pitch"])
                    min_y = min(avg_step.df["Yaw"])

                    max_rolls.append(max_r)
                    max_pitches.append(max_p)
                    max_yaws.append(max_y)
                    min_rolls.append(min_r)
                    min_pitches.append(min_p)
                    min_yaws.append(min_y)

                    set_dataset_name(d.name)
                    if random.randint(1, 10) <= 2:
                        plot_average_step([], d.average_step)

                export_data.append(f"Max roll (°)\t" + str(np.average(max_rolls)) + "\t" + "\t".join([str(m) for m in max_rolls]))
                export_data.append(f"Min roll (°)\t" + str(np.average(min_rolls)) + "\t" + "\t".join([str(m) for m in min_rolls]))
                export_data.append(f"Max pitch (°)\t" + str(np.average(max_pitches)) + "\t" + "\t".join([str(m) for m in max_pitches]))
                export_data.append(f"Min pitch (°)\t" + str(np.average(min_pitches)) + "\t" + "\t".join([str(m) for m in min_pitches]))
                export_data.append(f"Max yaw (°)\t" + str(np.average(max_yaws)) + "\t" + "\t".join([str(m) for m in max_yaws]))
                export_data.append(f"Min yaw (°)\t" + str(np.average(min_yaws)) + "\t" + "\t".join([str(m) for m in min_yaws]))
                export_data.append("")

    for e in export_data:
        print(e)

    save_as_txt(export_data, "data/", "export")
    plt.show()