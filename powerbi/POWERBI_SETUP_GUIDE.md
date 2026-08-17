# Power BI Dashboard — Setup Guide

Build this in Power BI Desktop using `data/scored_customer_dataset.csv`
(the fully scored, segmented output from the Python pipeline).

## 1. Load the data
- Get Data → Text/CSV → `data/scored_customer_dataset.csv`
- Set `Churn_Risk_Score` and `Projected_CLV` as Decimal Number,
  `Customer_Segment`, `Churn_Risk_Tier`, `Retention_Priority` as Text.

## 2. Core DAX measures

```dax
Total Customers = COUNTROWS('scored_customer_dataset')

Churned Customers =
CALCULATE(COUNTROWS('scored_customer_dataset'), 'scored_customer_dataset'[Churn] = "Yes")

Churn Rate % = DIVIDE([Churned Customers], [Total Customers], 0)

Avg CLV = AVERAGE('scored_customer_dataset'[Projected_CLV])

Total CLV = SUM('scored_customer_dataset'[Projected_CLV])

Priority Save Customers =
CALCULATE(COUNTROWS('scored_customer_dataset'), 'scored_customer_dataset'[Retention_Priority] = "Priority Save")

CLV at Risk =
CALCULATE([Total CLV], 'scored_customer_dataset'[Retention_Priority] = "Priority Save")

Avg Satisfaction = AVERAGE('scored_customer_dataset'[Satisfaction_Score])

Avg Support Tickets = AVERAGE('scored_customer_dataset'[Num_Support_Tickets])
```

## 3. Suggested page structure

**Page 1 — Executive Overview**
- KPI cards: Total Customers, Churn Rate %, Avg CLV, CLV at Risk
- Churn Rate by Contract Type (bar)
- Customer Segment distribution (donut)

**Page 2 — Retention Priority**
- Scatter: Churn_Risk_Score (x) vs Projected_CLV (y), colored by Churn_Risk_Tier
  — recreate the Python "priority matrix" as an interactive Power BI visual
- Table: customers where Retention_Priority = "Priority Save", sorted by
  Projected_CLV descending — this is the actionable retention call-list
- Card: Priority Save Customers, CLV at Risk

**Page 3 — Customer Segments**
- Segment scatter: Satisfaction vs CLV, bubble size = Tenure
- Avg CLV, Avg Satisfaction, Churn Rate by Customer_Segment (matrix/table)

**Page 4 — Churn Drivers**
- Static images from `/screenshots`: ROC curve, feature importance,
  support-tickets-vs-satisfaction heatmap
- Churn Rate by Payment_Method, Autopay_Enrolled (bar charts)

## 4. Formatting notes
- Segment colors: Champions = green (#2ECC71), Loyal Steady = blue (#3B82F6),
  At Risk = amber (#F5B041), Low Engagement = grey (#95A5A6)
- Risk tier colors: Low/Medium/High/Very High = green/amber/orange/red,
  consistent with the Python charts
- Save as `Churn_CLV_Dashboard.pbix` in `/powerbi`
- Export finished pages as PNG into `/screenshots` for the README
