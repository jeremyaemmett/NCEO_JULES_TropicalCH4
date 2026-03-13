import itertools
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def plot_parameter_combinations(parameters):
    """Generate all combinations of parameters and plot heatmaps per type group
       with proper formatting per parameter type."""
    
    # Generate all parameter combinations
    keys = list(parameters.keys())
    value_combinations = list(itertools.product(*(parameters[k]["values"] for k in keys)))

    # Helper to parse values
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
        for key, val in zip(keys, combo):
            row[key] = parse_value(val)
        rows.append(row)
    
    df = pd.DataFrame(rows).set_index("suite #")

    # Group parameters by type while preserving dictionary order
    type_groups = {}
    type_order = []
    for param_name, info in parameters.items():
        t = info["type"]
        if t not in type_groups:
            type_groups[t] = []
            type_order.append(t)
        type_groups[t].append(param_name)

    ordered_groups = [(t, type_groups[t]) for t in type_order]
    width_ratios = [len(cols) for _, cols in ordered_groups]

    # Convert categorical columns to codes for plotting, but keep type info for formatting
    for param_name, info in parameters.items():
        if not all(isinstance(parse_value(v), float) for v in info["values"]):
            df[param_name] = pd.Categorical(df[param_name]).codes

    # Colormap selector
    def get_cmap(series):
        return "Spectral_r"

    # Create subplots
    fig, axes = plt.subplots(
        1, len(ordered_groups), figsize=(4, 8),
        gridspec_kw={"width_ratios": width_ratios}
    )
    if len(ordered_groups) == 1:
        axes = [axes]

    for ax, (group, cols) in zip(axes, ordered_groups):
        # Determine annotation format based on parameter type
        # If group is continuous (all floats), use ".2f"; else integer "d"
        is_continuous = all(
            all(isinstance(parse_value(v), float) for v in parameters[c]["values"])
            for c in cols
        )
        fmt = ".2f" if is_continuous else "d"

        sns.heatmap(
            df[cols],
            cmap=get_cmap(df[cols[0]]),
            linewidths=0.5,
            linecolor="white",
            annot=True,
            fmt=fmt,
            cbar=False,
            annot_kws={"size": 8, "weight": "bold", "ha": "center", "va": "center", "color": "black"},
            ax=ax, alpha=0.5
        )

        # Format y-axis: show ticks on every subplot
        ax.set_yticks([i + 0.5 for i in range(df.shape[0])])
        ax.set_yticklabels(df.index, rotation=0, fontsize=8, va='center', ha='right')
        ax.tick_params(axis='y', length=0)
        ax.invert_yaxis()
        ax.set_ylabel(" ")

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    fig.suptitle("Ensemble Parameters", fontsize=12)

    plt.show()

    #plt.savefig('/Users/jae35/Desktop/paramspace.png', dpi=300, bbox_inches='tight')

# Example usage
parameters = {
    "q10_ch4_npp": {"pattern": "q10_ch4_npp", "values": [
                      "q10_ch4_npp=1.3\n", 
                      "q10_ch4_npp=1.5\n", 
                      "q10_ch4_npp=1.7\n",
                      "q10_ch4_npp=2.0\n",
                      "q10_ch4_npp=2.1\n",
                      "q10_ch4_npp=2.3\n",
                      "q10_ch4_npp=2.5\n",
                      "q10_ch4_npp=2.7\n"
                  ], 
                    "type": "q10"},

    "force_file": {"pattern": "file='${ANCIL_BASE_PWD}/qrparm.soil_${RESOLUTION}.nc'",
                  "values": [
                      "file='${ANCIL_BASE_PWD}/qrparm.soil_${RESOLUTION}_utisols.nc'",
                      "file='${ANCIL_BASE_PWD}/qrparm.soil_${RESOLUTION}_comsols.nc'"
                  ],
                  "type": "force_class"},

    "soil_file": {"pattern": "file='${ANCIL_BASE_PWD}/qrparm.soil_${RESOLUTION}.nc'",
                  "values": [
                      "file='${ANCIL_BASE_PWD}/qrparm.soil_${RESOLUTION}_oxisols.nc'",
                      "file='${ANCIL_BASE_PWD}/qrparm.soil_${RESOLUTION}_utisols.nc'",
                      "file='${ANCIL_BASE_PWD}/qrparm.soil_${RESOLUTION}_comsols.nc'"
                  ],
                  "type": "soil_class"}
}

plot_parameter_combinations(parameters)