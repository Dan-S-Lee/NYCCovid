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

age_fig = go.Figure(data = [go.Bar(name = 'Cases', x = city_dfs['by-age'].iloc[0:5]['Age Group'], y = city_dfs['by-age'].iloc[0:5]['Cases Rate']),
                            go.Bar(name = 'Hospitalizations', x = city_dfs['by-age'].iloc[0:5]['Age Group'], y = city_dfs['by-age'].iloc[0:5]['Hospitalization Rate']),
                            go.Bar(name = 'Deaths', x = city_dfs['by-age'].iloc[0:5]['Age Group'], y = city_dfs['by-age'].iloc[0:5]['Death Rate'], marker_color = 'black')],layout = layout)
age_fig.update_layout(title = {'text': 'Cases by Age Group (Per 100k)',
                                 'x': 0.5,
                                 'xanchor': 'center'},
                        font = dict(family = 'Montserrat', size = 14, color = '#FFFFFF'))

hosp_fig = go.Figure(data = [go.Line(name = 'New Cases', x = city_dfs['hosp-trends']['Date'], y = city_dfs['hosp-trends']['New Cases']),
                             go.Line(name = 'New Hospitalizations', x = city_dfs['hosp-trends']['Date'], y = city_dfs['hosp-trends']['Hospitalized Cases']),
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

top_5 = city_dfs['zipcode'].sort_values(by='Positive', ascending = False).iloc[0:5]
city_dfs['zipcode']['rate'] = city_dfs['zipcode']['Positive'] / city_dfs['zipcode']['Total_TOTAL POPULATION'] * 1000
top_5_rate = city_dfs['zipcode'].sort_values(by='rate', ascending = False).iloc[0:5]
top5_metrics = {}
top5_metrics['total'] = top_5
top5_metrics['rate'] = top_5_rate

def generate_html(metrics_dict, top5):
    html = E.HTML(
    E.HEAD(
        E.META(name = 'viewport', content = 'width=device-width, initial-scale=1'),
        E.LINK(href="https://www.w3schools.com/w3css/4/w3.css", rel="stylesheet"),
        E.LINK(href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300&amp;display=swap", rel="stylesheet"),
        E.LINK(rel="stylesheet", href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css", integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm", crossorigin="anonymous"),
        E.SCRIPT(src="https://cdn.plot.ly/plotly-latest.min.js"),
        E.STYLE(r".w3-montserrat {font-family: 'Montserrat', sans-serif;}")),
    E.BODY(E.CLASS('bg-dark'),
        E.DIV(E.CLASS('page-header w3-montserrat text-center bg-dark text-white'),
                    E.H2('NYC COVID-19 Cases by Zip Code'), style = "width:100%"),
        E.DIV(E.CLASS("container-fluid w3-montserrat bg-dark text-white"),
              E.DIV(E.CLASS('row'), 
                    E.DIV(E.CLASS('col-sm-2 flex-column d-flex justify-content-between'),
                            E.DIV(E.CLASS('card bg-dark text-white'),
                               E.DIV(E.CLASS('card-body'), 
                                     E.H6(E.CLASS('card-title'), 'Total Confirmed Cases'),
                                     E.H4(E.CLASS('card-text'), str('{:,.0f}'.format(int(metrics_dict['Cases']))))
                                    )
                                 ),
                            E.DIV(E.CLASS('card bg-dark text-white'),
                               E.DIV(E.CLASS('card-body'), 
                                     E.H6(E.CLASS('card-title'), 'Total Deaths'),
                                     E.H4(E.CLASS('card-text'), str('{:,.0f}'.format(int(metrics_dict['Deaths']))))
                                    )
                                 ),
                            E.DIV(E.CLASS('card bg-dark text-white'),
                               E.DIV(E.CLASS('card-body'), 
                                     E.H6(E.CLASS('card-title'), 'Total Hospitalized'),
                                     E.H4(E.CLASS('card-text'), str('{:,.0f}'.format(int(metrics_dict['Hosp']))))
                                    )
                                 )
                         ),
                    E.DIV(E.CLASS('col-sm-8'),
                         E.IFRAME(name ="main-map", style="border:0;", width ="100%", height="700", frameborder="0", src=r"https://sleepingtuna.github.io/NYCCovid-19Map.github.io/docs/new_master.html")),
                    E.DIV(E.CLASS('col-sm-2 my-auto'), 
                          E.H5('Zip Codes with Highest Case Counts'),
                          E.TABLE(E.CLASS('table table-bordered table-dark w-auto'),
                                  E.THEAD(E.CLASS('text-small'), 
                                        E.TH('ZIP CODE'),
                                        E.TH('CONFIRMED CASES')),
                                  E.TBODY(
                                      E.TR(E.TD(str(top5_metrics['total']['Zip'].iloc[0])),
                                           E.TD(str('{:,.0f}'.format(top5_metrics['total']['Positive'].iloc[0])))
                                          ),
                                      E.TR(E.TD(str(top5_metrics['total']['Zip'].iloc[1])),
                                           E.TD(str('{:,.0f}'.format(top5_metrics['total']['Positive'].iloc[1])))
                                          ),
                                      E.TR(E.TD(str(top5_metrics['total']['Zip'].iloc[2])),
                                           E.TD(str('{:,.0f}'.format(top5_metrics['total']['Positive'].iloc[2])))
                                          ),
                                      E.TR(E.TD(str(top5_metrics['total']['Zip'].iloc[3])),
                                           E.TD(str('{:,.0f}'.format(top5_metrics['total']['Positive'].iloc[3])))
                                          ),
                                      E.TR(E.TD(str(top5_metrics['total']['Zip'].iloc[4])),
                                           E.TD(str('{:,.0f}'.format(top5_metrics['total']['Positive'].iloc[4])))
                                          )
                                         )),
                          style = 'background-color:bg-dark;', align = 'center')
                    
                   ),
              align = 'center'
             ),
        E.DIV(E.CLASS('container-fluid'), 
              E.DIV(E.CLASS('row no-gutters'),
                    E.DIV(E.CLASS('col-sm-6'), lxml.html.fragment_fromstring(age_div, parser = ET.HTMLParser())),
                    E.DIV(E.CLASS('col-sm-6'), lxml.html.fragment_fromstring(cases_div, parser = ET.HTMLParser()))
                   ),
              E.DIV(E.CLASS('row no-gutters'), 
                    E.DIV(E.CLASS('col-sm-12'), lxml.html.fragment_fromstring(hosp_div, parser = ET.HTMLParser()))
                   )
             ),
        E.DIV(E.CLASS('page-footer font-small black w3-montserrat text-white'),
                E.DIV(E.CLASS('container-fluid text-center text-md-left'),
                     E.DIV(E.CLASS('row'),
                          E.DIV(E.CLASS('col-md-6'), 'Data is as of ' + metrics['As Of']),
                          E.DIV(E.CLASS('col-md-6'), 'Due to reporting lags, hospitalizations for recent days usually are underreported.')))),
        E.SCRIPT(src="https://code.jquery.com/jquery-3.2.1.slim.min.js", integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN", crossorigin="anonymous"),
        E.SCRIPT(src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js", integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q", crossorigin="anonymous"),
        E.SCRIPT(src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js", integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl", crossorigin="anonymous")
    )
    )
    
    return html

page = generate_html(metrics, top5_metrics)
with open('htmls/landingpage.html', 'w') as f:
    f.write(lxml.html.tostring(page, pretty_print=True).decode('utf-8'))