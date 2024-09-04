import numpy as np
from utils import analysis_respiration_phase_angle as resp
import matplotlib.pyplot as plt
from pathlib import Path

def respiration_to_phase_angle(figpath):

    # Parameters for simulation of respiratory data
    time = np.linspace(0, 50, 500)  # 100 seconds, 1000 samples
    frequency = 0.1
    base_amplitude = 7    
    noise_level = 0.2   # noise level

    # Create a varying amplitude over time
    amplitude_variation = 1 + 0.3 * np.sin(2 * np.pi * 0.01 * time)  # slow variation of amplitude
    amplitude = base_amplitude * amplitude_variation  # time-varying amplitude

    # Simulate the respiratory flow data
    respiration_timecourse = amplitude * np.sin(2 * np.pi * frequency * time) + noise_level * np.random.randn(time.size)

    # Extract normalized timecourse and phase angle
    normalised_ts, peaks, troughs, phase_angle = resp.extract_phase_angle(respiration_timecourse, widths=10)

    # Create a figure and axis
    fig, ax1 = plt.subplots(figsize=(8, 5), dpi=300)

    # Plot normalized respiratory timecourse on the primary y-axis
    ax1.plot(normalised_ts, lw=2, color="grey", alpha=0.5)
    ax1.set_xlim(0, 430)
    ax1.set_ylim(-2, 2)
    ax1.set_ylabel("Respiration (Z-score)", color="grey", zorder=-2)
    ax1.tick_params(axis='y', labelcolor="grey")
    
    # Hide the x-axis labels and ticks
    ax1.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)

    # Create a secondary y-axis to plot the phase angle
    ax2 = ax1.twinx()
    ax2.plot(phase_angle, lw=2, color="darkgreen", alpha=0.4)
    ax2.axhline(0, color="grey", ls="--", lw=1, zorder=-1)
    ax2.set_ylabel("Phase angle", color="darkgreen")
    ax2.set_ylim(-3.3, 3.3)
    ax2.tick_params(axis='y', labelcolor="darkgreen")

    # Add events to the phase angle plot
    events = [0, 1, 1]
    samples = [50, 258, 420]

    tmp_phase_angle = [phase_angle[i] for i in samples]
    ax2.scatter(samples, tmp_phase_angle, c = events, zorder=1, alpha = 1)


    # Add legend to the phase angle plot
    ax2.legend(loc="upper right")

    # Save the combined figure
    plt.savefig(figpath / "phase_angle_example")

    plt.close()


if __name__ in "__main__":
    path = Path(__file__)
    figpath = path.parent / "fig"

    if not figpath.exists():
        figpath.mkdir(parents=True)

    respiration_to_phase_angle(figpath=figpath)