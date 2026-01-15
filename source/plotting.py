import pandas as pd
import matplotlib.pyplot as plt
from pandas import DataFrame

from source.steps import Segment, Step

dataset_name = ""

def set_dataset_name(new_name):
    global dataset_name
    dataset_name = f"{new_name}: "


def quick_plot(df: pd.DataFrame, name="", show=False):
    plt.figure(figsize=(15, 10))
    plt.tight_layout(pad=2)
    plt.suptitle(f"{dataset_name}{name}")

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

    if show:
        plt.show()


def plot_axis(df: pd.DataFrame, axis, show=False):
    plt.figure(figsize=(15, 10))
    plt.tight_layout(pad=2)

    plt.grid(True, linestyle=':')
    plt.plot(df["Time"], df[axis])
    plt.title(f"{dataset_name} Osa {axis}")
    plt.ylabel(f"{axis} (° or mm)")
    plt.xlabel("Čas (s)")

    if show:
        plt.show()

def plot_all_data(df: pd.DataFrame):
    plt.figure()
    plt.figure(figsize=(15, 1000))

    header = list(df.columns.values)

    plt.grid(True, linestyle=':')
    plot_num = len(header)
    i = 1

    for y in header:
        plt.subplot(plot_num, 1, i)
        plt.grid(True, linestyle=':')
        plt.plot(df["Time"], df[y])
        plt.title(y)
        i += 1


def plot_segments_axis(segments: list[Segment], axis: str, plot_heels=True, text=False):
    plt.figure()
    plt.title(f"{dataset_name}Osa {axis}; Počet segmentů: {len(segments)}")
    for s in segments:
        plt.plot(s['Time'], s[axis], ".-")
        if plot_heels and s.heelstrikes is not None:
            for h in s.heelstrikes:
                plt.plot(s['Time'].iloc[h], s[axis].iloc[h], "o", color="red")
        if text:
            plt.text(s['Time'].tail(1), s[axis].tail(1),
                     f"{s['Time'].iloc[-1] - s['Time'].iloc[0]:.0f} s; {abs(s[axis].iloc[-1] - s[axis].iloc[0]):.2f}")


def plot_segment_data(segments: list[Segment], plot_heels=True, plot_legs=True):
    plt.figure(figsize=(15, 10))
    plt.tight_layout(pad=2)
    plt.suptitle(f"{dataset_name}Segmenty ({len(segments)}x)")

    i = 1
    for y in ["X", "Y", "Z"]:
        plt.subplot(3, 2, i)
        plt.grid(True, linestyle=':')
        for seg in segments:
            plt.plot(seg["Time"], seg[y])
            if plot_heels and seg.heelstrikes is not None:
                for k, h in enumerate(seg.heelstrikes):
                    plt.plot(seg['Time'].iloc[h], seg[y].iloc[h], "o", color="red")
                    if plot_legs and seg.step_legs is not None:
                        plt.text(seg['Time'].iloc[h], seg[y].iloc[h], f"  {seg.step_legs[k]}")
        plt.title(y)
        plt.ylabel(f"{y} (mm)")
        i += 2
    plt.xlabel("Čas (s)")

    i = 2
    for y in ["Roll", "Pitch", "Yaw"]:
        plt.subplot(3, 2, i)
        plt.grid(True, linestyle=':')
        for seg in segments:
            plt.plot(seg["Time"], seg[y])
            if plot_heels and seg.heelstrikes is not None:
                for k, h in enumerate(seg.heelstrikes):
                    plt.plot(seg['Time'].iloc[h], seg[y].iloc[h], "o", color="red")
                    if plot_legs and seg.step_legs is not None:
                        plt.text(seg['Time'].iloc[h], seg[y].iloc[h], f"  {seg.step_legs[k]}")
        plt.title(y)
        plt.ylabel(f"{y} (°)")
        i += 2
    plt.xlabel("Čas (s)")


def plot_average_step(steps: list[Step], average_step: Step, dropped_steps=None):
    if dropped_steps is None:
        dropped_steps = []
    plt.figure(figsize=(15, 10))
    plt.tight_layout(pad=2)
    plt.suptitle(f"{dataset_name}Průměrný krok (ze {len(steps)})")

    i = 1
    for y in ["Roll", "Pitch", "Yaw"]:
        plt.subplot(3, 1, i)
        plt.grid(True, linestyle=':')
        for step in dropped_steps:
            plt.plot(step.df["Time"], step.df[y], ".-", color="lightgray", label=f"Step {step.step_number}")
        for step in steps:
            plt.plot(step.df["Time"], step.df[y], ".-", color="darkgreen" if dropped_steps else "gray", label=f"Step {step.step_number}")
        plt.plot(average_step["Time"], average_step[y], ".-", color="orange")
        plt.title(y)
        plt.ylabel(f"{y} (°)")
        i += 1


def plot_valid_steps(all_data: DataFrame, steps: list[Step], plot_numbers=True):
    plt.figure(figsize=(15, 10))
    plt.tight_layout(pad=2)
    plt.suptitle(f"{dataset_name}Data vs. validní kroky ({len(steps)} kroků)")

    i = 0
    for y in ["X", "Roll", "Y", "Pitch", "Z", "Yaw"]:
        plt.subplot(3, 2, i := i + 1)
        plt.grid(True, linestyle=':')

        plt.plot(all_data["Time"], all_data[y])
        for step in steps:
            plt.plot(step.df_abs["Time"], step.df_abs[y], color="orange", label=f"Step {step.step_number}")
            plt.plot(step.df_abs["Time"].iloc[0], step.df_abs[y].iloc[0], "o", color="red")
            if plot_numbers:
                plt.text(step.df_abs["Time"].iloc[0], step.df_abs[y].iloc[0], f"{step.step_number}:")
            plt.plot(step.df_abs["Time"].iloc[-1], step.df_abs[y].iloc[-1], "o", color="red")

        plt.title(y)
        plt.ylabel(f"{y} ({'°' if y in ["Roll", "Pitch", "Yaw"] else 'mm'})")
    plt.xlabel("Čas (s)")
