import numpy as np
import matplotlib.pyplot as plt
from astropy.timeseries import LombScargle
import streamlit as st

# some statements to make the figures look nicer 
plt.rcParams.update({'axes.linewidth' : 1.5,
                     'ytick.major.width' : 1.5,
                     'ytick.minor.width' : 1.5,
                     'xtick.major.width' : 1.5,
                     'xtick.minor.width' : 1.5,
                     'xtick.labelsize': 12, 
                     'ytick.labelsize': 12,
                     'axes.labelsize': 18,
                     'axes.labelpad' : 5,
                     'axes.titlesize' : 22,
                     'axes.titlepad' : 10,
                     'font.family': 'Serif'
                    })

red = "#CA0020"
orange = "#F97100" 
blue = "#0571b0"

# Function to simulate the time series and compute Lomb-Scargle
def plot_lomb_scargle(length, num_observations, period, phase, y_noise_std, t_noise_std, day_fraction, irregular, logy):
    # Generate time series (regular or irregular)
    if irregular:
        t = np.sort(np.random.uniform(0, length*24, num_observations))
    else:
        t = np.linspace(0, length*24, num_observations)

    np.random.seed(0)
    
    # Generate sine wave with random noise
    y_sine = np.sin(2 * np.pi * t / period + phase)
    y_sine += np.random.normal(0, y_noise_std, len(t))
    
    # Apply noise to time values
    t += np.random.normal(0, t_noise_std, len(t))
    
    # Apply day/night cycle 
    mask = np.sin(2 * np.pi * t / 24) > np.cos(np.pi * day_fraction)
    y_sine_day_night = y_sine * mask 
    
    # Compute Lomb-Scargle periodogram
    frequency, power = LombScargle(t[mask], y_sine_day_night[mask], y_noise_std).autopower() if len(mask) > 10 else ([], [])

    # Plot the time series
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))
    
    idx = np.argsort(t)
    t = t[idx]
    y_sine_day_night = y_sine_day_night[idx]
    ax1.plot(t, y_sine_day_night, c='lightgray')
    idx2 = y_sine_day_night != 0
    if len(idx2) > 0:
        ax1.plot(t[idx2], y_sine_day_night[idx2], '.', c='dodgerblue', ms=3)
    ax1.set_title('Time Series')
    ax1.set_xlabel('Time [hr]')
    ax1.set_ylabel('Amplitude')

    # Plot Lomb-Scargle periodogram
    if len(frequency) > 0:
        ax2.plot(frequency, power, c='dodgerblue', alpha=0.8, lw=2)
    else:
        ax2.plot([], [])
    ax2.axhline(0, ls='--', lw=1.5, c='k', zorder=-9999)
    ax2.axvline(1/period, ls='-', c='orange', lw=3, zorder=-999, label='True period')
    if day_fraction < 1:
        ax2.axvline(np.abs(1/period - 1/24), ls='--', c='darkred', zorder=-999, label=r'Daily alias |1/p $-$ 1/day|', alpha=0.8)
        ax2.axvline(1/period + 1/24, ls=':', c='darkred', zorder=-999, label=r'Daily alias (1/p + 1/day)', alpha=0.8)
    
    if not irregular:
        ax2.axvline(1/35.17 + 1/(np.max(t)/len(t)), ls='--', c='darkgray', zorder=-999, label='Sampling alias (1/p + 1/sampling)')
        ax2.axvline(1/35.17 + 2/(np.max(t)/len(t)), ls=':', c='darkgray', zorder=-999, label='Sampling alias (1/p + 2/sampling)')

    ax2.legend(loc='best')
    ax2.semilogx()

    if logy:
        ax2.semilogy()
    #else: 
        #ax2.set_ylim([-0.08, np.max(power)*1.1])

    ax2.set_title('Lomb-Scargle Periodogram')
    ax2.set_xlabel('Frequency [1/hr]')
    ax2.set_ylabel('Power')

    plt.tight_layout()
    st.pyplot(fig)

# Streamlit App
st.title("Lomb-Scargle Periodogram of a Sine Wave with a Day/Night Cycle")

# Move user inputs to the sidebar
st.sidebar.title("Controls")

# Sidebar user inputs for the parameters
length = st.sidebar.slider('Length of Observation [days]', min_value=1, max_value=365*2, value=12, step=1)
num_observations = st.sidebar.slider('Number of Observations', min_value=10, max_value=10000, value=5000, step=10)
period = st.sidebar.slider('Period [hrs]', min_value=0.1, max_value=100.0, value=9.8, step=0.1)
phase = st.sidebar.slider('Phase [radians]', min_value=0.0, max_value=2 * np.pi, value=0.0, step=0.1)
y_noise_std = st.sidebar.slider('y noise std', min_value=0.0, max_value=10.0, value=0.0, step=0.1)
t_noise_std = st.sidebar.slider('t noise std', min_value=0.0, max_value=10.0, value=0.0, step=0.1)
day_fraction = st.sidebar.slider('Day/Night Duty Cycle', min_value=0.05, max_value=1.0, value=0.5, step=0.05)
irregular = st.sidebar.checkbox('Irregular Spacing', value=False)
logy = st.sidebar.checkbox('log power', value=False)

# Generate and plot results based on user input
plot_lomb_scargle(length, num_observations, period, phase, y_noise_std, t_noise_std, day_fraction, irregular, logy)
