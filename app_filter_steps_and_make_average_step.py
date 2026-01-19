from matplotlib import pyplot as plt

from source.data_processing import OneMeasSteps, OneMeasAverageStep
from source.files import load_with_pickle, get_all_files_in_directory, save_with_pickle
from source.plotting import plot_average_step, set_dataset_name, plot_most_deviant_step, plot_lowest_density_step
from source.steps import compute_average_step, filter_out_steps_by_derivation, calculate_average_maximum_derivation, \
    filter_out_steps_by_density, Step


def auto_filter_steps(steps: list[Step], log=True):
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

    kept_steps, dropped_steps_r = filter_out_steps_by_derivation(kept_steps, "Roll",  max(threshold_deriv_r, avg_deriv_r * threshold_deriv_as_frac_of_avg))
    kept_steps, dropped_steps_p = filter_out_steps_by_derivation(kept_steps, "Pitch", max(threshold_deriv_p, avg_deriv_p * threshold_deriv_as_frac_of_avg))
    kept_steps, dropped_steps_y = filter_out_steps_by_derivation(kept_steps, "Yaw",   max(threshold_deriv_y, avg_deriv_y * threshold_deriv_as_frac_of_avg))
    dropped_steps.extend([*dropped_steps_r, *dropped_steps_p, *dropped_steps_y])

    # report statistics
    if log:
        d, r, p, y = len(dropped_steps_d), len(dropped_steps_r), len(dropped_steps_p), len(dropped_steps_y)
        col = '\033[93m' if len(kept_steps)/len(steps) < 0.8 else "" # '\033[92m'
        print(col + f"{name}:\t{len(kept_steps):02.0f}/{len(steps):02.0f} ({round(100 * len(kept_steps)/len(steps)):03.0f}%) D:{d} R:{r} P:{p} Y:{y} | average r: {round(avg_deriv_r)} p: {round(avg_deriv_p)} y: {round(avg_deriv_y)}" + '\033[0m')

    # try:
    #     average_step = compute_average_step(kept_steps, True)
    #     plot_average_step(kept_steps, average_step, dropped_steps)
    #     plt.savefig(f"data/img_filt/{name.replace(":", "")}avg_steps.png")
    #     plt.close()
    # except IndexError:
    #     print(f"No steps left in data {name}")

    return kept_steps, dropped_steps


def find_average_step(name: str, data: OneMeasSteps):
    steps, average_step, no_of_steps = data.steps, data.average_step, data.no_of_steps

    kept_steps, dropped_steps = auto_filter_steps(steps)
    average_step = compute_average_step(kept_steps, True)

    return OneMeasAverageStep(name, average_step, kept_steps, filtered_manually=False)


if __name__ == "__main__":
    data = get_all_files_in_directory("data/processed_steps")

    for name in data:
        name = name.split(".")[0]
        set_dataset_name(name)

        d = load_with_pickle("data/processed_steps/", name)
        fd = find_average_step(name, d)
        save_with_pickle(fd, "data/average_steps/", name + "_avg")

    plt.show()
