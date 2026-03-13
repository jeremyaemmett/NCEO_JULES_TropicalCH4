import itertools
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def plot_parameter_combinations(parameters, split_first_group=False):
    keys = list(parameters.keys())
    value_combinations = list(itertools.product(*(parameters[k]["values"] for k in keys)))

    def parse_value(val):
        val = val.strip()
        if "=" in val:
            val = val.split("=")[1].strip()
        try:
            return float(val)
        except ValueError:
            return val

    # Build DataFrame
    rows = []
    for i, combo in enumerate(value_combinations, start=1):
        row = {"suite #": i}
        secondary_code = []
        for key, val in zip(keys, combo):
            parsed_val = parse_value(val)
            row[key] = parsed_val
            index_in_group = parameters[key]["values"].index(val) + 1
            secondary_code.append(str(index_in_group))
        row["secondary #"] = "".join(secondary_code)
        rows.append(row)
    
    df = pd.DataFrame(rows).set_index("suite #")

    # Group by type
    type_groups = {}
    type_order = []
    for param_name, info in parameters.items():
        t = info["type"]
        if t not in type_groups:
            type_groups[t] = []
            type_order.append(t)
        type_groups[t].append(param_name)
    ordered_groups = [(t, type_groups[t]) for t in type_order]

    # Identify categorical vs numeric columns
    cat_columns = []
    numeric_cols = []
    for param_name, info in parameters.items():
        if all(isinstance(parse_value(v), float) for v in info["values"]):
            numeric_cols.append(param_name)
        else:
            # Fix: specify categories in original order so codes are sequential
            df[param_name] = pd.Categorical(df[param_name], categories=[parse_value(v) for v in info["values"]]).codes
            cat_columns.append(param_name)

    # Precompute global min/max for each variable
    global_min = df[numeric_cols].min() if numeric_cols else pd.Series()
    global_max = df[numeric_cols].max() if numeric_cols else pd.Series()
    cat_min = {c: 0 for c in cat_columns}
    cat_max = {c: df[c].max() for c in cat_columns}

    first_group_type, first_group_cols = ordered_groups[0]
    if split_first_group:
        first_group_values = sorted(df[first_group_cols[0]].unique())
        subsets = [(val, df[df[first_group_cols[0]] == val]) for val in first_group_values]
    else:
        subsets = [(None, df)]

    num_subsets = len(subsets)
    width_ratios = []
    for _, cols in ordered_groups:
        width_ratios.extend([len(cols)] * num_subsets)

    fig, axes = plt.subplots(
        1, len(width_ratios), figsize=(len(width_ratios)*2.2, 9),
        gridspec_kw={"width_ratios": width_ratios}
    )
    if len(width_ratios) == 1:
        axes = [axes]
    axes = axes.flatten() if hasattr(axes, "shape") else list(axes)

    ax_idx = 0
    for val, sub_df in subsets:
        for _, cols in ordered_groups:
            ax = axes[ax_idx]

            # Determine global vmin/vmax for this group
            vmins = []
            vmaxs = []
            fmt = ""  # default format
            for c in cols:
                if c in numeric_cols:
                    vmins.append(global_min[c])
                    vmaxs.append(global_max[c])
                    fmt = ".2f"
                else:
                    vmins.append(cat_min[c])
                    vmaxs.append(cat_max[c])
                    fmt = "d"  # integer display for categorical

            vmin, vmax = min(vmins), max(vmaxs)

            sns.heatmap(
                sub_df[cols],
                cmap="Spectral_r",
                linewidths=0.5,
                linecolor="white",
                annot=True,
                fmt=fmt,
                cbar=False,
                annot_kws={"size": 8, "weight": "bold", "ha": "center", "va": "center", "color": "black"},
                ax=ax,
                vmin=vmin,
                vmax=vmax,
                alpha=0.5
            )

            ax.set_yticks([i + 0.5 for i in range(sub_df.shape[0])])
            ax.set_yticklabels(sub_df["secondary #"], rotation=0, fontsize=8, va='center', ha='right')
            ax.tick_params(axis='y', length=0)
            ax.invert_yaxis()
            ax.set_ylabel(" ")

            if split_first_group:
                ax.set_title(f"{first_group_cols[0]}={val}", fontsize=10)

            ax_idx += 1

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    fig.suptitle("Ensemble Parameters", fontsize=12)
    plt.show()


# -----------------------------
# Example parameter dictionary
# -----------------------------
parameters = {
    "force_file": {
        "pattern": "file='${ANCIL_BASE_PWD}/qrparm.soil_${RESOLUTION}.nc'",
        "values": [
            "file='${ANCIL_BASE_PWD}/qrparm.soil_${RESOLUTION}_ERA-Interim.nc'",
            "file='${ANCIL_BASE_PWD}/qrparm.soil_${RESOLUTION}_WFDEI.nc'",
            "file='${ANCIL_BASE_PWD}/qrparm.soil_${RESOLUTION}_CRU-NCEP.nc'"
        ],
        "type": "force_class"
    },
    "veg_mode": {
        "pattern": "file='${ANCIL_BASE_PWD}/qrparm.soil_${RESOLUTION}.nc'",
        "values": [
            "file='${ANCIL_BASE_PWD}/qrparm.soil_${RESOLUTION}_phenology.nc'",
            "file='${ANCIL_BASE_PWD}/qrparm.soil_${RESOLUTION}_triffid_fixed.nc'",
            "file='${ANCIL_BASE_PWD}/qrparm.soil_${RESOLUTION}_triffid_dynamic.nc'"
        ],
        "type": "veg_class"
    },
    "q10_ch4_npp": {
        "pattern": "q10_ch4_npp",
        "values": [
            "q10_ch4_npp=1.3\n", "q10_ch4_npp=1.5\n", "q10_ch4_npp=1.7\n",
            "q10_ch4_npp=2.0\n", "q10_ch4_npp=2.1\n", "q10_ch4_npp=2.3\n",
            "q10_ch4_npp=2.5\n", "q10_ch4_npp=2.7\n"
        ],
        "type": "q10"
    },
    "soil_file": {
        "pattern": "file='${ANCIL_BASE_PWD}/qrparm.soil_${RESOLUTION}.nc'",
        "values": [
            "file='${ANCIL_BASE_PWD}/qrparm.soil_${RESOLUTION}_oxisols.nc'",
            "file='${ANCIL_BASE_PWD}/qrparm.soil_${RESOLUTION}_utisols.nc'",
            "file='${ANCIL_BASE_PWD}/qrparm.soil_${RESOLUTION}_comsols.nc'"
        ],
        "type": "soil_class"
    }
}

# Run the function
plot_parameter_combinations(parameters, split_first_group=True)