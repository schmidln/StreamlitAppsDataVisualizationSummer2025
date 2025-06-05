import streamlit as st
import altair as alt
import pandas as pd

# Main Streamlit app
st.title("Inside Airbnb: Interactive Data Dashboard")

# Load and clean data
try:
    data = pd.read_csv("listings.csv")
    data['price'] = data['price'].replace('[\$,]', '', regex=True).astype(float)
    data = data.dropna(subset=['price', 'beds', 'estimated_occupancy_l365d', 'neighbourhood_cleansed'])
    data['beds'] = data['beds'].astype(int)
    data['estimated_occupancy_l365d'] = data['estimated_occupancy_l365d'].astype(float)
except FileNotFoundError:
    st.error("File not found. Please ensure the file path is correct.")
    data = pd.DataFrame()

# Visualization 1: Estimated Occupancy vs. Number of Beds
def visualization1(data):
    chart = alt.Chart(data, title="Estimated Occupancy vs. Number of Beds (Guest Preference)").mark_bar(size=20).encode(
        x=alt.X('beds:N', title='Number of Beds', axis=alt.Axis(labelAngle=0)),
        y=alt.Y('avg_occupancy:Q', title='Estimated Occupancy (Last 365 Days)')
    ).transform_aggregate(
        avg_occupancy='mean(estimated_occupancy_l365d)',
        groupby=['beds']
    ).properties(width=600, height=400)
    return chart

# Visualization 2: Most Popular Number of Beds by Host
def visualization2(data):
    bars = alt.Chart(data, title="Listings Count by Number of Beds (Host Preference)").transform_aggregate(
        count='count()', groupby=['beds']
    ).mark_bar(size=20).encode(
        x=alt.X('beds:N', title='Number of Beds', axis=alt.Axis(labelAngle=0)),
        y=alt.Y('count:Q', title='Listing Count'),
        color=alt.Color('beds:N'),
        tooltip=['beds:N', 'count:Q']
    )
    return bars

# Visualization 3: Pie Chart of Listings by Room Type
def visualization3(data):
    chart = alt.Chart(data, title="Distribution of Listings by Room Type").transform_aggregate(
        count='count()', groupby=['room_type']
    ).mark_arc().encode(
        theta=alt.Theta(field="count", type="quantitative"),
        color=alt.Color(field="room_type", type="nominal", title="Room Type"),
        tooltip=["room_type:N", "count:Q"]
    ).properties(width=400, height=400)
    return chart

# Visualization 4: Scatter Plot of Price vs Estimated Occupancy
def visualization4(data):
    chart = alt.Chart(data, title='Price (USD) vs. Estimated Occupancy').mark_circle(size=60).encode(
        x=alt.X('price:Q', title='Price (USD)'),
        y=alt.Y('estimated_occupancy_l365d:Q', title='Estimated Occupancy (Last 365 Days)'),
        color=alt.Color('beds:N', title='Beds'),
        tooltip=['price:Q', 'estimated_occupancy_l365d:Q', 'beds:N', 'room_type:N']
    ).properties(width=700, height=400)
    return chart

if not data.empty:
    # Sidebar filters
    st.sidebar.header("Filter Listings")

    min_beds = int(data['beds'].min())
    max_beds = int(data['beds'].max())
    beds_selected = st.sidebar.slider("Number of Beds", min_beds, max_beds, (1, 4))

    min_price = int(data['price'].min())
    max_price = int(data['price'].max())
    price_selected = st.sidebar.slider("Price Range ($)", min_price, min(1000, max_price), (50, 300))

    occupancy_selected = st.sidebar.slider("Estimated Occupancy (last 365 days)", 0, int(data['estimated_occupancy_l365d'].max()), (0, 200))

    neighborhoods = st.sidebar.multiselect(
        "Select Neighborhoods",
        sorted(data['neighbourhood_cleansed'].unique()),
        default=sorted(data['neighbourhood_cleansed'].unique())[:10]
    )

    # Filter data
    data_filtered = data[
        (data['beds'] >= beds_selected[0]) & (data['beds'] <= beds_selected[1]) &
        (data['price'] >= price_selected[0]) & (data['price'] <= price_selected[1]) &
        (data['estimated_occupancy_l365d'] >= occupancy_selected[0]) &
        (data['estimated_occupancy_l365d'] <= occupancy_selected[1]) &
        (data['neighbourhood_cleansed'].isin(neighborhoods))
    ]

    # SECTION 1: Bed Preferences
    st.subheader("🏨 Guest & Host Bed Preferences")
    st.altair_chart(visualization1(data_filtered), use_container_width=True)
    st.altair_chart(visualization2(data_filtered), use_container_width=True)

    # SECTION 2: Room Type Distribution and Value-for-Money Patterns
    st.subheader("📊 Room Types and Value Patterns")
    st.altair_chart(visualization3(data_filtered), use_container_width=True)
    st.altair_chart(visualization4(data_filtered), use_container_width=True)

    st.caption("Data source: Inside Airbnb")
