# Assignment_Session 14: RDKit exercise

In session 14, we had a look at a solubility dataset. You will use that (`delaney.csv`) and a dataset related to the last assignment (`ecoli_mics_sample.csv`). The datasets have roughly the same size, but the latter needs a bit of cleaning (remove entries that do not have a SMILES or a MIC defined).

This assignment is aimed at deepening your RDKit skills and your understanding of encoding molecular structures. You will produce some functions that you should be able to reuse on both datasets!

## Tasks

1) Load the data. Pay attention to relative paths.
2) Add a column with images of your sturctures to the dataframe (Hint: Use RdKit's `PandasTools`)
3) Create your own fingerprint system: Write a function that uses SMARTS in a substructure search to assess if a certain motif (e.g. aromatic ring, ketone, carbon chain longer than 3 C, double bonds, etc) is present which you believe is important. The resulting Boolean should be saved in a list (i.e. your custom fingerprint). Look for 5-10 motifs and append this list of binary values. In the end, your fingerprint should look something like this: `[0, 0, 1, 1, 1, 0, 1, 0, 1, 0]`, with each value representing a certain molecular functional group / motif.
4) Apply your function to the dataframe and store your fingerprints in a new column.
5) Create Morgan fingerprints as spearate feature (e.g. as column in your df).
6) Calculate all physical descriptors available in RDKit and add them to a new dataframe (hint: `Descriptors.CalcMolDescriptors` returns a dictionary of all available descriptors)
7) Use a Random Forest Regressor to predict the target to compare:
- your custom fingerprint,
- the Morgan fingerprints,
- the physical descriptors.
Which one would be the best feature set to predict your target? Note that for this task, the fingerprints should be represented as matrix, not one single entry like in the dataframe (snippet provided below). Interpret the results!
8) Repeat for the second dataset - focus on reusable code / functions, so that you can use them for both datasets. Compare the results for the two datasets and discuss!

```python
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import numpy as np

X = np.vstack(df["MorganFP"])  # for descriptors, you can simply use X = descr_df            
y = df["target"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)

rf = RandomForestRegressor(n_estimators=200, random_state=42)
rf.fit(X_train, y_train)

pred_train = rf.predict(X_train)
pred_test = rf.predict(X_test)

print("Train R2:", r2_score(y_train, pred_train))
print("Test  R2:", r2_score(y_test, pred_test))
print("Test RMSE:", mean_squared_error(y_test, pred_test) ** 0.5)
print("Test MAE:", mean_absolute_error(y_test, pred_test))```
