import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="Retail Sales Intelligence Dashboard")
st.title("🛍️ Retail Sales Intelligence App")
st.caption("Stack AI Foundation - AI Native App Building - Level 1")

# 1. DATA INTEGRATION
st.sidebar.header("1. Upload Data Files")
sales_file = st.sidebar.file_uploader("Upload retail_weekly_sales.xlsx", type=["xlsx"])
master_file = st.sidebar.file_uploader("Upload store_master.xlsx", type=["xlsx"])

if sales_file and master_file:
    df_sales = pd.read_excel(sales_file)
    df_master = pd.read_excel(master_file)
    
    # Standardize column naming rules to avoid case sensitivity conflicts
    df_sales.columns = df_sales.columns.str.strip().str.lower()
    df_master.columns = df_master.columns.str.strip().str.lower()
    
    # --- CRITICAL FIX: Clean and Force Numeric Conversion ---
    # This prevents the numpy/pandas sum error by cleaning dirty strings and filling empty slots with 0
    numeric_cols = ['net_sales', 'sales_target', 'transactions', 'returns_amount', 'discount_amount', 'gross_sales', 'stockouts']
    for col in numeric_cols:
        if col in df_sales.columns:
            # If columns contain currency signs or commas, strip them out
            if df_sales[col].dtype == 'object':
                df_sales[col] = df_sales[col].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False)
            df_sales[col] = pd.to_numeric(df_sales[col], errors='coerce').fillna(0.0)

    # Merge datasets using the specified common key
    df_master_clean = df_master[['store_id', 'store_name', 'city', 'store_format']].drop_duplicates() if 'store_name' in df_master.columns else df_master
    df = pd.merge(df_sales, df_master_clean, on="store_id", how="inner", suffixes=('', '_master'))

    # Use the master metadata column mapping if names match
    store_col = 'store_name_master' if 'store_name_master' in df.columns else 'store_name'
    city_col = 'city_master' if 'city_master' in df.columns else 'city'
    format_col = 'store_format_master' if 'store_format_master' in df.columns else 'store_format'
    region_col = 'region_master' if 'region_master' in df.columns else 'region'

    # 2. DYNAMIC SIDEBAR FILTERS
    st.sidebar.header("2. Dashboard Filters")
    weeks = st.sidebar.multiselect("Select Week", options=sorted(df["week_start_date"].unique().astype(str)))
    regions = st.sidebar.multiselect("Select Region", options=df[region_col].unique())
    stores = st.sidebar.multiselect("Select Store", options=df[store_col].unique())
    cities = st.sidebar.multiselect("Select City", options=df[city_col].unique())
    formats = st.sidebar.multiselect("Select Store Format", options=df[format_col].unique())
    categories = st.sidebar.multiselect("Select Product Category", options=df["product_category"].unique())

    # Build filtered execution layer
    filtered_df = df.copy()
    if weeks:
        filtered_df = filtered_df[filtered_df["week_start_date"].astype(str).isin(weeks)]
    if regions:
        filtered_df = filtered_df[filtered_df[region_col].isin(regions)]
    if stores:
        filtered_df = filtered_df[filtered_df[store_col].isin(stores)]
    if cities:
        filtered_df = filtered_df[filtered_df[city_col].isin(cities)]
    if formats:
        filtered_df = filtered_df[filtered_df[format_col].isin(formats)]
    if categories:
        filtered_df = filtered_df[filtered_df["product_category"].isin(categories)]

    # 3. MANDATORY KPI CARDS CALCULATIONS
    total_net_sales = float(filtered_df["net_sales"].sum())
    total_sales_target = float(filtered_df["sales_target"].sum())
    target_ach = (total_net_sales / total_sales_target * 100) if total_sales_target > 0 else 0.0
    
    total_transactions = float(filtered_df["transactions"].sum())
    atv = (total_net_sales / total_transactions) if total_transactions > 0 else 0.0
    
    total_returns = float(filtered_df["returns_amount"].sum())
    return_rate = (total_returns / total_net_sales * 100) if total_net_sales > 0 else 0.0
    
    total_discount = float(filtered_df["discount_amount"].sum())
    total_gross = float(filtered_df["gross_sales"].sum())
    discount_rate = (total_discount / total_gross * 100) if total_gross > 0 else 0.0

    # Layout Metrics Grid
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    kpi1.metric("Net Sales", f"${total_net_sales:,.2f}")
    kpi2.metric("Target Achievement", f"{target_ach:.1f}%")
    kpi3.metric("Avg Transaction Value (ATV)", f"${atv:,.2f}")
    kpi4.metric("Return Rate", f"{return_rate:.1f}%")
    kpi5.metric("Discount Rate", f"{discount_rate:.1f}%")

    st.markdown("---")

    # 4. MANDATORY CHARTS
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Weekly Sales Trend")
        trend_data = filtered_df.groupby("week_start_date")["net_sales"].sum().reset_index()
        fig_trend = px.line(trend_data, x="week_start_date", y="net_sales", markers=True)
        st.plotly_chart(fig_trend, use_container_width=True)

        st.subheader("📦 Category Performance")
        cat_data = filtered_df.groupby("product_category")["net_sales"].sum().reset_index().sort_values(by="net_sales")
        fig_cat = px.bar(cat_data, x="net_sales", y="product_category", orientation='h')
        st.plotly_chart(fig_cat, use_container_width=True)

    with col2:
        st.subheader("🌍 Sales by Region")
        region_data = filtered_df.groupby(region_col)["net_sales"].sum().reset_index()
        fig_region = px.pie(region_data, values="net_sales", names=region_col, hole=0.4)
        st.plotly_chart(fig_region, use_container_width=True)

        st.subheader("🚨 Stockout Risk by Category")
        stock_data = filtered_df.groupby("product_category")["stockouts"].sum().reset_index()
        fig_stock = px.bar(stock_data, x="product_category", y="stockouts", color="product_category")
        st.plotly_chart(fig_stock, use_container_width=True)

    st.subheader("🏆 Store Leaderboard (Top 10)")
    leaderboard_data = filtered_df.groupby(store_col)["net_sales"].sum().reset_index().sort_values(by="net_sales", ascending=False).head(10)
    fig_lead = px.bar(leaderboard_data, x=store_col, y="net_sales", color="net_sales")
    st.plotly_chart(fig_lead, use_container_width=True)

    st.markdown("---")

    # 5. BUSINESS INSIGHT SUMMARY
    st.subheader("📝 Automated Business Insights Summary")
    
    # Region Insights
    region_perf = filtered_df.groupby(region_col)["net_sales"].sum()
    if not region_perf.empty:
        st.write(f"🔹 **Top Performing Region:** {region_perf.idxmax()} with total sales of ${region_perf.max():,.2f}")
        st.write(f"🔹 **Underperforming Region:** {region_perf.idxmin()} with total sales of ${region_perf.min():,.2f}")
    
    # Store Achievement Insights
    store_perf = filtered_df.groupby(store_col)[["net_sales", "sales_target"]].sum()
    store_perf["ach"] = (store_perf["net_sales"] / store_perf["sales_target"]) * 100
    missing_target = store_perf[store_perf["ach"] < 100]
    st.write(f"🔹 **Stores Missing Target:** {len(missing_target)} individual location(s) currently tracking below 100% target baseline.")
    
    # Product Returns Insights
    cat_returns = filtered_df.groupby("product_category")[["returns_amount", "net_sales"]].sum()
    cat_returns["ret_rate"] = (cat_returns["returns_amount"] / cat_returns["net_sales"]) * 100
    if not cat_returns.empty:
        st.write(f"🔹 **Highest Return Rate Category:** {cat_returns['ret_rate'].idxmax()} ({cat_returns['ret_rate'].max():.1f}% return ratio)")

    # 6. EXPORT MODULE
    st.markdown("---")
    st.subheader("📥 Export Filtered Datasets")
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(label="Download Filtered Data as CSV", data=csv, file_name="filtered_retail_intelligence_report.csv", mime="text/csv")

else:
    st.info("⚠️ Please upload both 'retail_weekly_sales.xlsx' and 'store_master.xlsx' sheets in the left sidebar configuration window to initialize your executive business dashboard views.")
