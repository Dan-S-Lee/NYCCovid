# -*- coding: utf-8 -*-
"""
Created on Wed Apr  8 15:07:35 2020

@author: Daniel Lee
"""

import pandas as pd
import os
from xml.etree import ElementTree as ET

to_extract = ['HOUSEHOLD SIZE', 'HOUSING UNITS', 'RACE', 'SEX BY AGE', 'TOTAL POPULATION']
data_dir = 'data/US Census/cleaned/'
df_dict = {}

for file_name in to_extract:
    df_dict[file_name] = pd.read_csv(data_dir + file_name + '.csv', index_col = 0)

def create_html_string(metrics: dict):
    html = ET.Element('html')
    w3_link = ET.Element('link', 
                         attrib = {'rel' : 'stylesheet', 
                                   'href' : r'https://www.w3schools.com/w3css/4/w3.css'})
    
    font_link = ET.Element('link', 
                           attrib= {'rel' : 'stylesheet', 'href': r'https://fonts.googleapis.com/css2?family=Montserrat:wght@300&display=swap'})
    style = ET.Element('style')
    style.text = r".w3-montserrat {font-family: 'Montserrat', sans-serif;}"
    
    html.append(w3_link)
    html.append(font_link)
    html.append(style)
    
    red_div = ET.Element('div', attrib = {'class': 'w3-container w3-red w3-montserrat'})
    html.append(red_div)
    
    zipcode_div = ET.Element('div', attrib = {'class' : 'w3-bar-item'})
    zipcode_div.text = 'Zipcode:'
    red_div.append(zipcode_div)
    zipvalue_div = ET.Element('div', attrib = {'class' : 'w3-bar-item'})
    bold_div = ET.Element('b')
    bold_div.text = str(metrics['Zip'])
    zipvalue_div.append(bold_div)
    red_div.append(zipvalue_div)
    
    body_keys = [k for k in metrics.keys() if k != 'Zip']
    for k in body_keys:
        new_div = ET.Element('div', attrib = {'class': 'w3-container w3-montserrat'})
        
        name_div = ET.Element('div', attrib = {'class' : 'w3-bar-item'})
        name_div.text = k
        
        value_div = ET.Element('div', attrib = {'class' : 'w3-bar-item'})
        bold_div = ET.Element('b')
        try:
            bold_div.text = f"{metrics[k]:,d}"
        except:
            bold_div.text = '{:,.2f}'.format(metrics[k])
                
        value_div.append(bold_div)
        
        new_div.append(name_div)
        new_div.append(value_div)
        html.append(new_div)
        
    return ET.tostring(html)

def create_table_string(metrics: dict):
    html = ET.Element('html')
    w3_link = ET.Element('link', 
                         attrib = {'rel' : 'stylesheet', 
                                   'href' : r'https://www.w3schools.com/w3css/4/w3.css'})
    
    font_link = ET.Element('link', 
                           attrib= {'rel' : 'stylesheet', 'href': r'https://fonts.googleapis.com/css2?family=Montserrat:wght@300&display=swap'})
    style = ET.Element('style')
    style.text = r".w3-montserrat {font-family: 'Montserrat', sans-serif;}"
    
    html.append(w3_link)
    html.append(font_link)
    html.append(style)        
    
    header = ET.Element('header', attrib = {'class' : 'w3-container w3-red'})
    html.append(header)
    
    container = ET.Element('div', attrib = {'id':'summary','class': 'w3-container w3-montserrat'})
    html.append(container)
    
    table = ET.Element('table', attrib = {'class' : "w3-table w3-bordered w3-montserrat"})
    html.append(table)
    
    body_keys = [k for k in metrics.keys()]
    for k in body_keys:
        if k == "Zip Code:":
            header.text = k + str(metrics[k])
        else:
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
        
    return ET.tostring(html)

def create_tabbed_string(metrics: dict, demos: dict):
    html = ET.Element('html')
    w3_link = ET.Element('link', 
                         attrib = {'rel' : 'stylesheet', 
                                   'href' : r'https://www.w3schools.com/w3css/4/w3.css'})
    
    font_link = ET.Element('link', 
                           attrib= {'rel' : 'stylesheet', 'href': r'https://fonts.googleapis.com/css2?family=Montserrat:wght@300&display=swap'})
    style = ET.Element('style')
    style.text = r".w3-montserrat {font-family: 'Montserrat', sans-serif;}"
    
    html.append(w3_link)
    html.append(font_link)
    html.append(style)
    
    header = ET.Element('header', attrib = {'class' : 'w3-container w3-red'})
    html.append(header)
    h = ET.Element('h3')
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
    
    container = ET.Element('div', attrib = {'id':'Summary','class': 'w3-container table w3-montserrat'})
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
    
    demo_container = ET.Element('div', attrib = {'id':'Demo','class': 'w3-container table w3-montserrat', 'style' : 'display:none'})
    html.append(demo_container)
    
    table = ET.Element('table', attrib = {'class' : "w3-table w3-bordered w3-montserrat"})
    demo_container.append(table)
    
    tab_keys = [k for k in demos.keys()]
    for k in tab_keys:
        new_row = ET.Element('tr')
        name_cell = ET.Element('th')
        name_cell.text = k
        
        new_row.append(name_cell)
        
        value_cell = ET.Element('th')
        if not demos[k] == 'Percentage':
            value_cell.text = str(demos[k]) + '%'
        else:
            value_cell.text = demos[k]
                
        new_row.append(value_cell)
        
        table.append(new_row)
    
    script = ET.Element('script')
    script.text = 'function openTab(tabName) { var i;  var x = document.getElementsByClassName("table");  for (i = 0; i < x.length; i++) {    x[i].style.display = "none";  } document.getElementById(tabName).style.display = "block";  }'
    html.append(script)
    
    return ET.tostring(html)
htmlstring = create_tabbed_string({'Zip Code:': 10009, 'Population': 610}, {'Race': 'Percentage', 'African-American': '50.43'})
print(htmlstring.decode().replace('&lt;', '<'))