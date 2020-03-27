import requests
import csv
import io
import numpy as np
from datetime import datetime

# Update working database
def pull_data(url, datefmt):
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
            t = []
            for d in row[4:]:
                t.append(datetime.strptime(d, datefmt).strftime('%Y-%m-%d'))
            # t = [datetime.strptime(d, '%-m/%-d/%Y').strftime('%Y-%m-%d') for d in row[4:]]
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


def colour_from_str(s, colour_offset=0):
    n = 0
    i=0
    for c in s:
        n = n+(ord(c)-97)*26**i
        i += 1

    n = (n*15485863 - colour_offset)%(16**6)
    return '#{0:0{1}X}'.format(n,6)

def trim(T, Y, Tcutoff, Ycutoff):

    if Ycutoff is not None:
        # Truncate to only values higher than the cutoff
        T = T[Y>=Ycutoff]
        T = T - T[0]
        T = T.astype('int64')
        Y = Y[Y>=Ycutoff]

    if Tcutoff is not None:
        if T.shape[0] > Tcutoff:
            T = T[-Tcutoff:]
            Y = Y[-Tcutoff:]

    return (T,Y)
