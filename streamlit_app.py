#All libraries used
import streamlit as st
import pandas as pd
import numpy as np
import requests
import seaborn as sns
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os
import psycopg2 as psql

#Getting the details from secrets
load_dotenv()
sql_user = st.secrets['sql_user']
sql_pass = st.secrets['sql_pass']
my_host = st.secrets['host']

#Connect to the database
conn = psql.connect(
    database="pagila",
    user=sql_user,
    password=sql_pass,
    host=my_host,
    port=5432
)
cur = conn.cursor()

#Title
st.title("UK Weather App")
st.write("Select a city from the sidebar to get its weather details!")

#Sidebar for choosing a city
cities = ['London', 'Manchester', 'Birmingham', 'Liverpool', 'Leeds', 'Nottingham', 'Sheffield', 'Cardiff', 'Glasgow']
chosen_city = st.sidebar.selectbox('Choose a city', cities)

st.header(chosen_city)

#Selecting all data from the current weather db
select_current_query = "SELECT * FROM student.de10_dd_captest_current ORDER BY date DESC"
cur.execute(select_current_query)
rows = cur.fetchall()
#st.write(rows)

# Loop through the rows and search for the value
for row in rows:
    if row[1] == chosen_city.lower():
        #st.write("Found the value:", row)
        break

#Assign the variables (and split the date column into date and time)
date_time = row[0]
date_part = date_time.split()[0]
time_part = date_time.split()[1]
condition_img = f"https:{row[4]}"

#Variable for displaying the temp and condition in a box
current_weather_info = f'''
Temperature: {row[2]}°C
\nCondition: {row[3]}
'''

#The format for the page
col1, col2 = st.columns(2)
with col1:
    st.subheader("Current Weather:")
    st.write(f'''Date: {date_part}
             \n Time: {time_part}''')
    
with col2:
    st.info(current_weather_info)
    st.image(condition_img) 
    with st.expander("Extra details on the current weather"):
        st.write(f"""Humidity: {row[5]}%
                  \nCloud Cover: {row[6]}%
                 \nWind Speed: {row[7]}mph
                 \nPrecipitation: {row[8]}mm""")   

#Select data from the full forecast table
select_fc_query = f"""
    SELECT date,city,hr0_temp,hr1_temp,hr2_temp,hr3_temp,hr4_temp,hr5_temp,hr6_temp,hr7_temp,hr8_temp,hr9_temp,hr10_temp,hr11_temp,hr12_temp,hr13_temp,hr14_temp,hr15_temp,hr16_temp,hr17_temp,hr18_temp,hr19_temp,hr20_temp,hr21_temp,hr22_temp,hr23_temp
    FROM student.de10_dd_captest_full_forecast
    WHERE city = %s
    ORDER BY date DESC
    LIMIT 1
"""

# Execute the query with the specific value as a parameter
cur = conn.cursor()
cur.execute(select_fc_query, (chosen_city.lower(),))
row = cur.fetchone()  # Fetch the first (and only) row from the result set

#Variables and data for the graph
times = ['00:00','01:00','02:00','03:00','04:00','05:00','06:00','07:00','08:00','09:00','10:00','11:00','12:00','13:00','14:00','15:00','16:00','17:00','18:00','19:00','20:00','21:00','22:00','23:00']
temperatures_list = row[-24:]
forecast_temperatures = pd.DataFrame({'Time': times, 'Temperature': temperatures_list})

sns.set(style='whitegrid', palette='pastel', context='talk')

# Create a figure and axis
plt.figure(figsize=(12, 7))

# Create the line plot with enhancements
sns.lineplot(
    x='Time', 
    y='Temperature', 
    data=forecast_temperatures, 
    marker='o', 
    linestyle='-', 
    linewidth=2.5, 
    markersize=8, 
    color='b',
    alpha=0.7
)

# Add a title and axis labels
plt.title("Today's Temperature Variation", fontsize=16, weight='bold')
plt.xlabel('Time', fontsize=14)
plt.ylabel('Temperature (°C)', fontsize=14)

# Customize the grid and ticks
plt.grid(True, linestyle='--', alpha=0.6)
plt.xticks(rotation=45, fontsize=12)
plt.yticks(fontsize=12)

# Remove the top and right spines for a cleaner look
sns.despine()

# Ensure layout is tight
plt.tight_layout()

# Save the figure
plt.savefig('temperature_fc.png', dpi=300)
#plt.show()
# Close the plot
plt.close()

#Creating Accuracy DF and Plot
cursor = conn.cursor()
#Data from db about the actual temp
select_yesterday_real_query = """
    SELECT hr0_temp,hr1_temp,hr2_temp,hr3_temp,hr4_temp,hr5_temp,hr6_temp,hr7_temp,hr8_temp,hr9_temp,hr10_temp,hr11_temp,hr12_temp,hr13_temp,hr14_temp,hr15_temp,hr16_temp,hr17_temp,hr18_temp,hr19_temp,hr20_temp,hr21_temp,hr22_temp,hr23_temp
    FROM student.de10_dd_captest_full_forecast
    WHERE city = %s
    AND RIGHT(date, 5) = '23:00'
    ORDER BY date DESC
    LIMIT 2;
    """
cursor.execute(select_yesterday_real_query, (chosen_city.lower(),))
real = cursor.fetchall()

cursor = conn.cursor()
#Data from db about the predicted temp
select_yesterday_fc_query = """
    SELECT hr0_temp,hr1_temp,hr2_temp,hr3_temp,hr4_temp,hr5_temp,hr6_temp,hr7_temp,hr8_temp,hr9_temp,hr10_temp,hr11_temp,hr12_temp,hr13_temp,hr14_temp,hr15_temp,hr16_temp,hr17_temp,hr18_temp,hr19_temp,hr20_temp,hr21_temp,hr22_temp,hr23_temp
    FROM student.de10_dd_captest_full_forecast
    WHERE city = %s
    AND RIGHT(date, 5) = '00:00'
    ORDER BY date DESC
    LIMIT 2;
    """

cursor.execute(select_yesterday_fc_query, (chosen_city.lower(),))
yesterday_fc = cursor.fetchall()

#Creating DF for this data
accuracy = pd.DataFrame({
    'Forecasted': yesterday_fc[1],
    'Real': real[0]
})
accuracy['Time'] = times

# Plotting the data
plt.figure(figsize=(12, 8))

# Custom color palette
palette = sns.color_palette("coolwarm", 2)

# Plotting with markers and custom styles
sns.lineplot(data=accuracy, x='Time', y='Forecasted', marker='o', label='Forecasted Temperature', color=palette[0], linestyle='-', linewidth=2.5)
sns.lineplot(data=accuracy, x='Time', y='Real', marker='s', label='Actual Temperature', color=palette[1], linestyle='--', linewidth=2.5)

# Enhancing the plot
plt.title('Temperature Forecasted vs Actual Temperature', fontsize=16, fontweight='bold')
plt.xlabel('Time', fontsize=14)
plt.ylabel('Temperature (°C)', fontsize=14)
plt.grid(True, linestyle='--', alpha=0.6)
plt.xticks(rotation=45, fontsize=12)
plt.yticks(fontsize=12)
sns.despine()
plt.legend(title='Key', title_fontsize='13', fontsize='12')
plt.tight_layout()

# Save and show the plot
plt.savefig('accuracy.png')
#plt.show()


#The tabs for how the graphs created are displayed
tab1, tab2 = st.tabs(["Today's Temperature Variation", "Accuracy of Yesterday's forecast"])
tab1.image("temperature_fc.png")
tab2.image("accuracy.png")
