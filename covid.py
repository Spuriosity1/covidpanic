from covidlib import *

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats




COVID_URL = 'https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/'
CONFIRMED_EXTENSION = 'time_series_covid19_confirmed_global.csv'
DEATH_EXTENSION = 'time_series_covid19_deaths_global.csv'
RECOVERED_EXTENSION = 'time_series_covid19_recovered_global.csv'



class CovidData(object):
    """Has methods for pulling data, plotting and doing analysis."""

    def __init__(self):
        self.conf_url = COVID_URL + CONFIRMED_EXTENSION
        self.dead_url = COVID_URL + DEATH_EXTENSION
        self.recv_url = COVID_URL + RECOVERED_EXTENSION
        self.loaded = {}
        self.D = {
            'confirmed': ('confirmed', 'confirmedTime', 'COVID-19 Confirmed Cases'),
            'deaths': ('deaths', 'deathsTime', 'COVID-19 Deaths'),
            'recovered': ('recovered', 'recoveredTime', 'COVID-19 Recovered')
            }
        self.assume = {
            'incubation_days': 7
        }
        self.colour_offset = -5
        self.pull()

    def pull(self):
        old_conf = ''
        old_dead = ''

        if hasattr(self, 'conf') and hasattr(self,'dead'):
            old_conf = str(self.conf['tseries'][-1])[:10]
            old_dead = str(self.dead['tseries'][-1])[:10]

        self.conf = pull_data(self.conf_url, '%m/%d/%y')
        self.dead = pull_data(self.dead_url, '%m/%d/%y')

        new_conf = str(self.conf['tseries'][-1])[:10]
        new_dead = str(self.dead['tseries'][-1])[:10]

        print("Updated databases")
        print("   > Confirmed "+old_conf+" -> ",new_conf)
        print("   > Deaths    "+old_dead+" -> ",new_dead)
        # self.recv = pull_data(self.recv_url, '%m/%d/%Y')
        print()

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

    def load(self, country):
        if type(country) is list:
            for c in country:
                self.load(c)
            return
        elif type(country) is tuple:
            locale=country[1]
            country=country[0]
            l = locale+', '+country
        elif type(country) is str:
            l = country
            locale=None

        self.loaded[l]={}
        for metric, c in zip(['confirmed','deaths'], [self.conf, self.dead]):
            self.loaded[l][metric]= self.parse_label(country, locale, c)
            self.loaded[l][metric+'Time']=c['tseries']

    def unload(self, country=None):
        if type(country) is list:
            for c in country:
                self.unload(c)
            return
        elif type(country) is tuple:
            del self.loaded[country[1]+', '+country[0]]
        elif type(country) is str:
            del self.loaded[country]
        else:
            self.loaded={}



    # def unload(self, country=None, locale=None):
    #     if country is None:
    #         self.loaded = {}
    #     elif locale is None:
    #         del self.loaded[country]
    #     else:
    #         del self.loaded[locale+', '+country]

    def get_loaded(self):
        for l in self.loaded:
            print('['+l+']')

    def plot(self, metric='confirmed', Ycutoff=None, num_days=None, label=True, style=None):
        # metric may be confirmed or deaths
        # cutoff specified min cases
        Y_key, T_key, title = self.D[metric]

        for l in self.loaded:
            Y = self.loaded[l][Y_key]
            T = self.loaded[l][T_key]

            if style is None:
                style = {'confirmed': '--', 'deaths': '-', 'recovered': ':'}[metric]

            T, Y = trim(T, Y, num_days, Ycutoff)

            plt.plot( T, Y, style, label = l if label else None,
                color =colour_from_str(l, self.colour_offset) )

        plt.title(title)
        plt.legend()
        plt.xticks(rotation=45)
        plt.yscale('log')
        plt.show()

    def analysis(self, metric='confirmed', Ycutoff=100, num_days=None, plot=True):
        if num_days is not None:
            print("Using last {0} days' data.\n".format(num_days))

        if plot:
            plt.clf()

        Y_key, T_key, title = self.D[metric]

        max_T = 0

        for l in self.loaded:
            print('['+l+']')
            Y = self.loaded[l][Y_key]
            T = self.loaded[l][T_key]

            T, Y = trim(T, Y, num_days, Ycutoff, compare=True)

            max_T = max_T if T.shape[0] <= max_T else T.shape[0]

            if Y.shape[0] == 0:
                print('Could not find any points above the Y-cutoff.')
                return

            logY = np.log(Y)
            slope, intercept, r_value, p_value, std_err = stats.linregress(T,logY)
            print('   > Doubling time is {0:.1f} days'.format(np.log(2)/slope))
            num_current_infected = np.exp(intercept + slope*(T[-1]+self.assume['incubation_days']))
            print('   > Estimated current infected is {0:,}'.format(int(num_current_infected)))

            if plot:
                plt.plot( T, Y, '-', label = l,
                    color =colour_from_str(l, self.colour_offset) )
                plt.plot( T, np.exp(slope*T + intercept), '--',
                    color =colour_from_str(l, self.colour_offset) )

        if plot:
            DTIMES = [2,3,7]
            T = np.arange(max_T)
            for tau in DTIMES:
                plt.plot(T, Ycutoff*np.power(2,T/tau), 'k:')
            plt.xlabel('Days after hitting %d cases' % Ycutoff)
            plt.title(title)
            plt.legend()
            plt.yscale('log')
            plt.show()



d = CovidData()

plt.clf()
d.load('australia')
d.load('us')
d.load('denmark')
d.load('united kingdom')
d.load('austria')

d.plot('deaths')
d.analysis()
