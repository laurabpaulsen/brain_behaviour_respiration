import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate, signal


def extract_phase_angle(resp_timeseries:np.arrray, figpath = None):
    """ 
    Extracts continuous phase angle for respiration data by running an adapted peak detection algorithm

    Inspired by matlab code by Daniel Kluger (https://github.com/dansimk/oddtap/blob/main/oddtap_02_resppreproc.m)

    Parameters
    ----------
    resp_timeseries : np.array
        an array with the respiratory measurements

    figpath : str or pathlike, default None
        If provided, a plot useful for sanity check of extraction of phase angle is generated and saved to destination

    returns 
    """
    r = resp_timeseries.copy()

    # normalise timeseries and set outliers to NaN
    z_scores = np.abs((r - np.nanmean(r)) / np.nanstd(r))
    print(f"Found {sum(z_scores > 2.5)} outliers")
    r[z_scores > 2.5] = np.nan
    
    # linear interpolation of outlier segments
    nans = np.isnan(r)
    x_vals = np.where(~nans)[0]
    y_vals = r[~nans]
    interpolated_values = interpolate.interp1d(x_vals, y_vals, kind='linear', fill_value="extrapolate")
    r[nans] = interpolated_values(np.where(nans)[0])

    # normalize the interpolated time series
    normalised_ts = (r - np.nanmean(r)) / np.nanstd(r)

    # finding peaks and troughs
    peaks = signal.find_peaks(normalised_ts)[0]
    troughs = np.array([], dtype = int)

    for peak1, peak2 in zip(peaks, peaks[1:]):                  # finding the troughs -> the minimum between the peaks
        tmp_resp = normalised_ts[peak1:peak2]                   # respiration time course between the peaks
        trough_ind_tmp = np.where(tmp_resp == min(tmp_resp))
        trough_ind = int(trough_ind_tmp[0] + peak1)                # get the index relative to the entire time series

        troughs = np.append(troughs, trough_ind) 

    # calculate the phase angle
    phase_angle = np.zeros(len(normalised_ts))
    phase_angle[:] = np.nan # fill with nans
    
    # set troughs to pi and peaks to 0
    phase_angle[troughs], phase_angle[peaks] = np.pi, 0

    # interpolate the phase angle between peaks and troughs
    for peak1, peak2, trough in zip(peaks, peaks[1:], troughs):
        phase_angle[peak1:trough] = np.linspace(0 + np.pi/(trough-peak1), np.pi,  trough-peak1)
        phase_angle[trough:peak2] = np.linspace(-np.pi + np.pi/(peak2-trough), 0, peak2-trough)

    if figpath:
        sanity_check_phase_angle(resp_timeseries, normalised_ts, peaks, troughs, phase_angle, figpath)

    return normalised_ts, peaks, troughs, phase_angle



def sanity_check_phase_angle(resp_timeseries, normalised_ts, peaks, troughs, phase_angle, savepath):
    fig, ax = plt.subplots(1, 1, figsize = (12, 6), dpi = 300)
    ax.plot(resp_timeseries, label = "original timeseries")
    ax.plot(normalised_ts, label = "normalised interpolated timeseries")
    ax.plot(phase_angle, label = "phase_angle", color = "green")
    ax.scatter(peaks, np.zeros(len(peaks)), s = 4, label = "peaks")
    ax.scatter(troughs, np.zeros(len(troughs)), s = 4, label = "troughs")

    ax.legend()

    plt.savefig(savepath)