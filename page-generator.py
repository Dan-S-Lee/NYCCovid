# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 15:41:08 2020

@author: Daniel Lee
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import plotly
from lxml import etree as ET
from lxml.html import builder as E
import lxml.html
import scipy.stats

city_dfs = {}
city_dfs['by-borough'] = pd.read_csv('https://raw.githubusercontent.com/nychealth/coronavirus-data/master/boro.csv')
city_dfs['by-age'] = pd.read_csv('https://raw.githubusercontent.com/nychealth/coronavirus-data/master/by-age.csv')
city_dfs['by-sex'] = pd.read_csv('https://raw.githubusercontent.com/nychealth/coronavirus-data/master/by-sex.csv')
city_dfs['hosp-trends'] = pd.read_csv('https://raw.githubusercontent.com/nychealth/coronavirus-data/master/case-hosp-death.csv')
city_dfs['summary'] = pd.read_csv('https://raw.githubusercontent.com/nychealth/coronavirus-data/master/summary.csv', names = ['Metric', 'Number'])
city_dfs['zipcode'] = pd.read_csv('data/US Census/cleaned/TOTAL POPULATION.csv', index_col = 'MODZCTA')

city_dfs['by-borough'].columns = ['Borough', 'Total Cases', 'Cases Rate (Per 100k)']
city_dfs['by-age'].columns = ['Age Group', 'Cases Rate', 'Hospitalization Rate', 'Death Rate']
city_dfs['by-sex'].columns = ['Sex', 'Cases Rate', 'Hospitalization Rate', 'Death Rate']
city_dfs['hosp-trends'].columns = ['Date', 'New Cases', 'Hospitalized Cases', 'Deaths']

city_dfs['by-age']['Age Group'].loc[4] = '75 and older'

layout = go.Layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)')

cases_fig = px.bar(city_dfs['by-borough'].iloc[0:5], x='Borough', y='Total Cases', color = 'Cases Rate (Per 100k)', title = 'Total Cases by Borough', color_continuous_scale = 'Reds')
cases_fig.update_layout(title = {'text': 'Total Cases by Borough',
                                 'x': 0.5,
                                 'xanchor': 'center'},
                        font = dict(family = 'Montserrat', size = 14, color = '#FFFFFF'))
cases_fig.update_layout({'paper_bgcolor':'rgba(0,0,0,0)',
    'plot_bgcolor':'rgba(0,0,0,0)'})

age_fig = go.Figure(data = [go.Bar(name = 'Cases', x = city_dfs['by-age'].iloc[0:5]['Age Group'], y = city_dfs['by-age'].iloc[0:5]['Cases Rate'],marker_color = 'rgb(255,245,240)'),
                            go.Bar(name = 'Hospitalizations     ', x = city_dfs['by-age'].iloc[0:5]['Age Group'], y = city_dfs['by-age'].iloc[0:5]['Hospitalization Rate']),
                            go.Bar(name = 'Deaths', x = city_dfs['by-age'].iloc[0:5]['Age Group'], y = city_dfs['by-age'].iloc[0:5]['Death Rate'], marker_color = 'black')],layout = layout)
age_fig.update_layout(title = {'text': 'Cases by Age Group (Per 100k)',
                                 'x': 0.5,
                                 'xanchor': 'center'},
                        font = dict(family = 'Montserrat', size = 14, color = '#FFFFFF'))

hosp_fig = go.Figure(data = [go.Line(name = 'New Cases', x = city_dfs['hosp-trends']['Date'], y = city_dfs['hosp-trends']['New Cases']),
                             go.Line(name = 'New Hospitalizations     ', x = city_dfs['hosp-trends']['Date'], y = city_dfs['hosp-trends']['Hospitalized Cases']),
                             go.Line(name = 'Deaths', x = city_dfs['hosp-trends']['Date'], y = city_dfs['hosp-trends']['Deaths'], marker_color = 'black')], layout = layout)
hosp_fig.update_layout(title = {'text': 'Hospital Trends',
                                 'x': 0.5,
                                 'xanchor': 'center'},
                        font = dict(family = 'Montserrat', size = 14, color = '#FFFFFF'))

cases_fig.write_html('htmls/cases_fig.html')
age_fig.write_html('htmls/age_fig.html')
hosp_fig.write_html('htmls/hosp_fig.html')

config = dict({'responsive':True})

age_div = plotly.offline.plot(age_fig, include_plotlyjs=False, output_type='div', config = config)
cases_div = plotly.offline.plot(cases_fig, include_plotlyjs=False, output_type='div', config = config)
hosp_div = plotly.offline.plot(hosp_fig, include_plotlyjs=False, output_type='div', config = config)

metrics = {}
metrics['Cases'] = city_dfs['summary']['Number'].iloc[0]
metrics['Deaths'] = city_dfs['summary']['Number'].iloc[1]
metrics['Hosp'] = city_dfs['summary']['Number'].iloc[2]
metrics['As Of'] = city_dfs['summary']['Number'].iloc[4]

top_5 = city_dfs['zipcode'].sort_values(by='Positive', ascending = False).iloc[0:10]
city_dfs['zipcode']['rate'] = city_dfs['zipcode']['Positive'] / city_dfs['zipcode']['Total_TOTAL POPULATION'] * 1000
top_5_rate = city_dfs['zipcode'].sort_values(by='rate', ascending = False).iloc[0:5]
top5_metrics = {}
top5_metrics['total'] = top_5
top5_metrics['rate'] = top_5_rate

zip_data = city_dfs['zipcode'].copy()
zip_data.rename(columns = {'MODZCTA': 'zipcode', 'zcta_cum.perc_pos': '%_positive'}, inplace = True)
zip_geo = f'data/zipcode_polygons.json'

to_extract = ['HOUSEHOLD SIZE', 'HOUSING UNITS', 'RACE', 'SEX BY AGE', 'TOTAL POPULATION', 'HOUSEHOLD SIZE Percentage', 'RACE Percentage', 'SEX BY AGE Percentage','MEDIAN INCOME']
data_dir = 'data/US Census/cleaned/'
df_dict = {}

for file_name in to_extract:
    df_dict[file_name] = pd.read_csv(data_dir + file_name + '.csv', index_col = 'MODZCTA')
pop_data = df_dict['TOTAL POPULATION']
data = pop_data.merge(df_dict['RACE'], on = 'MODZCTA', how ='inner')
demo_renaming = {'White':'White alone', 
                 'African American': 'Black or African American alone', 
                 'Native American': 'American Indian and Alaska Native alone', 
                 'Asian': 'Asian alone',
                 'Pacific Islander': 'Native Hawaiian and Other Pacific Islander alone',
                 'Other Races': 'Some Other Race alone',
                 'Two or More Races': 'Two or More Races'}
config = dict({'responsive':False})

demo_dict = {'Race' : 'Percentage'}
for k,v in demo_renaming.items():
    data[k + '_percentage'] = data[v]/data['Total_TOTAL POPULATION'] * 100
data['infected_per_1000'] = data['Positive_x'] / data['Total_TOTAL POPULATION'] * 1000
x_dict = {}
for k,v in demo_renaming.items():
    x_dict[k] = data[k + '_percentage']
y = data['infected_per_1000']
graph_dict = {}
for k,v in x_dict.items():
    spear_r, p_val = scipy.stats.spearmanr(x_dict[k], y)
    slope, intercept, r, p, stderr = scipy.stats.linregress(x_dict[k], y)
    line = f'Regression line: y={intercept:.2f}+{slope:.2f}x, r= {spear_r:.2f}, p= {p_val:.2f}          '
    #ax.plot(x_dict[k], y, linewidth=0, marker='s', label='Data points')
    #ax.plot(x_dict[k], intercept + slope * x_dict[k], label=line)
    layout = go.Layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)')
    reg_fig = go.Figure()
    reg_fig.add_trace(go.Scatter(x=x_dict[k], y=y, name='ZCTA XY Pairs      ', mode = 'markers'))
    reg_fig.add_trace(go.Line(x=x_dict[k], y=intercept + slope * x_dict[k], name = line))
    reg_fig.update_layout(title = {'text': k,
                                     'x': 0.5,
                                     'xanchor': 'center'},
                            font = dict(family = 'Montserrat', size = 14, color = '#FFFFFF'),
                          xaxis_title=k + ' (%)',
                          yaxis_title='Infected per 1,000',
                         legend_orientation="h",
                         legend=dict(
                                    x=0.5,
                                    y=1,
                                    traceorder="normal",
                                    font=dict(
                                        family="Montserrat",
                                        size=12,
                                        color="black"
                                    ),
                                    bgcolor="LightSteelBlue",
                                    bordercolor="Black",
                                    borderwidth=2
                                ))
    
    reg_fig.update_layout({'paper_bgcolor':'rgba(0,0,0,0)',
        'plot_bgcolor':'rgba(0,0,0,0)'})
    reg_fig.update_xaxes(automargin=True)
    reg_fig.update_yaxes(automargin=True)
    graph_dict[k] = plotly.offline.plot(reg_fig, include_plotlyjs=False, output_type='div')

data = pop_data.merge(df_dict['MEDIAN INCOME'], on = 'MODZCTA', how ='inner')
data['infected_per_1000'] = data['Positive_x'] / data['Total_TOTAL POPULATION'] * 1000
x = data['Median household income (dollars)']/1000
y = data['infected_per_1000']
spear_r, p_val = scipy.stats.spearmanr(x, y)
slope, intercept, r, p, stderr = scipy.stats.linregress(x, y)
line = f'Regression line: y={intercept:.2f}+{slope:.2f}x, r= {spear_r:.2f}, p= {p_val:.2f}      '
layout = go.Layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)')
reg_fig = go.Figure()
reg_fig.add_trace(go.Scatter(x=x, y=y, name='ZCTA XY Pairs      ', mode = 'markers'))
reg_fig.add_trace(go.Line(x=x, y=intercept + slope * x, name = line))
reg_fig.update_layout(title = {'text': 'Median Household Income',
                                 'x': 0.5,
                                 'xanchor': 'center'},
                        font = dict(family = 'Montserrat', size = 14, color = '#FFFFFF'),
                      xaxis_title='Median Household Income' + ' (In Thousands)',
                      yaxis_title='Infected per 1,000',
                     legend_orientation="h",
                     legend=dict(
                                x=0.5,
                                y=1,
                                traceorder="normal",
                                font=dict(
                                    family="Montserrat",
                                    size=12,
                                    color="black"
                                ),
                                bgcolor="LightSteelBlue",
                                bordercolor="Black",
                                borderwidth=2
                            ))

reg_fig.update_layout({'paper_bgcolor':'rgba(0,0,0,0)',
    'plot_bgcolor':'rgba(0,0,0,0)'})
reg_fig.update_xaxes(automargin=True)
reg_fig.update_yaxes(automargin=True)
graph_dict['Household Income'] = plotly.offline.plot(reg_fig, include_plotlyjs=False, output_type='div')

def generate_stats_html(metrics_dict, top5, stats_dict, background_color, card_color):
    table_tag = E.TBODY()
    for i in range(len(top5_metrics['total'])):
        table_tag.insert(int(i), 
                         E.TR(
                             E.TD(str(top5_metrics['total']['Zip'].iloc[i])),
                             E.TD(str('{:,.0f}'.format(top5_metrics['total']['Positive'].iloc[i])))
                             )
                        )
    stats_paragraph = E.DIV(E.CLASS('jumbotron jumbotron-fluid'),
                           E.DIV(E.CLASS('container'),
                                E.H2(E.CLASS('display-4'), 
                                     'Linear Regressions By Income and Race'),
                                E.P(E.CLASS('lead'),
                                   'Each marker represents a zip code that reported data on COVID-19. The respective p-values and Spearman correlation coefficients are displayed. Remember that correlation does not imply causation!' )
                                ),
                            style = 'background-color:' + background_color
                           )
    row_1 = E.DIV(E.CLASS('row'),
                  E.DIV(E.CLASS('col-xs-12 col-md-6 flex-column'),
                        lxml.html.fragment_fromstring(stats_dict['White'], parser = ET.HTMLParser())),
                  E.DIV(E.CLASS('col-xs-12 col-md-6 flex-column'),
                        lxml.html.fragment_fromstring(stats_dict['African American'], parser = ET.HTMLParser()))
                 )
    row_2 = E.DIV(E.CLASS('row'),
                  E.DIV(E.CLASS('col-xs-12 col-md-6 flex-column'),
                        lxml.html.fragment_fromstring(stats_dict['Asian'], parser = ET.HTMLParser())),
                  E.DIV(E.CLASS('col-xs-12 col-md-6 flex-column'),
                        lxml.html.fragment_fromstring(stats_dict['Native American'], parser = ET.HTMLParser()))
                 )
    row_3 = E.DIV(E.CLASS('row'),
                  E.DIV(E.CLASS('col-xs-12 col-md-6 flex-column'),
                        lxml.html.fragment_fromstring(stats_dict['Other Races'], parser = ET.HTMLParser())),
                  E.DIV(E.CLASS('col-xs-12 col-md-6 flex-column'),
                        lxml.html.fragment_fromstring(stats_dict['Two or More Races'], parser = ET.HTMLParser()))
                 )
    income_row = E.DIV(E.CLASS('row h-50'),
                       E.DIV(E.CLASS('col-md-2')),
                       E.DIV(E.CLASS('col-md-8'),
                            lxml.html.fragment_fromstring(stats_dict['Household Income'], parser = ET.HTMLParser())),
                       E.DIV(E.CLASS('col-md-2')))
    html = E.HTML(
    E.HEAD(
        E.META(name = 'viewport', content = 'width=device-width, initial-scale=1'),
        E.LINK(href="https://sleepingtuna.github.io/NYCCovid-19Map.github.io/docs/css/w3.css", rel="stylesheet"),
        E.LINK(href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300&amp;display=swap", rel="stylesheet"),
        E.LINK(rel="stylesheet", href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css", integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm", crossorigin="anonymous"),
        E.SCRIPT(src="https://cdn.plot.ly/plotly-latest.min.js"),
        E.STYLE(r".w3-montserrat {font-family: 'Montserrat', sans-serif;}")),
    E.BODY(
        E.DIV(E.CLASS('page-header w3-montserrat text-center text-white'),
                    E.H2('NYC COVID-19 Cases by Zip Code'), style = "width:100% background-color:" + background_color),
        E.UL(E.CLASS('nav nav-pills nav-justified justify-content-center text-white w3-montserrat'),
            E.LI(E.CLASS('nav-item'),
                E.A(E.CLASS('nav-link btn-dark'), 'Summary', 
                    {'id':'pills-home-tab',
                     'href':"https://sleepingtuna.github.io/NYCCovid-19Map.github.io/docs/landingpage.html",
                     'aria-selected':"false"})),
            E.LI(E.CLASS('nav-item'),
                E.A(E.CLASS('nav-link active btn-dark'), 'Statistics',
                   {'id':'pills-stat-tab',
                    'href':"https://sleepingtuna.github.io/NYCCovid-19Map.github.io/docs/statistics.html", 
                    'role':"tab", 'aria-controls':"pills-stat", 'aria-selected':"true"}))
            ),
        E.DIV(E.CLASS("tab-content w3-montserrat text-white container-fluid"), {'id':'pills-tabContent'},
              E.DIV(E.CLASS('tab-pane'), {'id': 'pills-home', 'role':'tabpanel', 'aria-labelledby':'pills-home-tab'}),
              E.DIV(E.CLASS('tab-pane show active'), {'id': 'pills-stat','role':'tabpanel', 'aria-labelledby':'pills-stat-tab'},
                   E.DIV(E.CLASS('container-fluid'),
                         stats_paragraph,
                         income_row,
                         row_1,
                         row_2,
                         row_3)
                   ),
              align = 'center',
              style = 'background-color:' + background_color
             ),
        E.DIV(E.CLASS('container-fluid'), 
              E.DIV(E.CLASS('row'),
                    E.DIV(E.CLASS('col-xs-12 col-md-6 flex-column'), lxml.html.fragment_fromstring(age_div, parser = ET.HTMLParser())),
                    E.DIV(E.CLASS('col-xs-12 col-md-6 flex-column'), lxml.html.fragment_fromstring(cases_div, parser = ET.HTMLParser()))
                   ),
              E.DIV(E.CLASS('row'), 
                    E.DIV(E.CLASS('col-sm-12'), lxml.html.fragment_fromstring(hosp_div, parser = ET.HTMLParser()))
                   ),
              style = 'background-color:' + background_color
             ),
        E.DIV(E.CLASS('page-footer font-small black w3-montserrat text-white'),
                E.DIV(E.CLASS('container-fluid text-center text-md-left'),
                     E.DIV(E.CLASS('row'),
                          E.DIV(E.CLASS('col-md-6'), 'Data is as of ' + metrics['As Of']),
                          E.DIV(E.CLASS('col-md-6'), 'Due to reporting lags, hospitalizations for recent days usually are underreported.')))),
        E.SCRIPT(src="https://code.jquery.com/jquery-3.2.1.slim.min.js", integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN", crossorigin="anonymous"),
        E.SCRIPT(src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js", integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q", crossorigin="anonymous"),
        E.SCRIPT(src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js", integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl", crossorigin="anonymous"),
        style = 'background-color:' + background_color
    )
    )
    
    return html

bg_color = '#282828' + ';'
cd_color = '#181818' + ';'

page = generate_stats_html(metrics, top5_metrics, graph_dict, bg_color, cd_color)

with open(r'C:\Users\Daniel Lee\Documents\GitHub\NYCCovid-19Map.github.io\docs\statistics.html', 'w') as f:
    f.write(lxml.html.tostring(page, pretty_print=True).decode('utf-8'))
    
def generate_home_html(metrics_dict, top5, stats_dict, background_color, card_color):
    table_tag = E.TBODY()
    for i in range(len(top5_metrics['total'])):
        table_tag.insert(int(i), 
                         E.TR(
                             E.TD(str(top5_metrics['total']['Zip'].iloc[i])),
                             E.TD(str('{:,.0f}'.format(top5_metrics['total']['Positive'].iloc[i])))
                             )
                        )
    stats_paragraph = E.DIV(E.CLASS('jumbotron jumbotron-fluid'),
                           E.DIV(E.CLASS('container'),
                                E.H2(E.CLASS('display-4'), 
                                     'Linear Regressions By Census-Designated Race'),
                                E.P(E.CLASS('lead'),
                                   'Each marker represents a zip code that reported data on COVID-19. The respective p-values and Spearman correlation coefficients are displayed. Remember that correlation does not imply causation!' )
                                ),
                            style = 'background-color:' + background_color
                           )
    row_1 = E.DIV(E.CLASS('row'),
                  E.DIV(E.CLASS('col-xs-6'),
                        lxml.html.fragment_fromstring(stats_dict['White'], parser = ET.HTMLParser())),
                  E.DIV(E.CLASS('col-xs-6'),
                        lxml.html.fragment_fromstring(stats_dict['African American'], parser = ET.HTMLParser()))
                 )
    row_2 = E.DIV(E.CLASS('row'),
                  E.DIV(E.CLASS('col-xs-6'),
                        lxml.html.fragment_fromstring(stats_dict['Asian'], parser = ET.HTMLParser())),
                  E.DIV(E.CLASS('col-xs-6'),
                        lxml.html.fragment_fromstring(stats_dict['Native American'], parser = ET.HTMLParser()))
                 )
    row_3 = E.DIV(E.CLASS('row'),
                  E.DIV(E.CLASS('col-xs-6'),
                        lxml.html.fragment_fromstring(stats_dict['Other Races'], parser = ET.HTMLParser())),
                  E.DIV(E.CLASS('col-xs-6'),
                        lxml.html.fragment_fromstring(stats_dict['Two or More Races'], parser = ET.HTMLParser()))
                 )
    html = E.HTML(
    E.HEAD(
        E.META(name = 'viewport', content = 'width=device-width, initial-scale=1'),
        E.LINK(href="https://sleepingtuna.github.io/NYCCovid-19Map.github.io/docs/css/w3.css", rel="stylesheet"),
        E.LINK(href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300&amp;display=swap", rel="stylesheet"),
        E.LINK(rel="stylesheet", href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css", integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm", crossorigin="anonymous"),
        E.SCRIPT(src="https://cdn.plot.ly/plotly-latest.min.js"),
        E.STYLE(r".w3-montserrat {font-family: 'Montserrat', sans-serif;}")),
    E.BODY(
        E.DIV(E.CLASS('page-header w3-montserrat text-center text-white'),
                    E.H1('NYC COVID-19 Cases by Zip Code'), style = "width:100% background-color:" + background_color),
        E.UL(E.CLASS('nav nav-pills nav-justified justify-content-center text-white w3-montserrat'),
            E.LI(E.CLASS('nav-item'),
                E.A(E.CLASS('nav-link active btn-dark'), 'Summary', 
                    {'id':'pills-home-tab',
                     'href':"https://sleepingtuna.github.io/NYCCovid-19Map.github.io/docs/landingpage.html",
                     'aria-selected':"false"})),
            E.LI(E.CLASS('nav-item'),
                E.A(E.CLASS('nav-link btn-dark'), 'Statistics',
                   {'id':'pills-stat-tab',
                    'href':"https://sleepingtuna.github.io/NYCCovid-19Map.github.io/docs/statistics.html", 
                    'role':"tab", 'aria-controls':"pills-stat", 'aria-selected':"true"}))
            ),
        E.DIV(E.CLASS("container-fluid w3-montserrat"),
              E.DIV(E.CLASS('row mt-4'),
                        E.DIV(E.CLASS('col-xs-12 col-md-2 flex-column d-flex justify-content-between'),
                                E.DIV(E.CLASS('card border-light text-white'),
                                   E.DIV(E.CLASS('card-body'), 
                                         E.H6(E.CLASS('card-title'), 'Total Confirmed Cases',
                                             style='font-size:1vw'),
                                         E.H4(E.CLASS('card-text'), str('{:,.0f}'.format(int(metrics_dict['Cases']))),
                                             style='font-size:2vw')
                                        ),
                                      style = 'background-color:' + card_color
                                     ),
                                E.DIV(E.CLASS('card border-light text-white'),
                                   E.DIV(E.CLASS('card-body'), 
                                         E.H6(E.CLASS('card-title'), 'Total Deaths',
                                             style='font-size:1vw'),
                                         E.H4(E.CLASS('card-text'), str('{:,.0f}'.format(int(metrics_dict['Deaths']))),
                                             style='font-size:2vw')
                                        ),
                                      style = 'background-color:' + card_color
                                     ),
                                E.DIV(E.CLASS('card border-light text-white'),
                                   E.DIV(E.CLASS('card-body'), 
                                         E.H6(E.CLASS('card-title'), 'Total Hospitalized',
                                             style='font-size:1vw'),
                                         E.H4(E.CLASS('card-text'), str('{:,.0f}'.format(int(metrics_dict['Hosp']))),
                                             style='font-size:2vw')
                                        ),
                                      style = 'background-color:' + card_color
                                     )
                             ),
                        E.DIV(E.CLASS('col-xs-12 col-md-8'),
                             E.IFRAME(name ="main-map", style="min-height: 400; border:0;", width ="100%", height="100%", frameborder="0", src=r"https://sleepingtuna.github.io/NYCCovid-19Map.github.io/docs/new_master.html")),
                        E.DIV(E.CLASS('col-xs-12 col-md-2 my-auto'), 
                              E.H5('Zip Codes with Highest Case Counts'),
                              E.DIV(E.CLASS('table-responsive'),
                                    E.TABLE(E.CLASS('table table-bordered text-white w-auto'),
                                      E.THEAD(E.CLASS('text-small'), 
                                            E.TH('ZIP CODE'),
                                            E.TH('CONFIRMED CASES')),
                                            table_tag,
                                      style = 'background-color:' + card_color)
                                   ),
                              align = 'center'),
                        style = 'min-height: 75vh; background-color:' + background_color), 
              E.DIV(E.CLASS('row'),
                    E.DIV(E.CLASS('col-xs-12 col-md-6'), lxml.html.fragment_fromstring(age_div, parser = ET.HTMLParser())),
                    E.DIV(E.CLASS('col-xs-12 col-md-6'), lxml.html.fragment_fromstring(cases_div, parser = ET.HTMLParser()))
                   ),
              E.DIV(E.CLASS('row'), 
                    E.DIV(E.CLASS('col-xs-12 col-md-12 flex-column'), lxml.html.fragment_fromstring(hosp_div, parser = ET.HTMLParser())),
                    style = 'min-height: 50vh'
                   ),
                align = 'center',
              style = 'background-color:' + background_color),
        E.DIV(E.CLASS('page-footer font-small black w3-montserrat text-white'),
                E.DIV(E.CLASS('container-fluid text-center text-md-left'),
                     E.DIV(E.CLASS('row'),
                          E.DIV(E.CLASS('col-xs-6'), 'Data is as of ' + metrics['As Of']),
                          E.DIV(E.CLASS('col-xs-6'), 'Due to reporting lags, hospitalizations for recent days usually are underreported.')))),
        E.SCRIPT(src="https://code.jquery.com/jquery-3.2.1.slim.min.js", integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN", crossorigin="anonymous"),
        E.SCRIPT(src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js", integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q", crossorigin="anonymous"),
        E.SCRIPT(src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js", integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl", crossorigin="anonymous"),
        style = 'background-color:' + background_color
    )
    )
    
    return html

bg_color = '#282828' + ';'
cd_color = '#181818' + ';'

page = generate_home_html(metrics, top5_metrics, graph_dict, bg_color, cd_color)

with open(r'C:\Users\Daniel Lee\Documents\GitHub\NYCCovid-19Map.github.io\docs\home.html', 'w') as f:
    f.write(lxml.html.tostring(page, pretty_print=True).decode('utf-8'))