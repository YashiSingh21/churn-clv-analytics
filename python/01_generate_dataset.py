"""
Customer Churn & Lifetime Value Analytics
Step 1: Synthetic Dataset Generation

Author: Yashi Singh

Description:
Generates a synthetic subscription-business customer dataset (telecom/SaaS
style) with realistic relationships between customer behavior (tenure,
contract type, support tickets, usage, satisfaction) and churn outcome.
Churn probability is built from a weighted risk function with injected
noise, giving the dataset genuine, learnable signal for the downstream
churn model and CLV calculation.
"""

import numpy as np
import pandas as pd

np.random.seed(7)

N = 5000

contract_types = ["Month-to-Month", "One Year", "Two Year"]
payment_methods = ["Credit Card", "Bank Transfer", "Digital Wallet", "Mailed Check"]
service_tiers = ["Basic", "Standard", "Premium"]

contract_type = np.random.choice(contract_types, N, p=[0.55, 0.27, 0.18])
payment_method = np.random.choice(payment_methods, N, p=[0.35, 0.28, 0.27, 0.10])
service_tier = np.random.choice(service_tiers, N, p=[0.30, 0.45, 0.25])

tenure_months = np.random.gamma(shape=2.2, scale=14, size=N).clip(1, 72).round().astype(int)

tier_base_price = {"Basic": 25, "Standard": 55, "Premium": 95}
monthly_charges = np.array([
    tier_base_price[t] + np.random.normal(0, 6) for t in service_tier
]).clip(15, 130).round(2)

total_charges = (monthly_charges * tenure_months * np.random.uniform(0.92, 1.0, N)).round(2)

tier_usage_mean = {"Basic": 25, "Standard": 55, "Premium": 95}
avg_usage_gb = np.array([
    np.random.normal(tier_usage_mean[t], 15) for t in service_tier
]).clip(2, 200).round(1)

num_support_tickets = np.random.poisson(1.4, N).clip(0, 15)
satisfaction_score = np.clip(
    np.round(np.random.normal(3.6, 0.9, N) - 0.15 * num_support_tickets), 1, 5
).astype(int)

num_addon_services = np.random.poisson(1.1, N).clip(0, 6)
autopay_enrolled = np.random.choice([1, 0], N, p=[0.62, 0.38])

# ---- Build genuine churn-risk signal ----
risk_score = (
    np.where(contract_type == "Month-to-Month", 2.2, 0)
    + np.where(contract_type == "One Year", 0.55, 0)
    + 0.5 * num_support_tickets
    - 0.75 * satisfaction_score
    - 0.04 * tenure_months
    + 0.016 * monthly_charges
    - 0.35 * num_addon_services
    + np.where(autopay_enrolled == 0, 0.7, 0)
    + np.where(payment_method == "Mailed Check", 0.55, 0)
    + np.random.normal(0, 1.0, N)
)

churn_prob = 1 / (1 + np.exp(-(risk_score - 1.2) / 1.6))
churn = np.where(np.random.uniform(0, 1, N) < churn_prob, "Yes", "No")

df = pd.DataFrame({
    "Customer_ID": [f"CUST{200000+i}" for i in range(N)],
    "Tenure_Months": tenure_months,
    "Contract_Type": contract_type,
    "Service_Tier": service_tier,
    "Payment_Method": payment_method,
    "Autopay_Enrolled": autopay_enrolled,
    "Monthly_Charges": monthly_charges,
    "Total_Charges": total_charges,
    "Avg_Monthly_Usage_GB": avg_usage_gb,
    "Num_Support_Tickets": num_support_tickets,
    "Satisfaction_Score": satisfaction_score,
    "Num_Addon_Services": num_addon_services,
    "Churn": churn,
})

df.to_csv("/home/claude/churn-clv-analytics/data/subscription_customer_dataset.csv", index=False)

print(f"Dataset generated: {df.shape[0]} rows, {df.shape[1]} columns")
print(f"Churn rate: {(df['Churn'] == 'Yes').mean():.1%}")
print(df.head())
