import pandas as pd
import numpy as np
from functools import reduce
import matplotlib.pyplot as plt
from pyDecision.algorithm.waspas import waspas_method
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, value
from tabulate import tabulate

# DEA Functions
def getOverallEfficiency(r):
    model = LpProblem('CRS_model', LpMinimize)
    theta_r = LpVariable(f'theta_r')
    lambda_k = LpVariable.dicts(f'lambda_k', coordinates, lowBound=0)
    model += theta_r
    for i in input_factors:
        model += lpSum([lambda_k[k] * X[i][k] for k in coordinates]) <= theta_r * X[i][coordinates[r]]
    for j in output_factors:
        model += lpSum([lambda_k[k] * Y[j][k] for k in coordinates]) >= Y[j][coordinates[r]]
    model.solve()
    return round(value(model.objective), 3)

def getTechnicalEfficiency(r):
    model = LpProblem('VRS_model', LpMinimize)
    theta_r = LpVariable(f'theta_r')
    lambda_k = LpVariable.dicts(f'lambda_k', coordinates, lowBound=0)
    model += theta_r
    for i in input_factors:
        model += lpSum([lambda_k[k] * X[i][k] for k in coordinates]) <= theta_r * X[i][coordinates[r]]
    for j in output_factors:
        model += lpSum([lambda_k[k] * Y[j][k] for k in coordinates]) >= Y[j][coordinates[r]]
    model += lpSum([lambda_k[k] for k in coordinates]) == 1
    model.solve()
    return round(value(model.objective), 3)

def ahp_method(dataset, wd = 'm'):
    inc_rat  = np.array([0, 0, 0, 0.58, 0.9, 1.12, 1.24, 1.32, 1.41, 1.45, 1.49, 1.51, 1.48, 1.56, 1.57, 1.59])
    X        = np.copy(dataset)
    weights  = np.zeros(X.shape[1])
    if (wd == 'm' or wd == 'mean'):
        weights  = np.mean(X/np.sum(X, axis = 0), axis = 1)
        vector   = np.sum(X*weights, axis = 1)/weights
        lamb_max = np.mean(vector)
    elif (wd == 'g' or wd == 'geometric'):
        for i in range (0, X.shape[1]):
            weights[i] = reduce( (lambda x, y: x * y), X[i,:])**(1/X.shape[1])
        weights  = weights/np.sum(weights)   
        vector   = np.sum(X*weights, axis = 1)/weights
        lamb_max = np.mean(vector)
    elif (wd == 'me' or wd == 'max_eigen'):
        eigenvalues, eigenvectors = np.linalg.eig(X)
        eigenvalues_real          = np.real(eigenvalues)
        lamb_max_index            = np.argmax(eigenvalues_real)
        lamb_max                  = eigenvalues_real[lamb_max_index]
        principal_eigenvector     = np.real(eigenvectors[:, lamb_max_index])
        weights                   = principal_eigenvector / principal_eigenvector.sum()
    cons_ind = (lamb_max - X.shape[1])/(X.shape[1] - 1)
    rc       = cons_ind/inc_rat[X.shape[1]]
    return weights, rc

# Function: Rank 
def ranking_m(flow_1, flow_2, flow_3):    
    rank_xy = np.zeros((flow_1.shape[0] + 1, 6)) 
    for i in range(0, rank_xy.shape[0]):
        rank_xy[i, 0] = -1
        rank_xy[i, 1] = flow_1.shape[0]-i+1     
        rank_xy[i, 2] = 0
        rank_xy[i, 3] = flow_2.shape[0]-i+1  
        rank_xy[i, 4] = 1
        rank_xy[i, 5] = flow_3.shape[0]-i+1    
    plt.text(rank_xy[0, 0],  rank_xy[0, 1], 'WSM', size = 12, ha = 'center', va = 'center', color = 'white', bbox = dict(boxstyle = 'round', ec = (0.0, 0.0, 0.0), fc = (0, 0, 0),))
    plt.text(rank_xy[0, 2],  rank_xy[0, 3], 'WPM', size = 12, ha = 'center', va = 'center', color = 'white', bbox = dict(boxstyle = 'round', ec = (0.0, 0.0, 0.0), fc = (0, 0, 0),))
    plt.text(rank_xy[0, 4],  rank_xy[0, 5], 'WASPAS', size = 12, ha = 'center', va = 'center', color = 'white', bbox = dict(boxstyle = 'round', ec = (0.0, 0.0, 0.0), fc = (0, 0, 0),))
    for i in range(1, rank_xy.shape[0]):
        plt.text(rank_xy[i, 0],  rank_xy[i, 1], 'a' + str(int(flow_1[i-1,0])), size = 12, ha = 'center', va = 'center', bbox = dict(boxstyle = "round", ec = (0.0, 0.0, 0.0), fc = (0.8, 1.0, 0.8),))
        plt.text(rank_xy[i, 2],  rank_xy[i, 3], 'a' + str(int(flow_2[i-1,0])), size = 12, ha = 'center', va = 'center', bbox = dict(boxstyle = 'round', ec = (0.0, 0.0, 0.0), fc = (0.8, 1.0, 0.8),))
        plt.text(rank_xy[i, 4],  rank_xy[i, 5], 'a' + str(int(flow_3[i-1,0])), size = 12, ha = 'center', va = 'center', bbox = dict(boxstyle = 'round', ec = (0.0, 0.0, 0.0), fc = (0.8, 1.0, 0.8),)) 
    for i in range(1, rank_xy.shape[0]-1):
        plt.arrow(rank_xy[i, 0], rank_xy[i, 1], rank_xy[i+1, 0] - rank_xy[i, 0], rank_xy[i+1, 1] - rank_xy[i, 1], head_width = 0.01, head_length = 0.2, overhang = 0.0, color = 'black', linewidth = 0.9, length_includes_head = True)
        plt.arrow(rank_xy[i, 2], rank_xy[i, 3], rank_xy[i+1, 2] - rank_xy[i, 2], rank_xy[i+1, 3] - rank_xy[i, 3], head_width = 0.01, head_length = 0.2, overhang = 0.0, color = 'black', linewidth = 0.9, length_includes_head = True)
        plt.arrow(rank_xy[i, 4], rank_xy[i, 5], rank_xy[i+1, 4] - rank_xy[i, 4], rank_xy[i+1, 5] - rank_xy[i, 5], head_width = 0.01, head_length = 0.2, overhang = 0.0, color = 'black', linewidth = 0.9, length_includes_head = True)
    axes = plt.gca()
    axes.set_xlim([-2, +2])
    ymin = np.amin(rank_xy[:,1])
    ymax = np.amax(rank_xy[:,1])
    if (ymin < ymax):
        axes.set_ylim([ymin, ymax])
    else:
        axes.set_ylim([ymin-1, ymax+1])
    plt.axis('off')
    plt.show() 
    return

# Function: WASPAS
def waspas_method(dataset, criterion_type, weights, lambda_value = 0.5, graph = True):
    x = np.zeros((dataset.shape[0], dataset.shape[1]), dtype = float)
    for j in range(0, dataset.shape[1]):
        if (criterion_type[j] == 'max'):
            x[:,j] = 1 + ( dataset[:,j] - np.min(dataset[:,j]) ) / ( np.max(dataset[:,j]) - np.min(dataset[:,j]) )
        else:
            x[:,j] = 1 + ( np.max(dataset[:,j]) - dataset[:,j] ) / ( np.max(dataset[:,j]) - np.min(dataset[:,j]) )
    wsm    = np.sum(x*weights, axis = 1)
    wpm    = np.prod(x**weights, axis = 1)
    waspas = (lambda_value)*wsm + (1 - lambda_value)*wpm
    if (graph == True):
        flow_1 = np.copy(wsm)
        flow_1 = np.reshape(flow_1, (wsm.shape[0], 1))
        flow_1 = np.insert(flow_1, 0, list(range(1, wsm.shape[0]+1)), axis = 1)
        flow_2 = np.copy(wpm)
        flow_2 = np.reshape(flow_2, (wpm.shape[0], 1))
        flow_2 = np.insert(flow_2, 0, list(range(1, wpm.shape[0]+1)), axis = 1)
        flow_3 = np.copy(waspas)
        flow_3 = np.reshape(flow_3, (waspas.shape[0], 1))
        flow_3 = np.insert(flow_3, 0, list(range(1, waspas.shape[0]+1)), axis = 1)
        ranking_m(flow_1[np.argsort(flow_1[:, 1])[::-1]], flow_2[np.argsort(flow_2[:, 1])[::-1]], flow_3[np.argsort(flow_3[:, 1])[::-1]])
    return wsm, wpm, waspas


# --- DEA PHASE ---
input_factors = ['RELATIVE_HUMIDITY', 'WIND_SPEED_10m', 'NDVI', 'LST']
output_factors = ['DHI', 'DNI', 'GHI']

# Load data
dea_df = pd.read_csv('data/First-sample.csv')

# Get district per coordinate (most common district if multiple)
district_lookup = (
    dea_df.groupby(['Latitude', 'Longitude'])['Districts']
    .agg(lambda x: x.mode().iloc[0])  # get most frequent district
    .reset_index()
)

# Average 31-day data per coordinate
grouped = dea_df.groupby(['Latitude', 'Longitude'], as_index=False).mean(numeric_only=True)

# Add district info to the grouped data
grouped = pd.merge(grouped, district_lookup, on=['Latitude', 'Longitude'])

# Coordinates list
coordinates = list(zip(grouped['Latitude'], grouped['Longitude']))

# DEA input/output mappings
X = {i: dict(zip(coordinates, grouped[i])) for i in input_factors}
Y = {j: dict(zip(coordinates, grouped[j])) for j in output_factors}

# Run DEA
results = []
for r in range(len(coordinates)):
    CRS = getOverallEfficiency(r)
    VRS = getTechnicalEfficiency(r)
    SE = round(CRS / VRS, 3) if VRS != 0 else None
    results.append({
        "Latitude": coordinates[r][0],
        "Longitude": coordinates[r][1],
        "CRS": CRS,
        "VRS": VRS,
        "SE": SE,
        "Fully Efficient": "Yes" if CRS == 1.0 and VRS == 1.0 and SE == 1.0 else "No"
    })

results_df = pd.DataFrame(results)

# Merge district info into results
results_df = pd.merge(results_df, district_lookup, on=['Latitude', 'Longitude'])

# Save efficiency results
results_df.to_csv('data/efficiencies.csv', index=False)
print(tabulate(results_df, headers="keys", tablefmt="pretty"))

# --- AHP-TOPSIS PHASE (Filtered) ---
# Merge with grouped to get full data for efficient coordinates
filtered_group = pd.merge(grouped, results_df[["Latitude", "Longitude", "Fully Efficient"]],
                          on=["Latitude", "Longitude"])
filtered_group = filtered_group[filtered_group["Fully Efficient"] == "Yes"]

# AHP-TOPSIS on filtered coordinates
criteria_columns = ['DHI', 'DNI', 'GHI', 'RELATIVE_HUMIDITY', 'WIND_SPEED_10m', 'NDVI', 'LST']
decision_matrix = filtered_group[criteria_columns].values
coordinates = filtered_group[['Latitude', 'Longitude']]
districts = filtered_group['Districts']

# AHP pairwise comparison matrix
pairwise_matrix = np.array([
    [1,    1,    0.5,  4,    3,    5,    4], #DHI   
    [1,    1,    0.5,  3,    3,    5,    3], #DNI  
    [2,    2,    1,    4,    4,    5,    4], #GHI  
    [0.25, 0.333, 0.25, 1,   2,    3,    1], #Relative Humidity
    [0.333,0.333, 0.25, 0.5, 1,    3,    1], #Wind Speed
    [0.2,  0.2,   0.2,  0.333, 0.333, 1, 0.5], #Vegetation
    [0.25, 0.333, 0.25, 1,    1,    2, 1] #Land Surface Temperature
])


subjective_weights, CR = ahp_method(pairwise_matrix)
criteria_type = ['max', 'max', 'max', 'min', 'min', 'min', 'min']

# Save AHP weights and CR to CSV
ahp_results_df = pd.DataFrame({
    'Criteria': criteria_columns,
    'AHP_Weight': subjective_weights
})

# Append CR as a separate row
ahp_results_df.loc[len(ahp_results_df.index)] = ['Consistency Ratio (CR)', CR]

# Save to CSV
ahp_results_df.to_csv('data/ahp_weights_cr.csv', index=False)

wsm, wpm, waspas = waspas_method(
    decision_matrix, criteria_type, subjective_weights, lambda_value = 0.5, graph = False
)

# Final ranking with coordinates and districts
final_ranking = pd.DataFrame({
    'Latitude': coordinates['Latitude'],
    'Longitude': coordinates['Longitude'],
    'District': districts,
    'WASPAS_Score': waspas,
}).sort_values('WASPAS_Score', ascending=False)

final_ranking.to_csv('data/efficient_waspas_ranking.csv', index=False)

print("\nFinal Ranking of Fully Efficient Coordinates:")
print(final_ranking.head(10))
