import copy

from datetime import datetime
import pandas as pd
from io import StringIO

from source.parameters import Parameters


class Dataset:
    def __init__(self, name, metadata, data, segments, steps, average_step):
        self.name = name
        self.metadata = metadata
        self.date_of_processing = datetime.now()

        self.data = data
        self.segments = segments
        self.steps = steps
        self.average_step = average_step

        self.no_of_segments = len(segments)
        self.no_of_steps = len(steps)
        self.parameters = Parameters()


def tsv_to_dataframe(path, return_metadata=False):
    # remove diacritics
    with open(path, "r") as file:
        file_content = file.read()
        for r, b in {"á": "a"}.items():
            file_content = file_content.replace(r, b)
        file = StringIO(file_content)

    # find header row
    metadata = ""
    file_lines = file_content.split("\n")
    i = 0
    for line in file_lines:
        if line.startswith("Frame"):
            metadata += line + "\n"
            break
        else:
            i += 1

    df = pd.read_table(file, header=i, encoding='utf8')
    df.rename(columns={"panev X": "X"}, inplace=True)

    if return_metadata:
        return df, metadata
    else:
        return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df[df.columns[:9]]  # keep only first 9 columns: Frame, Time, 3 trans, 3 rot, Residual
    df = df.dropna()  # drop NaN rows

    return df


def split_data_into_segments(df: pd.DataFrame) -> list:
    # --- Compute differences ---
    df['time_diff'] = df['Time'].diff()
    df['dXdt'] = df['X'].diff() / df['Time'].diff()

    # --- Thresholds ---
    time_threshold = 0.25 # adjust to your data
    deriv_threshold = 4000  # adjust to your data

    # --- Boolean conditions for starting a new segment ---
    gap_condition = df['time_diff'] > time_threshold
    deriv_condition = df['dXdt'].abs() > deriv_threshold

    # --- Combined segmentation criterion ---
    df['segment_combined'] = (gap_condition | deriv_condition).cumsum()

    # --- Split into continuous segments ---
    segments = [
        g.drop(columns=['time_diff', 'dXdt'])
        for _, g in df.groupby('segment_combined')]

    return segments


def clean_segments(segments: list) -> list:
    ## KEEP ONLY SEGMENTS SO LONG
    min_duration = 3.0  # seconds
    min_distance = 3000  # mm

    valid_segments = []

    for seg in segments:
        duration = seg["Time"].iloc[-1] - seg["Time"].iloc[0]
        distance = abs(seg["X"].iloc[-1] - seg["X"].iloc[0])
        if duration >= min_duration and distance >= min_distance:
            valid_segments.append(seg)

    return valid_segments


def clean_segment_angles(segments: list) -> list:
    threshold_180 = 100

    for axis in ["Roll", "Pitch", "Yaw"]:
        for seg in segments:
            if seg[axis].abs().mean() > threshold_180:
                seg[axis] %= 360
                seg[axis] -= 180  # warning: danger of unintentional flip

    return segments

def rolling_average(df: pd.DataFrame, window=None) -> pd.DataFrame:
    rolling_average_window = 5

    if window is None:
        window = rolling_average_window

    return df.rolling(window=window).mean().dropna()

def rolling_average_segments(segments: list) -> list:
    for i in range(len(segments)):
        segments[i] = rolling_average(segments[i]).dropna()
        segments[i]["Time"] = segments[i]["Time"].round(2)

    return segments

def normalize_time(df: pd.DataFrame) -> pd.DataFrame:
    normalized = copy.deepcopy(df)
    normalized["Time"] = normalized["Time"] - normalized["Time"].iloc[0]
    normalized["Time"] = normalized["Time"].round(2)
    return normalized
