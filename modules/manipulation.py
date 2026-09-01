"""Data manipulation utilities for the radiation/light-intensity experiment.

This module reads, cleans, filters, and transforms the raw angular-scan
data ("corridas" / runs) produced by the spectrometer used in this
experiment, converting each run from (angular position, relative
intensity) into (wavelength, relative intensity) so it can be compared
against the spectral shape predicted by Planck's law. See the project
README for the full experimental and theoretical background.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import CubicSpline
import matplotlib as mpl

def dominio(corrida,
            angulo_min=0,
            angulo_max=360,
            intensidade_min=0,
            intensidade_max=100,
            visualizar=True):
    """Restrict a run to a chosen angular/intensity window.

    Filters the rows of a cleaned run so that only the angular positions
    and relative intensities within the given bounds are kept. This is
    typically used to isolate the useful peak region of a raw angular
    scan (e.g. the spectral peak seen between roughly 12-21 degrees)
    while discarding background and noise from the rest of the sweep.

    Args:
        corrida (pandas.DataFrame): Cleaned run with numeric
            'Posição_Angular(graus)' and 'Intensidade_rel_(%)' columns
            (see `ler_limpar_visualizar`).
        angulo_min (float): Minimum angular position to keep, in degrees.
            Defaults to 0.
        angulo_max (float): Maximum angular position to keep, in degrees.
            Defaults to 360.
        intensidade_min (float): Minimum relative intensity to keep, in
            percent. Defaults to 0.
        intensidade_max (float): Maximum relative intensity to keep, in
            percent. Defaults to 100.
        visualizar (bool): If True, show a scatter plot (relative
            intensity vs. angular position) of the filtered data.
            Defaults to True.

    Returns:
        pandas.DataFrame: A filtered copy of `corrida` containing only
        the rows within the given angular and intensity bounds.
    """
    corrida_filtrada = corrida.copy()
    corrida_filtrada = corrida_filtrada[corrida_filtrada['Posição_Angular(graus)'] >= angulo_min]
    corrida_filtrada = corrida_filtrada[corrida_filtrada['Posição_Angular(graus)'] <= angulo_max]
    corrida_filtrada = corrida_filtrada[corrida_filtrada['Intensidade_rel_(%)'] >= intensidade_min]
    corrida_filtrada = corrida_filtrada[corrida_filtrada['Intensidade_rel_(%)'] <= intensidade_max]
    if visualizar:
        plt.figure(figsize=(17, 6))
        plt.scatter(corrida_filtrada["Posição_Angular(graus)"], corrida_filtrada["Intensidade_rel_(%)"], color="blue", label="Dados experimentais",marker='o',s=8)
        plt.xlabel("Posição angular (°)")
        plt.ylabel("Intensidade rel.")
        plt.title("Intensidade relativa vs Posição angular")
        plt.grid()
        plt.show()
    return corrida_filtrada

def theta_para_lambda(theta, A=13900, B=1.689):
    """Convert a spectrometer angular reading into a wavelength.

    Converts an angular position (theta) read off the prism-spectrometer
    into the corresponding refractive index of the prism, then inverts a
    two-term Cauchy dispersion relation, n(lambda) = B + A / lambda**2,
    to obtain the wavelength associated with that angular reading.

    The angle-to-index relation encodes the fixed geometry (apex angle
    and incidence angle) of this particular prism-spectrometer setup;
    the constant 1.3439 (in radians) inside the formula is specific to
    that configuration and must be re-derived if the optical setup
    changes. The default coefficients `A` and `B` are Cauchy dispersion
    constants that were calibrated beforehand for the prism used in this
    experiment (e.g. from the known emission lines of a calibration
    lamp); replace them with your own calibration values if you repeat
    this experiment with a different prism or apparatus.

    Args:
        theta (float or array-like): Angular position(s), in degrees, as
            read from the spectrometer.
        A (float): Cauchy dispersion coefficient, in nm**2. Defaults to
            13900 (calibrated for this experiment's prism).
        B (float): Dimensionless Cauchy dispersion coefficient. Defaults
            to 1.689 (calibrated for this experiment's prism).

    Returns:
        float or numpy.ndarray: Wavelength(s), in nm, corresponding to
        `theta`.
    """
    theta_rad = np.deg2rad(theta)
    n = ( ( 2*np.sin(1.3439-theta_rad)/(3**0.5) + (1/2) ) ** 2 + (3/4) ) ** 0.5
    lambida = ( A / (n - B) ) ** 0.5
    return lambida

def transformacao_de_eixo(corrida, visualizar=True):
    """Add a wavelength column to a run by transforming its angular axis.

    Applies `theta_para_lambda` to the 'Posição_Angular(graus)' column of
    a copy of `corrida` and stores the result in a new
    'Comprimento_de_onda(nm)' column, so the run can be analyzed and
    plotted in wavelength space instead of angular-position space.

    Args:
        corrida (pandas.DataFrame): Run with a numeric
            'Posição_Angular(graus)' column (typically the output of
            `dominio`).
        visualizar (bool): If True, show a scatter plot (relative
            intensity vs. wavelength) of the transformed data. Defaults
            to True.

    Returns:
        pandas.DataFrame: A copy of `corrida` with an added
        'Comprimento_de_onda(nm)' column.
    """
    corrida_transformada = corrida.copy()
    corrida_transformada['Comprimento_de_onda(nm)'] = theta_para_lambda(corrida_transformada['Posição_Angular(graus)'])
    if visualizar:
        plt.figure(figsize=(17, 6))
        plt.scatter(corrida_transformada["Comprimento_de_onda(nm)"], corrida_transformada["Intensidade_rel_(%)"], color="blue", label="Dados experimentais",marker='o',s=8)
        plt.xlabel("Comprimento de onda (nm)")
        plt.ylabel("Intensidade rel.")
        plt.title("Intensidade relativa vs Comprimento de onda")
        plt.grid()
        plt.show()
    return corrida_transformada

def filtrar_transformar(corrida, angulo_min=0, angulo_max=360, intensidade_min=0, intensidade_max=100, visualizar=False):
    """Filter a run to its useful domain and convert it to wavelength.

    Convenience wrapper that chains `dominio` (angular/intensity
    filtering) and `transformacao_de_eixo` (angle-to-wavelength
    conversion) in a single call.

    Args:
        corrida (pandas.DataFrame): Cleaned run with numeric
            'Posição_Angular(graus)' and 'Intensidade_rel_(%)' columns.
        angulo_min (float): Minimum angular position to keep, in degrees.
            Defaults to 0.
        angulo_max (float): Maximum angular position to keep, in degrees.
            Defaults to 360.
        intensidade_min (float): Minimum relative intensity to keep, in
            percent. Defaults to 0.
        intensidade_max (float): Maximum relative intensity to keep, in
            percent. Defaults to 100.
        visualizar (bool): If True, show the intermediate and final
            scatter plots produced by `dominio` and
            `transformacao_de_eixo`. Defaults to False.

    Returns:
        pandas.DataFrame: The filtered run with an added
        'Comprimento_de_onda(nm)' column.
    """
    corrida_filtrada = dominio(corrida, angulo_min, angulo_max, intensidade_min, intensidade_max, visualizar=visualizar)
    corrida_transformada = transformacao_de_eixo(corrida_filtrada, visualizar=visualizar)
    return corrida_transformada


