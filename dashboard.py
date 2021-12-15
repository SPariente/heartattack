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
    [html.H1('Heart Disease data exploration dashboard',#App title
             style = {
                 'textalign': 'center',
                 'font-size': 40}),
     html.Br(),
     html.H2('Primary filters',#Title for primary filters field
             style = {
                 'textalign':'left',
                 'font-size': 20,
                 'padding': 10}),
     html.A("Select a gender:",
            style = {
                'textalign': 'left',
                'font-size': 16}),
     dcc.Dropdown(#Sex dropdown
         id = 'sex_input',
         value = 'Any',
         options = sex_list,
         placeholder = 'Filter by gender here',
         searchable = True),
     html.Br(),
     html.A("Select an age range:",
            style = {
                'textalign': 'left',
                'font-size': 16}),
     dcc.RangeSlider(#Double-ended age range slider
         id = 'age_input',
         min = 25,
         max = 80,
         step = 5,
         value = [min(h_data['Age']), max(h_data['Age'])],
         marks = {
             30:'30',
             40:'40',
             50:'50',
             60:'60',
             70:'70',
             80:'80'
         }
     ),
     html.Div(children = [#Create a sub-division containing all graphs
         html.Div(children = [#Create a sub-division containing categorical indicator graphs
             html.H2('Categorical indicators',
                     style = {
                         'textalign':'left',
                         'font-size': 20,
                         'padding': 10}
                    ), 
             html.Br(),
             html.A('Select a categorical predictor:',
                    style = {'textalign': 'left',
                             'font-size': 16}
                   ),
             dcc.Dropdown(#Dropdown input field to select a categorical predictor
                 id = 'predictors_cat_input',
                 value = hd_predictors_cat_list[0],
                 options = hd_predictors_cat,
                 placeholder = "Select a categorical predictor",
                 searchable = True
             ),
             html.Label('Heart disease sunburst chart:',
                        style = {
                            'textalign': 'left',
                            'font-size': 18}
                       ),
             html.Div(dcc.Graph(id = 'sb_chart')),#Sunburst chart
             html.Label('Heart disease bar chart:',
                        style = {
                            'textalign': 'left',
                            'font-size': 18}
                       ),
             html.Div(dcc.Graph(id = 'bar_chart'))#Bar chart
         ], 
                  style = {'width': '200px', 'margin-left': 0,'padding':10, 'flex':1}),
         html.Div(children = [#Create a sub-division containing numerical indicator graphs
             html.H2('Numerical indicators',
                     style = {
                         'textalign':'left',
                         'font-size': 20,
                         'padding': 10}
                    ),
             html.Br(),
             html.A('Select two numerical predictors for the scatter plot:',
                    style = {
                        'textalign': 'left',
                        'font-size': 16}
                   ),
             dcc.Dropdown(#Dropdown input field to select a numerical predictor for the scatter plot
                 id = 'predictors_num_input1',
                 value = hd_predictors_num_list[0],
                 options = hd_predictors_num,
                 placeholder = "Select a numerical predictor",
                 searchable = True
             ),
             dcc.Dropdown(#Dropdown input field to select a second numerical predictor for the scatter plot
                 id = 'predictors_num_input2',
                 value = hd_predictors_num_list[1],
                 options = hd_predictors_num,
                 placeholder = "Select another numerical predictor",
                 searchable = True
             ),
             dcc.Checklist(#Check box to ask for a local regression curve
                 id = 'loess_check',
                 options = [{'label':'Loess (optional)', 'value':'loess'}]
             ),
             html.Div(#Fraction selection if loess has been selected
                 id = 'loess_option',
                 children = [
                     html.A('Select the fraction of data used for the loess (0 to 1):',
                            style = {'textalign': 'left',
                                     'font-size': 16}
                           ),
                     dcc.Input(
                         id = 'loess_frac',
                         pattern = '(0.?\d*)|1',#Any number between 0 and 1, inclusive
                         value = 0
                     )                     
                 ],
                 hidden = True
             ),
             html.Br(),
             html.Label('Heart disease scatter plot:',
                        style = {
                            'textalign': 'left',
                            'font-size': 18}
                       ),
             html.Div(dcc.Graph(id = 'scatter_plot')),#Scatter plot
             html.Br(),
             html.A('Select a numerical predictor for the box plot:',
                    style = {
                        'textalign': 'left',
                        'font-size': 16}
                   ),
             dcc.Dropdown(#Dropdown input field to select a numerical predictor for the box plot
                 id = 'predictors_num_input',
                 options = hd_predictors_num,
                 value = hd_predictors_num_list[0],
                 placeholder = "Select a numerical predictor",
                 searchable = True
             ),
             html.Label('Heart disease box plot:',
                        style = {
                            'textalign': 'left',
                            'font-size': 18}
                       ),
             html.Div(dcc.Graph(id = 'box_plot'))#Box plot
         ],style={'width': '200px', 'margin-left': 0,'padding':10, 'flex':1})
     ],
              style={'display': 'flex', 'flex-direction': 'row'})#Ensures the two subdivisions created for graphs appear side by side
    ])                      

#Suburst chart callback
@app.callback(Output(component_id = 'sb_chart', component_property = 'figure'),
              [Input(component_id = 'sex_input', component_property = 'value'),
               Input(component_id = 'age_input', component_property = 'value'),
               Input(component_id = 'predictors_cat_input', component_property = 'value')
              ])
def get_sb_chart(sex, age, predictor):
    if sex == 'Any':
        px_data = h_data[h_data['Age'].between(age[0],age[1])]
    else:
        px_data = h_data[(h_data['Sex']==sex) & (h_data['Age'].between(age[0],age[1]))]
        
    px_data['HeartDisease'] = px_data['HeartDisease'].astype('str')
    fig = px.sunburst(px_data, path = ('HeartDisease', predictor),
                color = 'HeartDisease',
                color_discrete_map={'0':'blue', '1':'red'})
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
               Input(component_id = 'loess_check', component_property = 'value'),
               Input(component_id = 'loess_frac', component_property = 'value')
              ])
def get_scatter_plot(sex, age, predictor1, predictor2, loess_check, frac):
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
    
    if loess_check == ['loess']: #Adds loess line plot if selected
        loess = sm.nonparametric.lowess(
            px_data[predictor2],
            px_data[predictor1],
            frac = float(frac)
        )
        
        fig.add_trace(
            px.line(
                x = loess[:,0], 
                y = loess[:,1], 
                color_discrete_sequence=['black'], 
                labels = {"y":'Loess'}
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

#Loess fraction selection div callback
@app.callback(Output(component_id = 'loess_option', component_property = 'hidden'),
              Input(component_id = 'loess_check', component_property = 'value')
             )
def get_frac_div(loess_check): #Hides or shows the fraction field for the loess plot
    if loess_check == ['loess']:
        return False
    else:
        return True

#Run the app
if __name__ == '__main__':
    app.run_server(debug = True)