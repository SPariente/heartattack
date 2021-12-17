#Import used packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import statsmodels.api as sm

#Import dataframe
h_data = pd.read_csv('https://raw.githubusercontent.com/SPariente/heartattack/master/heart.csv')

#Initialise dash app
app = dash.Dash(__name__)

#Create a list of sexes
sex_list = [{'label':'Any', 'value':'Any'}]
for i in h_data['Sex'].unique():
    sex_list.append({'label': i, 'value': i})

#Find the range of ages in the dataframe
age_range = [min(h_data['Age']), max(h_data['Age'])]

#Create a list of categorical (i.e. non-numerical) predictors from the dataframe
hd_predictors_cat_list = h_data.select_dtypes(object).columns.to_list()
hd_predictors_cat = []
for i in hd_predictors_cat_list:
    hd_predictors_cat.append({'label':i, 'value':i})

#Create a list of numerical predictors from the dataframe
hd_predictors_num_list = h_data.drop(['HeartDisease'], axis = 1).select_dtypes(np.number).columns.to_list()
hd_predictors_num = []
for i in hd_predictors_num_list:
    hd_predictors_num.append({'label':i, 'value':i})

#Define the layout of the dash app
app.layout = html.Div( 
    [html.H1('Heart Disease data exploration dashboard', #App title
             style = { 
                 'textalign': 'center',
                 'font-size': 40,
                 'font-weight': 'bold'
             }
            ),
     html.Br(),
     html.H2('Primary filters', #Title for primary filters field
             style = { 
                 'textalign':'left',
                 'font-size': 20
             }
            ),
     html.A("Select a gender:", #Directions for the dropdown menu
            style = {
                'textalign': 'left',
                'font-size': 16
            }
           ),
     dcc.Dropdown( #Sex dropdown menu
         id = 'sex_input', 
         value = 'Any',
         options = sex_list,
         placeholder = 'Filter by gender here',
         searchable = True),
     html.Br(),
     html.A("Select an age range:", #Directions for the slider
            style = {
                'textalign': 'left',
                'font-size': 16
            }
           ),
     dcc.RangeSlider( #Double-ended age range slider
         id = 'age_input',
         min = 25,
         max = 80,
         step = 5, #5 year step for slider
         value = [min(h_data['Age']), max(h_data['Age'])], #Initial values = whole range in data set
         marks = { #Major ticks every 10 years
             min(h_data['Age']):str(min(h_data['Age'])),
             max(h_data['Age']):str(max(h_data['Age'])),
             30:'30',
             40:'40',
             50:'50',
             60:'60',
             70:'70'
         }
     ),
     html.Div(children = [#Create a sub-division containing all graphs
         html.Div(children = [#Create a sub-division containing categorical indicator graphs
             html.H2('Categorical values',
                     style = {
                         'textalign':'left',
                         'font-size': 20,
                         'font-weight':'bold'
                     }
                    ), 
             html.Br(),
             html.A('Select a categorical predictor:', #Directions for the dropdown menu
                    style = {
                        'textalign': 'left',
                        'font-size': 16
                    }
                   ),
             dcc.Dropdown( #Dropdown input field to select a categorical predictor
                 id = 'predictors_cat_input',
                 value = hd_predictors_cat_list[0],
                 options = hd_predictors_cat,
                 placeholder = "Select a categorical predictor",
                 searchable = True
             ),
             html.Br(),
             html.Label('Heart disease sunburst chart', #Title of the chart
                        style = {
                            'textalign': 'left',
                            'font-size': 18
                        }
                       ),
             html.Div(dcc.Graph(id = 'sb_chart')),#Sunburst chart
             html.Br(),
             html.Label('Heart disease bar chart', #Title of the chart
                        style = {
                            'textalign': 'left',
                            'font-size': 18
                        }
                       ),
             html.Div(dcc.Graph(id = 'bar_chart')) #Bar chart
         ], 
                  style = {
                      'width': '400px',
                      'margin-left': 0,
                      'flex':1,
                      'border-style': 'none solid none none',
                      'border-width': '1px',
                      'border-color': 'gray',
                      'padding':10
                  }
                 ),
         html.Div(children = [ #Create a sub-division containing numerical indicator graphs
             html.H2('Numerical values', #Title of the section
                     style = {
                         'textalign':'left',
                         'font-size': 20,
                         'font-weight':'bold'
                     }
                    ),
             html.Br(),
             html.Label('Heart disease scatter plot', #Title of the figure
                        style = {
                            'textalign': 'left',
                            'font-size': 18
                        }
                       ),
             html.Br(),
             html.Br(),
             html.A('Select two numerical predictors for the scatter plot:', #Directions for the dropdown menus
                    style = {
                        'textalign': 'left',
                        'font-size': 16
                    }
                   ),
             dcc.Dropdown( #Dropdown input field to select a numerical predictor for the scatter plot
                 id = 'predictors_num_input1',
                 value = hd_predictors_num_list[0],
                 options = hd_predictors_num,
                 placeholder = "Select a numerical predictor",
                 searchable = True
             ),
             dcc.Dropdown( #Dropdown input field to select a second numerical predictor for the scatter plot
                 id = 'predictors_num_input2',
                 value = hd_predictors_num_list[1],
                 options = hd_predictors_num,
                 placeholder = "Select another numerical predictor",
                 searchable = True
             ),
             dcc.Checklist( #Check box to ask for a local regression curve if selected
                 id = 'lowess_check',
                 options = [{'label':'Lowess (optional)', 'value':'lowess'}]
             ),
             html.Div( #Fraction selection if lowess has been selected
                 id = 'lowess_option',
                 children = [
                     html.A('Select the fraction of data used for the lowess (0 to 1):', #Directions for the input field
                            style = {
                                'textalign': 'left',
                                'font-size': 16
                            }
                           ),
                     dcc.Input(
                         id = 'lowess_frac',
                         pattern = '(0.?\d*)|1', #Any number between 0 and 1, inclusive
                         value = 0
                     )                     
                 ],
                 hidden = True #Is set to False if lowess is selected, making the div visible
             ),
             html.Br(),
             html.Div(dcc.Graph(id = 'scatter_plot')),#Scatter plot
             html.Br(),
             html.Label('Heart disease box plot', #Title of the figure
                        style = {
                            'textalign': 'left',
                            'font-size': 18
                        }
                       ),
             html.Br(),
             html.Br(),
             html.A('Select a numerical predictor for the box plot:', #Directions for the dropdown menu
                    style = {
                        'textalign': 'left',
                        'font-size': 16
                    }
                   ),
             dcc.Dropdown( #Dropdown input field to select a numerical predictor for the box plot
                 id = 'predictors_num_input',
                 options = hd_predictors_num,
                 value = hd_predictors_num_list[0],
                 placeholder = "Select a numerical predictor",
                 searchable = True
             ),
             html.Div(dcc.Graph(id = 'box_plot')) #Box plot
         ],
                  style={
                      'width': '400px',
                      'margin-left': 0,
                      'flex':1,
                      'border-style': 'none none none solid',
                      'border-width': '1px',
                      'border-color': 'gray',
                      'padding':10
                  }
                 )
     ],
              style={
                  'display': 'flex',
                  'flex-direction': 'row' #Ensures the two subdivisions created for graphs appear side by side
              }
             )
    ],
    style = {
        'font-family': 'Verdana',
        'padding': 10
            }
)                      

#Suburst chart callback
@app.callback(Output(component_id = 'sb_chart', component_property = 'figure'), #sunburst chart component
              [Input(component_id = 'sex_input', component_property = 'value'), #sex selection component
               Input(component_id = 'age_input', component_property = 'value'), #age range selection component
               Input(component_id = 'predictors_cat_input', component_property = 'value') #categorical predictor selection component
              ])
def get_sb_chart(sex, age, predictor):
    if sex == 'Any': #Get full data set if 'any' sex selected
        px_data = h_data[h_data['Age'].between(age[0],age[1])]
    else: #Filter data set on the selected sex
        px_data = h_data[(h_data['Sex']==sex) & (h_data['Age'].between(age[0],age[1]))]
        
    px_data['HeartDisease'] = px_data['HeartDisease'].astype('str') #Set type of the 'HeartDisease' field to string
    fig = px.sunburst(
        px_data, path = ('HeartDisease', predictor),
        color = 'HeartDisease',
        color_discrete_map={'0':'blue', '1':'red'}
    )
    return fig

#Bar chart callback
@app.callback(Output(component_id = 'bar_chart', component_property = 'figure'),
              [Input(component_id = 'sex_input', component_property = 'value'),
               Input(component_id = 'age_input', component_property = 'value'),
               Input(component_id = 'predictors_cat_input', component_property = 'value')
              ])
def get_bar_chart(sex, age, predictor):
    if sex == 'Any':
        px_data = h_data[h_data['Age'].between(age[0],age[1])]
    else:
        px_data = h_data[(h_data['Sex']==sex) & (h_data['Age'].between(age[0],age[1]))]
        
    px_data = px_data[[predictor, 'HeartDisease']].groupby(predictor).mean('HeartDisease')
    px_data['Healthy'] = 1-px_data['HeartDisease']
    px_data.sort_values(by = 'HeartDisease', ascending = False, inplace = True)
    fig = px.bar(px_data.reindex(columns = ['Healthy', 'HeartDisease'],copy = False),
                 color_discrete_map={'Healthy':'blue', 'HeartDisease':'red'})
    fig.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        'legend': {'title': {'text': 'Legend'}, 'tracegroupgap': 0},
        'yaxis': {'anchor': 'x', 'domain': [0, 1], 'title': {'text': 'Proportion'}}
    })
    return fig

#Scatter plot callback
@app.callback(Output(component_id = 'scatter_plot', component_property = 'figure'),
              [Input(component_id = 'sex_input', component_property = 'value'),
               Input(component_id = 'age_input', component_property = 'value'),
               Input(component_id = 'predictors_num_input1', component_property = 'value'),
               Input(component_id = 'predictors_num_input2', component_property = 'value'),
               Input(component_id = 'lowess_check', component_property = 'value'),
               Input(component_id = 'lowess_frac', component_property = 'value')
              ])
def get_scatter_plot(sex, age, predictor1, predictor2, lowess_check, frac):
    if sex == 'Any':
        px_data = h_data[h_data['Age'].between(age[0],age[1])]
    else:
        px_data = h_data[(h_data['Sex']==sex) & (h_data['Age'].between(age[0],age[1]))]
        
    px_data['HeartDisease'] = px_data['HeartDisease'].astype('str')
    fig = px.scatter(px_data, x = predictor1, y = predictor2, color = 'HeartDisease')
    fig.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)'})
    fig.update_yaxes(gridcolor = 'lightgray')
    
    if lowess_check == ['lowess']: #Adds lowess line plot if selected
        lowess_pred = sm.nonparametric.lowess(
            px_data[predictor2],
            px_data[predictor1],
            frac = float(frac)
        )
        
        fig.add_trace(
            px.line(
                x = lowess_pred[:,0], 
                y = lowess_pred[:,1], 
                color_discrete_sequence=['black'], 
                labels = {"y":'Lowess'}
            ).data[0]
        )
        
    return fig

#Box plot callback
@app.callback(Output(component_id = 'box_plot', component_property = 'figure'),
              [Input(component_id = 'sex_input', component_property = 'value'),
               Input(component_id = 'age_input', component_property = 'value'),
               Input(component_id = 'predictors_num_input', component_property = 'value')
              ])
def get_box_plot(sex, age, predictor):
    if sex == 'Any':
        px_data = h_data[h_data['Age'].between(age[0],age[1])]
    else:
        px_data = h_data[(h_data['Sex']==sex) & (h_data['Age'].between(age[0],age[1]))]
        
    fig = px.box(px_data,
                 x = 'HeartDisease',
                 y = predictor, 
                 color = 'HeartDisease',
                 color_discrete_map={0:'blue', 1:'red'})
    fig.update_layout(showlegend=False)
    fig.update_layout(
        {'plot_bgcolor': 'rgba(0, 0, 0, 0)',
         'paper_bgcolor': 'rgba(0, 0, 0, 0)'
        })
    fig.update_yaxes(gridcolor = 'lightgray')
    return fig

#Numerical predictors list callback
@app.callback(Output(component_id = 'predictors_num_input2', component_property = 'options'),
              Input(component_id = 'predictors_num_input1', component_property = 'value')
             )
def get_predictors_num_list(pred_list): #Removes the already selected predictor from the second choice list
    hd_predictors_num_unique = hd_predictors_num.copy()
    hd_predictors_num_unique.remove({'label':pred_list, 'value':pred_list})
    return hd_predictors_num_unique

#Lowess fraction selection div callback
@app.callback(Output(component_id = 'lowess_option', component_property = 'hidden'),
              Input(component_id = 'lowess_check', component_property = 'value')
             )
def get_frac_div(lowess_check): #Hides or shows the fraction field for the lowess plot
    if lowess_check == ['lowess']:
        return False
    else:
        return True

#Run the app
if __name__ == '__main__':
    app.run_server(debug = True)