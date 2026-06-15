import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------------
# PAGE CONFIG
# ----------------------------------

st.set_page_config(
    page_title="Factory Optimization Dashboard",
    layout="wide"
)

# ----------------------------------
# LOAD DATA
# ----------------------------------

df = pd.read_csv(
    "../outputs/reports/final_nassau_dataset.csv"
)

recommendations = pd.read_csv(
    "../outputs/reports/factory_recommendations.csv"
)

kpi = pd.read_csv(
    "../outputs/reports/kpi_summary.csv"
)

original_df = pd.read_csv(
    "../data/Nassau_Candy_Distributor.csv"
)

# ----------------------------------
# SIDEBAR
# ----------------------------------

st.sidebar.title("Optimization Controls")

product = st.sidebar.selectbox(
    "Select Product",
    sorted(recommendations["Product Name"].unique())
)

region = st.sidebar.selectbox(
    "Select Region",
    sorted(original_df["Region"].unique())
)

ship_mode = st.sidebar.selectbox(
    "Select Ship Mode",
    sorted(original_df["Ship Mode"].unique())
)

priority = st.sidebar.slider(
    "Optimization Priority (Speed ↔ Profit)",
    0,
    100,
    50
)

# ----------------------------------
# FILTER DATA
# ----------------------------------

filtered_df = original_df[
    (original_df["Region"] == region)
    &
    (original_df["Ship Mode"] == ship_mode)
]

st.sidebar.info(
    f"Matching Records: {len(filtered_df)}"
)

# ----------------------------------
# PRIORITY WEIGHTING
# ----------------------------------

speed_weight = priority / 100

profit_weight = 1 - speed_weight

recommendations["AdjustedScore"] = (
    recommendations["ImprovementPercent"]
    * speed_weight
    +
    (recommendations["ProfitImpact"] / 1000)
    * profit_weight
)

# ----------------------------------
# TITLE
# ----------------------------------

st.title(
    "Factory Reallocation & Shipping Optimization System"
)

st.info(
    """
    This system predicts shipping performance and recommends
    optimal factory-product reallocations to reduce lead times,
    improve profitability, and minimize logistics risk.
    """
)

# ----------------------------------
# KPI DASHBOARD
# ----------------------------------

st.subheader("Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)


lead_time_reduction = kpi[
    kpi["Metric"] == "Lead Time Reduction %"
]["Value"].iloc[0]

profit_stability = kpi[
    kpi["Metric"] == "Profit Stability"
]["Value"].iloc[0]

scenario_confidence = kpi[
    kpi["Metric"] == "Scenario Confidence"
]["Value"].iloc[0]

coverage = kpi[
    kpi["Metric"] == "Coverage %"
]["Value"].iloc[0]

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Lead Time Reduction %",
    round(lead_time_reduction, 2)
)

col2.metric(
    "Profit Stability",
    round(profit_stability, 2)
)

col3.metric(
    "Scenario Confidence",
    round(scenario_confidence, 2)
)

col4.metric(
    "Coverage %",
    round(coverage, 2)
)
st.markdown("---")

# ----------------------------------
# FACTORY OPTIMIZATION SIMULATOR
# ----------------------------------

st.header("Factory Optimization Simulator")

selected_product = recommendations[
    recommendations["Product Name"].astype(str).str.strip()
    ==
    str(product).strip()
]

if len(selected_product) > 0:

    st.dataframe(
        selected_product,
        use_container_width=True
    )

    current_factory = selected_product[
        "CurrentFactory"
    ].iloc[0]

    recommended_factory = selected_product[
        "RecommendedFactory"
    ].iloc[0]

    st.success(
        f"Move from {current_factory} → {recommended_factory}"
    )

else:

    st.error(
        f"No recommendation found for {product}"
    )

    st.stop()

st.markdown("---")

# ----------------------------------
# WHAT-IF ANALYSIS
# ----------------------------------

st.header("What-If Scenario Analysis")

comparison_df = pd.DataFrame({

    "Lead Time Type": [
        "Current Lead Time",
        "Recommended Lead Time"
    ],

    "Days": [
        selected_product[
            "CurrentLeadTime"
        ].iloc[0],

        selected_product[
            "NewLeadTime"
        ].iloc[0]
    ]
})

fig = px.bar(
    comparison_df,
    x="Lead Time Type",
    y="Days",
    title="Current vs Recommended Lead Time"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.markdown("---")

# ----------------------------------
# RECOMMENDATION DASHBOARD
# ----------------------------------

st.header("Recommendation Dashboard")

top10 = recommendations.sort_values(
    by="AdjustedScore",
    ascending=False
).head(10)

st.dataframe(
    top10,
    use_container_width=True
)

fig = px.bar(
    top10,
    x="Product Name",
    y="ImprovementPercent",
    title="Expected Efficiency Gains"
)

st.plotly_chart(
    fig,
    use_container_width=True
)