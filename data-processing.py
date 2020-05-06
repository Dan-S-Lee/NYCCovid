# -*- coding: utf-8 -*-
"""
Created on Wed Apr  8 10:19:37 2020

@author: Daniel Lee
"""

import pandas as pd
import json
import os
import numpy as np

'''
Gets coordinates of every NYC zipcode
'''
nyc_json =  json.loads(open('data/zipcode_polygons.json','r').read())
zipcode_set = set()
for feature in nyc_json['features']:
    zip_code = feature['properties']['postalCode']
    zipcode_set.add(zip_code)

zc_df = pd.read_csv('data/ny-zip-code-latitude-and-longitude.csv', sep = ';')

zc_df = zc_df[zc_df.Zip.isin(zipcode_set)]
zc_df.drop(columns = ['Timezone', 'Daylight savings time flag'], inplace = True)
zc_df.to_csv('data/nyc_zip_codes.csv')

'''
Rename files based on 2nd line of data
'''

data_dir = 'data/US Census/raw'
titles = [os.path.join(data_dir,f) for f in os.listdir(data_dir) if 'table_title' in f]
names = [open(f, 'r').readlines()[1] for f in titles]
datasets = [os.path.join(data_dir,f) for f in os.listdir(data_dir) if 'data' in f]
title_dict = {open(f, 'r').readlines()[0]: open(f, 'r').readlines()[1] for f in titles}

for table in datasets:
    for k in title_dict.keys():
        if k.strip() + '_data' in table:
            temp_df = pd.read_csv(table)
            temp_df.to_csv('data/US Census/renamed/' + title_dict[k].strip() + '.csv')

new_dir = 'data/US Census/renamed'
datasets_renamed = [os.path.join(new_dir,f) for f in os.listdir(new_dir)]


'''
Get coronavirus data from NYC-Health
'''


corona_data = pd.read_csv('https://raw.githubusercontent.com/nychealth/coronavirus-data/master/tests-by-zcta.csv')
corona_data['Zip'] = corona_data['MODZCTA'].fillna(0).astype(int)

data = corona_data.merge(zc_df, how = 'inner', on = 'Zip')

#data.to_csv('data/coronavirus_full_data.csv')
#data['popup'] = '<div class="w3-bar w3-border w3-green"> <div class = "w3-bar-item"> <b>Zipcode: </b>' + data['Zip'].astype(str) + '</div> </div>' + '<br/> <b>Tested Positive: </b>' + data['Positive'].astype(str)

#demo_df = pd.read_csv('data/Demographic_Statistics_By_Zip_Code.csv')

'''
Extract and clean key demographic figures such as Race and Household Size
'''

to_extract = ['HOUSEHOLD SIZE', 'HOUSING UNITS', 'RACE', 'SEX BY AGE', 'TOTAL POPULATION', 'SELECTED ECONOMIC CHARACTERISTICS']

data_dir = 'data/US Census/renamed'

df_dict = {}
for file in to_extract:
    df = pd.read_csv(os.path.join(data_dir,file + '.csv'))
    df.columns = df.iloc[0].values.tolist()
    df = df[1:]
    df = df.loc[:, ~(df == '(X)').all()]
    df['Zip'] = df['Geographic Area Name'].apply(lambda x: x.split()[1].replace(',', '')).astype(int)
    new_df = data.merge(df, how = 'inner', on = 'Zip', suffixes = ('', '_' + file))
    df_dict[file] = new_df
    
    new_col_list = [str(col).replace('Total!!', '') for col in new_df.columns.values]
    new_df.columns = new_col_list
    
    new_df.to_csv('data/US Census/cleaned/' + file + '.csv')

percentage_dict = {}
percentage_list = ['RACE', 'SEX BY AGE', 'HOUSEHOLD SIZE']
for name in percentage_list:
    df = df_dict[name].copy()
    
    for col in df.columns.values.tolist():
        if col == 'Total_' + name:
            ind = df.columns.values.tolist().index(col)
    metrics_list = df.columns.values.tolist()[ind:]
    for i in range(1, len(metrics_list)):
        df[metrics_list[i]] = round(df[metrics_list[i]].astype(int) / df['Total_' + name].astype(int) * 100, 2)
    percentage_dict[name] = df
    df.to_csv('data/US Census/cleaned/' + name + ' Percentage.csv')
    
household_df = pd.read_csv('data/US Census/cleaned/HOUSEHOLD SIZE Percentage.csv')
sizes_list = household_df.columns.values.tolist()[-7:]
n_list = list(range(1,8))
household_df['Weighted Avg'] = household_df[sizes_list].apply(lambda x: np.dot(x, n_list)/100, axis = 1)
household_df.to_csv('data/US Census/cleaned/HOUSEHOLD SIZE Percentage.csv')

original_cols = list(data.columns.values)
new_cols = []
renamed_cols = []
for col in df_dict['SELECTED ECONOMIC CHARACTERISTICS'].columns.values:
    if col in original_cols:
        renamed_cols.append(col)
        new_cols.append(col)
    elif 'Median' in col and 'Margin of Error' not in col:
        df_dict['SELECTED ECONOMIC CHARACTERISTICS'][col] = df_dict['SELECTED ECONOMIC CHARACTERISTICS'][col].str.replace('+', '')
        df_dict['SELECTED ECONOMIC CHARACTERISTICS'][col] = df_dict['SELECTED ECONOMIC CHARACTERISTICS'][col].str.replace(',', '')
        df_dict['SELECTED ECONOMIC CHARACTERISTICS'][col] = df_dict['SELECTED ECONOMIC CHARACTERISTICS'][col].astype(int)
        new_cols.append(col)
        renamed_cols.append(col.split('!!')[-1])
    #elif 'HEALTH' in col and 'Margin of Error' not in col:
        #new_cols.append(col)

median_df = df_dict['SELECTED ECONOMIC CHARACTERISTICS'][new_cols].copy()
median_df.columns = renamed_cols
median_df.to_csv('data/US Census/cleaned/' + 'MEDIAN INCOME' + '.csv')

original_cols = list(data.columns.values)
new_cols = []
renamed_cols = []
for col in df_dict['SELECTED ECONOMIC CHARACTERISTICS'].columns.values:
    if col in original_cols:
        renamed_cols.append(col)
        new_cols.append(col)
    elif ('HEALTH INSURANCE' in col) and ('Percent' in col) and ('coverage' in col) and ('Margin of Error' not in col) and ('years' not in col):
        new_cols.append(col)
        renamed_cols.append(col.split('!!')[-1])
health_df = df_dict['SELECTED ECONOMIC CHARACTERISTICS'][new_cols].copy()
health_df.columns = renamed_cols
health_df.to_csv('data/US Census/cleaned/' + 'HEALTH INSURANCE' + '.csv')

original_cols = list(data.columns.values)
new_cols = []
renamed_cols = []
for col in df_dict['SELECTED ECONOMIC CHARACTERISTICS'].columns.values:
    if col in original_cols:
        renamed_cols.append(col)
        new_cols.append(col)
    elif ('POVERTY' in col) and ('Percent' in col) and ('Margin of Error' not in col) and ('All people' in col):
        new_cols.append(col)
        renamed_cols.append('Below Poverty Level - ' + col.split('!!')[-1])
poverty_df = df_dict['SELECTED ECONOMIC CHARACTERISTICS'][new_cols].copy()
poverty_df.columns = renamed_cols
poverty_df.to_csv('data/US Census/cleaned/' + 'POVERTY' + '.csv')