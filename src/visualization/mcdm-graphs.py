import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def normalize_columns(df, method_cols):
    df_normalized = df.copy()
    for col in method_cols:
        min_val = df[col].min()
        max_val = df[col].max()
        if col == 'VIKOR_Score':
            df_normalized[col] = 1 - ((df[col] - min_val) / (max_val - min_val))
        else:
            df_normalized[col] = (df[col] - min_val) / (max_val - min_val)
    return df_normalized

def melt_for_plot(df, method_cols):
    return df.melt(
        id_vars=['District'],
        value_vars=method_cols,
        var_name='Method',
        value_name='Normalized_Score'
    )

# Load CSV
df = pd.read_csv('data/all-method-score.csv')

score_cols = ['TOPSIS_Score', 'MARCOS_Score', 'VIKOR_Score', 'WASPAS_Score']

df_normalized = normalize_columns(df, score_cols)
df_melted = melt_for_plot(df_normalized, score_cols)

# Line plot
plt.figure(figsize=(14, 6))
sns.lineplot(data=df_melted, x='District', y='Normalized_Score', hue='Method', marker='o')
plt.title("Comparison of MCDM Methods Across Districts", fontsize=16, weight='bold')
plt.xlabel("District", fontsize=14, weight='bold')
plt.ylabel("Normalized Score", fontsize=14, weight='bold')
plt.xticks(rotation=45, fontsize=14, weight='bold')
plt.yticks(fontsize=12, weight='bold')
plt.grid(True)
plt.legend(title='Method', title_fontsize=13, fontsize=12)
plt.tight_layout()
plt.savefig("mcdm_comparison_line.png", dpi=300)

# Bar plot
plt.figure(figsize=(14, 6))
sns.barplot(data=df_melted, x='District', y='Normalized_Score', hue='Method')
plt.title("MCDM Method Comparison (Grouped Bar Chart)", fontsize=16, weight='bold')
plt.xlabel("District", fontsize=14, weight='bold')
plt.ylabel("Normalized Score", fontsize=14, weight='bold')
plt.xticks(rotation=45, fontsize=12, weight='bold')
plt.yticks(fontsize=12, weight='bold')
plt.legend(title='Method', title_fontsize=13, fontsize=12)
plt.tight_layout()
plt.savefig("mcdm_comparison_bar.png", dpi=300)

# Heatmap
heatmap_data = df_normalized.set_index('District')[score_cols]
plt.figure(figsize=(10, 8))
sns.heatmap(heatmap_data, annot=True, cmap='YlGnBu', cbar_kws={'label': 'Normalized Score'})
plt.title("Heatmap of MCDM Method Scores", fontsize=16, weight='bold')
plt.xlabel("Method", fontsize=14, weight='bold')
plt.ylabel("District", fontsize=14, weight='bold')
plt.xticks(fontsize=12, weight='bold')
plt.yticks(fontsize=12, weight='bold')
plt.tight_layout()
plt.savefig("mcdm_comparison_heatmap.png", dpi=300)

# Radar chart
top_district = df_normalized.iloc[0] 
labels = score_cols
scores = [top_district[col] for col in labels]
angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
scores += scores[:1]
angles += angles[:1]

fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
ax.plot(angles, scores, 'o-', linewidth=2, label=top_district['District'])
ax.fill(angles, scores, alpha=0.25)
ax.set_thetagrids(np.degrees(angles[:-1]), labels, fontsize=12, weight='bold')
plt.title(f"Radar Chart for {top_district['District']}", fontsize=16, weight='bold')
plt.legend(fontsize=12)
plt.tight_layout()
plt.savefig("mcdm_comparison_radar.png", dpi=300)

# Box plot
plt.figure(figsize=(10, 6))
sns.boxplot(data=df_melted, x='Method', y='Normalized_Score')
plt.title("Distribution of Normalized Scores", fontsize=16, weight='bold')
plt.xlabel("Method", fontsize=14, weight='bold')
plt.ylabel("Normalized Score", fontsize=14, weight='bold')
plt.xticks(fontsize=12, weight='bold')
plt.yticks(fontsize=12, weight='bold')
plt.tight_layout()
plt.savefig("mcdm_comparison_boxplot.png", dpi=300)

# Rank calculation
ranks = df[score_cols].rank(ascending=False)
df['Average_Rank'] = ranks.mean(axis=1)
best_districts = df.loc[df['Average_Rank'] == df['Average_Rank'].min(), 'District']
print("Top performing district(s):", list(best_districts))
