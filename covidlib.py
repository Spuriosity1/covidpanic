import requests
import csv
import io
import numpy as np
from datetime import datetime

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

    return {'tseries': tseries, 'data': np.array(data, dtype='int'), 'labels': dataLabels}

def colour_from_str(s):
    n = 0
    i=0
    for c in s:
        n = n+(ord(c)-97)*26**i
        i += 1

    n = (n*15485863)%(16**6)
    return '#{0:0{1}X}'.format(n,6)
