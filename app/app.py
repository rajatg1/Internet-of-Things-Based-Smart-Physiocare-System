import json
import time
import datetime
from random import randint
from firebase import firebase
import requests
import plotly
import plotly.plotly as py
import collections
import plotly.graph_objs as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from lib import firebasepy as fbpy
import pprint


firebase_url = 'https://rehab-thing.firebaseio.com'
fb = firebase.FirebaseApplication(firebase_url, None)

def init():
    plotly.tools.set_credentials_file(username='tseph', api_key='kwgMYM5MjnjUB7wtTmbq')


def send(iterations):
    for i in range(0, iterations):
        now = int(time.time())
        datum = {'sensor' : 'myoware', 'time' : now, 'emg' : randint(200, 700), 'threshold' : True}
        try:
            result = fb.post('/emg', data=json.dumps(datum))
            print(result)
        except IOError as e:
            print(e.message)
        time.sleep(1)


def get():
    fb = firebase.FirebaseApplication(firebase_url, None)
    result = fb.get('/emg', None)

    th = 1000
    dict = {}
    for id in result:
        item = json.loads(result[id])
        dict[item['time']] = item['emg']
        if item['threshold'] == True:
            th = min(th, item['emg'])
    # print(dict)
    odict = collections.OrderedDict(sorted(dict.items()))
    return odict, th


def plot(data, th):
    # keys = map(lambda key: datetime.datetime.utcfromtimestamp(key), list(data.keys()))

    trace = go.Scatter(
        # x = keys,
        x = list(data.keys()),
        y = list(data.values()),
        mode = 'lines+markers',
        name = 'emg'
    )
    line = go.Scatter(
        x = list(data.keys()),
        y = [th] * len(data),
        mode = 'lines',
        name = 'threshold'
    )
    return [trace, line]


def threshold(data, th):
    threshold = []
    for key, value in data.iteritems():
        if value > th:
            threshold.append(dict(
                time = key,
                # time = datetime.datetime.utcfromtimestamp(key),
                emg = value))
    return threshold


def annotations():
    th = threshold(*get())
    annotations = []
    for pair in th:
        annotations.append(
            dict(
                x = pair['time'],
                y = pair['emg'],
                xref = 'x',
                yref = 'y',
                text = 'rep',
                showarrow = True,
                arrowhead = 7,
                ax = 0,
                ay = -40
            )
        )
    return annotations


def header():
    return html.Div([
            html.Img(
                src='https://i.pinimg.com/736x/54/8d/8d/548d8d8d045f669c1f96af62b5a761f7--interactive-museum-science-museum.jpg',
                className='two columns',
                style={
                    'height': '60',
                    'width': '160',
                    'float': 'left',
                    'position': 'relative',
                },
            ),
            html.H1(
                'Smart Rehab Manager',
                className='eight columns',
                style={'text-align': 'center'}),
            html.Img(
                src='https://i.pinimg.com/736x/54/8d/8d/548d8d8d045f669c1f96af62b5a761f7--interactive-museum-science-museum.jpg',
                className='two columns',
                style={
                    'height': '60',
                    'width': '160',
                    'float': 'right',
                    'position': 'relative',
                },
            ),
        ],
            className='row')


def hr():
    return html.Hr(
            style={'margin': '0', 'margin-bottom': '5'})


app = dash.Dash()

# style
external_css = ['https://fonts.googleapis.com/css?family=Overpass:300,300i',
                'https://cdn.rawgit.com/plotly/dash-app-stylesheets/dab6f937fd5548cebf4c6dc7e93a10ac438f5efb/dash-technical-charting.css']

for css in external_css:
    app.css.append_css({'external_url' : css})

# layout
app.layout = html.Div(
    [
        header(),
        hr(),
        html.Div([
            dcc.Graph(
                id='emg-readings',
                figure={'data': plot(*get()),
                        'layout' : {
                            'annotations' : annotations()}
                        }),
            dcc.Interval(
                id='interval-component',
                interval=4*1000,
                n_intervals=0
            )
        ])
    ],
    style={
        'width': '85%',
        'max-width': '1400',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'font-family': 'overpass',
        'background-color': '#F3F3F3',
        'padding': '40',
        'padding-top': '20',
        'padding-bottom': '20'
    }
)


if __name__ == '__main__':
    # init()
    # send(100)

    # traces = plot(get())
    # py.plot(traces, filename='example')
    app.run_server(debug=True)
