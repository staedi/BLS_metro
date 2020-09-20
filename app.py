# pylint: disable=unused-variable
# pylint: disable=anomalous-backslash-in-string

'''
app.py: Frontend runner file for nCovid_19 Streamlit application

Dependencies
data: geojson
data/CPI-W: CPI for Urban Wage Workers
data/Employment Statistics: Current Employment Statistics
modules:
frontend.py: Front-end works
generic.py: Load necessary files (infections, map)
'''

import streamlit as st
import pandas as pd
import generic
import frontend
import pydeck as pdk
import math

file_path = {'data':'data/','sm':'data/Employment Statistics/','cpi':'data/CPI-W/'}

presets_file = {'data':{'geo_data':'cb_2018_us_cbsa_500k.json'},'sm':{'industry':'sm.industry.txt','area':'sm.area.txt','area_map':'area_map.txt','datatype':'sm.data_type.txt','state':'sm.state.txt'},'cpi':{'area':'cw.area.txt','item':'cw.item.txt'}}

sm_dict = {'Total Private':'sm.data.56.TotalPrivate.Current.txt','Goods Producing':'sm.data.57.GoodsProducing.Current.txt','Private Service Providing':'sm.data.59.PrivateSevcProviding.Current.txt','Construction':'sm.data.62.Construction.Current.txt','Manufacturing':'sm.data.63.Manufacturing.Current.txt','Trade, Transportation, and Utilities':'sm.data.66.TradeTransUtilities.Current.txt','Financial Activities':'sm.data.71.FinancialActivities.Current.txt','Professional and Business Services':'sm.data.72.ProfBusSrvc.Current.txt','Education and Health Services':'sm.data.73.EduHealthSrvc.Current.txt','Leisure and Hospitality':'sm.data.74.LeisureAndHospitality.Current.txt','Other Services':'sm.data.75.OtherServices.Current.txt'}

cpi_dict = {2:'cw.data.2.Summaries.txt'}

weights = {0:{'All items':1,'Commodities':0,'Food and beverages':0,'Housing':0,'Medical care':0,'Recreation':0,'Transportation':0},1:{'All items':0,'Commodities':0.1,'Food and beverages':0.2,'Housing':0.55,'Medical care':0,'Recreation':0,'Transportation':0.15},2:{'All items':0,'Commodities':0.25,'Food and beverages':0.2,'Housing':0.25,'Medical care':0,'Recreation':0.2,'Transportation':0.1},3:{'All items':0,'Commodities':0.05,'Food and beverages':0.3,'Housing':0.25,'Medical care':0.3,'Recreation':0,'Transportation':0.1}}

################################################################
# Header and preprocessing

# Set Title
st.title('US metro-areas princing power comparison')

# Preset data load for sidebar display
# update_status = st.markdown("Loading infections data...")
# supersector
sm_presets = generic.read_dataset(file_path['sm'],presets_file['sm'])
cpi_presets = generic.read_dataset(file_path['cpi'],presets_file['cpi'])
# update_status.markdown('Load complete!')

################################################################
# Sidebar section (Supersector, Region and Year of interest)
sel_sector, sel_year, sel_limit, sel_focus  = frontend.display_sidebar(sm_presets)

################################################################
# Main section
if sel_sector != 'Choose one':
    ## Preprocessing steps
    # Employment data
    employments = generic.preprocess_data('sm',file_path['sm'],sm_dict[sel_sector],sel_year,sm_presets)

    # CPI data
    inflations = generic.preprocess_data('cpi',file_path['cpi'],cpi_dict[2],sel_year,cpi_presets)

    # Merge two datasets
    merged_data = generic.merge_dataset('merge',employments,inflations)

    # Calculating employment ranks
    merged_data = generic.calc_ranks(merged_data,sel_limit)

    # Calculate weighted Price Indexes
    merged_data = generic.calc_CPI(merged_data,weights[int(sel_focus[0])])

    # Simplify area name
    merged_data = generic.simplify_area(merged_data)

    # Display chart and map
    frontend.show_chart(merged_data,weights[int(sel_focus[0])])
    frontend.show_map(merged_data,file_path['data']+presets_file['data']['geo_data'])


# Caption for credits
st.subheader('Credits')
data_source = 'US Bureau of Labor Statistics'
st.write('Data source: ' + data_source)
st.write('Map shapedata: Natural Earth')
st.write('Map provider: Mapbox, OpenStreetMap')
