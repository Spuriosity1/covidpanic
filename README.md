# covidpanic
A small python 3 script for plotting the terrifying progress of the virus.

##Intended workflow:
1. Run the script from `ipython --matplotlib`
2. plot('country_name', [locale, e.g. state], metric=('confirmed'|'deaths'))
3. Optionally, format the graph with plt.yscale('log')

##Dependencies
`NumPy`, `matplotlib`, `requests`

Tested on OSX with Homebrew ipython 7.3.0
