import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate, signal
import pandas as pd

def extract_phase_angle(resp_timeseries:np.array, widths = 500, min_sample = 100, figpath = None):
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
        normalised_ts, peaks, troughs, phase_angle
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
    print("done with linear interpolation")

    # normalize the interpolated time series
    normalised_ts = (r - np.nanmean(r)) / np.nanstd(r)
    print("done normalising")

    # finding peaks and troughs
    print("Started looking for peaks")
    peaks = signal.find_peaks_cwt(normalised_ts, widths = widths)

    # if any two peaks are within the sample limit of eachother, remove the last peak
    peaks = [peaks[i] for i in range(len(peaks)) if i == 0 or (peaks[i] - peaks[i-1]) > min_sample]


    # old way of doing it -> peaks = signal.find_peaks(normalised_ts)[0] figure out what works best on data!!
    print("Done looking for peaks")
    troughs = np.array([], dtype = int)

    for peak1, peak2 in zip(peaks, peaks[1:]):                  # finding the troughs -> the minimum between the peaks
        tmp_resp = normalised_ts[peak1:peak2]                   # respiration time course between the peaks

        # DIFFERENT WAYS OF FINDING TROUGH

        # take the index in the middle between the two peaks
        #trough_ind = peak2 - peak1

        # finding minimum between two peaks
        trough_ind_tmp = np.where(tmp_resp == min(tmp_resp))
        try:
            trough_ind = int(trough_ind_tmp[0] + peak1)                # get the index relative to the entire time series
        except TypeError:
            trough_ind = int(np.mean(trough_ind_tmp[0]) + peak1) 
            print(trough_ind_tmp[0])


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



def sanity_check_phase_angle(resp_timeseries = None, normalised_ts = None, peaks = None, troughs = None, phase_angle = None, savepath = None):
    fig, ax = plt.subplots(1, 1, figsize = (40, 4), dpi = 300)

    for var, label, color in zip([resp_timeseries, normalised_ts, phase_angle], ["original timeseries", "normalised interpolated timeseries", "phase angle"], ["darkblue", "forestgreen", "k", "grey"]):
        if var is not None:
            ax.plot(var, label = label, linewidth=1, color = color, alpha = 0.6)
    
    for var, label in zip([peaks, troughs], ["peaks", "troughs"]):
        tmp_y = [normalised_ts[i] for i in var]
        ax.scatter(var, tmp_y, zorder=1, alpha=0.5, s=2, label = label)

    ax.legend()

    ax.set_xlim((0, len(normalised_ts))) # will give problems if normalised timeseries is not provided...

    plt.tight_layout()

    if savepath:
        plt.savefig(savepath)

    else:
        return fig, ax


def summary_plots(peaks, troughs, phase_angle, savepath = None):
    fig, axes = plt.subplots(2, 2, figsize = (10, 8), dpi = 300, sharey = "row")

    # time between peaks and troughs
    peak_to_trough = []
    trough_to_peak = []
    peak_to_peak = []
    trough_to_trough = []

    hz = 1/100

    for peak, trough in zip(peaks, troughs):
        peak_to_trough.append((trough - peak)*hz)

    for peak, trough in zip(peaks[1:], troughs):
        trough_to_peak.append((peak - trough)*hz)

    for peak1, peak2 in zip(peaks, peaks[1:]):
        peak_to_peak.append((peak2 - peak1)*hz)

    for trough1, trough2 in zip(troughs, troughs[1:]):
        trough_to_trough.append((trough2 - trough1)*hz)

    for ax, data, label in zip(axes.flatten(), [peak_to_trough, trough_to_peak, peak_to_peak, trough_to_trough], ["peak and trough", "trough and peak", "peaks", "troughs"]):
        ax.scatter(range(len(data)), data, s=2)
        ax.set_title(f"Time between {label}")
        ax.set_ylabel("Time (s)")
        ax.set_xlabel("No respiratory cycle")
        ax.axhline(0, linestyle = "--", alpha = 0.5, color = "k", linewidth = 1)
    
    plt.tight_layout()

    if savepath:
        plt.savefig(savepath)


def phase_angle_events(phase_angles:np.array, events:np.array): # come up with a better name for this function
    
    df = pd.DataFrame()

    for event in events:
        sample, _, trigger = event
        try: 
            new_data = pd.DataFrame.from_dict({
                "phase_angle": [phase_angles[sample]],
                "trigger": [trigger],
                "sample": [sample]
            })

            df = pd.concat([df, new_data])
        except:
            print(f"failed on sample {sample}, length of phase angle: {len(phase_angles)}")
    return df