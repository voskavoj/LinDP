import sys

from matplotlib import pyplot as plt

from find_heelstrikes import process_data


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        path = sys.argv[1]
        process_data(path)
        plt.show()
    else:
        while True:
            path = input("Vloz cestu na soubor :)\n")
            process_data(path)
            plt.show()