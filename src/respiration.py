import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate, signal
from scipy.stats import gaussian_kde
import pandas as pd
import cmath




def eulers_formula(angle: float) -> complex:
    return cmath.exp(1j * angle)

def average_vectors(vectors) -> np.ndarray:
    return sum(vectors) / len(vectors)

def plot_phase_vectors(phase_angles, average_vector = None, ax = None):
    """
    Plot phase vectors and their average on a polar plot.
    """
    if not ax:
        fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(7, 7))

    # Plot each phase angle vector
    for i, angle in enumerate(phase_angles):
        ax.plot([0, angle], [0, 1], color='forestgreen', alpha=0.5, linewidth = 0.5, label='Phase Vector' if i == 0 else "")

    # Plot the average vector
    if average_vector:
        ax.plot([0, cmath.phase(average_vector)], [0, abs(average_vector)], 
                color='red', linewidth=1, label='Average Vector')

    # Configure plot
    ax.legend()

def average_phase_angle(phase_angles):
    """
    Measure consistency in phase angles by averaging vectors in the complex plane.
    Returns the average phase and average magnitude.
    based on this video: https://www.youtube.com/watch?v=R1Pro555H6s

    """
    # Convert phase angles to unit vectors
    unit_vectors = [eulers_formula(angle) for angle in phase_angles]
    
    # Compute the average vector
    average = average_vectors(unit_vectors)
    
    # Compute the phase and magnitude of the average vector
    average_phase = cmath.phase(average)
    average_magnitude = abs(average)
    
    return average_phase, average_magnitude

def plot_average_phase_vectors(phase_angles, magnitiudes, ax = None, color = "red"):
    """
    Plot phase vectors and their average on a polar plot.
    """
    if not ax:
        fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(7, 7))

    # Plot each phase angle vector
    for angle, magni in zip(phase_angles, magnitiudes):
        ax.plot([0, angle], [0, magni], 
            color=color, linewidth=1)

    # Configure plot
    #ax.legend()


def circular_mean(angles: np.ndarray) -> float:
    """
    Calculate the circular mean of an array of angles (in radians).
    
    Parameters:
    angles (np.array): An array of angles in radians.

    Returns:
    float: The circular mean of the angles in radians.
    """
    # Compute the sum of the unit vectors for each angle
    sin_sum = np.sum(np.sin(angles))
    cos_sum = np.sum(np.cos(angles))
    
    # Compute the mean angle in radians
    mean_angle_rad = np.arctan2(sin_sum, cos_sum)
    
    # Ensure the angle is in the range [0, 2*pi)
    if mean_angle_rad < 0:
        mean_angle_rad += 2 * np.pi

    return mean_angle_rad


def polar_density_plot(angles: list[np.ndarray], labels: list[str], plot_circular_mean: bool = True, bw_method = 0.05):
    """
    Plot polar density plots for multiple angle datasets.


    bw_method:
        The method used to calculate the estimator bandwidth. 
        This can be "scott", "silverman", a scalar constant or a callable. If a scalar, this will be used directly as kde.factor. If a callable, it should take a gaussian_kde instance as only parameter and return a scalar. If None (default), "scott" is used.
    """
    fig, ax = plt.subplots(1, 1, figsize=(4, 4), dpi=300, subplot_kw={'projection': 'polar'})

    ax.set_rticks([])  # Remove radial ticks

    # Color palette for multiple sets
    colors = plt.cm.tab10(np.linspace(0, 1, len(angles)))

    for i, (tmp_angles, label) in enumerate(zip(angles, labels)):
        # Scatter plot for data points
        ax.scatter(tmp_angles, [0.1] * len(tmp_angles), s=2, alpha=0.8, color=colors[i], 
                label=f"{label} (n={len(tmp_angles)})")

        # Extend the angles to avoid boundary artifacts
        extended_angles = np.concatenate([tmp_angles + 2 * np.pi, tmp_angles, tmp_angles - 2 * np.pi])

        # Density plot using Gaussian KDE
        density = gaussian_kde(extended_angles, bw_method=bw_method)
        xs = np.linspace(-2 * np.pi, 2 * np.pi, 2000)  # Extend range
        density_vals = density(xs)

        # Mask to plot only [-pi, pi]
        mask = (xs >= -np.pi) & (xs <= np.pi)
        ax.plot(xs[mask], density_vals[mask], color=colors[i], linewidth=1.5)

        # Plot circular mean 
        if plot_circular_mean:
            mean_angle = circular_mean(tmp_angles)
            ax.plot([mean_angle, mean_angle], [0, max(density_vals)], color=colors[i], linestyle='--', linewidth=1)

    # Highlight angular regions
    ax.axvspan(0, np.pi, color="lightgreen", alpha=0.05)
    ax.axvspan(-np.pi, 0, color="lightblue", alpha=0.05)

    ax.legend(loc="upper right")
    plt.tight_layout()
    plt.show()


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
    print("Done with linear interpolation of NaN")

    # normalize the interpolated time series
    normalised_ts = (r - np.nanmean(r)) / np.nanstd(r)
    print("Done normalising")

    # finding peaks and troughs
    print("Looking for peaks - this may take a while")
    peaks = signal.find_peaks_cwt(normalised_ts, widths = widths)#, distance = min_sample)
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


        # other ways??


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
    fig, axes = plt.subplots(2, 1, figsize = (40, 4), dpi = 300)

    for var, label, color in zip([resp_timeseries, normalised_ts], ["original timeseries", "normalised interpolated timeseries"], ["darkblue", "forestgreen", "k"]):
        if var is not None:
            axes[0].plot(var, label = label, linewidth=1, color = color, alpha = 0.6)
    
    for var, label in zip([peaks, troughs], ["peaks", "troughs"]):
        tmp_y = [normalised_ts[i] for i in var]
        axes[0].scatter(var, tmp_y, zorder=1, alpha=0.5, s=2, label = label)

    if phase_angle is not None: 
        axes[1].plot(phase_angle, color = "grey", linewidth = 1)
        axes[1].set_ylabel("phase angle")

    axes[0].legend()

    for ax in axes:
        ax.set_xlim((0, len(normalised_ts))) # will give problems if normalised timeseries is not provided...

    plt.tight_layout()

    if savepath:
        plt.savefig(savepath)

    else:
        return fig, axes


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

def phase_angle_events(phase_angles: np.ndarray, events: np.ndarray, hz: int, event_ids: dict = None):
    """
    Collects phase angle events and returns a DataFrame.

    Args:
        phase_angles (np.ndarray): Array of phase angles.
        events (np.ndarray): Array of events, where each event contains sample, _, trigger.
        hz (int): sample rate.
        event_ids (dict, optional): Mapping of event names to trigger values.

    Returns:
        pd.DataFrame: DataFrame containing phase angles, triggers, and optional event names.
    """

    data = []

    for event in events:
        sample, _, trigger = event
        if sample < len(phase_angles):
            new_data = {
                "phase_angle": phase_angles[sample],
                "trigger": trigger,
                f"sample_{hz}": sample
            }
            data.append(new_data)
        else:
            print(f"Failed on sample {sample}, length of phase angle: {len(phase_angles)}")

    df = pd.DataFrame(data)

    if event_ids:
        # Create reverse mapping from trigger to event name
        trigger_to_event = {v: k for k, v in event_ids.items()}
        
        df["event"] = df["trigger"].map(trigger_to_event).fillna("Unknown")

    return df

