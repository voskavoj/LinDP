import sys

from source.data_processing import tsv_to_dataframe
from source.plotting import quick_plot


def open_and_plot(path):
    df = tsv_to_dataframe(path)
    quick_plot(df, name=path.split("/")[-1].split(".")[0], show=True)


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        path = sys.argv[1]
        open_and_plot(path)
    else:
        while True:
            path = input("Vloz cestu na soubor :)\n")
            open_and_plot(path)


