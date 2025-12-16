import numpy as np
from matplotlib import pyplot as plt
from scipy.signal import argrelextrema
from scipy.optimize import curve_fit

from apps.source.data_processing import rolling_average


def find_heelstrikes_from_z(segments):
    neighbors = 15

    heelstrikes = []
    for seg in segments:
        heelstrikes.append(argrelextrema(seg["Z"].values, np.less, order=neighbors)[0])  # np.less for minima

    return heelstrikes



def sine_function(x, A, B, C, D):
    return A * np.sin(B * x + C) + D

def fit_step_with_sine(segment, segment_heelstrikes):
    start, middle, end = segment_heelstrikes[1], segment_heelstrikes[2], segment_heelstrikes[2]

    segment = rolling_average(segment, 5)

    x = segment["Time"].iloc[start:end]
    y = segment["Y"].iloc[start:end]

    # Initial guess for the parameters [A, B, C, D]
    initial_guess = [2, -1, 0, 0]

    # Perform the curve fitting
    params, covariance = curve_fit(sine_function, x, y, p0=initial_guess)

    # Extract the fitted parameters
    A_fit, B_fit, C_fit, D_fit = params

    print(f"Fitted parameters: A={A_fit}, B={B_fit}, C={C_fit}, D={D_fit}")
    # Generate y values using the fitted parameters
    y_fit = sine_function(x, A_fit, B_fit, C_fit, D_fit)

    # Plot the original data and the fitted curve
    plt.scatter(x, y, label='Sample Data')
    plt.plot(x, y_fit, label='Fitted Curve', color='red')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Sine Curve Fitting')
    plt.legend()
    plt.show()
