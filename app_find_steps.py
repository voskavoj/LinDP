import pickle
import sys

from matplotlib import pyplot as plt

from source.plotting import plot_average_step, plot_valid_steps, set_dataset_name
from source.steps import identify_segment_travel_direction, identify_segment_step_legs, \
    extract_steps_from_segments, compute_average_step
from source.data_processing import rolling_average_segments, OneMeasSteps
from source.steps import find_heelstrikes_from_z, Segment, Step
from source.data_processing import clean_data, split_data_into_segments, clean_segments, clean_segment_angles
from source.plotting import plot_segment_data
from source.data_processing import tsv_to_dataframe


def process_data(path):
    df, metadata = tsv_to_dataframe(path, return_metadata=True)
    df = clean_data(df)

    segments = split_data_into_segments(df)
    segments = clean_segments(segments)
    segments = clean_segment_angles(segments)
    segments = rolling_average_segments(segments)

    segments = [Segment(s) for s in segments]

    for seg in segments:
        seg.heelstrikes = find_heelstrikes_from_z(seg.df)
        seg.travel_direction = identify_segment_travel_direction(seg)
        seg.step_legs = identify_segment_step_legs(seg)

    steps = extract_steps_from_segments(segments)
    average_step = compute_average_step(steps, crop_to_shortest=True)

    plot_valid_steps(df, steps)
    plot_average_step(steps, average_step)
    plot_segment_data(segments)

    one_measurement_steps = OneMeasSteps(path, metadata, df, segments, steps, average_step)

    return one_measurement_steps


if __name__ == "__main__":

    data = [

    ]


    for filename in data:
        name = filename.replace("_6D.tsv", "")

        set_dataset_name(name)
        processed_data = process_data(f"data/{filename}")
        processed_data.name = name

        print(f"Processing data {name}\tValid steps found: {processed_data.no_of_steps}")

        with open(f"data/{name}.pickle", "wb") as f:
            pickle.dump(processed_data, f, protocol=pickle.HIGHEST_PROTOCOL)

    plt.show()


