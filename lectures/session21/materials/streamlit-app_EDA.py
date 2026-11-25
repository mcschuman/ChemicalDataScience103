import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

# page configuration
st.set_page_config(page_title="EDA_Streamlit", layout="wide") # first streamlit command
st.title("Interactive Plotting for EDA (Matplotlib & Seaborn)")
sns.set_theme(style="whitegrid")


# Choose data source

@st.cache_data
def load_csv(file) -> pd.DataFrame:
    return pd.read_csv(file)

st.sidebar.header("1. Data & Target")
uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is None:
    st.info("Upload a CSV file in the sidebar to begin exploring.")
    st.stop() # immediately stops execution if file not loaded

try:
    df = load_csv(uploaded_file)
except Exception as e:
    st.error(f"Could not read CSV file: {e}")
    st.stop()

if df.empty:
    st.warning("The uploaded CSV is empty.")
    st.stop()

all_cols = list(df.columns)
numeric_cols = df.select_dtypes(include="number").columns.tolist()

# manual target column selection ("None" allows ungrouped exploration)
target_options = ["None (Ungrouped)"] + all_cols
target_col_choice = st.sidebar.selectbox(
    "Target / Grouping Column",
    target_options,
    index=len(all_cols) if len(all_cols) > 0 else 0,
)
target_col = None if target_col_choice == "None (Ungrouped)" else target_col_choice

# optional: treat a numeric target with few unique values as a categorical label
treat_target_as_category = False
hue_col = None
if target_col is not None:
    n_unique = df[target_col].nunique(dropna=True)
    is_numeric_target = target_col in numeric_cols
    if is_numeric_target and n_unique <= 20:
        treat_target_as_category = st.sidebar.checkbox(
            f"Treat '{target_col}' as categorical ({n_unique} unique values)",
            value=True,
        )
    if is_numeric_target and not treat_target_as_category:
        # Continuous numeric target: keep as numeric series for coloring/plotting
        hue_col = target_col
    else:
        # Categorical or string target: convert NaNs cleanly to label for grouping
        hue_col = "__target_category__"
        df[hue_col] = df[target_col].fillna("Missing").astype(str)

if not numeric_cols:
    st.warning("No numeric columns found in this CSV for plotting or filtering.")
    st.stop()

# plot & filter controls
st.sidebar.header("2. Plot & Filter Controls")

plot_type = st.sidebar.selectbox(
    "Plot Type",
    ["Scatter Plot", "Violin + Box Plot", "Histogram / KDE", "Correlation Heatmap"],
)

default_x = 0
default_y = 1 if len(numeric_cols) > 1 else 0

x_feature = st.sidebar.selectbox("X-Axis Feature", numeric_cols, index=default_x)
y_feature = st.sidebar.selectbox(
    "Y-Axis Feature",
    numeric_cols,
    index=default_y,
    disabled=(plot_type in ["Histogram / KDE", "Correlation Heatmap"]),
)

use_target_grouping = st.sidebar.checkbox(
    "Apply Target Grouping / Hue",
    value=(target_col is not None),
    disabled=(target_col is None),
)
active_hue = hue_col if (use_target_grouping and target_col is not None) else None

st.sidebar.subheader("Scales & Range Filter")
log_x = st.sidebar.checkbox("Log Scale (X-Axis)", value=False)
log_y = st.sidebar.checkbox("Log Scale (Y-Axis)", value=False)

# Slider filter on any chosen numeric column
filter_col = st.sidebar.selectbox("Range Filter Column", numeric_cols, index=0)
col_min = float(df[filter_col].min())
col_max = float(df[filter_col].max())

if col_min < col_max:
    selected_range = st.sidebar.slider(
        f"Filter '{filter_col}'",
        min_value=col_min,
        max_value=col_max,
        value=(col_min, col_max),
    )
    filtered_df = df[df[filter_col].between(selected_range[0], selected_range[1], inclusive="both")]
else:
    st.sidebar.caption(f"'{filter_col}' has a constant value ({col_min}).")
    filtered_df = df.copy()

# Top summary metrics
m1, m2, m3, m4 = st.columns(4)
m1.metric("Rows Shown", f"{len(filtered_df)} / {len(df)}")
m2.metric("Target Column", target_col if target_col else "None")
m3.metric(f"Mean {x_feature}", f"{filtered_df[x_feature].mean():.2f}" if not filtered_df.empty else "N/A")
if plot_type in ["Scatter Plot", "Violin + Box Plot"] and not filtered_df.empty:
    m4.metric(f"Mean {y_feature}", f"{filtered_df[y_feature].mean():.2f}")
else:
    m4.metric("Numeric Features", len(numeric_cols))

if filtered_df.empty:
    st.warning("No rows match the current filter range.")
    st.stop()

# Render plot
fig, ax = plt.subplots(figsize=(10, 5.5))

if plot_type == "Scatter Plot":
    plot_data = filtered_df.dropna(subset=[x_feature, y_feature])
    sns.scatterplot(
        data=plot_data,
        x=x_feature,
        y=y_feature,
        hue=active_hue,
        alpha=0.85,
        s=65,
        ax=ax,
    )
    ax.set_title(f"{y_feature} vs. {x_feature}")

elif plot_type == "Violin + Box Plot":
    if active_hue is not None and active_hue == "__target_category__":
        plot_data = filtered_df.dropna(subset=[y_feature])
        sns.violinplot(
            data=plot_data,
            x=active_hue,
            y=y_feature,
            hue=active_hue,
            inner="box",
            cut=0,
            legend=False,
            ax=ax,
        )
        ax.set_xlabel(target_col)
        ax.tick_params(axis="x", rotation=20)
    else:
        plot_data = filtered_df.dropna(subset=[x_feature, y_feature])
        sns.scatterplot(
            data=plot_data,
            x=x_feature,
            y=y_feature,
            hue=active_hue,
            alpha=0.85,
            s=65,
            ax=ax,
        )
        st.caption(
            "Tip: Select a categorical target column (or enable 'Treat target as categorical') for grouped violin/box plots."
        )
    ax.set_title(f"Distribution of {y_feature}")

elif plot_type == "Histogram / KDE":
    plot_data = filtered_df.dropna(subset=[x_feature])
    sns.histplot(
        data=plot_data,
        x=x_feature,
        hue=active_hue,
        kde=True,
        element="step",
        common_norm=False,
        ax=ax,
    )
    ax.set_title(f"Distribution of {x_feature}")

else:  # Correlation heatmap
    if len(numeric_cols) < 2:
        st.warning("Need at least 2 numeric columns to compute a correlation matrix.")
        plt.close(fig)
        st.stop()
    corr = filtered_df[numeric_cols].corr(numeric_only=True)
    sns.heatmap(
        corr,
        annot=len(numeric_cols) <= 15,
        fmt=".2f",
        cmap="RdBu_r",
        vmin=-1,
        vmax=1,
        square=True,
        annot_kws={"size": 8},
        ax=ax,
    )
    ax.set_title("Numeric Feature Correlation Matrix (Pearson)")

# Safe log-scale application
if plot_type != "Correlation Heatmap":
    if log_x and ax.get_xscale() != "log":
        if (filtered_df[x_feature].dropna() > 0).all():
            ax.set_xscale("log")
        else:
            st.caption("Skipped X log scale: feature has zero, negative, or missing values.")

    if log_y and plot_type in ["Scatter Plot", "Violin + Box Plot"]:
        if (filtered_df[y_feature].dropna() > 0).all():
            ax.set_yscale("log")
        else:
            st.caption("Skipped Y log scale: feature has zero, negative, or missing values.")

fig.tight_layout()
st.pyplot(fig)
plt.close(fig)

# Data & summary section
with st.expander("Inspect Filtered Data & Summary Statistics"):
    display_cols = [c for c in all_cols if c != "__target_category__"]
    tab_stats, tab_raw = st.tabs(["Summary Stats", "Raw Data"])
    with tab_stats:
        st.dataframe(filtered_df[numeric_cols].describe().T, width="stretch")
    with tab_raw:
        st.dataframe(filtered_df[display_cols], width="stretch")