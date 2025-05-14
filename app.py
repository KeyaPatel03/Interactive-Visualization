import streamlit as st
import pandas as pd
import plotly.express as px

# Set Streamlit config
st.set_page_config(page_title="SCU Waste Dashboard", layout="wide")

# Load and clean data
@st.cache_data
def load_data():
    df = pd.read_csv("waste_data.csv")
    df["Category"] = df["Category"].str.strip().str.title()  # Normalize names
    df["Weight (lbs)"] = pd.to_numeric(df["Weight (lbs)"], errors="coerce")
    df = df.dropna(subset=["Weight (lbs)", "Year", "Category"])
    df["Year"] = df["Year"].astype(int)
    return df

df = load_data()

# Group data by Year and Category
df_grouped = df.groupby(["Year", "Category"])["Weight (lbs)"].sum().reset_index()

# All years from 2005 to 2025
years_full = list(range(2005, 2026))
categories_unique = sorted(df_grouped["Category"].unique())

# --- Sidebar filters ---
st.sidebar.header("🧭 Filters")

# Year range slider
min_year, max_year = st.sidebar.select_slider(
    "Select Year Range",
    options=years_full,
    value=(years_full[0], years_full[-1])
)

# Waste category multiselect
selected_categories = st.sidebar.multiselect(
    "Select Waste Categories",
    options=categories_unique,
    default=categories_unique
)

# --- Filter and fill missing years/categories ---
full_index = pd.MultiIndex.from_product(
    [range(min_year, max_year + 1), selected_categories],
    names=["Year", "Category"]
)

filtered_df = df_grouped.set_index(["Year", "Category"]) \
                        .reindex(full_index, fill_value=0) \
                        .reset_index()

# --- Page Header ---
st.title("📊 Santa Clara University Waste Visualization Dashboard")
st.markdown("Analyze and explore trends in campus waste streams by year and category.")

custom_colors = ['#28ab9d', '#ff7e47', '#c7d86e', '#f37fb9']

# --- Pie Chart ---
st.subheader(f"🟢 Total Waste Distribution ({min_year} to {max_year})")
agg_pie = filtered_df.groupby("Category")["Weight (lbs)"].sum().reset_index()
fig_pie = px.pie(agg_pie, names="Category", values="Weight (lbs)", hole=0.4,color_discrete_sequence=custom_colors)
st.plotly_chart(fig_pie, use_container_width=True)

# --- Grouped Vertical Bar Chart ---
st.subheader("🔵 Grouped Bar Chart: Waste by Year and Category")
fig_bar = px.bar(
    filtered_df,
    x="Year",
    y="Weight (lbs)",
    color="Category",
    barmode="group",
    title="Grouped Waste Volumes Over Time",
    color_discrete_sequence=custom_colors
)
fig_bar.update_xaxes(type='category', categoryarray=years_full)
fig_bar.update_yaxes(title="Weight (lbs)")
st.plotly_chart(fig_bar, use_container_width=True)

# --- Multi-Line Chart ---
st.subheader("📈 Multi-Line Chart: Category Trends Over Time")
fig_line = px.line(
    filtered_df,
    x="Year",
    y="Weight (lbs)",
    color="Category",
    markers=True,
    title="Yearly Waste Trend per Category",
    color_discrete_sequence=custom_colors
)
fig_line.update_xaxes(type='category', categoryarray=years_full)
st.plotly_chart(fig_line, use_container_width=True)

# --- Dot Plot ---
st.subheader("🔴 Dot Plot: Waste by Year and Category")
fig_dot = px.scatter(
    filtered_df,
    x="Year",
    y="Weight (lbs)",
    color="Category",
    size="Weight (lbs)",
    hover_name="Category",
    title="Waste Distribution Dots",
    color_discrete_sequence=custom_colors
)
fig_dot.update_xaxes(type='category', categoryarray=years_full)
st.plotly_chart(fig_dot, use_container_width=True)

# --- Raw Data (optional) ---
with st.expander("📄 View Filtered Data Table"):
    st.dataframe(filtered_df)
