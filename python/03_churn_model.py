"""
Customer Churn & Lifetime Value Analytics
Step 3: Churn Prediction Model

Author: Yashi Singh

Description:
Trains a Random Forest and Logistic Regression to predict churn from
customer behavior and contract attributes. Selects the better model by
ROC-AUC, scores every customer with a Churn_Risk_Score (0-100), and
combines that with Projected_CLV to flag high-value, high-risk customers
that a retention team should prioritize.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, roc_curve, classification_report

df = pd.read_csv("/home/claude/churn-clv-analytics/data/segmented_customer_dataset.csv")
OUT = "/home/claude/churn-clv-analytics/screenshots"

y = (df["Churn"] == "Yes").astype(int)
numeric_features = [
    "Tenure_Months", "Monthly_Charges", "Avg_Monthly_Usage_GB",
    "Num_Support_Tickets", "Satisfaction_Score", "Num_Addon_Services",
    "Autopay_Enrolled",
]
categorical_features = ["Contract_Type", "Service_Tier", "Payment_Method"]
feature_cols = numeric_features + categorical_features
X = df[feature_cols]

preprocess = ColumnTransformer([
    ("num", StandardScaler(), numeric_features),
    ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
])

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

logreg = Pipeline([("prep", preprocess), ("clf", LogisticRegression(max_iter=1000))])
logreg.fit(X_train, y_train)
logreg_probs = logreg.predict_proba(X_test)[:, 1]
logreg_auc = roc_auc_score(y_test, logreg_probs)

rf = Pipeline([("prep", preprocess), ("clf", RandomForestClassifier(
    n_estimators=300, max_depth=8, min_samples_leaf=15, random_state=42
))])
rf.fit(X_train, y_train)
rf_probs = rf.predict_proba(X_test)[:, 1]
rf_auc = roc_auc_score(y_test, rf_probs)

print(f"Logistic Regression ROC-AUC: {logreg_auc:.3f}")
print(f"Random Forest ROC-AUC:       {rf_auc:.3f}")

best_model, best_probs, best_name = (
    (rf, rf_probs, "Random Forest") if rf_auc >= logreg_auc
    else (logreg, logreg_probs, "Logistic Regression")
)
print(f"\nSelected model: {best_name}")
print(classification_report(y_test, (best_probs >= 0.5).astype(int), target_names=["Retained", "Churned"]))

# ---- ROC curve ----
plt.figure(figsize=(7, 6))
for name, probs in [("Logistic Regression", logreg_probs), ("Random Forest", rf_probs)]:
    fpr, tpr, _ = roc_curve(y_test, probs)
    auc = roc_auc_score(y_test, probs)
    plt.plot(fpr, tpr, label=f"{name} (AUC = {auc:.3f})", linewidth=2)
plt.plot([0, 1], [0, 1], "k--", linewidth=0.8)
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curve — Churn Prediction Models")
plt.legend()
plt.tight_layout()
plt.savefig(f"{OUT}/06_roc_curve.png", dpi=150)
plt.close()

# ---- Feature importance ----
ohe_cols = rf.named_steps["prep"].named_transformers_["cat"].get_feature_names_out(categorical_features)
all_names = numeric_features + list(ohe_cols)
imp = pd.DataFrame({
    "feature": all_names,
    "importance": rf.named_steps["clf"].feature_importances_
}).sort_values("importance", ascending=False).head(10)

plt.figure(figsize=(8, 6))
plt.barh(imp["feature"][::-1], imp["importance"][::-1], color="#5B4B8A")
plt.title("Top Churn Drivers (Random Forest Feature Importance)")
plt.xlabel("Relative Importance")
plt.tight_layout()
plt.savefig(f"{OUT}/07_feature_importance.png", dpi=150)
plt.close()

# ---- Score full dataset ----
full_probs = best_model.predict_proba(X)[:, 1]
df["Churn_Risk_Score"] = (full_probs * 100).round(1)

q50, q80, q95 = np.quantile(full_probs, [0.50, 0.80, 0.95])
def tier(p):
    if p >= q95: return "Very High"
    if p >= q80: return "High"
    if p >= q50: return "Medium"
    return "Low"
df["Churn_Risk_Tier"] = pd.Series(full_probs, index=df.index).apply(tier)

# Priority flag: high CLV AND high churn risk = save this customer first
clv_75th = df["Projected_CLV"].quantile(0.75)
df["Retention_Priority"] = np.where(
    (df["Projected_CLV"] >= clv_75th) & (df["Churn_Risk_Tier"].isin(["High", "Very High"])),
    "Priority Save", "Standard"
)

df.to_csv("/home/claude/churn-clv-analytics/data/scored_customer_dataset.csv", index=False)

print(f"\nPriority Save customers: {(df['Retention_Priority'] == 'Priority Save').sum()}")
print(f"Total CLV at risk in Priority Save group: ${df.loc[df['Retention_Priority']=='Priority Save', 'Projected_CLV'].sum():,.0f}")
