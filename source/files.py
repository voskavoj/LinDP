import pickle
from os import listdir
from os.path import isfile, join


def save_with_pickle(processed_data, base_path: str, filename: str):
    with open(f"{base_path}{"/" if base_path.endswith("/") or base_path.endswith("\\") else ""}{filename}.pickle", "wb") as f:
        pickle.dump(processed_data, f, protocol=pickle.HIGHEST_PROTOCOL)


def load_with_pickle(base_path: str, filename: str):
    with open(f"{base_path}{"/" if base_path.endswith("/") or base_path.endswith("\\") else ""}{filename.replace(".pickle", "")}.pickle", "rb") as f:
        data = pickle.load(f)
    return data


def get_all_files_in_directory(directory, filter_extensions=None):
    files = [f for f in listdir(directory) if isfile(join(directory, f))]

    if filter_extensions is not None:
        files = [f for f in files if f.endswith(filter_extensions)]

    return files