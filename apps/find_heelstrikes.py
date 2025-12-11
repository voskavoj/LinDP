import sys

from matplotlib import pyplot as plt

from source.data_processing import clean_data, split_data_into_segments, clean_segments, clean_segment_angles
from source.plotting import plot_segment_data
from source.data_processing import tsv_to_dataframe


def open_and_plot(path):
    df = tsv_to_dataframe(path)
    df = clean_data(df)

    segments = split_data_into_segments(df)
    segments = clean_segments(segments)
    segments = clean_segment_angles(segments)

    plot_segment_data(segments)



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


