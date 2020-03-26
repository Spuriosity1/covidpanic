from covidlib import *

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats




COVID_URL = 'https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/'
CONFIRMED_EXTENSION = 'time_series_covid19_confirmed_global.csv'
DEATH_EXTENSION = 'time_series_covid19_deaths_global.csv'



class CovidData(object):
    """Has methods for pulling data, plotting and doing analysis."""

    def __init__(self):
        self.conf_url = COVID_URL + CONFIRMED_EXTENSION
        self.dead_url = COVID_URL + DEATH_EXTENSION
        self.loaded = {}
        self.D = {
            'confirmed': ('confirmed', 'confirmedTime', 'COVID-19 Confirmed Cases'),
            'deaths': ('deaths', 'deathsTime', 'COVID-19 Deaths')
            }
        self.pull()

    def pull(self):
        self.conf = pull_data(self.conf_url)
        self.dead = pull_data(self.dead_url)


    def parse_label(self, country, locale, case):
        try:
            if locale is None:
                if type(case['labels'][country]) is int:
                    X = case['data'][case['labels'][country]]
                elif type(case['labels'][country]) is dict:
                    X = np.zeros_like(case['data'][0,:])
                    for l in case['labels'][country]:
                        X += case['data'][case['labels'][country][l]]
                else:
                    print("Unexpected type found in case_labels")
            else:
                X = case['data'][case['labels'][country][locale]]
        except KeyError:
            try:
                choice = case['labels'][country].keys()
                print('Available locales in ' + country + ':')
                print(choice)
            except KeyError:
                choice = case['labels'].keys()
                print('Available countries:')
                print(case['labels'].keys())
        else:
            return X

    def load(self, country, locale=None):
        l = country if locale is None else locale+', '+country
        self.loaded[l]={}
        for metric, c in zip(['confirmed','deaths'], [self.conf, self.dead]):
            self.loaded[l][metric]= self.parse_label(country, locale, c)
            self.loaded[l][metric+'Time']=c['tseries']

    def plot(self, metric='confirmed', cutoff=None):
        # metric may be confirmed or deaths
        # cutoff specified min cases
        Y_key, T_key, title = self.D[metric]

        for l in self.loaded:
            Y = self.loaded[l][Y_key]
            T = self.loaded[l][T_key]

            if cutoff is not None:
                T = T[Y>=cutoff]
                T = T-T[0]
                Y = Y[Y>=cutoff]

            plt.plot( T, Y, '--', label = l, color =colour_from_str(l) )

        plt.title(title)
        plt.legend()
        plt.xticks(rotation=45)
        plt.show()

    def analysis(self, metric='confirmed', cutoff=100):
        # Does not accept both.
        for l in self.loaded:
            X = self.loaded[l][metric]
            T = self.loaded[l][metric+'Time']
            if cutoff is not None:
                # Truncate to only values higher than the cutoff
                T = T[X>=cutoff]
                T = T - T[0]
                X = X[X>=cutoff]

            logX = np.log(X)
            slope, intercept, r_value, p_value, std_err = stats.linregress(T,logX)
            print('Doubling time is ', np.log(2)/slope)



d = CovidData()


d.load('australia', 'victoria')
d.load('australia', 'new south wales')
d.load('malaysia')

d.plot()
d.analysis()
