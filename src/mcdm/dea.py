import csv
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, value
from tabulate import tabulate

# Set building, cities(K), input_factors(I), output_factors(J)
cities = ["Bathinda", "Sangrur", "Patiala", "Nabha", "Fazilka", "Muktsar", "Maler Kotla", "Kot Kapura", "Dharmkot", "Ludhiana", "Machhiwara", "Firozpur", "Ropar", "Anandpur Sahib", "Jalandhar", "Amritsar", "Garshankar", "Kapurthala", "Kartarpur", "Tarn Taran Sahib", "Hoshiarpur", "Jandiala Guru", "Urmar Tanda", "Majitha", "Batala", "Dasuya", "Gurdaspur", "Dera Baba Nanak", "Dinanagar", "Pathankot"]  # DMUs
input_factors = ["air_temp_avg(X1)", "precipitation_avg(X2)", "humidity_avg(X3)", "surface_pressure_avg(X4)", "wind_speed_avg(X5)"] # Input factors
output_factors = ["Elevation(Y1)", 	"global_horizontal_irradiance(Y2)",	"direct_normal_irradiance(Y3)"] # Output factors

print("Cities Count:", len(cities))

# Initialize X and Y dictionaries
X = {i: {k: 0 for k in cities} for i in input_factors}  # Inputs
Y = {j: {k: 0 for k in cities} for j in output_factors}  # Outputs

# Import CSV data
with open('data/sample.csv', newline='') as csvfile:
    rows = csv.DictReader(csvfile)
    k = 0
    for row in rows:
        for i in input_factors:
            X[i][cities[k]] = float(row[i])  # Read inputs
        for j in output_factors:
            Y[j][cities[k]] = float(row[j])  # Read outputs
        k += 1

# CRS_DEA_Model
def getOverallEfficiency(r):
    # Model Building
    model = LpProblem('CRS_model', LpMinimize)

    # Decision variables Building
    theta_r = LpVariable(f'theta_r')
    lambda_k = LpVariable.dicts(f'lambda_k', cities, lowBound=0)  # Lambda variables for all DMUs

    # Objective Function setting
    model += theta_r

    # Constraints setting
    for i in input_factors:
        model += lpSum([lambda_k[k] * X[i][k] for k in cities]) <= theta_r * float(X[i][cities[r]])
    for j in output_factors:
        model += lpSum([lambda_k[k] * Y[j][k] for k in cities]) >= float(Y[j][cities[r]])

    # Model solving
    model.solve()

    return round(value(model.objective), 3)  # Return the efficiency score

# VRS_DEA_Model for Technical Efficiency
def getTechnicalEfficiency(r):
    # Model Building
    model = LpProblem('VRS_model', LpMinimize)

    # Decision variables Building
    theta_r = LpVariable(f'theta_r')
    lambda_k = LpVariable.dicts(f'lambda_k', cities, lowBound=0)  # Lambda variables for all DMUs

    # Objective Function setting
    model += theta_r

    # Constraints setting
    for i in input_factors:
        model += lpSum([lambda_k[k] * X[i][k] for k in cities]) <= theta_r * float(X[i][cities[r]])
    for j in output_factors:
        model += lpSum([lambda_k[k] * Y[j][k] for k in cities]) >= float(Y[j][cities[r]])
    model += lpSum([lambda_k[k] for k in cities]) == 1  # VRS constraint

    # Model solving
    model.solve()

    return round(value(model.objective), 3)  # Return the efficiency score

# Calculate and display efficiencies
results = []
for r in range(len(cities)):
    overall_efficiency = getOverallEfficiency(r)  # CRS Efficiency
    technical_efficiency = getTechnicalEfficiency(r)  # VRS Efficiency
    results.append({
    "DMU": cities[r],
    "Overall Efficiency (CRS)": overall_efficiency,
    "Technical Efficiency (VRS)": technical_efficiency,
    "Scale Efficiency (SE)": round(overall_efficiency / technical_efficiency, 3) if technical_efficiency != 0 else None
})

# Print results in tabular format
print(tabulate(results, headers="keys", tablefmt="pretty"))

# Define the output CSV file path
output_file = "data/efficiencies.csv"

# Define the fieldnames for the CSV (keys of the dictionaries in results + the highlight column)
fieldnames = ["DMU", "Overall Efficiency (CRS)", "Technical Efficiency (VRS)", "Scale Efficiency (SE)", "Fully Efficient"]

# Add the "Fully Efficient" status to each row
for result in results:
    result["Fully Efficient"] = "Yes" if (result["Overall Efficiency (CRS)"] == 1.0 and 
                                          result["Technical Efficiency (VRS)"] == 1.0 and 
                                          result["Scale Efficiency (SE)"] == 1.0) else "No"

# Write the results to a CSV file
with open(output_file, mode='w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    # Write the header row
    writer.writeheader()
    
    # Write the data rows
    writer.writerows(results)

print(f"Efficiency results with highlights saved to '{output_file}'")
