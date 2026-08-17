"""
Customer Churn & Lifetime Value Analytics
Step 4: Visualizations

Author: Yashi Singh

Description:
Generates the business-facing visualizations for the README and Power BI
reference: churn rate by contract type, a customer segment scatter (CLV vs
satisfaction), a tenure-based retention curve, and a CLV-vs-churn-risk
priority matrix that identifies which customers to focus retention effort
on.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
OUT = "/home/claude/churn-clv-analytics/screenshots"

df = pd.read_csv("/home/claude/churn-clv-analytics/data/scored_customer_dataset.csv")

SEGMENT_COLORS = {
    "Champions": "#2ECC71",
    "Loyal Steady": "#3B82F6",
    "At Risk": "#F5B041",
    "Low Engagement": "#95A5A6",
}
TIER_COLORS = {"Low": "#2ECC71", "Medium": "#F5B041", "High": "#E67E22", "Very High": "#D7263D"}

# ---- 1. Churn rate by contract type ----
plt.figure(figsize=(7, 6))
churn_by_contract = df.groupby("Contract_Type")["Churn"].apply(lambda s: (s == "Yes").mean() * 100)
churn_by_contract = churn_by_contract.sort_values(ascending=False)
bars = plt.bar(churn_by_contract.index, churn_by_contract.values,
                color=["#D7263D", "#F5B041", "#2ECC71"])
for b in bars:
    plt.text(b.get_x() + b.get_width()/2, b.get_height() + 0.5,
              f"{b.get_height():.1f}%", ha="center", fontweight="bold")
plt.title("Churn Rate by Contract Type", fontsize=13, fontweight="bold")
plt.ylabel("Churn Rate (%)")
plt.tight_layout()
plt.savefig(f"{OUT}/01_churn_by_contract.png", dpi=150)
plt.close()

# ---- 2. Customer segment scatter: CLV vs Satisfaction, sized by tenure ----
plt.figure(figsize=(9, 7))
for seg, color in SEGMENT_COLORS.items():
    sub = df[df["Customer_Segment"] == seg]
    plt.scatter(sub["Satisfaction_Score"] + np.random.uniform(-0.15, 0.15, len(sub)),
                sub["Projected_CLV"], s=sub["Tenure_Months"] * 0.8,
                alpha=0.4, color=color, label=seg, edgecolors="none")
plt.title("Customer Segments: CLV vs Satisfaction (bubble size = tenure)", fontsize=13, fontweight="bold")
plt.xlabel("Satisfaction Score")
plt.ylabel("Projected CLV ($)")
plt.legend(title="Segment", loc="upper left", markerscale=0.5)
plt.tight_layout()
plt.savefig(f"{OUT}/02_segment_scatter.png", dpi=150)
plt.close()

# ---- 3. Retention curve: % retained by tenure month ----
plt.figure(figsize=(9, 6))
max_tenure = 72
retained_pct = []
months = range(0, max_tenure, 2)
for m in months:
    cohort = df[df["Tenure_Months"] >= m]
    still_active = cohort[cohort["Churn"] == "No"]
    retained_pct.append(len(still_active) / len(df) * 100 if len(df) else 0)
plt.plot(list(months), retained_pct, color="#3B82F6", linewidth=2.5, marker="o", markersize=3)
plt.fill_between(list(months), retained_pct, alpha=0.15, color="#3B82F6")
plt.title("Customer Retention Curve by Tenure", fontsize=13, fontweight="bold")
plt.xlabel("Tenure (Months)")
plt.ylabel("% of Total Customer Base Still Active")
plt.tight_layout()
plt.savefig(f"{OUT}/03_retention_curve.png", dpi=150)
plt.close()

# ---- 4. CLV vs Churn Risk priority matrix ----
plt.figure(figsize=(9, 7))
for tier, color in TIER_COLORS.items():
    sub = df[df["Churn_Risk_Tier"] == tier]
    plt.scatter(sub["Churn_Risk_Score"], sub["Projected_CLV"],
                alpha=0.35, s=18, color=color, label=tier, edgecolors="none")
clv_75 = df["Projected_CLV"].quantile(0.75)
plt.axhline(clv_75, color="black", linestyle="--", linewidth=1, alpha=0.6)
plt.axvline(80, color="black", linestyle="--", linewidth=1, alpha=0.6)
plt.text(82, df["Projected_CLV"].max() * 0.95, "PRIORITY\nSAVE ZONE",
          fontweight="bold", fontsize=10, color="#D7263D")
plt.title("Retention Priority Matrix: CLV vs Churn Risk", fontsize=13, fontweight="bold")
plt.xlabel("Churn Risk Score")
plt.ylabel("Projected CLV ($)")
plt.legend(title="Risk Tier", loc="upper left")
plt.tight_layout()
plt.savefig(f"{OUT}/04_priority_matrix.png", dpi=150)
plt.close()

# ---- 5. Support tickets vs satisfaction heatmap ----
plt.figure(figsize=(8, 6))
pivot = df.pivot_table(index="Num_Support_Tickets", columns="Satisfaction_Score",
                        values="Customer_ID", aggfunc="count", fill_value=0)
pivot = pivot[pivot.index <= 6]
sns.heatmap(pivot, cmap="rocket_r", annot=True, fmt="d", cbar_kws={"label": "Customer Count"})
plt.title("Support Tickets vs Satisfaction Score", fontsize=13, fontweight="bold")
plt.xlabel("Satisfaction Score")
plt.ylabel("Number of Support Tickets")
plt.tight_layout()
plt.savefig(f"{OUT}/05_tickets_vs_satisfaction.png", dpi=150)
plt.close()

print("Saved 5 visualizations to", OUT)
print("\nChurn rate by contract:\n", churn_by_contract.round(1))
