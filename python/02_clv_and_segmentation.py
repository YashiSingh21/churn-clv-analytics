"""
Customer Churn & Lifetime Value Analytics
Step 2: CLV Calculation & Customer Segmentation

Author: Yashi Singh

Description:
Calculates a projected Customer Lifetime Value (CLV) per customer, then
segments the customer base into behavioral clusters using KMeans on
tenure, spend, usage, and satisfaction. Clusters are labeled into
business-readable segment names (e.g. "Champions", "At Risk High Value")
based on their cluster-center profile.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

df = pd.read_csv("/home/claude/churn-clv-analytics/data/subscription_customer_dataset.csv")

# ---- CLV: simple projected-lifetime model ----
# Expected remaining lifetime (months) approximated from observed tenure
# distribution by contract type, then CLV = monthly charges x expected
# total lifetime months (historical + projected remaining).
avg_lifetime_by_contract = {
    "Month-to-Month": 18,
    "One Year": 34,
    "Two Year": 52,
}
df["Expected_Lifetime_Months"] = df["Contract_Type"].map(avg_lifetime_by_contract)
df["Projected_CLV"] = (df["Monthly_Charges"] * df["Expected_Lifetime_Months"]).round(2)

# ---- Segmentation ----
features = ["Tenure_Months", "Monthly_Charges", "Avg_Monthly_Usage_GB", "Satisfaction_Score"]
X = df[features].copy()
X_scaled = StandardScaler().fit_transform(X)

kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
df["Cluster"] = kmeans.fit_predict(X_scaled)

# Profile each cluster to assign a business-readable label
profile = df.groupby("Cluster")[features + ["Projected_CLV"]].mean()
print("Cluster profiles:\n", profile.round(1))

# Rank clusters by CLV and satisfaction to assign labels dynamically
profile_sorted = profile.sort_values("Projected_CLV", ascending=False)
labels_by_rank = ["Champions", "Loyal Steady", "At Risk", "Low Engagement"]
cluster_to_label = {}
for rank, cluster_id in enumerate(profile_sorted.index):
    sat = profile.loc[cluster_id, "Satisfaction_Score"]
    clv = profile.loc[cluster_id, "Projected_CLV"]
    if clv == profile["Projected_CLV"].max():
        cluster_to_label[cluster_id] = "Champions"
    elif sat == profile["Satisfaction_Score"].min():
        cluster_to_label[cluster_id] = "At Risk"
    elif clv == profile["Projected_CLV"].min():
        cluster_to_label[cluster_id] = "Low Engagement"
    else:
        cluster_to_label[cluster_id] = "Loyal Steady"

df["Customer_Segment"] = df["Cluster"].map(cluster_to_label)

df.to_csv("/home/claude/churn-clv-analytics/data/segmented_customer_dataset.csv", index=False)

print("\nSegment distribution:")
print(df["Customer_Segment"].value_counts())
print("\nAvg CLV by segment:")
print(df.groupby("Customer_Segment")["Projected_CLV"].mean().round(0).sort_values(ascending=False))
