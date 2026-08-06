from pathlib import Path
import numpy as np
import pandas as pd


# =====================================================
# VARIABLE TABLE
# =====================================================

variable_table = pd.DataFrame(
[
    [0,1,0],
    [0,1,1],
    [0,2,0],
    [0,2,1],
    [0,3,0],
    [0,3,1],
    [0,4,0],
    [0,4,1],

    [1,1,0],
    [1,1,1],
    [1,2,0],
    [1,2,1],
    [1,3,0],
    [1,3,1],
    [1,4,0],
    [1,4,1],

    [2,1,0],
    [2,1,1],
    [2,2,0],
    [2,2,1],
    [2,3,0],
    [2,3,1],
    [2,4,0],
    [2,4,1],
],
columns=[
    "substrate",
    "q10",
    "soilmap"
]
)


print("\nVARIABLE TABLE")
print(variable_table.to_string(index=False))


# =====================================================
# READ JULES RESULTS
# =====================================================

directory = Path(
    "/Users/jae35/Desktop/JULES_test_data/ID_suites"
)


rows = []


for subdir in sorted(directory.iterdir()):

    if not subdir.is_dir():
        continue

    name = subdir.name


    try:

        code = name.split("_")[1]

        substrate = int(code[0])
        q10 = int(code[1])
        soilmap = int(code[2])

    except:
        continue


    filepath = (
        subdir
        / "plots"
        / "output"
        / "fch4_wetl"
        / "_arealmean_tseries.txt"
    )


    if filepath.exists():

        y = np.loadtxt(filepath)

        rows.append(
            {
                "suite": name,
                "substrate": substrate,
                "q10": q10,
                "soilmap": soilmap,
                "fCH4": np.mean(y)
            }
        )


df = pd.DataFrame(rows)


print("\nJULES VALUE TABLE")
print(df.to_string(index=False))


# =====================================================
# FACTORIAL DECOMPOSITION
# =====================================================

grand_mean = df["fCH4"].mean()

total_ss = np.sum(
    (df["fCH4"] - grand_mean)**2
)


components = {}


# -----------------------------------------------------
# Main effects
# -----------------------------------------------------

for factor in [
    "substrate",
    "q10",
    "soilmap"
]:

    means = (
        df.groupby(factor)["fCH4"]
        .mean()
    )


    ss = sum(
        len(df[df[factor] == level]) *
        (mean - grand_mean)**2
        for level, mean in means.items()
    )

    components[factor] = ss


# -----------------------------------------------------
# Two-way interactions
# -----------------------------------------------------

pairs = [
    ("substrate", "q10"),
    ("substrate", "soilmap"),
    ("q10", "soilmap")
]


for a, b in pairs:

    table = (
        df.groupby([a,b])["fCH4"]
        .mean()
    )


    mean_a = df.groupby(a)["fCH4"].mean()
    mean_b = df.groupby(b)["fCH4"].mean()


    ss = 0

    for (ia, ib), value in table.items():

        interaction = (
            value
            - mean_a[ia]
            - mean_b[ib]
            + grand_mean
        )

        n = len(
            df[
                (df[a] == ia) &
                (df[b] == ib)
            ]
        )

        ss += n * interaction**2


    components[f"{a}:{b}"] = ss


# -----------------------------------------------------
# Three-way interaction
# -----------------------------------------------------

table = (
    df.groupby(
        [
            "substrate",
            "q10",
            "soilmap"
        ]
    )["fCH4"]
    .mean()
)


ss = 0


for (s,q,m), value in table.items():

    smean = df.groupby("substrate")["fCH4"].mean()[s]
    qmean = df.groupby("q10")["fCH4"].mean()[q]
    mmean = df.groupby("soilmap")["fCH4"].mean()[m]


    sq = (
        df.groupby(
            [
                "substrate",
                "q10"
            ]
        )["fCH4"]
        .mean()
    )

    sm = (
        df.groupby(
            [
                "substrate",
                "soilmap"
            ]
        )["fCH4"]
        .mean()
    )

    qm = (
        df.groupby(
            [
                "q10",
                "soilmap"
            ]
        )["fCH4"]
        .mean()
    )


    interaction = (
        value
        - sq.loc[(s,q)]
        - sm.loc[(s,m)]
        - qm.loc[(q,m)]
        + smean
        + qmean
        + mmean
        - grand_mean
    )


    ss += interaction**2


components["substrate:q10:soilmap"] = ss



# =====================================================
# OUTPUT
# =====================================================

result = pd.DataFrame(
    {
        "sum_sq": components
    }
)


result["fraction"] = (
    result["sum_sq"]
    /
    total_ss
)


print("\nVARIANCE DECOMPOSITION")
print(result)


print("\nPERCENT CONTRIBUTION")

for name, row in result.iterrows():

    print(
        f"{name:35s}"
        f"{row['fraction']*100:8.3f}%"
    )