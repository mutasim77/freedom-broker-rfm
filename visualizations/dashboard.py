import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

st.set_page_config(page_title="Client Trading Prediction Dashboard", layout="wide")

st.title("📈 Client Trading Prediction & Segmentation Dashboard")
st.markdown("""
This dashboard helps visualize predicted trading behavior, urgency scores, and expected commissions for clients.

Use the sidebar to filter and explore key metrics that support client outreach, marketing prioritization, and revenue forecasting.
""")

# Load Data
uploaded_file = st.sidebar.file_uploader("Upload your client prediction CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Date Conversion (if applicable)
    if 'predicted_next_trade_date' in df.columns:
        df['predicted_next_trade_date'] = pd.to_datetime(df['predicted_next_trade_date'], errors='coerce')

    # Sidebar Filters
    st.sidebar.header("🔎 Filter Options")
    sex_filter = st.sidebar.multiselect("Select Sex Type", options=df['sex_type'].unique(), default=df['sex_type'].unique())
    urgency_filter = st.sidebar.multiselect("Select Urgency Category", options=df['trading_urgency_category'].unique(), default=df['trading_urgency_category'].unique())

    filtered_df = df[(df['sex_type'].isin(sex_filter)) & (df['trading_urgency_category'].isin(urgency_filter))]

    # KPI Metrics
    st.subheader("📊 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Clients", len(filtered_df))
    col2.metric("Avg. Trade Prob. (30d)", f"{filtered_df['trade_probability_30days'].mean():.2%}")
    col3.metric("Expected 30d Commission", f"${filtered_df['expected_commission_30days'].sum():,.2f}")
    col4.metric("Urgency: Very High", (filtered_df['trading_urgency_category'] == 'Very High').sum())

    # Urgency Distribution
    st.subheader("📌 Trading Urgency Distribution")
    urgency_counts = filtered_df['trading_urgency_category'].value_counts()
    fig1, ax1 = plt.subplots()
    ax1.pie(urgency_counts, labels=urgency_counts.index, autopct='%1.1f%%', startangle=90, colors=sns.color_palette("pastel"))
    ax1.axis('equal')
    st.pyplot(fig1)

    # Trade Probability by Age Segment
    st.subheader("📈 Trade Probability by Age Segment")
    fig2, ax2 = plt.subplots(figsize=(10, 4))
    sns.boxplot(data=filtered_df, x='age_segment', y='trade_probability_30days', ax=ax2)
    st.pyplot(fig2)

    # Histogram: Predicted Days Until Next Trade
    st.subheader("⏳ Predicted Days Until Next Trade")
    fig3, ax3 = plt.subplots(figsize=(10, 4))
    sns.histplot(filtered_df['predicted_days_to_next_trade'], kde=True, bins=30, color='skyblue')
    ax3.set_xlabel("Days")
    st.pyplot(fig3)

    # Client Table
    st.subheader("📋 Client Detail Table")
    st.dataframe(filtered_df[['client_id','login','age_segment','sex_type','cluster','predicted_next_trade_date',
                             'trade_probability_7days','trade_probability_30days','trading_urgency_category',
                             'expected_commission_30days','expected_commission_90days']]
                .sort_values(by='trade_probability_30days', ascending=False).reset_index(drop=True))

    st.markdown("---")
    st.markdown("Made with ❤️ using Streamlit. Help your business grow through data.")

else:
    st.info("👈 Upload a CSV file from your predictive model to get started!")
