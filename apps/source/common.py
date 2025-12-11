import pandas as pd
from io import StringIO

def tsv_to_dataframe(path):

    # remove diacritics
    with open(path, "r") as file:
        file_content = file.read()
        for r, b in {"á": "a"}.items():
            file_content = file_content.replace(r, b)
        file = StringIO(file_content)

    # find header row
    file_lines = file_content.split("\n")
    i = 0
    for line in file_lines:
        if line.startswith("Frame"):
            break
        else:
            i += 1

    df = pd.read_table(file, header=i, encoding='utf8')
    df.rename(columns={"panev X": "X"}, inplace=True)
    print(df.head())

    return df