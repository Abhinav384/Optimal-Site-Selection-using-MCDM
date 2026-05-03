import numpy as np
import pandas as pd
from pyDecision.algorithm.ahp import ahp_method
from pyDecision.algorithm.topsis import topsis_method

# Step 1: Load your CSV data
df = pd.read_csv('data/First_Evaluation.csv')

# Step 2: Preprocessing

# First, group by 'Latitude', 'Longitude', 'Districts' and take MEAN over 31 days
grouped = df.groupby(['Latitude', 'Longitude', 'Districts']
                     ).mean(numeric_only=True).reset_index()

# print("Groupeed Data 1: ", grouped)

# Select only necessary columns for criteria
# (Adjust here if you want to remove or add some factors)
criteria_columns = ['DHI', 'DNI', 'GHI', 'RELATIVE_HUMIDITY',
                    'WIND_SPEED_10m', 'NDVI']

# Decision matrix
grouped = grouped.dropna(subset=criteria_columns)
print("Groupeed Data 2: ", grouped)

decision_matrix = grouped[criteria_columns].values
# print("Decision Matrix: ", decision_matrix)

# print("Any NaNs in decision matrix?", np.isnan(decision_matrix).any())
# print("Refined Decision matrix:\n", decision_matrix)

# Save coordinates and districts separately for final output
coordinates = grouped[['Latitude', 'Longitude']]
districts = grouped['Districts']

# print("Filtered Coordinates:\n", coordinates)
# print("Filtered Districts:\n", districts)

# -----------------
# Step 3: AHP - Subjective Weights

# Define your pairwise comparison matrix (number of criteria x number of criteria)
pairwise_matrix = np.array([
    [1,    2,    2,    4,    3,    5],
    [0.5,  1,    2,    3,    3,    5],
    [0.5,  0.5,  1,    2,    3,    4],
    [0.25, 0.333, 0.5, 1,    2,    3],
    [0.333, 0.333, 0.333, 0.5, 1,    3],
    [0.2,  0.2,  0.25, 0.333, 0.333, 1]
])

# Calculate AHP subjective weights
subjective_weights, CR = ahp_method(pairwise_matrix)
print("\nSubjective AHP Weights:", subjective_weights)
# print("Consistency Ratio (CR):", CR) # Should be less than or equal to 0.10

# -----------------
# Step 4: Entropy - Objective Weights
# Normalize decision matrix
norm_matrix = decision_matrix / decision_matrix.sum(axis=0)

print("Normalized matrix: ", norm_matrix)

eps = 1e-12  # to prevent log(0)

# Entropy calculation
k = 1 / np.log(len(norm_matrix))
print("Value of k: ", k)

pij = norm_matrix
entropy = -k * np.sum(pij * np.log(pij + eps), axis=0)

print("Entropy: ", entropy)

# Degree of diversification
d = 1 - entropy

print("Diversification: ", d)

# Objective weights
objective_weights = d / d.sum()
print("\nObjective Entropy Weights:", objective_weights)

# -----------------
# Step 5: Hybrid Weights (Simple Average)

hybrid_weights = (subjective_weights + objective_weights) / 2
print("\nHybrid Weights:", hybrid_weights)

# -----------------
# Step 6: Apply TOPSIS using Hybrid Weights

# Assume all criteria are beneficial (i.e., 'max')
criteria_type = ['max', 'max', 'max', 'min', 'min', 'min']
print("Criteria type: ", criteria_type)

# Apply TOPSIS
topsis_scores = topsis_method(
    decision_matrix, hybrid_weights, criteria_type, graph = False, verbose = True)

print("Topsis Score: ", topsis_scores)

# -----------------
# Step 7: Final Output - Coordinates + Districts + Scores

final_ranking = pd.DataFrame({
    'Latitude': coordinates['Latitude'],
    'Longitude': coordinates['Longitude'],
    'District': districts,
    'TOPSIS_Score': topsis_scores,
})

# Sort by Rank
print("Final Ranking: ", final_ranking)
final_ranking = final_ranking.sort_values('TOPSIS_Score', ascending=False)

# Save to CSV if needed
final_ranking.to_csv('final_coordinate_ranking.csv', index=False)

print("\nFinal Ranking (Top 10 shown):")
print(final_ranking.head(10))
