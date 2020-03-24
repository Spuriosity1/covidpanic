import requests
import csv
import io
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime


COVID_URL = 'https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/'
CONFIRMED_EXTENSION = 'time_series_covid19_confirmed_global.csv'
DEATH_EXTENSION = 'time_series_covid19_deaths_global.csv'

HELPTEXT = {}

# Update working database
def pull_data(url):
    r = requests.get(url, allow_redirects=True)
    if r.status_code != 200:
        print("Error: bad request")
    f = io.StringIO(r.text)
    dataLabels = {}
    reader = csv.reader(f, delimiter=',')

    data=[]
    tseries = np.empty((0,))

    idx = -1
    for row in reader:
        if idx == -1:
            # First row, the time series labels
            t = [datetime.strptime(d, '%m/%d/%y').strftime('%Y-%m-%d') for d in row[4:]]
            tseries = np.array(t,dtype='datetime64')
            idx=0
            continue

        country = row[1].lower()
        locale = row[0].lower()

        if country in dataLabels:
            # row[1] is country code
            dataLabels[country][locale] = idx
        else:
            dataLabels[country] = {}
            if locale == '':
                #Only country-level info available
                dataLabels[country] = idx
            else:
                dataLabels[country][locale] = idx

        data.append(row[4:])
        idx += 1

    return (tseries, np.array(data, dtype='int'), dataLabels)



def plot(country, locale=None, metric='confirmed'):
    url = COVID_URL
    if metric == 'confirmed':
        url += CONFIRMED_EXTENSION
    elif metric == 'deaths':
        url += DEATH_EXTENSION
    else:
        print('select `confirmed` or `deaths`')
        raise ValueError

    case_t, case, case_labels = pull_data(url)

    text = ''

    try:
        if locale is None:
            text += country
            if type(case_labels[country]) is int:
                X = case[case_labels[country]]
            elif type(case_labels[country]) is dict:
                X = np.zeros_like(case[0,:])
                for l in case_labels[country]:
                    X += case[case_labels[country][l]]
            else:
                print("Unexpected type found in case_labels")
        else:
            text += country +' - '+locale
            X = case[case_labels[country][locale]]
    except KeyError:
        try:
            print(case_labels[country].keys())
        except KeyError:
            print(case_labels.keys())
    else:
        plt.plot(case_t, X, '-' if metric is 'deaths' else '--',label = text)
        formatting()

def formatting():
    plt.legend()
    plt.title('COVID-19 confirmed cases')
    plt.xticks(rotation=45)
    plt.show()

# HELPTEXT['help'] = {'args': ['command'], 'text': 'Get detailed help for [command]'}
# def help(cmd):
#     str = ''
#     if cmd in HELPTEXT:
#         str += '!virus %s' % cmd
#         for a in HELPTEXT[cmd]['args']:
#             str += ' [%s]' % a
#         str += ': %s\n' % HELPTEXT[cmd]['text']
#     else:
#         str += 'Virus commands:\n\n'
#         for text in HELPTEXT:
#             str += '!virus %s' % text
#             for a in HELPTEXT[text]['args']:
#                 str += ' [%s]' % a
#             str += '\n'
#     return str
