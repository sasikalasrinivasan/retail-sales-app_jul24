import streamlit as st
import pandas as pd
import plotly.express as px

# ==============================================================================
# RETAIL SALES INTELLIGENCE APP - STREAMLIT DASHBOARD
# Meets Level 1 Compliance Parameters
# ==============================================================================

st.set_page_config(
    page_title="Retail Sales Intelligence App",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🛍️ Retail Sales Intelligence App")
st.markdown("---")

# ------------------------------------------------------------------------------
# 1. DATA INTEGRATION & FILE UPLOADER
# ------------------------------------------------------------------------------
st.sidebar.header("📁 1. Data Integration")

weekly_sales_file = st.sidebar.file_uploader(
    "Upload 'retail_weekly_sales.xlsx'",
    type=["xlsx", "xls"],
    key="sales_upload"
)

store_master_file = st.sidebar.file_uploader(
    "Upload 'store_master.xlsx'",
    type=["xlsx", "xls"],
    key="store_upload"
)

@st.cache_data
def load_and_merge_data(sales_file, master_file):
    if sales_file is not None and master_file is not None:
        df_sales = pd.read_excel(sales_file)
        df_master = pd.read_excel(master_file)
        
        # Standardize column names to lowercase for robust merging
        df_sales.columns = df_sales.columns.str.strip().str.lower()
        df_master.columns = df_master.columns.str.strip().str.lower()
        
        # Merge datasets on 'store_id'
        df_merged = pd.merge(df_sales, df_master, on="store_id", how="left")
        return df_merged
    return None

df_raw = load_and_merge_data(weekly_sales_file, store_master_file)

# 6. FRIENDLY INFO MESSAGE IF FILES ARE NOT UPLOADED
if df_raw is None:
    st.info("👈 Please upload both 'retail_weekly_sales.xlsx' and 'store_master.xlsx' in the sidebar to view the dashboard.")
    st.stop()

# ------------------------------------------------------------------------------
# 2. SIDEBAR FILTERS (DYNAMIC CASCADING)
# ------------------------------------------------------------------------------
st.sidebar.header("🔍 2. Filters")

df_filtered = df_raw.copy()

# week_start_date
if 'week_start_date' in df_raw.columns:
    weeks = sorted(df_raw['week_start_date'].dropna().astype(str).unique().tolist())
    sel_weeks = st.sidebar.multiselect("Select week_start_date", options=weeks, default=weeks)
    if sel_weeks:
        df_filtered = df_filtered[df_filtered['week_start_date'].astype(str).isin(sel_weeks)]

# region
if 'region' in df_filtered.columns:
    regions = sorted(df_filtered['region'].dropna().unique().tolist())
    sel_regions = st.sidebar.multiselect("Select region", options=regions, default=regions)
    if sel_regions:
        df_filtered = df_filtered[df_filtered['region'].isin(sel_regions)]

# city
if 'city' in df_filtered.columns:
    cities = sorted(df_filtered['city'].dropna().unique().tolist())
    sel_cities = st.sidebar.multiselect("Select city", options=cities, default=cities)
    if sel_cities:
        df_filtered = df_filtered[df_filtered['city'].isin(sel_cities)]

# store_format
if 'store_format' in df_filtered.columns:
    formats = sorted(df_filtered['store_format'].dropna().unique().tolist())
    sel_formats = st.sidebar.multiselect("Select store_format", options=formats, default=formats)
    if sel_formats:
        df_filtered = df_filtered[df_filtered['store_format'].isin(sel_formats)]

# store_name
if 'store_name' in df_filtered.columns:
    stores = sorted(df_filtered['store_name'].dropna().unique().tolist())
    sel_stores = st.sidebar.multiselect("Select store_name", options=stores, default=stores)
    if sel_stores:
        df_filtered = df_filtered[df_filtered['store_name'].isin(sel_stores)]

# product_category
if 'product_category' in df_filtered.columns:
    categories = sorted(df_filtered['product_category'].dropna().unique().tolist())
    sel_categories = st.sidebar.multiselect("Select product_category", options=categories, default=categories)
    if sel_categories:
        df_filtered = df_filtered[df_filtered['product_category'].isin(sel_categories)]

# ------------------------------------------------------------------------------
# 3. MANDATORY KPI CARDS
# ------------------------------------------------------------------------------
st.subheader("📌 Mandatory KPI Cards")

net_sales_sum = df_filtered['net_sales'].sum() if 'net_sales' in df_filtered.columns else 0.0
sales_target_sum = df_filtered['sales_target'].sum() if 'sales_target' in df_filtered.columns else 0.0
transactions_sum = df_filtered['transactions'].sum() if 'transactions' in df_filtered.columns else 0.0
returns_amount_sum = df_filtered['returns_amount'].sum() if 'returns_amount' in df_filtered.columns else 0.0
discount_amount_sum = df_filtered['discount_amount'].sum() if 'discount_amount' in df_filtered.columns else 0.0
gross_sales_sum = df_filtered['gross_sales'].sum() if 'gross_sales' in df_filtered.columns else 0.0

# Formulas
target_achievement_pct = (net_sales_sum / sales_target_sum * 100) if sales_target_sum > 0 else 0.0
atv = (net_sales_sum / transactions_sum) if transactions_sum > 0 else 0.0
return_rate_pct = (returns_amount_sum / net_sales_sum * 100) if net_sales_sum > 0 else 0.0
discount_rate_pct = (discount_amount_sum / gross_sales_sum * 100) if gross_sales_sum > 0 else 0.0

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

kpi1.metric("Net Sales", f"${net_sales_sum:,.2f}")
kpi2.metric("Target Achievement (%)", f"{target_achievement_pct:.1f}%")
kpi3.metric("Average Transaction Value (ATV)", f"${atv:,.2f}")
kpi4.metric("Return Rate (%)", f"{return_rate_pct:.2f}%")
kpi5.metric("Discount Rate (%)", f"{discount_rate_pct:.2f}%")

st.markdown("---")

# ------------------------------------------------------------------------------
# 4. MANDATORY CHARTS (PLOTLY EXPRESS)
# ------------------------------------------------------------------------------
st.subheader("📊 Performance Analytics & Visualizations")

row1_col1, row1_col2 = st.columns([2, 1])

with row1_col1:
    # 1. Weekly Trend: Line chart showing 'net_sales' over 'week_start_date'
    if 'week_start_date' in df_filtered.columns and 'net_sales' in df_filtered.columns:
        df_weekly = df_filtered.groupby('week_start_date', as_index=False)['net_sales'].sum()
        fig_weekly = px.line(
            df_weekly,
            x='week_start_date',
            y='net_sales',
            title="Weekly Trend: Net Sales over Week Start Date",
            markers=True
        )
        st.plotly_chart(fig_weekly, use_container_width=True)

with row1_col2:
    # 2. Sales by Region: Pie chart showing 'net_sales' distribution across 'region'
    if 'region' in df_filtered.columns and 'net_sales' in df_filtered.columns:
        df_region = df_filtered.groupby('region', as_index=False)['net_sales'].sum()
        fig_region = px.pie(
            df_region,
            names='region',
            values='net_sales',
            title="Sales by Region",
            hole=0.4
        )
        st.plotly_chart(fig_region, use_container_width=True)

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    # 3. Category Performance: Horizontal bar chart sorted by highest 'net_sales' across 'product_category'
    if 'product_category' in df_filtered.columns and 'net_sales' in df_filtered.columns:
        df_cat = df_filtered.groupby('product_category', as_index=False)['net_sales'].sum()
        df_cat = df_cat.sort_values('net_sales', ascending=True)
        fig_cat = px.bar(
            df_cat,
            x='net_sales',
            y='product_category',
            orientation='h',
            title="Category Performance (Net Sales by Product Category)",
            color='net_sales',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig_cat, use_container_width=True)

with row2_col2:
    # 4. Store Leaderboard: Top 10 stores based on 'net_sales' across 'store_name'
    store_key = 'store_name' if 'store_name' in df_filtered.columns else 'store_id'
    if store_key in df_filtered.columns and 'net_sales' in df_filtered.columns:
        df_store_lead = df_filtered.groupby(store_key, as_index=False)['net_sales'].sum().nlargest(10, 'net_sales')
        df_store_lead = df_store_lead.sort_values('net_sales', ascending=True)
        fig_leaderboard = px.bar(
            df_store_lead,
            x='net_sales',
            y=store_key,
            orientation='h',
            title="Store Leaderboard (Top 10 Stores by Net Sales)",
            color='net_sales',
            color_continuous_scale='Greens'
        )
        st.plotly_chart(fig_leaderboard, use_container_width=True)

# 5. Stockout Risk: Bar chart displaying the sum of 'stockouts' across 'product_category'
if 'product_category' in df_filtered.columns and 'stockouts' in df_filtered.columns:
    df_stockout = df_filtered.groupby('product_category', as_index=False)['stockouts'].sum()
    fig_stockout = px.bar(
        df_stockout,
        x='product_category',
        y='stockouts',
        title="Stockout Risk: Out-of-Stock Days by Product Category",
        color='stockouts',
        color_continuous_scale='Reds'
    )
    st.plotly_chart(fig_stockout, use_container_width=True)

st.markdown("---")

# ------------------------------------------------------------------------------
# 5. BUSINESS INSIGHT SUMMARY
# ------------------------------------------------------------------------------
st.subheader("💡 Business Insight Summary")

bcol1, bcol2, bcol3 = st.columns(3)

# Best and worst performing region by sales volume
if 'region' in df_filtered.columns and 'net_sales' in df_filtered.columns:
    df_reg_sales = df_filtered.groupby('region', as_index=False)['net_sales'].sum().sort_values('net_sales', ascending=False)
    if not df_reg_sales.empty:
        best_region = df_reg_sales.iloc[0]
        worst_region = df_reg_sales.iloc[-1]
        with bcol1:
            st.success(f"**Best Region:** {best_region['region']} (${best_region['net_sales']:,.2f})")
            st.error(f"**Worst Region:** {worst_region['region']} (${worst_region['net_sales']:,.2f})")

# Stores with target achievement under 100%
store_key = 'store_name' if 'store_name' in df_filtered.columns else 'store_id'
if store_key in df_filtered.columns and 'net_sales' in df_filtered.columns and 'sales_target' in df_filtered.columns:
    df_store_achieve = df_filtered.groupby(store_key, as_index=False).agg({
        'net_sales': 'sum',
        'sales_target': 'sum'
    })
    df_store_achieve['achievement_%'] = (df_store_achieve['net_sales'] / df_store_achieve['sales_target']) * 100
    underperforming = df_store_achieve[df_store_achieve['achievement_%'] < 100]
    with bcol2:
        st.warning(f"**Stores Missing Target (<100%):** {len(underperforming)} stores")
        if not underperforming.empty:
            for _, r in underperforming.head(4).iterrows():
                st.write(f"- **{r[store_key]}**: {r['achievement_%']:.1f}% (${r['net_sales']:,.2f} / ${r['sales_target']:,.2f})")

# Highlight product category with highest return rate
if 'product_category' in df_filtered.columns and 'returns_amount' in df_filtered.columns and 'net_sales' in df_filtered.columns:
    df_cat_returns = df_filtered.groupby('product_category', as_index=False).agg({
        'returns_amount': 'sum',
        'net_sales': 'sum'
    })
    df_cat_returns['return_rate_%'] = (df_cat_returns['returns_amount'] / df_cat_returns['net_sales']) * 100
    df_cat_returns = df_cat_returns.sort_values('return_rate_%', ascending=False)
    if not df_cat_returns.empty:
        top_return_cat = df_cat_returns.iloc[0]
        with bcol3:
            st.error(f"**Highest Return Category:** {top_return_cat['product_category']}")
            st.write(f"- Return Rate: **{top_return_cat['return_rate_%']:.2f}%**")
            st.write(f"- Returns Amount: ${top_return_cat['returns_amount']:,.2f}")

st.markdown("---")

# ------------------------------------------------------------------------------
# 6. DATA EXPORT
# ------------------------------------------------------------------------------
st.subheader("📥 Data Export")

@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

csv_data = convert_df_to_csv(df_filtered)

st.download_button(
    label="📄 Download Filtered Dataset as CSV",
    data=csv_data,
    file_name="filtered_retail_sales.csv",
    mime="text/csv"
)
