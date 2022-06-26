""" Signal processing library
"""
import numpy as np
from obspy import read, UTCDateTime

def preprocess(stream, samp_rate, freq_band):
    # time alignment
    start_time = max([trace.stats.starttime for trace in stream])
    end_time = min([trace.stats.endtime for trace in stream])
    if start_time>=end_time: print('bad data!'); return []
    st = stream.slice(start_time, end_time)
    # resample data
    samp_rate = int(samp_rate)
    org_rate = int(st[0].stats.sampling_rate)
    if org_rate!=samp_rate: st = st.interpolate(samp_rate)
    for ii in range(3):
        st[ii].data[np.isnan(st[ii].data)] = 0
        st[ii].data[np.isinf(st[ii].data)] = 0
    # filter
    st = st.detrend('demean').detrend('linear').taper(max_percentage=0.05, max_length=10.)
    freq_min, freq_max = freq_band
    if freq_min and freq_max:
        return st.filter('bandpass', freqmin=freq_min, freqmax=freq_max)
    elif not freq_max and freq_min:
        return st.filter('highpass', freq=freq_min)
    elif not freq_min and freq_max:
        return st.filter('lowpass', freq=freq_max)
    else:
        print('filter type not supported!'); return []

def sac_ch_time(st):
    for tr in st:
        t0 = tr.stats.starttime
        tr.stats.sac.nzyear = t0.year
        tr.stats.sac.nzjday = t0.julday
        tr.stats.sac.nzhour = t0.hour
        tr.stats.sac.nzmin = t0.minute
        tr.stats.sac.nzsec = t0.second
        tr.stats.sac.nzmsec = t0.microsecond / 1e3
    return st

