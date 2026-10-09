"""
wine_eda.py
-----------
Homework: Exploratory Data Analysis on the Wine dataset.

Goals:
1. Load and inspect the data
2. Perform exploratory analysis
3. Produce some plots for visualisations
4. Apply PCA
5. Apply some simple ML models for classification
6. Summarise results
"""

# Imports
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.datasets import load_wine
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA



# Main analysis function
def main():
    # --- 1. Load data ---
    print("Loading dataset...")
    wine = load_wine()
    df = pd.DataFrame(wine.data, columns=wine.feature_names)
    # add a 'target' column


    # print basic info (shape, first rows, summary statistics)

    # --- 2. Basic exploration ---
    # print class distribution and check for missing values as well as duplicates

    
    # --- 3. Visualisations ---
    # create and save a pairplot using a few selected features
    # create and save a boxplot comparing one feature across classes
    # plot and save a heatmap (e.g. 'heatmap.png')
    

    # --- 4. Scaling and PCA ---
    # separate features (X) and target (y)
    # scale the features using StandardScaler
    # apply PCA (2 components)
    # create a DataFrame with PCA results and target
    # plot and save a scatterplot of the first two components (color by target)

    # --- 5. Classification models ---
    # Do a random train-test split (20%) 
    # Scale training and test features (fit_transform() on X_train, transform() on X_test)
    # Train logistic regression, a decision tree and a random forest (default hyperparameters)
    # Compare the label prediction accuracy of the different models.
    # Train and evaluate the three models on the PCA data.

# Entry point
if __name__ == "__main__":
    main()