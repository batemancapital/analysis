import numpy as np

import pandas as pd
import pandas_datareader as pd_reader
import matplotlib.pyplot as plt
import datetime
import time
from pandas.plotting import register_matplotlib_converters
import requests_cache
import matplotlib.dates as mdates

import cufflinks as cf
cf.go_offline()

cf.set_config_file(theme='space')


############################## PRELUDE ##############################

# initiate converters
register_matplotlib_converters()

# rc config
plt.rcParams['figure.figsize'] = [20, 8]
plt.rcParams['figure.titlesize'] = 'large'
plt.rcParams['figure.titleweight'] = 'bold'
plt.rcParams['xtick.labelsize'] = plt.rcParams['ytick.labelsize'] = 15
plt.rcParams['axes.titlesize'] = 'large'
plt.rcParams['font.size'] = 20
plt.rcParams['font.weight'] = 'bold'
plt.rcParams['axes.labelweight'] = "bold"
plt.rcParams['axes.titlepad'] = 10
plt.rcParams['axes.titleweight'] = "bold"
plt.rcParams['legend.fontsize'] = 14
plt.rcParams["lines.linewidth"] = 5.0
plt.style.use('dark_background')

expire_after = datetime.timedelta(hours=12)
session = requests_cache.CachedSession(
    cache_name='cache', backend='sqlite', expire_after=expire_after)

start = datetime.datetime(1990, 6, 1)
end = datetime.date.today()


def fred_reader(symbol, start=start):
    return pd_reader.data.DataReader(symbol, 'fred', start, end, session=session)


def fred_reader_series(symbol, start=start):
    return pd_reader.data.DataReader(symbol, 'fred', start, end, session=session)[symbol]


def fred_reader_multi(d, start=start):
    for (name, fred_name) in d.items():
        d[name] = fred_reader_series(fred_name, start)
    return pd.DataFrame(d).dropna()

# forward fill time series with last valid value


def fill(s):
    first, last = s.index[0], s.index[-1]
    rs = s.reindex(pd.date_range(first, last), method='ffill')
    return rs


def yahoo_reader(symbol, start=start):
    return pd_reader.data.DataReader(symbol, "yahoo", start, end, session=session)


def draw_span(ax, begin, end, leftmost, color='tab:grey', alpha=0.3):
    if begin > leftmost:
        ax.axvspan(begin, end, color=color, alpha=alpha)


def plot_recession(ax, leftmost):
    try:
        recs = fred_reader('USREC', start=datetime.datetime(
            1920, 1, 1)).query('USREC==1')
        recs_90 = recs.loc['1990':'1991']
        recs90_bgn = recs_90.index[0]
        recs90_end = recs_90.index[-1]
        draw_span(ax, recs90_bgn, recs90_end, leftmost)
        recs_2k = recs.loc['2001']
        recs2k_bgn = recs_2k.index[0]
        recs2k_end = recs_2k.index[-1]
        draw_span(ax, recs2k_bgn, recs2k_end, leftmost)
        recs_2k8 = recs.loc['2008':]
        recs2k8_bgn = recs_2k8.index[0]
        recs2k8_end = recs_2k8.index[-1]
        draw_span(ax, recs2k8_bgn, recs2k8_end, leftmost)
        plt.text(0, -0.15, "Shaded areas indicate US recessions",
                 horizontalalignment='left',
                 verticalalignment='center',
                 fontsize=14,
                 transform=ax.transAxes)
    except Exception as e:
        print(e)
        pass


def plot_qe(ax, leftmost):
    # Plot QE periods based on https://www.yardeni.com/chronology-of-feds-quantitative-easing/
    try:
        qe1_start = datetime.datetime(2008, 11, 25)
        qe1_end = datetime.datetime(2010, 5, 31)
        draw_span(ax, qe1_start, qe1_end, leftmost,
                  color='tab:orange', alpha=0.3)
        qe2_start = datetime.datetime(2010, 11, 3)
        qe2_end = datetime.datetime(2011, 9, 21)
        draw_span(ax, qe2_start, qe2_end, leftmost,
                  color='tab:orange', alpha=0.3)
        #twist_start = datetime.datetime(2011, 9, 21)
        #twist_end = datetime.datetime(2012, 6, 29)
        #draw_span(ax, twist_start, twist_end, leftmost,
        #          color='tab:olive', alpha=0.3)
        qe3_start = datetime.datetime(2012, 9, 13)
        qe3_end = datetime.datetime(2013, 12, 18)
        draw_span(ax, qe3_start, qe3_end, leftmost,
                  color='tab:orange', alpha=0.3)
        #taper_start = datetime.datetime(2013, 12, 18)
        #taper_end = datetime.datetime(2014, 10, 29)
        #draw_span(ax, taper_start, taper_end, leftmost,
        #          color='tab:pink', alpha=0.3)
        qe4_start = datetime.datetime(2020, 3, 11)
        qe4_end = datetime.datetime.today()
        draw_span(ax, qe4_start, qe4_end, leftmost,
                  color='tab:orange', alpha=0.3)
        plt.text(0, -0.15, "Shaded color areas indicate major Fed QE programs - Twist and Tapering ignored",
                 horizontalalignment='left',
                 verticalalignment='center',
                 fontsize=14,
                 transform=ax.transAxes)
    except Exception as e:
        print(e)
        pass


def add_source(ax, source):
    plt.text(0, -0.1, 'Source: ' + source,
             horizontalalignment='left',
             verticalalignment='center',
             fontsize=14,
             transform=ax.transAxes)
    current_time = time.strftime("%m-%d-%Y %T %Z", time.localtime(time.time()))
    plt.text(1.0, -0.1, 'Date: ' + current_time,
             horizontalalignment='right',
             verticalalignment='center',
             fontsize=14,
             transform=ax.transAxes)
    current_year = time.strftime("%Y", time.localtime(time.time()))
    plt.text(1.0, -0.15, "Copyright © 2019 - " + current_year + " Bateman Capital",
             horizontalalignment='right',
             verticalalignment='center',
             fontsize=14,
             transform=ax.transAxes)
