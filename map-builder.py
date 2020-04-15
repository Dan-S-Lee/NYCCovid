# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 16:02:41 2020

@author: Daniel Lee
"""

import pandas as pd
import folium
from folium import IFrame
import json
import folium.features as features
from xml.etree import ElementTree as ET
from bs4 import BeautifulSoup
import math

zip_data = pd.read_csv('data/tests-by-zcta.csv')
zip_data.rename(columns = {'MODZCTA': 'zipcode', 'zcta_cum.perc_pos': '%_positive'}, inplace = True)
zip_geo = f'data/zipcode_polygons.json'

to_extract = ['HOUSEHOLD SIZE', 'HOUSING UNITS', 'RACE', 'SEX BY AGE', 'TOTAL POPULATION', 'HOUSEHOLD SIZE Percentage', 'RACE Percentage', 'SEX BY AGE Percentage' ]
data_dir = 'data/US Census/cleaned/'
df_dict = {}

for file_name in to_extract:
    df_dict[file_name] = pd.read_csv(data_dir + file_name + '.csv', index_col = 'MODZCTA')

def create_tabbed_string(metrics: dict, demos: dict):
    html = ET.Element('html')
    w3_link = ET.Element('link', 
                         attrib = {'rel' : 'stylesheet', 
                                   'href' : r'https://www.w3schools.com/w3css/4/w3.css'})
    
    font_link = ET.Element('link', 
                           attrib= {'rel' : 'stylesheet', 'href': r'https://fonts.googleapis.com/css2?family=Montserrat:wght@300&display=swap'})
    style = ET.Element('style')
    style.text = r".w3-montserrat {font-family: 'Montserrat', sans-serif;} header {border-radius: 12px 12px 0px 0px}"
    
    html.append(w3_link)
    html.append(font_link)
    html.append(style)
    
    header = ET.Element('header', attrib = {'class' : 'w3-container w3-red w3-montserrat'})
    html.append(header)
    h = ET.Element('h4')
    h.text = 'Zip Code:' + ' ' + str(metrics['Zip Code:'])
    
    header.append(h)
    
    '''create buttons'''
    
    button_div = ET.Element('div', attrib = {'class': 'w3-bar w3-black'})
    html.append(button_div)
    
    button = ET.Element('button', attrib = {'class': 'w3-bar-item w3-button', 'onclick':"openTab('Summary')"})
    button.text = 'Summary'
    button_div.append(button)
    
    button = ET.Element('button', attrib = {'class': 'w3-bar-item w3-button', 'onclick':"openTab('Demo')"})
    button.text = 'Demographics'
    button_div.append(button)
    
    '''container for the summary tab'''
    
    container = ET.Element('div', attrib = {'id':'Summary','class': 'w3-container table w3-montserrat w3-padding-0'})
    html.append(container)
    
    table = ET.Element('table', attrib = {'class' : "w3-table w3-bordered w3-montserrat"})
    container.append(table)
    
    body_keys = [k for k in metrics.keys() if k != 'Zip Code:']
    for k in body_keys:
        new_row = ET.Element('tr')
        name_cell = ET.Element('th')
        name_cell.text = k
        
        new_row.append(name_cell)
        
        value_cell = ET.Element('th')
        if k != 'Zip Code:':
            try:
                value_cell.text = f"{metrics[k]:,d}"
            except:
                value_cell.text = '{:,.2f}'.format(metrics[k])
        else:
            value_cell.text = str(metrics[k])
                
        new_row.append(value_cell)
        
        table.append(new_row)
        
    '''container for demographics tab'''
    
    demo_container = ET.Element('div', attrib = {'id':'Demo','class': 'w3-container table w3-montserrat w3-padding-0', 'style' : 'display:none'})
    html.append(demo_container)
    
    table = ET.Element('table', attrib = {'class' : "w3-table w3-bordered w3-montserrat w3-padding-0"})
    demo_container.append(table)
    
    tab_keys = [k for k in demos.keys()]
    for k in tab_keys:
        new_row = ET.Element('tr')
        if k == 'Race':
            name_cell = ET.Element('th')
            value_cell = ET.Element('th')
        else:
            name_cell = ET.Element('td')
            value_cell = ET.Element('td')
        name_cell.text = k
        
        new_row.append(name_cell)
        
        if not demos[k] == 'Percentage':
            value_cell.text = str(demos[k])
        else:
            value_cell.text = demos[k]
                
        new_row.append(value_cell)
        
        table.append(new_row)
    
    script = ET.Element('script')
    script.text = 'function openTab(tabName) { var i;  var x = document.getElementsByClassName("table");  for (i = 0; i < x.length; i++) {    x[i].style.display = "none";  } document.getElementById(tabName).style.display = "block";  }'
    html.append(script)
    
    return ET.tostring(html)

def metrics_organizer(df_, categories, ind, val, symbol):
    '''
    pulls dataframe values based on categories at a given index
    
    inputs: 
    df - Dataframe
    categories - dictionary used to rename column while preserving dataframe naming scheme
    ind - row index of df
    val - actual row of df at given ind
    symbol - symbol to append at each value
    
    returns:
    metrics - dictionary to feed into string-generator
    '''
    metrics = {}
    for key in categories.keys():
        metrics[key] = str(df_.loc[int(ind)][categories[key]]) + ' '+ symbol
    return metrics
m = folium.Map(location = [40.7128, -74.0060], zoom_start = 12)
zip_geo = f'data/zipcode_polygons.json'
style = {'fillColor': '#00000000', 'lineColor': '#00FFFFFF'}
zipcode_layer = folium.GeoJson(zip_geo, style_function = lambda x: style).add_to(m)

df = df_dict['TOTAL POPULATION']
for i, v in df.iterrows():
    
    metrics_dict = {}
    metrics_dict['Zip Code:'] = df.loc[i]['Zip']
    
    metrics_dict['Tested Positive:'] = df.loc[i]['Positive']
    metrics_dict['Per 1,000:'] = round(df.loc[i]['Positive'] / df_dict['TOTAL POPULATION'].loc[i]['Total_TOTAL POPULATION'] * 1000,2)
 
    metrics_dict['Population:'] = df_dict['TOTAL POPULATION'].loc[i]['Total_TOTAL POPULATION']
    
    demo_renaming = {'White':'White alone', 
                     'African American': 'Black or African American alone', 
                     'Native American': 'American Indian and Alaska Native alone', 
                     'Asian': 'Asian alone',
                     'Pacific Islander': 'Native Hawaiian and Other Pacific Islander alone',
                     'Other Races': 'Some Other Race alone',
                     'Two or More Races': 'Two or More Races'}
    
    demo_dict = {'Race' : 'Percentage'}
    demo_dict.update(metrics_organizer(df_dict['RACE Percentage'], demo_renaming, i, v, '%'))
    
    popup_text = create_tabbed_string(metrics_dict, demo_dict).decode().replace('&lt;', '<')
    iframe = IFrame(html=popup_text, width = '100%', height = 200)
    popup = folium.Popup(iframe, max_width = 300, min_width = 300)
    
    tooltip_text = '<b> ZipCode: </b>' + df.loc[i]['Zip'].astype(str) + ' <br/> Click for more info.'
    tooltip = folium.Tooltip(tooltip_text)
    
    icon = features.DivIcon(icon_size = (50,50), icon_anchor = (0,0), html = '<b>' + df.loc[i]['Zip'].astype(str) + '</b>')
    
    folium.Circle(tuple(df.loc[i][['Latitude', 'Longitude']]), radius = float(min(math.log(metrics_dict['Per 1,000:']) * 150, 1000)), tooltip = tooltip, popup= popup, fill = True, fill_color = '#FF0000', color = '#FF0000', icon = icon).add_to(m)

m.save('master.html')
soup = BeautifulSoup(open("master.html"))
links = soup.findAll('link')
for link in links:
    link['href'] = link['href'].replace(r"https://cdn.jsdelivr.net/npm/leaflet@1.5.1/dist/leaflet.css", "https://sleepingtuna.github.io/NYCCovid-19Map.github.io/docs/css/leaflet.css")
with open("new_master.html", "w") as file:
    file.write(str(soup))