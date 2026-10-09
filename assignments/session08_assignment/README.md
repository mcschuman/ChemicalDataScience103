# Assignment_Session 08: Exploratory Data Analysis
You have seen EDA in practice on the iris dataset. Now, your task is to write a python script doing the EDA tasks so that you could reuse this to a large extent for later explorations of different datasets. 

You will apply the script on another classic dataset, the wine dataset, and use the entire EDA process to gain some insights into the data.

In order to complete the assignment, all tasks stated below must be completed. Files to submit include the python script and a summary of your insights into the wine dataset.


## Goals

- Apply your EDA skills from the Iris dataset to a new dataset — the Wine dataset from scikit-learn.
- Write a Python script (wine_eda.py) that performs a complete exploratory data analysis (EDA). You can use the provided template `wine_eda.py` as a starting point.
- Make sure that the script has an organised structure and features clear comments. It should provide terminal output (`print`) for the summary statistics and save pictures of the plots.
- Summarise your gained insights into a separate file.


## Dataset

Use the built-in Wine dataset from sklearn.datasets by importing:
```python

from sklearn.datasets import load_wine

```

This dataset contains:

- 178 samples
- 13 numeric features describing chemical properties of wines
- 3 target classes (wine cultivars)

## Tasks
### 1. Load and inspect

- Load the dataset and convert it into a pandas DataFrame.
- Add a column named "target" for the wine class.
- Print the shape, column names, and first 10 rows.
- Show and print basic summary statistics.

### 2. Basic exploration

- Count how many samples belong to each class.
- Check for missing values and duplicates.

### 3. Visualisation

- Create and save the following plots (as PNG files):
- A pairplot of selected features (choose 4–5 interesting ones).
- A boxplot or violin plot comparing one feature across wine classes.
- A correlation heatmap: Compute the correlation matrix and display it as a heatmap (seaborn.heatmap).

Tip: Label plots clearly and use plt.savefig() instead of plt.show() to produce output files.

### 4. Scaling and PCA

- Standardise the numeric features (StandardScaler) and save them as a new DataFrame.
- Perform PCA to reduce dimensions to 2 components.
- Plot a 2D scatterplot of the two principal components, colored by target class.

### 5. Classification models

- Apply a linear regression model, a decision tree and a random forest to the wine data set. Don't forget to standardise the values (you can use the syntax from the demo notebooks).
- Investigate feature importance in the Decision Tree and Random Forest.
- Rerun the models using the PCs from the PCA as features and compare the model accuracy.

### 6. Interpretation & Discussion

- Interpret the EDA. Which patterns did you find, which anomalies, which correlations? What does the PCA tell you? Postulate some potential research questions and discuss potential hypotheses - use the results from your EDA as arguments.
- Report your findings in a separate text file (e.g. an `.md` file), which also needs to be submitted together with your script.



