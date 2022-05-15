import pandas as pd
import sqlite3 
import geopy.distance
import folium
from streamlit_folium import st_folium, folium_static
import altair as alt
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
import datetime
from streamlit_bokeh_events import streamlit_bokeh_events
import geocoder
import logging


st.set_page_config(layout="wide")
st.title('實名制快篩地圖')
#st.header('快篩地圖')
container = st.empty()
loc_button = Button(label="Get Location")
loc_button.js_on_event("button_click", CustomJS(code="""
    navigator.geolocation.getCurrentPosition(
        (loc) => {
            document.dispatchEvent(new CustomEvent("GET_LOCATION", {detail: {lat: loc.coords.latitude, lon: loc.coords.longitude}}))
        }
    )
    """))
result = streamlit_bokeh_events(
    loc_button,
    events="GET_LOCATION",
    key="get_location",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0)

@st.cache(allow_output_mutation=True)
def get_pharm_list(date):
    conn = sqlite3.connect("./rapidtest.sqlite")
    df = pd.read_sql("select * from rapidtest order by Time DESC limit 80000",conn, )
    conn.close()
    df.Time = pd.to_datetime(df.Time)
    pharm = df.groupby("Code").last().reset_index()
    return pharm

def get_map(MeGeo):
    pharm_list_0 = get_pharm_list(f"{datetime.datetime.now():%Y%m%d %H}")
    pharm_list = pharm_list_0.copy(deep=True)
    pharm_list['Distance'] = pharm_list.apply(lambda x: geopy.distance.distance((x.Latitude,x.Longitude), (MeGeo['lat'],MeGeo['lon'])).km, axis=1)
    conn = sqlite3.connect("./rapidtest.sqlite")
    df = pd.read_sql(f"select * from rapidtest where Code in {tuple(pharm_list[pharm_list.Distance<5].Code.unique())} order by Time DESC limit 8000",conn, )
    conn.close()
    df.Time = pd.to_datetime(df.Time)
    xdf = df.groupby(['Code','Name','Addr','Tel',"Latitude","Longitude",'Note','Time']).Stock.first().unstack().interpolate(method='linear', axis=1, limit=2, inplace=False, limit_direction='forward', limit_area='inside', downcast=None,).fillna(0).astype(int)
    sdf = xdf.iloc[:,-1:]
    ts = xdf.iloc[:,-36:].stack()
    print(datetime.datetime.now(), MeGeo, flush=True)
    print('df',len(df), 'sdf',len(sdf), 'ts',len(ts), flush=True)
    ts = ts.reset_index()
    sdf= sdf.reset_index()
    ts.columns = ['Code', 'Name', 'Addr', 'Tel', 'Latitude', 'Longitude', 'Note', 'Time',"Stock"]
    map_f = folium.Map(location=(MeGeo['lat'],MeGeo['lon']), zoom_start=15, )

    for r in sdf.itertuples():
        chart = alt.Chart(ts[ts.Code==r.Code],).mark_line().encode(x='Time',y='Stock').properties(title=r.Name, height=50)
        Pop = folium.Popup()
        Pop.add_child(folium.VegaLite(chart, height=30))
        
        folium.Marker(location=(r.Latitude, r.Longitude),
        tooltip=f"<b>{r.Name}</b><br/>{r.Addr}<br/>{r.Tel}<br/>庫存: {r[-1]}<br/>{sdf.columns[-1]}<br/>{r.Note[:45]}",
        popup=Pop,
        #<br/>{r.Addr}<br/>庫存:{r[-1]}<br/>{r.Note}<br/>{sdf.columns[-1]}",
        icon=folium.Icon(color="red" if r[-1]==0 else "blue", icon="fa-plus-square", prefix='fa') 
        #icon=folium.Icon(color="red" if r[-1]==0 else "blue", icon="capsules", prefix='fa') 
        ).add_to(map_f)
    return map_f

if result!=None:
    MeGeo = result['GET_LOCATION']
    st.write(f"GeoLocation: {MeGeo['lat']}, {MeGeo['lon']}")
    #g = geocoder.google( [MeGeo['lat'],MeGeo['lon']] , method='reverse')
    #st.write(g.json)
    RRMAP = get_map(MeGeo)
    #st_folium(folium.Map(location=(MeGeo['lat'],MeGeo['lon'])))
    folium_static(RRMAP, width=800)
