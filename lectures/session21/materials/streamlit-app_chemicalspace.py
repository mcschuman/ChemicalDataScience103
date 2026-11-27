# generated code (Gemini), treat with caution

from io import BytesIO

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from rdkit import Chem
from rdkit.Chem import Draw, rdFingerprintGenerator
from rdkit.Chem.Descriptors import MolWt
from rdkit.Chem.rdMolDescriptors import CalcMolFormula
from sklearn.cluster import DBSCAN, KMeans
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

st.set_page_config(page_title="Chemical Space Explorer", layout="wide")
st.title("Chemical Space Clustering & Dimensionality Reduction")


@st.cache_data
def read_csv_cached(file) -> pd.DataFrame:
    return pd.read_csv(file)


@st.cache_data
def smiles_to_png_bytes(smiles: str, size: tuple[int, int] = (320, 320)) -> bytes | None:
    """Render a SMILES string to PNG bytes via RDKit."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    img = Draw.MolToImage(mol, size=size)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@st.cache_data
def featurize_smiles(
    smiles_list: list[str], radius: int = 2, n_bits: int = 2048
) -> tuple[pd.DataFrame, np.ndarray, list[str]]:
    """Parse SMILES with RDKit and compute Morgan fingerprints + molecular properties."""
    gen = rdFingerprintGenerator.GetMorganGenerator(radius=radius, fpSize=n_bits)
    valid_rows = []
    fps = []
    invalid_smiles = []

    for idx, smi in enumerate(smiles_list):
        if not isinstance(smi, str) or not smi.strip():
            invalid_smiles.append(str(smi))
            continue
        clean_smi = smi.strip()
        mol = Chem.MolFromSmiles(clean_smi)
        if mol is None:
            invalid_smiles.append(clean_smi)
            continue

        fp = gen.GetFingerprintAsNumPy(mol).astype(np.float32)
        fps.append(fp)
        valid_rows.append(
            {
                "_orig_index": idx,
                "_smiles": clean_smi,
                "_formula": CalcMolFormula(mol),
                "_mol_wt": round(MolWt(mol), 2),
            }
        )

    meta_df = pd.DataFrame(valid_rows)
    fp_matrix = np.vstack(fps) if fps else np.empty((0, n_bits), dtype=np.float32)
    return meta_df, fp_matrix, invalid_smiles


# --- Sidebar: 1. Data & Fingerprints ---
st.sidebar.header("1. CSV & Fingerprints")
uploaded_file = st.sidebar.file_uploader("Upload CSV containing SMILES", type=["csv"])

if uploaded_file is None:
    st.info("Upload a CSV file with a SMILES column in the sidebar to explore chemical space.")
    st.stop()

try:
    raw_df = read_csv_cached(uploaded_file)
except Exception as exc:
    st.error(f"Failed to read CSV: {exc}")
    st.stop()

if raw_df.empty:
    st.warning("Uploaded CSV is empty.")
    st.stop()

cols = list(raw_df.columns)
default_smiles_idx = next((i for i, c in enumerate(cols) if "smile" in c.lower()), 0)
smiles_col = st.sidebar.selectbox("SMILES Column", cols, index=default_smiles_idx)

label_options = ["(Row Index)"] + cols
label_col_choice = st.sidebar.selectbox("Optional Compound ID / Label Column", label_options, index=0)

fp_radius = st.sidebar.slider("Morgan Fingerprint Radius", min_value=1, max_value=4, value=2)
fp_bits = st.sidebar.selectbox("Fingerprint Bit Length", [512, 1024, 2048, 4096], index=2)

meta_df, fp_matrix, invalid_smiles = featurize_smiles(
    raw_df[smiles_col].tolist(), radius=fp_radius, n_bits=fp_bits
)

if invalid_smiles:
    st.sidebar.warning(f"Skipped {len(invalid_smiles)} invalid/empty SMILES entries.")

n_valid = len(meta_df)
if n_valid < 3:
    st.error("Need at least 3 valid SMILES structures to run dimensionality reduction and clustering.")
    st.stop()

merged_df = meta_df.copy().reset_index(drop=True)
if label_col_choice != "(Row Index)":
    merged_df["_label"] = raw_df.loc[merged_df["_orig_index"], label_col_choice].astype(str).values
else:
    merged_df["_label"] = [f"Mol #{i}" for i in merged_df["_orig_index"]]

# --- Sidebar: 2. Dimensionality Reduction ---
st.sidebar.header("2. Dimensionality Reduction")
dim_method = st.sidebar.selectbox("Method", ["PCA", "t-SNE"])

if dim_method == "PCA":
    pca_random_state = st.sidebar.number_input("Random State", min_value=0, value=42, step=1)
    coords = PCA(n_components=2, random_state=int(pca_random_state)).fit_transform(fp_matrix)
else:
    max_perp = max(2, min(50, n_valid - 1))
    default_perp = min(30, max_perp)
    perplexity = st.sidebar.slider(
        "t-SNE Perplexity",
        min_value=2.0,
        max_value=float(max_perp),
        value=float(default_perp),
        step=1.0,
    )
    # learning_rate = st.sidebar.select_slider(
    #     "t-SNE Learning Rate",
    #     options=[50.0, 100.0, 200.0, 500.0, "auto"],
    #     value=200.0,
    # )
    tsne_seed = st.sidebar.number_input("Random State", min_value=0, value=42, step=1)
    coords = TSNE(
        n_components=2,
        perplexity=perplexity,
        # learning_rate=learning_rate,
        init="pca",
        random_state=int(tsne_seed),
    ).fit_transform(fp_matrix)

merged_df["dim_1"] = coords[:, 0]
merged_df["dim_2"] = coords[:, 1]

# --- Sidebar: 3. Clustering (scikit-learn) ---
st.sidebar.header("3. Clustering")
cluster_method = st.sidebar.selectbox("Clustering Algorithm", ["KMeans", "DBSCAN"])

if cluster_method == "KMeans":
    max_k = min(15, n_valid)
    n_clusters = st.sidebar.slider(
        "Number of Clusters (k)", min_value=2, max_value=max(2, max_k), value=min(4, max(2, max_k))
    )
    km_seed = st.sidebar.number_input("KMeans Random State", min_value=0, value=42, step=1)
    labels = KMeans(n_clusters=n_clusters, n_init="auto", random_state=int(km_seed)).fit_predict(
        fp_matrix
    )
    merged_df["cluster"] = [f"Cluster {c}" for c in labels]
else:
    eps = st.sidebar.slider(
        "DBSCAN eps (neighborhood radius)",
        min_value=0.1,
        max_value=15.0,
        value=3.5,
        step=0.1,
    )
    min_samples = st.sidebar.slider(
        "DBSCAN min_samples",
        min_value=2,
        max_value=min(25, n_valid),
        value=min(4, n_valid),
        step=1,
    )
    metric = st.sidebar.selectbox("Distance Metric", ["euclidean", "manhattan", "cosine"])
    labels = DBSCAN(eps=eps, min_samples=min_samples, metric=metric).fit_predict(fp_matrix)
    merged_df["cluster"] = ["Noise (-1)" if c == -1 else f"Cluster {c}" for c in labels]

# --- Top Metrics ---
n_found_clusters = len(set(labels) - {-1})
n_noise = int((labels == -1).sum())

c1, c2, c3, c4 = st.columns(4)
c1.metric("Valid Molecules", f"{n_valid} / {len(raw_df)}")
c2.metric("Projection", dim_method)
c3.metric("Clusters Found", n_found_clusters)
c4.metric("Noise Points (-1)", n_noise if cluster_method == "DBSCAN" else 0)


@st.fragment
def render_plot_and_inspector(
    df: pd.DataFrame, proj_name: str, clust_name: str
) -> None:
    option_indices = df.index.tolist()
    if not option_indices:
        return

    if (
        "mol_inspector_select" not in st.session_state
        or st.session_state["mol_inspector_select"] not in option_indices
    ):
        st.session_state["mol_inspector_select"] = option_indices[0]

    plot_col, mol_col = st.columns([2.2, 1.0], gap="medium")

    fig = go.Figure()
    unique_clusters = sorted(df["cluster"].unique(), key=lambda x: (x.startswith("Noise"), x))

    for cl_name in unique_clusters:
        sub = df[df["cluster"] == cl_name]
        custom = np.stack(
            [sub.index.to_numpy(), sub["_label"].values, sub["_smiles"].values],
            axis=-1,
        )
        is_noise = cl_name.startswith("Noise")

        fig.add_trace(
            go.Scatter(
                x=sub["dim_1"],
                y=sub["dim_2"],
                mode="markers",
                name=cl_name,
                customdata=custom,
                marker=dict(
                    size=10,
                    opacity=0.65 if is_noise else 0.92,
                    symbol="x" if is_noise else "circle",
                    line=dict(width=1, color="rgba(30,30,30,0.45)"),
                ),
                hovertemplate=(
                    "<b>%{customdata[1]}</b><br>"
                    "Cluster: " + cl_name + "<br>"
                    "SMILES: %{customdata[2]}<br>"
                    "<i>Click point to inspect 2D structure</i>"
                    "<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        title=f"Chemical Space ({proj_name}) Colored by {clust_name}",
        xaxis_title=f"{proj_name} 1",
        yaxis_title=f"{proj_name} 2",
        height=620,
        hovermode="closest",
        legend_title="Cluster",
        margin=dict(l=40, r=20, t=50, b=40),
    )

    with plot_col:
        event = st.plotly_chart(
            fig,
            use_container_width=True,
            on_select="rerun",
            selection_mode="points",
            key="chem_space_plot",
            config={"displaylogo": False, "responsive": True},
        )

    # Sync clicked point directly into the selectbox's session_state key
    if event and event.selection and event.selection.points:
        pt = event.selection.points[0]
        if "customdata" in pt and pt["customdata"]:
            clicked_idx = int(pt["customdata"][0])
            if (
                clicked_idx in option_indices
                and st.session_state["mol_inspector_select"] != clicked_idx
            ):
                st.session_state["mol_inspector_select"] = clicked_idx
                st.rerun(scope="fragment")

    with mol_col:
        st.subheader("Structure Inspector")
        chosen_idx = st.selectbox(
            "Click a point or pick a molecule",
            options=option_indices,
            format_func=lambda i: f"{df.loc[i, '_label']} ({df.loc[i, 'cluster']})",
            key="mol_inspector_select",
        )

        row = df.loc[chosen_idx]
        png_bytes = smiles_to_png_bytes(row["_smiles"], size=(320, 320))

        if png_bytes is not None:
            st.image(png_bytes, caption=row["_label"], use_container_width=True)

        st.markdown(f"**Cluster:** {row['cluster']}")
        st.markdown(f"**Formula:** {row['_formula']}  |  **MW:** {row['_mol_wt']}")
        st.code(row["_smiles"], language="text")


render_plot_and_inspector(merged_df, dim_method, cluster_method)

# --- Cluster Summary & Table ---
with st.expander("Inspect Clustered Molecules & Summary"):
    counts = (
        merged_df["cluster"]
        .value_counts()
        .rename_axis("Cluster")
        .reset_index(name="Molecule Count")
    )
    st.dataframe(counts, use_container_width=True, hide_index=True)

    show_cols = ["_label", "_smiles", "_formula", "_mol_wt", "cluster", "dim_1", "dim_2"]
    st.dataframe(merged_df[show_cols], use_container_width=True, hide_index=True)

