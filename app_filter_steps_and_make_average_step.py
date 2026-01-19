from matplotlib import pyplot as plt

from source.data_processing import OneMeasSteps, OneMeasAverageStep
from source.files import load_with_pickle, get_all_files_in_directory, save_with_pickle
from source.plotting import set_dataset_name
from source.steps import compute_average_step, auto_filter_steps


def find_average_step(data: OneMeasSteps):
    steps, average_step, no_of_steps = data.steps, data.average_step, data.no_of_steps

    kept_steps, dropped_steps = auto_filter_steps(steps, log_name=name)
    average_step = compute_average_step(kept_steps, True)

    return OneMeasAverageStep(name, average_step, kept_steps, filtered_manually=False)


if __name__ == "__main__":
    data = get_all_files_in_directory("data/processed_steps")

    for name in data:
        name = name.split(".")[0]
        set_dataset_name(name)

        d = load_with_pickle("data/processed_steps/", name)
        fd = find_average_step(d)
        save_with_pickle(fd, "data/average_steps/", name + "_avg")

    plt.show()
