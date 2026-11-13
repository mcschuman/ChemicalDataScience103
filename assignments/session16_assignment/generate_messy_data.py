"""
Generate a deliberately messy compound-screening dataset for a data-wrangling exercise.

Scenario: a small screening lab measured physicochemical properties and assay conditions for
~1,500 compounds and recorded whether each compound was "active" in a biochemical assay.
The *clean* underlying data follow a simple, learnable rule (activity depends on logP, TPSA,
MW, HBD and assay pH). On top of that we inject typical real-life problems:

  - inconsistent column names (spaces, units in names, mixed case, typos)
  - mixed units (temperature C/K/F, solubility uM/mM/mg/mL)
  - numbers stored as text with units ("352.4 g/mol")
  - many different missing-value codes (NA, n.a., -, -999, empty ...)
  - "<LOD" entries, sensor glitches / impossible values, true outliers
  - exact duplicates and re-measurements of the same compound
  - inconsistent categorical labels (FP / fp / Fluorescence Polarization ...)
  - mixed date formats
  - free-text notes that signal unreliable measurements (contaminated, precipitated ...)
  - a constant column and an ID column that carry no information

Usage:  python generate_messy_data.py [seed]
Every seed gives a different (but statistically similar) dataset, so each cohort can get its own.
"""
import sys
import numpy as np
import pandas as pd

seed = int(sys.argv[1]) if len(sys.argv) > 1 else 42
rng = np.random.default_rng(seed)
N = 1500

# ---------------------------------------------------------------- clean "ground truth"
mw = np.clip(rng.normal(360, 85, N), 150, 700)
logp = np.clip(rng.normal(2.6, 1.3, N), -2, 7)
tpsa = np.clip(rng.normal(85, 30, N) + 6 * (logp - 2.6) * -1, 10, 200)
hbd = np.clip(rng.poisson(1.8, N), 0, 6)
ph = rng.choice([6.5, 7.0, 7.4, 8.0], size=N, p=[0.15, 0.25, 0.45, 0.15])
temp_c = rng.choice([20.0, 25.0, 30.0, 37.0], size=N, p=[0.15, 0.45, 0.10, 0.30]) + rng.normal(0, 0.3, N)
sol_um = np.exp(rng.normal(np.log(80) - 0.5 * (logp - 2.6) - 0.004 * (mw - 360), 0.8, N))  # uM

score = (0.9 * (logp - 2.6)
         - 0.035 * (tpsa - 85)
         + 0.005 * (mw - 360)
         - 0.35 * (hbd - 1.8)
         + 0.8 * (ph - 7.2)
         + 0.6 * np.log(sol_um / 80)
         + 0.07 * (temp_c - 28)
         + rng.normal(0, 0.4, N))
active = (score > np.median(score) + 0.2).astype(int)

methods = rng.choice(["FP", "TR-FRET", "AlphaScreen"], size=N, p=[0.5, 0.3, 0.2])
operators = rng.choice(["Anna Keller", "Ben Meier", "Chiara Rossi", "David Huber"], size=N)
plates = rng.integers(1, 25, N)
dates = pd.to_datetime("2024-01-08") + pd.to_timedelta(rng.integers(0, 300, N), unit="D")

df = pd.DataFrame({
    "compound_id": [f"CPD-{i:04d}" for i in range(1, N + 1)],
    "mw": mw, "logp": logp, "tpsa": tpsa, "hbd": hbd.astype(float),
    "ph": ph, "temp_c": temp_c, "sol_um": sol_um,
    "method": methods, "operator": operators, "plate": plates, "date": dates,
    "active": active,
})
notes_pool = np.array([""] * N, dtype=object)

# ---------------------------------------------------------------- inject: unreliable measurements
# Rows with quality problems: their activity label is partly random (=> removing them helps a model)
bad_note_kinds = ["contaminated sample", "Sample precipitated", "pipetting error", "hemolysed", "CONTAMINATION?"]
bad_idx = rng.choice(N, size=int(0.10 * N), replace=False)
for i in bad_idx:
    notes_pool[i] = rng.choice(bad_note_kinds)
    if rng.random() < 0.7:
        df.loc[i, "active"] = rng.integers(0, 2)
harmless = ["repeat measurement", "ok", "re-run on new plate", "fresh DMSO stock", "see ELN p.34"]
ok_idx = rng.choice(np.setdiff1d(np.arange(N), bad_idx), size=int(0.12 * N), replace=False)
for i in ok_idx:
    notes_pool[i] = rng.choice(harmless)
df["notes"] = notes_pool

# ---------------------------------------------------------------- inject: real outliers / glitches
n_out = int(0.02 * N)
idx = rng.choice(N, n_out, replace=False)
df.loc[idx[: n_out // 3], "logp"] = rng.choice([25.0, 99.9, -45.0], n_out // 3)
df.loc[idx[n_out // 3: 2 * n_out // 3], "tpsa"] = rng.choice([-10.0, 900.0, 0.0], len(idx[n_out // 3: 2 * n_out // 3]))
df.loc[idx[2 * n_out // 3:], "mw"] = rng.choice([0.0, 35000.0, 3.5], len(idx[2 * n_out // 3:]))

# ---------------------------------------------------------------- inject: mixed units
# Temperature -> column "Temp" + unit column
temp_val = df["temp_c"].copy()
temp_unit = np.array(["C"] * N, dtype=object)
r = rng.random(N)
k_mask, f_mask = r < 0.15, (r >= 0.15) & (r < 0.27)
temp_val[k_mask] = temp_val[k_mask] + 273.15
temp_val[f_mask] = temp_val[f_mask] * 9 / 5 + 32
temp_unit[k_mask] = rng.choice(["K", "kelvin"], k_mask.sum())
temp_unit[f_mask] = rng.choice(["F", "°F"], f_mask.sum())
temp_unit[(~k_mask) & (~f_mask)] = rng.choice(["C", "°C", "c"], ((~k_mask) & (~f_mask)).sum(), p=[0.6, 0.3, 0.1])

# Solubility -> value + unit (uM, mM, mg/mL; mg/mL needs MW for the conversion)
sol_val = df["sol_um"].copy()
sol_unit = np.array(["uM"] * N, dtype=object)
r = rng.random(N)
mm_mask, mg_mask = r < 0.25, (r >= 0.25) & (r < 0.50)
sol_val[mm_mask] = sol_val[mm_mask] / 1000.0
sol_unit[mm_mask] = "mM"
true_mw = mw  # convert with the TRUE mw (not the glitched one)
sol_val[mg_mask] = sol_val[mg_mask] * 1e-6 * true_mw[mg_mask]  # uM -> mol/L -> g/L (= mg/mL)
sol_unit[mg_mask] = "mg/mL"
um_mask = ~(mm_mask | mg_mask)
sol_unit[um_mask] = rng.choice(["uM", "µM", "UM"], um_mask.sum(), p=[0.5, 0.4, 0.1])

# ---------------------------------------------------------------- assemble the messy table
messy = pd.DataFrame({
    "Compound ID": df["compound_id"],
    "MW (g/mol)": df["mw"].round(1).astype(object),
    "LogP": df["logp"].round(2).astype(object),
    "tPSA [A^2]": df["tpsa"].round(1).astype(object),
    "H-Bond Donors": df["hbd"].astype(object),
    "Assay pH": df["ph"].astype(object),
    "Temp": np.round(temp_val, 2).astype(object),
    "Temp_unit": temp_unit,
    "Solubility": sol_val.map(lambda v: float(f"{v:.3g}")).astype(object),
    "Solubilty unit": sol_unit,   # typo on purpose
    "Method": df["method"].astype(object),
    "operator ": df["operator"].astype(object),
    "PLATE": df["plate"].astype(object),
    "Measurement Date": df["date"],
    "Project": "PRJ-042",
    "Notes": df["notes"],
    "Active?": df["active"].astype(object),
})

# numbers as text with units for part of the MW column
m = rng.random(N) < 0.10
messy.loc[m, "MW (g/mol)"] = [f"{v} g/mol" for v in messy.loc[m, "MW (g/mol)"]]

# <LOD in solubility
lod = rng.random(N) < 0.03
messy.loc[lod, "Solubility"] = "<LOD"

# missing values with many different codes
for col, frac in [("MW (g/mol)", 0.02), ("LogP", 0.04), ("tPSA [A^2]", 0.05), ("H-Bond Donors", 0.03),
                  ("Assay pH", 0.03), ("Solubility", 0.04), ("Method", 0.02)]:
    mm = rng.random(N) < frac
    messy.loc[mm, col] = rng.choice(["NA", "n.a.", "-", "", -999, "N/A", np.nan], mm.sum())

# inconsistent categorical labels
method_variants = {
    "FP": ["FP", "fp", "Fluorescence Polarization", "FP "],
    "TR-FRET": ["TR-FRET", "TRFRET", "tr-fret", "TR-FRET "],
    "AlphaScreen": ["AlphaScreen", "Alphascreen", "alpha screen"],
}
messy["Method"] = [rng.choice(method_variants[v]) if v in method_variants else v for v in messy["Method"]]
messy["operator "] = [v.upper() if rng.random() < 0.1 else (v.lower() if rng.random() < 0.1 else v)
                      for v in messy["operator "]]
messy["operator "] = [(" " + v if rng.random() < 0.08 else v) for v in messy["operator "]]

label_map = {1: ["active", "Active", "1", "yes", "ACTIVE"], 0: ["inactive", "Inactive", "0", "no", "INACTIVE"]}
messy["Active?"] = [rng.choice(label_map[int(v)]) for v in messy["Active?"]]

# mixed date formats
fmt_choice = rng.choice(3, N, p=[0.5, 0.35, 0.15])
def fmt(d, c):
    return [d.strftime("%Y-%m-%d"), d.strftime("%d.%m.%Y"), d.strftime("%B %d, %Y")][c]
messy["Measurement Date"] = [fmt(d, c) for d, c in zip(df["date"], fmt_choice)]

# ---------------------------------------------------------------- duplicates & re-measurements
exact = messy.sample(int(0.04 * N), random_state=seed)
remeas = messy.sample(int(0.05 * N), random_state=seed + 1).copy()
for col in ["LogP", "tPSA [A^2]"]:
    vals = pd.to_numeric(remeas[col], errors="coerce")
    remeas[col] = (vals * rng.normal(1.0, 0.01, len(remeas))).round(2)
remeas["Notes"] = "repeat measurement"
messy = pd.concat([messy, exact, remeas], ignore_index=True).sample(frac=1, random_state=seed).reset_index(drop=True)

out = "compound_screening_raw.csv"
messy.to_csv(out, index=False)
print(f"wrote {out}: {messy.shape[0]} rows x {messy.shape[1]} columns (seed={seed})")
