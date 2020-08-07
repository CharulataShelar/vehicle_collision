import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

DATA_URL = ("./data/Motor_Vehicle_Collisions_Crashes.csv")
st.title("Motor Vehicle Collisions in New York City")
st.markdown("This application is a streamlit dashboard that can be used to analyze motor vehicle collisions in NYC")

@st.cache(persist=True)
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows, parse_dates=[['CRASH DATE', 'CRASH TIME']])
    data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data.rename(columns={"crash date_crash time": 'date_time'}, inplace=True)
    return data

data = load_data(10000)
org_data = data.copy()
data.columns = ['date_time', 'borough', 'zip_code', 'latitude', 'longitude', 'location',
                'on_street_name',
                'cross_street_name', 'off_street_name', 'number_of_persons_injured', 'number_of_persons_killed',
                'number_of_pedestrians_injured', 'number_of_pedestrians_killed', 'number_of_cyclist_injured',
                'number_of_cyclist_killed', 'number_of_motorist_injured', 'number_of_motorist_killed',
                'contributing_factor_vehicle_1', 'contributing_factor_vehicle_2', 'contributing_factor_vehicle_3',
                'contributing_factor_vehicle_4', 'contributing_factor_vehicle_5', 'collision_id',
                'vehicle_type_code_1',
                'vehicle_type_code_2', 'vehicle_type_code_3', 'vehicle_type_code_4', 'vehicle_type_code_5']

max_injuries = int(data['number_of_persons_injured'].max())
st.subheader("Where are the most people injured in NYC?")
injured_ppl = st.slider("Number of persons injured in vehicle collisions", 0, max_injuries)

st.map(data.query("number_of_persons_injured >= @injured_ppl")[["latitude", "longitude"]].dropna(how="any"))
st.subheader("How many collisions occur during given time of the day?")
hour = st.slider("Hour to look at", 0, 23)
data = data[data['date_time'].dt.hour == hour]

st.markdown("Vehicle collisions between {}:00 and {}:00".format(hour, (hour+1)%24))
midpoint = (np.average(data['latitude']), np.average(data['longitude']))

st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude" : midpoint[0],
        "longitude": midpoint[1],
        "zoom": 11,
        "pitch":50,
    },
    layers=[
        pdk.Layer(
        "HexagonLayer",
        data=data[['date_time', 'latitude', 'longitude']],
        get_position=['longitude', 'latitude'],
        radius=100,
        extruded=True,
        pickable=True,
        elevation_scale=4,
        elevation_range=[0, 1000],
        ),
    ],
))

st.subheader("Breakdown by minute between {} and {}".format(hour, (hour+1)%24))
filter_data=data[(data['date_time'].dt.hour >= hour) &
                 (data['date_time'].dt.hour < (hour+1))]
hist=np.histogram(filter_data['date_time'].dt.minute, bins=60, range=(0,60))[0]
chart_data =pd.DataFrame({'minute':range(60), 'crashes':hist})
fig= px.bar(chart_data, x='minute', y='crashes', hover_data=['minute', 'crashes'], height=400)
st.write(fig)

st.subheader("Top 5 dangerous streets by affected type")
select = st.selectbox("Affected type of people", ['Pedestrian', 'Cyclists', 'Motorists'])
if select == "Pedestrian":
    st.write(org_data.loc[org_data['number_of_pedestrians_injured'] >= 1, ['on_street_name',
                                                                           'number_of_pedestrians_injured']].
             sort_values(by=['number_of_pedestrians_injured'], ascending=False).dropna(how='any')[:5])
if select == "Cyclists":
    st.write(org_data.loc[org_data['number_of_cyclist_injured'] >= 1, ['on_street_name',
                                                                       'number_of_cyclist_injured']].
             sort_values(by=['number_of_cyclist_injured'], ascending=False).dropna(how='any')[:5])

if select == "Motorists":
    st.write(org_data.loc[org_data['number_of_motorist_injured'] >= 1, ['on_street_name',
                                                                       'number_of_motorist_injured']].
             sort_values(by=['number_of_motorist_injured'], ascending=False).dropna(how='any')[:5])

if st.checkbox("Show Raw Data", False):
    st.subheader("Raw Data")
    st.write(data)

