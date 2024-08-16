import streamlit as st
import pandas as pd
import plotly.express as px
import os
import warnings
import numpy as np
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")

st.set_page_config(page_title="WallMart Dashboard", page_icon=":bar_chart:", layout="wide") 

st.title("Dashboard")

st.markdown("<style> dev.block-container {padding: 0px;}</style>", unsafe_allow_html=True)

f1 = st.file_uploader(":file_folder: Upload File", type=["csv", "xlsx", "xls", "txt"])

if f1 is not None:
    filename = f1.name
    st.write(filename)
    df = pd.read_csv(filename, encoding="ISO-8859-1")
else:
    os.chdir(r"/home/devang/Desktop/projects/Walmart-Sparkathon/datastore")
    df = pd.read_csv("sales_admin.csv", encoding="ISO-8859-1")

col1, col2 = st.columns((2))
df["date_"] = pd.to_datetime(df["date_"]) 

startDate = pd.to_datetime(df["date_"].min())
endDate = pd.to_datetime(df["date_"].max())

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df = df[(df["date_"] >= date1) & (df["date_"] <= date2)].copy()

st.sidebar.header("Choose your filter: ")

# Create for city_name only
city = st.sidebar.multiselect("Pick the city", df["city_name"].unique())

# Filter the data based on city_name
if not city:
    filtered_df = df
else:
    filtered_df = df[df["city_name"].isin(city)]

# category_df = filtered_df.groupby(by = ["Category"], as_index = False)["Sales"].sum()

with col1:
    st.subheader("City-wise Sales procured quantity")
    fig = px.pie(filtered_df, values="procured_quantity", names="city_name", hole=0.5)
    fig.update_traces(text=filtered_df["city_name"], textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("City-wise Sales")
    fig = px.pie(filtered_df, values="total_weighted_landing_price", names="city_name", hole=0.5)
    fig.update_traces(text=filtered_df["city_name"], textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

cl1, cl2 = st.columns((2))

with cl1:
    with st.expander("City-wise Procurement Quantity Data"):
        city_procured_quantity = filtered_df.groupby(by="city_name", as_index=False)["procured_quantity"].sum()
        st.write(city_procured_quantity.style.background_gradient(cmap="Blues"))
        csv = city_procured_quantity.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="City_Procured_Quantity.csv", mime="text/csv",
                           help='Click here to download the data as a CSV file')

with cl2:
    with st.expander("City-wise Total Weighted Landing Price Data"):
        city_landing_price = filtered_df.groupby(by="city_name", as_index=False)["total_weighted_landing_price"].sum()
        st.write(city_landing_price.style.background_gradient(cmap="Oranges"))
        csv = city_landing_price.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="City_Total_Weighted_Landing_Price.csv", mime="text/csv",
                           help='Click here to download the data as a CSV file')


filtered_df["month_year"] = filtered_df["date_"].dt.to_period("M")
st.subheader('Time Series Analysis')


# Convert Order Date to weekly period
filtered_df["week_year"] = filtered_df["date_"].dt.to_period("W").apply(lambda r: r.start_time)

# Aggregate by week
linechart_weekly = pd.DataFrame(filtered_df.groupby(filtered_df["week_year"])["procured_quantity"].sum()).reset_index()
linechart_weekly.columns = ['week_year', 'procured_quantity']

fig2_weekly = px.line(linechart_weekly, x="week_year", y="procured_quantity", labels={"procured_quantity": "Procured Quantity"}, height=500, width=1000, template="gridon")
st.plotly_chart(fig2_weekly, use_container_width=True, markers = True)


with st.expander("View Data of TimeSeries:"):
    st.write(linechart_weekly.T.style.background_gradient(cmap="Blues"))
    csv = linechart_weekly.to_csv(index=False).encode("utf-8")
    st.download_button('Download Data', data = csv, file_name = "TimeSeries.csv", mime ='text/csv')

# Aggregate by week for total_weighted_landing_price
linechart_weekly = pd.DataFrame(filtered_df.groupby(filtered_df["week_year"])["total_weighted_landing_price"].sum()).reset_index()
linechart_weekly.columns = ['week_year', 'total_weighted_landing_price']

fig2_weekly = px.line(linechart_weekly, x="week_year", y="total_weighted_landing_price", labels={"total_weighted_landing_price": "Total Weighted Landing Price"}, height=500, width=1000, template="gridon")
st.plotly_chart(fig2_weekly, use_container_width=True, markers = True)

with st.expander("View Weekly Data of TimeSeries:"):
    st.write(linechart_weekly.T.style.background_gradient(cmap="Blues"))
    csv = linechart_weekly.to_csv(index=False).encode("utf-8")
    st.download_button('Download Weekly Data', data=csv, file_name="Weekly_TimeSeries.csv", mime='text/csv')


# Discount Impact Analysis
st.subheader('Discount Impact Analysis')

# Scatter plot for Discount Amount vs. Unit Selling Price
fig_discount = px.scatter(
    filtered_df,
    x="total_discount_amount",
    y="unit_selling_price",
    color="city_name",  # Optional: to differentiate by city
    title="Discount Amount vs. Unit Selling Price",
    labels={"total_discount_amount": "Total Discount Amount", "unit_selling_price": "Unit Selling Price"},
    template="plotly_white"
)
st.plotly_chart(fig_discount, use_container_width=True, markers = True)

# Calculate average discount and selling price
avg_discount = filtered_df["total_discount_amount"].mean()
avg_selling_price = filtered_df["unit_selling_price"].mean()

st.write(f"**Average Discount Amount:** {avg_discount:.2f}")
st.write(f"**Average Selling Price:** {avg_selling_price:.2f}")

# Additional analysis: how discount impacts sales volume
discount_sales_volume = filtered_df.groupby("total_discount_amount").agg({"procured_quantity": "sum"}).reset_index()

# Create line plot with specified y-axis range
fig_discount_sales = px.line(
    discount_sales_volume,
    x="total_discount_amount",
    y="procured_quantity",
    title="Impact of Discount Amount on Sales Volume",
    labels={"total_discount_amount": "Total Discount Amount", "procured_quantity": "Procured Quantity"},
    template="plotly_white"
)

# Set the y-axis range with a maximum value of 200
fig_discount_sales.update_yaxes(range=[0, 75])

st.plotly_chart(fig_discount_sales, use_container_width=True)


# Calculate profitability
filtered_df["profitability"] = (filtered_df["procured_quantity"] * (filtered_df["unit_selling_price"] - filtered_df["total_discount_amount"]) ) - filtered_df["total_weighted_landing_price"]

# Aggregate profitability by product_id
product_profitability = filtered_df.groupby("product_id").agg({"profitability": "sum"}).reset_index()

# Plot profitability by product
fig_product_profitability = px.bar(
    product_profitability,
    x="product_id",
    y="profitability",
    title="Profitability by Product",
    labels={"profitability": "Total Profitability"},
    template="plotly_white"
)
st.plotly_chart(fig_product_profitability, use_container_width=True)

# Aggregate profitability by city_name
city_profitability = filtered_df.groupby("city_name").agg({"profitability": "sum"}).reset_index()

# Plot profitability by city
fig_city_profitability = px.bar(
    city_profitability,
    x="city_name",
    y="profitability",
    title="Profitability by City",
    labels={"profitability": "Total Profitability"},
    template="plotly_white"
)
st.plotly_chart(fig_city_profitability, use_container_width=True)

# Analyze how discounts impact profitability
discount_profitability = filtered_df.groupby("total_discount_amount").agg({"profitability": "mean"}).reset_index()

# Plot the impact of discount on profitability
fig_discount_profitability = px.line(
    discount_profitability,
    x="total_discount_amount",
    y="profitability",
    title="Impact of Discount Amount on Profitability",
    labels={"total_discount_amount": "Total Discount Amount", "profitability": "Average Profitability"},
    template="plotly_white",
    markers=True
)
st.plotly_chart(fig_discount_profitability, use_container_width=True)