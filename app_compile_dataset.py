from source.data_processing import OneMeasAverageStep
from source.files import load_with_pickle, get_all_files_in_directory, save_with_pickle


if __name__ == "__main__":
    data = get_all_files_in_directory("data/average_steps")

    all_data = dict()
    for h in ("Z", "N"):
        all_data[h] = dict()
        for m in ("M", "O"):
            all_data[h][m] = dict()
            for b in ("pred", "po"):
                all_data[h][m][b] = list()

    for name in data:
        name = name.split(".")[0]

        d = load_with_pickle("data/average_steps/", name)
        d: OneMeasAverageStep
        all_data[d.arg_health][d.arg_menstr][d.arg_before].append(d)

    for h in ("Z", "N"):
        for m in ("M", "O"):
            for b in ("pred", "po"):
                dataset = all_data[h][m][b]

                print(h, m, b)
                for d in dataset:
                    print("\t", d.name)
                save_with_pickle(dataset, "data/datasets/", f"dataset_{h}_{m}_{b}")
    save_with_pickle(all_data, "data/datasets/", f"dataset_dict")

