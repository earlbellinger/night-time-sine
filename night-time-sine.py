import numpy as np
import matplotlib.pyplot as plt
from astropy.timeseries import LombScargle
import streamlit as st

# some statements to make the figures look nicer 
plt.rcParams.update({'axes.linewidth' : 1,
                     'ytick.major.width' : 1,
                     'ytick.minor.width' : 1,
                     'xtick.major.width' : 1,
                     'xtick.minor.width' : 1,
                     'xtick.labelsize': 10, 
                     'ytick.labelsize': 10,
                     'axes.labelsize': 12,
                     'font.family': 'Serif'
                    })

# Function to simulate the time series and compute Lomb-Scargle
def plot_lomb_scargle(length, num_observations, period, phase, y_noise_std, t_noise_std, day_fraction, irregular):
    # Generate time series (regular or irregular)
    if irregular:
        t = np.sort(np.random.uniform(0, length, num_observations))
    else:
        t = np.linspace(0, length, num_observations)

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
    frequency, power = LombScargle(t[mask], y_sine_day_night[mask]).autopower()

    # Plot the time series
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))

    idx = np.argsort(t)
    t = t[idx]
    y_sine_day_night = y_sine_day_night[idx]
    ax1.plot(t, y_sine_day_night, c='lightgray')
    ax1.plot(t[y_sine_day_night != 0], y_sine_day_night[y_sine_day_night != 0], 'b.')
    ax1.set_title('Time Series')
    ax1.set_xlabel('Time [hr]')
    ax1.set_ylabel('Amplitude')

    # Plot Lomb-Scargle periodogram
    ax2.plot(frequency, power)
    ax2.axhline(0, ls='--', c='k', zorder=-99)
    ax2.axvline(1/period, ls='-', c='orange', zorder=-999, label='True period')
    if day_fraction < 1:
        ax2.axvline(np.abs(1/period - 1/24), ls='--', c='red', zorder=-999, label=r'Day/Night Alias |1/p $-$ 1/day|')
        ax2.axvline(1/period + 1/24, ls='-', c='red', zorder=-999, label='Day/Night Alias (1/p + 1/day)')
    
    if not irregular:
        ax2.axvline(1/35.17 + 1/(np.max(t)/len(t)), ls='-', c='darkgray', zorder=-999, label='1/p + 1/sampling')
        ax2.axvline(1/35.17 + 2/(np.max(t)/len(t)), ls='-', c='darkgray', zorder=-999, label='1/p + 2/sampling rate')

    ax2.legend()
    ax2.semilogx()
    ax2.set_title('Lomb-Scargle Periodogram')
    ax2.set_xlabel('Frequency [1/hr]')
    ax2.set_ylabel('Power')

    st.pyplot(fig)

# Streamlit App
st.title("Lomb-Scargle Periodogram of a Sine Wave with a Day/Night Cycle")

# Move user inputs to the sidebar
st.sidebar.title("Controls")

# Sidebar user inputs for the parameters
length = st.sidebar.slider('Length of Observation [hrs]', min_value=10, max_value=1000, value=300, step=10)
num_observations = st.sidebar.slider('Number of Observations', min_value=10, max_value=10000, value=5000, step=10)
period = st.sidebar.slider('Period [hrs]', min_value=0.1, max_value=100.0, value=35.17, step=0.1)
phase = st.sidebar.slider('Phase [radians]', min_value=0.0, max_value=2 * np.pi, value=0.0, step=0.1)
y_noise_std = st.sidebar.slider('Y Noise Std', min_value=0.0, max_value=10.0, value=0.0, step=0.1)
t_noise_std = st.sidebar.slider('T Noise Std', min_value=0.0, max_value=10.0, value=0.0, step=0.1)
day_fraction = st.sidebar.slider('Day/Night Duty Cycle', min_value=0.0, max_value=1.0, value=0.5, step=0.05)
irregular = st.sidebar.checkbox('Irregular Spacing', value=False)

# Generate and plot results based on user input
plot_lomb_scargle(length, num_observations, period, phase, y_noise_std, t_noise_std, day_fraction, irregular)
