import scipy.stats as st

from source.data_processing import OneMeasAverageStep
from source.plotting import translate_ids


Max = 1
Min = 2
Range = 3
Roll = 1
Pitch = 2
Yaw = 3


class DatasetStatistics:
    def __init__(self, dataset: list[OneMeasAverageStep], h, m, b):
        self.dataset = dataset
        self.size = len(dataset)
        self.id = (h, m, b)

        self.names = [one_meas_type.name for one_meas_type in dataset]

        self.max_roll  = [max(one_meas_type.average_step.df["Roll"])  for one_meas_type in dataset]
        self.max_pitch = [max(one_meas_type.average_step.df["Pitch"]) for one_meas_type in dataset]
        self.max_yaw   = [max(one_meas_type.average_step.df["Yaw"])   for one_meas_type in dataset]

        self.min_roll  = [min(one_meas_type.average_step.df["Roll"])  for one_meas_type in dataset]
        self.min_pitch = [min(one_meas_type.average_step.df["Pitch"]) for one_meas_type in dataset]
        self.min_yaw   = [min(one_meas_type.average_step.df["Yaw"])   for one_meas_type in dataset]

        self.range_roll  = [m - n for m, n in zip(self.max_roll, self.min_roll)]
        self.range_pitch = [m - n for m, n in zip(self.max_pitch, self.min_pitch)]
        self.range_yaw   = [m - n for m, n in zip(self.max_yaw, self.min_yaw)]

    def get(self, tp, val):
        if type(tp) is int:
            tp = {1: "max", 2: "min", 3: "range"}[tp]
        if type(val) is int:
            val = {1: "roll", 2: "pitch", 3: "yaw"}[val]

        return getattr(self, tp.lower() + "_" + val.lower())

    def header(self):
        return translate_ids(*self.id) + "\t" + "\t".join([name for name in self.names])

    def lines(self):
        lines = []
        for val in ["Roll", "Pitch", "Yaw"]:
            for tp in ["Min", "Max", "Range"]:
                lines.append(f"{val}, {tp} (°)\t" + "\t".join([str(m) for m in self.get(tp, val)]))

        return lines


def perform_shapiro_wilk_test(a):
    # a = np.round(a, 4)
    statistic, pvalue = st.shapiro(a, nan_policy='raise')
    return statistic, pvalue

def perform_independent_t_test(a, b, welch=False, alternative='two-sided'):
    res = st.ttest_ind(a, b, equal_var= not welch, alternative=alternative, nan_policy='raise')
    # print(res.statistic, res.pvalue, res.df, res.confidence_interval())
    return res.statistic, res.pvalue

def perform_paired_t_test(a, b, alternative='two-sided'):
    res = st.ttest_rel(a, b, alternative=alternative, nan_policy='raise')
    # print(res.statistic, res.pvalue, res.df, res.confidence_interval())
    return res.statistic, res.pvalue

def perform_mann_whitney_u_test(a, b, alternative='two-sided'):
    res = st.mannwhitneyu(a, b, use_continuity=True, alternative=alternative, nan_policy='raise')
    return res.statistic, res.pvalue

def perform_wilcoxon_test(a, b, alternative='two-sided'):
    res = st.wilcoxon(a, b, alternative=alternative, nan_policy='raise')
    return res.statistic, res.pvalue

def compare_different_groups_same_time(a, b, p_threshold):
    report = []

    # normality test
    print(f"Delam Shappiro test normality pro A")
    s, p = perform_shapiro_wilk_test(a)
    a_dist = "normalni" if p >= p_threshold else "nenormalni"
    print(f"Vysledek: s = {s}, p = {p}. p {'<' if p < p_threshold else '>='} {p_threshold} ==> {a_dist}")
    report.extend([f"Shappiro A", s, p, a_dist])

    print(f"Delam Shappiro test normality pro B")
    s, p = perform_shapiro_wilk_test(b)
    b_dist = "normalni" if p >= p_threshold else "nenormalni"
    print(f"\tVysledek: s = {s}, p = {p}. p {'<' if p < p_threshold else '>='} {p_threshold} ==> {b_dist}")
    report.extend([f"Shappiro B", s, p, b_dist])

    if a_dist == "normalni" and b_dist == "normalni":
        print("Oba vzorky jsou normalni, pokracuji nezavislym T-testem")
        s, p = perform_independent_t_test(a, b)
        significance = "signifikantni" if p < p_threshold else "nesignifikantni"
        print(f"\tVysledek: s = {s}, p = {p}. p {'<' if p < p_threshold else '>='} {p_threshold} ==> {significance}")
        report.extend([f"Nez. T test", s, p, significance])
    else:
        print("Oba vzorky nejsou normalni, pokracuji Mann-Whitney testem")
        s, p = perform_mann_whitney_u_test(a, b)
        significance = "signifikantni" if p < p_threshold else "nesignifikantni"
        print(f"\tVysledek: s = {s}, p = {p}. p {'<' if p < p_threshold else '>='} {p_threshold} ==> {significance}")
        report.extend([f"Mann. whitney", s, p, significance])
    
    return report


def compare_same_groups_different_time(a, b, p_threshold):
    report = []

    # normality test
    print(f"Delam Shappiro test normality pro A")
    s, p = perform_shapiro_wilk_test(a)
    a_dist = "normalni" if p >= p_threshold else "nenormalni"
    print(f"\tVysledek: s = {s}, p = {p}. p {'<' if p < p_threshold else '>='} {p_threshold} ==> {a_dist}")
    report.extend([f"Shappiro A", s, p, a_dist])

    print(f"Delam Shappiro test normality pro B")
    s, p = perform_shapiro_wilk_test(b)
    b_dist = "normalni" if p >= p_threshold else "nenormalni"
    print(f"\tVysledek: s = {s}, p = {p}. p {'<' if p < p_threshold else '>='} {p_threshold} ==> {b_dist}")
    report.extend([f"Shappiro B", s, p, b_dist])

    if a_dist == "normalni" and b_dist == "normalni":
        print("Oba vzorky jsou normalni, pokracuji parovym T-testem")
        s, p = perform_paired_t_test(a, b)
        significance = "signifikantni" if p < p_threshold else "nesignifikantni"
        print(f"\tVysledek: s = {s}, p = {p}. p {'<' if p < p_threshold else '>='} {p_threshold} ==> {significance}")
        report.extend([f"Par. T test", s, p, significance])
    else:
        print("Oba vzorky nejsou normalni, pokracuji Wilcoxon testem")
        s, p = perform_wilcoxon_test(a, b)
        significance = "signifikantni" if p < p_threshold else "nesignifikantni"
        print(f"\tVysledek: s = {s}, p = {p}. p {'<' if p < p_threshold else '>='} {p_threshold} ==> {significance}")
        report.extend([f"Wilcoxon", s, p, significance])
    
    return report
