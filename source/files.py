import pickle

def save_with_pickle(processed_data, base_path: str, filename: str):
    with open(f"{base_path}{"/" if base_path.endswith("/") or base_path.endswith("\\") else ""}{filename}.pickle", "wb") as f:
        pickle.dump(processed_data, f, protocol=pickle.HIGHEST_PROTOCOL)

def load_with_pickle(base_path: str, filename: str):
    with open(f"{base_path}{"/" if base_path.endswith("/") or base_path.endswith("\\") else ""}{filename}.pickle", "rb") as f:
        data = pickle.load(f)
    return data
