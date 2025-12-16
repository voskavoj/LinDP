import sys
import pandas as pd
import matplotlib.pyplot as plt

from apps.source.steps import Segment


def quick_plot(df, name="", show=False):
    plt.figure(figsize=(15, 10))
    plt.tight_layout(pad=2)
    plt.suptitle(name)

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


def plot_axis(df, axis, show=False):
    plt.figure(figsize=(15, 10))
    plt.tight_layout(pad=2)

    plt.grid(True, linestyle=':')
    plt.plot(df["Time"], df[axis])
    plt.title(axis)
    plt.ylabel(f"{axis} (° or mm)")
    plt.xlabel("Čas (s)")

    if show:
        plt.show()

def plot_all_data(df):
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
    plt.title(f"Axis {axis}; No. of segments: {len(segments)}")
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