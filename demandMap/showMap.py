import pandas as pd
import numpy as np
import folium
from ipywidgets import interact, Dropdown
from IPython.display import display

# (Previous code for data generation remains the same)

# Function to create a map based on the selected product
def create_map(product):
    # Filter data for the selected product
    product_data = df_trend[df_trend['product'] == product]
    
    # Create a folium map centered around India
    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)
    
    # Add the demand data with trends to the map
    for _, row in product_data.iterrows():
        if row['percentage_change'] > 0:
            icon = folium.Icon(color="green", icon="arrow-up")
            trend_color = "green"
            trend_arrow = "&#9650;"  # Unicode up arrow
        else:
            icon = folium.Icon(color="red", icon="arrow-down")
            trend_color = "red"
            trend_arrow = "&#9660;"  # Unicode down arrow
        
        # Create a custom HTML for the popup
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; padding: 10px; background-color: #f0f0f0; border-radius: 5px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
            <h3 style="margin: 0 0 10px 0; color: #333;">{row['city']}</h3>
            <p style="margin: 5px 0; font-size: 14px;"><strong>Product:</strong> {product}</p>
            <p style="margin: 5px 0; font-size: 14px;"><strong>Demand:</strong> {row['demand']} units</p>
            <p style="margin: 5px 0; font-size: 14px;">
                <strong>Expected change:</strong> 
                <span style="color: {trend_color}; font-weight: bold;">
                    {trend_arrow} {row['percentage_change']}%
                </span>
            </p>
        </div>
        """
        
        folium.Marker(
            location=[row['lat'], row['lon']],
            icon=icon,
            popup=folium.Popup(popup_html, max_width=300)
        ).add_to(m)
    
    # Display the map
    return m

# Create a dropdown widget for product selection
product_dropdown = Dropdown(
    options=products,
    value=products[0],
    description='Product:',
    disabled=False,
)

# Use interact to update the map based on the selected product
interact(create_map, product=product_dropdown)