# pylint: disable=unused-variable
# pylint: disable=anomalous-backslash-in-string

# import generic
import pandas as pd
import numpy as np
from datetime import datetime
import math
import altair as alt
import pydeck as pdk
import streamlit as st

# Module to display sidebar
def display_sidebar(data):
    sel_sector, sel_year, sel_limit, sel_case = None, None, None, None

    st.sidebar.header('Choose selections below')

    # 1) Choose an industry sector to analyze
    st.sidebar.markdown('Choose a job category')

    sector = sorted(data['industry']['industry_name'].unique())
    sector = list(['Choose one']+sector)
    sel_sector = st.sidebar.selectbox('Sector',sector)

    # # 2) Choose region category to analyze
    # # st.text([val[1] for val in read_columns.values()])
    # st.sidebar.markdown('Choose a region basis to compare between (e.g., Metro-level)')
    # sel_region = st.sidebar.selectbox('Industry sector',['Metro-level','State-level','Division-level'])

    # 2) Choose base and target years to analyze
    # st.text([val[1] for val in read_columns.values()])
    st.sidebar.markdown('Choose an year to compare')
    base_year = 2010
    latest_year = datetime.now().year-1

    sel_year = st.sidebar.slider('Target year',min_value=base_year,max_value=latest_year,value=latest_year)

    # 3) Choose limit ranges of regions
    st.sidebar.markdown('Choose a threshold for selections')
    sel_limit = st.sidebar.slider('Selections',min_value=5,max_value=50,step=5)

    # 4) Choose spending scenario
    st.sidebar.markdown('Choose a spending focus')

    focus = list(['0: Overall','1: Housing','2: Energy','3: Medical'])
    sel_focus = st.sidebar.selectbox('CPI category',focus)

    return sel_sector, sel_year, sel_limit, sel_focus

# Load mapdata for selected region
def show_map(data,geo_path,stat=None):
    st.subheader('Color maps')
    st.write('Color depths: Pricing Power [100+: Affordable]')
    st.write('Elevation: Employment Strengths [Max: 100]')

    # Load in the JSON data
    src_geo = geo_path
    json_geo = pd.read_json(src_geo)
    df = pd.DataFrame()

    # Custom color scale (colorbrewer2.org -> Sequential Single-Hue)
    breaks = [.0, .25, .5, .75, 1]
    color_range = [
        # 5-class Diverging
        [202,0,32],
        [244,165,130],
        [247,247,247],
        [146,197,222],
        [5,113,176],
    ]

    def color_scale(val):
        for i, b in enumerate(breaks):
            if val <= b:
                return color_range[i]
        return color_range[i]

    def elevation_scale(val,scale):
        for i, b in enumerate(breaks):
            if val <= b:
                return i*scale


    def set_nan(val):
        if np.isnan(val):
            return -1
        else:
            return val


    # Parse the geometry out in Pandas
    df["coordinates"] = json_geo["features"].apply(lambda row: row["geometry"]["coordinates"])
    df["name"] = json_geo["features"].apply(lambda row: row["properties"]["name"])

    stat = {'rank':'Rank','All Employees':'All Employees (1K)','Avg Hourly Wages':'Avg Hourly Wages','eWage':'Pricing Power','score':'Employment Strengths','eCPI':'Price Index'}

    # stat = {'eWage':'Pricing Power','score':'Employment Strengths','eCPI':'Price Index','All Employees':'All Employees (1K)','Avg Hourly Wages':'Avg Hourly Wages (USD)'}

    stat_text = list(stat.values())[0]
    stat_keys = list(stat.keys())

    data = data[['year','cbsa_area','Metro area']+stat_keys]

    df = pd.merge(df,data,how='inner',left_on=['name'],right_on=['cbsa_area'])
    zoom = 3

    df['fill_color'] = ((df[stat_keys[3]]-df[stat_keys[3]].min())/(df[stat_keys[3]].max()-df[stat_keys[3]].min())).replace(np.nan,0).apply(color_scale)
    # df['elevation'] = ((df[stat_keys[1]].max()-df[stat_keys[1]]+1)/df[stat_keys[1]].max()).replace(np.nan,0).apply(lambda x:elevation_scale(x,2.5e4))
    df['elevation'] = (df[stat_keys[4]]/df[stat_keys[4]].max()).replace(np.nan,0).apply(lambda x:elevation_scale(x,2.5e4))


    df['param'] = stat_text
    df.rename(columns={stat_keys[0]:'stat_0',stat_keys[1]:'stat_1',stat_keys[2]:'stat_2',stat_keys[3]:'stat_3',stat_keys[4]:'stat_4',stat_keys[5]:'stat_5'},inplace=True)

    # st.write(df)

    view_state = pdk.ViewState(
        latitude = 40,
        longitude = -100,
        # bearings=15,
        # pitch=45,
        zoom=zoom)

    polygon_layer = pdk.Layer(
        "PolygonLayer",
        df,
        id="geojson",
        opacity=0.2,
        stroked=False,
        get_polygon="coordinates",
        filled=True,
        get_elevation='elevation',
        # elevation_scale=1e5,
        # elevation_range=[0,100],
        extruded=True,
        # wireframe=True,
        get_fill_color= 'fill_color',
        get_line_color=[255, 255, 255],
        auto_highlight=True,
        pickable=True,
    )

    tooltip = {"html": "<b>Metro Area:</b> {Metro area} <br /><b>Employment Ranks:</b> {stat_0} <br /><b>All Employees (1K):</b> {stat_1} <br /><b>Avg Hourly Wages (USD):</b> {stat_2} <br /><b>Pricing Power:</b> {stat_3}"}


    r = pdk.Deck(
        layers=[polygon_layer],
        initial_view_state=view_state,
        tooltip=tooltip,
        )

    # return r
    st.pydeck_chart(r, use_container_width=True)


def show_chart(data,items):
    stat = {'rank':'Rank','All Employees':'All Employees (1K)','Avg Hourly Wages':'Avg Hourly Wages','eWage':'Pricing Power','score':'Employment Strengths','eCPI':'Price Index'}

    stat_text = list(stat.values())
    stat_keys = list(stat.keys())
    items = [key for key, value in items.items() if value!=0]

    data = data[['year','cbsa_area','Metro area']+stat_keys+items]

    st.subheader('Employment strengths')

    # Employment strengths scatter
    scatter = (alt.Chart(data)
        .mark_circle()
        .encode(
            x=alt.X(stat_keys[1],title=stat_text[1]),
            y=alt.Y(stat_keys[2],title=stat_text[2]),
            size=alt.Size(stat_keys[4],legend=None),
            tooltip=[alt.Tooltip('Metro area'),alt.Tooltip(stat_keys[0],title=stat_text[0]),alt.Tooltip(stat_keys[1],title=stat_text[1]),alt.Tooltip(stat_keys[2],title=stat_text[2],format='$')]
        )
    )

    st.altair_chart(scatter,use_container_width=True)

    st.subheader('Price Index')

    # Price Index stacked_bar
    stacked_cpi = (alt.Chart(data)
        .transform_fold(items,['Item','Price Index'])
        .mark_bar()
        .encode(
            x=alt.X('Price Index:Q'),
            y=alt.Y('Metro area:N',sort=alt.EncodingSortField(field=stat_keys[5],order='descending')),
            color=alt.Color('Item:N'),
            tooltip=[alt.Tooltip('Metro area'),alt.Tooltip('Item:N'),alt.Tooltip('Price Index:Q'),alt.Tooltip(stat_keys[5],title=stat_text[5])]
        )
    )

    st.altair_chart(stacked_cpi,use_container_width=True)

    st.subheader('Pricing Power')

    # Employment strengths scatter
    stacked_pp = (alt.Chart(data)
        .mark_bar()
        .encode(
            x=alt.X(stat_keys[3],title=stat_text[3]),
            y=alt.Y('Metro area:N',sort=alt.EncodingSortField(field=stat_keys[3],order='descending')),
            tooltip=[alt.Tooltip('Metro area'),alt.Tooltip(stat_keys[2],title=stat_text[2]),alt.Tooltip(stat_keys[5],title=stat_text[5]),alt.Tooltip(stat_keys[3],title=stat_text[3])]
        )
    )

    st.altair_chart(stacked_pp,use_container_width=True)
