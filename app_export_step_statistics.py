import numpy as np
from matplotlib import pyplot as plt

from source.files import load_with_pickle, save_as_txt
from source.plotting import plot_dataset_average_steps, translate_ids, alias, alcol, translate_axis, \
    plot_dataset_average_steps_no_legend
from source.statistics import compare_different_groups_same_time, compare_same_groups_different_time, DatasetStatistics
from source.steps import compute_average_step


def plot_versus(name_a, name_b, dataset_a, dataset_b):
    # make average step
    avg_step_a = compute_average_step([one_meas_type.average_step for one_meas_type in dataset_a], True)
    avg_step_b = compute_average_step([one_meas_type.average_step for one_meas_type in dataset_b], True)

    plt.figure(figsize=(15, 10))
    plt.tight_layout(pad=2)
    plt.suptitle(f"Srovnání {name_a} vs {name_b}")

    i = 1
    for y in ["Roll", "Pitch", "Yaw"]:
        plt.subplot(3, 1, i)
        plt.grid(True, linestyle=':')
        plt.plot(avg_step_a.df["Time"], avg_step_a.df[y], ".-", label=name_a)
        plt.plot(avg_step_b.df["Time"], avg_step_b.df[y], ".-", label=name_b)
        plt.ylabel(f"{translate_axis(y)} (°)")
        i += 1

    plt.xlabel("Čas (s)")
    plt.legend()

    plt.savefig(f"export/Srovnání {name_a} vs {name_b}.png")



def filter_by_indices(list_1: list, indices: list):
    return [list_1[i] for i in indices]

def find_common_data_indices(set1, set2):
    names1 = [name.split("_")[1] + "_" + name.split("_")[2] for name in set1.names]
    names2 = [name.split("_")[1] + "_" + name.split("_")[2] for name in set2.names]

    indices1, indices2 = [], []

    for idx1, name in enumerate(names1):
        idx2 = names2.index(name) if name in names2 else None

        if idx2 is not None:
            indices1.append(idx1)
            indices2.append(idx2)

    assert(filter_by_indices(names1, indices1) == filter_by_indices(names2, indices2))

    return indices1, indices2



if __name__ == "__main__":
    export_lines = []

    all_data = load_with_pickle("data/datasets/", "dataset_dict")
    data_statistics = all_data

    # prepare data, calculate ranges
    for h in ("Z", "N"):
        for m in ("M", "O"):
            for b in ("pred", "po"):
                dataset = DatasetStatistics(all_data[h][m][b], h, m, b)
                data_statistics[h][m][b] = dataset

                plot_dataset_average_steps(dataset.dataset, translate_ids(h, m, b), save=True)
                plot_dataset_average_steps_no_legend(dataset.dataset, translate_ids(h, m, b), save=True)
                export_lines.append(dataset.header())
                export_lines.extend(dataset.lines())
                export_lines.append("")
                
    for e in export_lines:
        print(e)

    # do statistics
    export_lines.append("")
    del (h, m, b)
    header_row = "Parametr\tTest\ts\tp\tVýsledek\tTest\ts\tp\tVýsledek\tTest\ts\tp\tVýsledek"
    P_VALUE = 0.05

    # 1) ZDRAVÉ vs NEMOCNÉ před cvičením, zvlášť pro ovulaci a menstruaci
    b = "pred"
    h1 = "Z"
    h2 = "N"
    for m in ("M", "O"):
        export_lines.append(f"Srovnání {translate_ids(h1, m, b)} vs {translate_ids(h2, m, b)}")
        export_lines.append(header_row + "\tPrůmer A\tPrůměr B")

        plot_versus(translate_ids(h1, m, b), translate_ids(h2, m, b), data_statistics[h1][m][b].dataset, data_statistics[h2][m][b].dataset)

        for val in ["Roll", "Pitch", "Yaw"]:
            for tp in ["Min", "Max", "Range"]:
                rep = compare_different_groups_same_time(data_statistics[h1][m][b].get(tp, val), data_statistics[h2][m][b].get(tp, val), P_VALUE)
                export_lines.append(f"{val}, {tp} (°)\t" + "\t".join(str(r) for r in rep) + f"\t{np.average(data_statistics[h1][m][b].get(tp, val))}" + f"\t{np.average(data_statistics[h2][m][b].get(tp, val))}")
        export_lines.append("")
    export_lines.append("")
    del (h1, h2, m, b)

    # 1B) ZDRAVÉ vs NEMOCNÉ po cvičení, zvlášť pro ovulaci a menstruaci
    b = "po"
    h1 = "Z"
    h2 = "N"
    for m in ("M", "O"):
        export_lines.append(f"Srovnání {translate_ids(h1, m, b)} vs {translate_ids(h2, m, b)}")
        export_lines.append(header_row + "\tPrůmer A\tPrůměr B")

        plot_versus(translate_ids(h1, m, b),
                    translate_ids(h2, m, b),
                    data_statistics[h1][m][b].dataset,
                    data_statistics[h2][m][b].dataset)

        for val in ["Roll", "Pitch", "Yaw"]:
            for tp in ["Min", "Max", "Range"]:
                rep = compare_different_groups_same_time(data_statistics[h1][m][b].get(tp, val), data_statistics[h2][m][b].get(tp, val), P_VALUE)
                export_lines.append(f"{val}, {tp} (°)\t" + "\t".join(str(r) for r in rep) + f"\t{np.average(data_statistics[h1][m][b].get(tp, val))}" + f"\t{np.average(data_statistics[h2][m][b].get(tp, val))}")
        export_lines.append("")
    export_lines.append("")
    del (h1, h2, m, b)

    # 2, 3) zdravé/nemocné PŘED vs zdravé/nemocné PO cvičení, zvlášť pro ovulaci a menstruaci
    for h in ("Z", "N"):
        b1 = "pred"
        b2 = "po"
        for m in ("M", "O"):
            export_lines.append(f"Srovnání {translate_ids(h, m, b1)} vs {translate_ids(h, m, b2)}")
            export_lines.append(header_row + "\tTest\tc_d\tEfekt" + "\tPrůmer A\tPrůměr B")

            plot_versus(translate_ids(h, m, b1),
                        translate_ids(h, m, b2),
                        data_statistics[h][m][b1].dataset,
                        data_statistics[h][m][b2].dataset)

            for val in ["Roll", "Pitch", "Yaw"]:
                for tp in ["Min", "Max", "Range"]:
                    data_before, data_after = data_statistics[h][m][b1], data_statistics[h][m][b2]
                    common_indices1, common_indices2 = find_common_data_indices(data_before, data_after)

                    rep = compare_same_groups_different_time(filter_by_indices(data_before.get(tp, val), common_indices1),
                                                             filter_by_indices(data_after.get(tp, val), common_indices2),
                                                             P_VALUE)
                    export_lines.append(f"{val}, {tp} (°)\t" + "\t".join(str(r) for r in rep) + f"\t{np.average(data_statistics[h][m][b1].get(tp, val))}" + f"\t{np.average(data_statistics[h][m][b2].get(tp, val))}")
            export_lines.append(f"Pouze {filter_by_indices(data_before.names, common_indices1)}")
            export_lines.append(f"proti {filter_by_indices(data_after.names, common_indices2)}")
            export_lines.append("")

        export_lines.append("")

    save_as_txt(export_lines, "export/", "statistiky")

    plt.show()
