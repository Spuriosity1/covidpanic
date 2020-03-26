# covidpanic
A small python 3 script for plotting the terrifying progress of the virus.

## Example workflow:
Firstly, run
`zsh% ipython --matplotlib`
In ipython, run
```python3
In[1]: run covid.py # populates your namespace
In[2]: plot('china', metric='deaths')
In[3]: plot('australia', 'new south wales', metric='confirmed')
In[4]: plt.yscale('log') # Optional log scale for deceiving yourself
```

## Dependencies
`NumPy`, `matplotlib`, `requests`

Tested on OSX with Homebrew ipython 7.3.0
