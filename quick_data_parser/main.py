import sys
import pandas as pd
import matplotlib.pyplot as plt



def open_and_print(path):
    df = pd.read_table(path, header=13)
    df.rename(columns={"panev X": "X"}, inplace=True)
    print(df.head())

    quick_plot(df)
    plt.show()

def quick_plot(df):
    plt.figure(figsize=(15, 10))
    plt.tight_layout(pad=2)
    i = 1

    for y in ["X", "Y", "Z"]:
        plt.subplot(3, 2, i)
        plt.grid(True, linestyle=':')
        plt.plot(df["Time"], df[y])
        plt.title(y)
        plt.ylabel(f"{y} (mm)")
        i += 2
    plt.xlabel("Čas (s)")

    i = 2
    for y in ["Roll", "Pitch", "Yaw"]:
        plt.subplot(3, 2, i)
        plt.grid(True, linestyle=':')
        plt.plot(df["Time"], df[y])
        plt.title(y)
        plt.ylabel(f"{y} (°)")
        i += 2
    plt.xlabel("Čas (s)")


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        path = sys.argv[1]
        open_and_print(path)
    else:
        while True:
            path = input("Vloz cestu na soubor :)\n")
            open_and_print(path)


