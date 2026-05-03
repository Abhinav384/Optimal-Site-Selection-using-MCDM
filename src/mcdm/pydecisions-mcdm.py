import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from functools import reduce

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

def ranking(flow):    
    rank_xy = np.zeros((flow.shape[0], 2))
    for i in range(0, rank_xy.shape[0]):
        rank_xy[i, 0] = 0
        rank_xy[i, 1] = flow.shape[0]-i           
    for i in range(0, rank_xy.shape[0]):
        plt.text(rank_xy[i, 0],  rank_xy[i, 1], 'a' + str(int(flow[i,0])), size = 12, ha = 'center', va = 'center', bbox = dict(boxstyle = 'round', ec = (0.0, 0.0, 0.0), fc = (0.8, 1.0, 0.8),))
    for i in range(0, rank_xy.shape[0]-1):
        plt.arrow(rank_xy[i, 0], rank_xy[i, 1], rank_xy[i+1, 0] - rank_xy[i, 0], rank_xy[i+1, 1] - rank_xy[i, 1], head_width = 0.01, head_length = 0.2, overhang = 0.0, color = 'black', linewidth = 0.9, length_includes_head = True)
    axes = plt.gca()
    axes.set_xlim([-1, +1])
    ymin = np.amin(rank_xy[:,1])
    ymax = np.amax(rank_xy[:,1])
    if (ymin < ymax):
        axes.set_ylim([ymin, ymax])
    else:
        axes.set_ylim([ymin-1, ymax+1])
    plt.axis('off')
    plt.show() 
    return

def topsis_method(dataset, weights, criterion_type, graph = True, verbose = True):
    X = np.copy(dataset)
    w = np.copy(weights)
    sum_cols = np.sum(X*X, axis = 0)
    sum_cols = sum_cols**(1/2)
    r_ij = X/sum_cols
    v_ij = r_ij*w
    p_ideal_A = np.zeros(X.shape[1])
    n_ideal_A = np.zeros(X.shape[1])
    for i in range(0, dataset.shape[1]):
        if (criterion_type[i] == 'max'):
            p_ideal_A[i] = np.max(v_ij[:, i])
            n_ideal_A[i] = np.min(v_ij[:, i])
        else:
            p_ideal_A[i] = np.min(v_ij[:, i])
            n_ideal_A[i] = np.max(v_ij[:, i]) 
    p_s_ij = (v_ij - p_ideal_A)**2
    p_s_ij = np.sum(p_s_ij, axis = 1)**(1/2)
    n_s_ij = (v_ij - n_ideal_A)**2
    n_s_ij = np.sum(n_s_ij, axis = 1)**(1/2)
    c_i    = n_s_ij / ( p_s_ij  + n_s_ij )
    if (verbose == True):
        for i in range(0, c_i.shape[0]):
            print('a' + str(i+1) + ': ' + str(round(c_i[i], 2)))
    if ( graph == True):
        flow = np.copy(c_i)
        flow = np.reshape(flow, (c_i.shape[0], 1))
        flow = np.insert(flow, 0, list(range(1, c_i.shape[0]+1)), axis = 1)
        flow = flow[np.argsort(flow[:, 1])]
        flow = flow[::-1]
        ranking(flow)
    return c_i


# Input the sample data in CSV format
df = pd.read_csv('data/First-sample.csv')

# First, group by 'Latitude', 'Longitude', 'Districts' and take mean over 31 days
grouped = df.groupby(['Latitude', 'Longitude', 'Districts']
                     ).mean(numeric_only=True).reset_index()

# Select only necessary columns for criteria
criteria_columns = ['DHI', 'DNI', 'GHI', 'RELATIVE_HUMIDITY',
                    'WIND_SPEED_10m', 'NDVI', 'LST']

# Decision matrix
grouped = grouped.dropna(subset=criteria_columns)
decision_matrix = grouped[criteria_columns].values

# Save coordinates and districts separately for final output
coordinates = grouped[['Latitude', 'Longitude']]
districts = grouped['Districts']

# Define your pairwise comparison matrix (number of criteria x number of criteria)

pairwise_matrix = np.array([
    [1,    2,    2,    4,    3,    5,    4],    
    [0.5,  1,    2,    3,    3,    5,    3],    
    [0.5,  0.5,  1,    2,    3,    4,    3],    
    [0.25, 0.333, 0.5, 1,    2,    3,    1],    
    [0.333, 0.333, 0.333, 0.5, 1,    3,   1],  
    [0.2,  0.2,  0.25, 0.333, 0.333, 1,   0.5],
    [0.25, 0.333, 0.333, 1,    1,    2,   1]   
])

# Calculate AHP subjective weights
subjective_weights, CR = ahp_method(pairwise_matrix)

print("\nSubjective AHP Weights:", subjective_weights)

# Divide the criteria 
criteria_type = ['max', 'max', 'max', 'min', 'min', 'min', 'min']

# Apply TOPSIS
topsis_scores = topsis_method(
    decision_matrix, subjective_weights, criteria_type, graph = False, verbose = False)

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
final_ranking.to_csv('first-sample-rank.csv', index=False)

print("\nFinal Ranking (Top 10 shown):")
print(final_ranking.head(10))
