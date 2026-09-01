"""Plotting utilities for the radiation/light-intensity experiment.

This module contains the plotting functions used throughout the
analysis: quick scatter plots of a run, a single-run log-intensity plot
used to visually assess the Planck's-law-like spectral decay, and a
multi-run overlay plot used to compare spectra across runs.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import CubicSpline
import matplotlib as mpl

def visualizar_dados(corrida):
    """Plot relative intensity against angular position for a run.

    Draws a simple scatter plot of 'Intensidade_rel_(%)' vs.
    'Posição_Angular(graus)' for quick visual inspection of a raw or
    cleaned run.

    Args:
        corrida (pandas.DataFrame): Run with numeric
            'Posição_Angular(graus)' and 'Intensidade_rel_(%)' columns.

    Returns:
        None
    """
    plt.figure(figsize=(17, 6))
    plt.scatter(corrida["Posição_Angular(graus)"], corrida["Intensidade_rel_(%)"], color="blue", label="Dados experimentais",marker='o',s=8)
    plt.xlabel("Posição angular (°)")
    plt.ylabel("Intensidade rel.")
    plt.title("Intensidade relativa vs Posição angular")
    plt.grid()
    plt.show()
    return None

def lei_de_plank(corrida, spline=False, lim_inferior=None, lim_superior=None):
    """Plot the log-intensity spectrum of a single run.

    Plots ln(Intensidade_rel_(%) + 1e-10) against wavelength for one run,
    which is a convenient way to visually compare the measured spectral
    decay against the qualitative shape expected from Planck's law /
    Wien's approximation (an exponential falloff in intensity at long
    wavelengths appears as an approximately smooth, monotonic curve on
    this log scale). The small 1e-10 offset avoids taking the log of
    zero or negative values, which can occur after baseline subtraction.

    Args:
        corrida (pandas.DataFrame): Run with 'Comprimento_de_onda(nm)'
            and 'Intensidade_rel_(%)' columns (the output of
            `transformacao_de_eixo` or `filtrar_transformar` in
            `manipulation.py`).
        spline (bool): If True, overlay a cubic-spline interpolation of
            the log-intensity curve. Defaults to False.
        lim_inferior (float or None): Lower x-axis (wavelength) limit,
            in nm. Defaults to None (automatic).
        lim_superior (float or None): Upper x-axis (wavelength) limit,
            in nm. Defaults to None (automatic).

    Returns:
        None
    """

    x = corrida["Comprimento_de_onda(nm)"]
    y = np.log(corrida["Intensidade_rel_(%)"] + 1e-10)

    plt.figure(figsize=(17, 6))

    # gráfico original
    plt.plot(x, y, color="blue", label="Dados")

    # spline opcional
    if spline:

        # garante ordenação
        ordem = np.argsort(x)
        x_sorted = np.array(x)[ordem]
        y_sorted = np.array(y)[ordem]

        # spline cúbica
        cs = CubicSpline(x_sorted, y_sorted)

        # pontos interpolados
        x_fit = np.linspace(x_sorted.min(), x_sorted.max(), 1000)
        y_fit = cs(x_fit)

        plt.plot(
            x_fit,
            y_fit,
            color="blue",
            linewidth=2,
            label="Spline cúbica"
        )

    plt.xlabel("Comprimento de onda (nm)")
    plt.ylabel("Intensidade rel.")
    plt.title("Intensidade relativa vs Comprimento de onda")
    plt.grid()
    plt.xlim(lim_inferior, lim_superior)
    plt.legend()
    plt.show()

    return None

def lei_de_plank_varias(corridas, spline=False, lim_inferior=None, lim_superior=None, rm_offset=False, normalizar=False, save_fig=False, nome_fig="lei_de_plank.png"):
    """Overlay the intensity-vs-wavelength spectra of one or more runs.

    Plots 'Intensidade_rel_(%)' against 'Comprimento_de_onda(nm)' (on a
    linear, not log, scale) for one or more runs on the same axes, each
    colored along a viridis gradient, to visually compare spectral shape
    and peak position across different runs (e.g. repeated measurements
    of the same source).

    Args:
        corridas (pandas.DataFrame or list of pandas.DataFrame): A
            single run or a list of runs, each with
            'Comprimento_de_onda(nm)' and 'Intensidade_rel_(%)' columns.
        spline (bool): If True, overlay a cubic-spline interpolation for
            each run. Defaults to False.
        lim_inferior (float or None): Lower x-axis (wavelength) limit,
            in nm. Defaults to None (automatic).
        lim_superior (float or None): Upper x-axis (wavelength) limit,
            in nm. Defaults to None (automatic).
        rm_offset (bool): If True, shift each run's intensity so its
            minimum is zero before plotting (baseline removal). Defaults
            to False.
        normalizar (bool): If True, scale each run's intensity so its
            maximum is 1 (peak normalization). Defaults to False.
        save_fig (bool): If True, save the figure as a PNG file under a
            local 'figs/' directory (the directory must already exist).
            Defaults to False.
        nome_fig (str): Filename used when `save_fig` is True. Defaults
            to "lei_de_plank.png".

    Returns:
        None
    """

    plt.figure(figsize=(17, 6))

    # garante que entrada única também funcione
    if not isinstance(corridas, list):
        corridas = [corridas]

    cores = plt.cm.viridis(np.linspace(0, 1, len(corridas)))

    for i, corrida in enumerate(corridas):

        x = corrida["Comprimento_de_onda(nm)"]
        y = corrida["Intensidade_rel_(%)"]

        if rm_offset:
            y = y - y.min()  # desloca para mínimo zero

        if normalizar:
            y = y / y.max()  # escala para máximo 1

        cor = cores[i]

        # curva original
        plt.plot(
            x,
            y,
            color=cor,
            alpha=1,
            label=f"Corrida {i+1}"
        )

        # spline opcional
        if spline:

            ordem = np.argsort(x)

            x_sorted = np.array(x)[ordem]
            y_sorted = np.array(y)[ordem]

            cs = CubicSpline(x_sorted, y_sorted)

            x_fit = np.linspace(
                x_sorted.min(),
                x_sorted.max(),
                1000
            )

            y_fit = cs(x_fit)

            plt.plot(
                x_fit,
                y_fit,
                color=cor,
                linewidth=2
            )

    plt.xlabel("Comprimento de onda (nm)", fontsize=18)
    plt.ylabel("Intensidade", fontsize=18)
    plt.title("Intensidade vs Comprimento de onda", fontsize=20)
    plt.xlim(lim_inferior, lim_superior)  # ajuste conforme necessário
    #plt.grid()
    plt.yticks([])  # remove ticks do eixo y para melhor visualização
    plt.legend(fontsize=15)
    plt.tight_layout()
    if save_fig:
        plt.savefig(f"figs/{nome_fig}", dpi=300, bbox_inches='tight')
    plt.show()

    return None

def ler_limpar_visualizar(corrida_caminho, visualizar=True):
    """Read, clean, and (optionally) plot a raw run file in one call.

    Reads a tab-separated run file and converts the
    'Posição_Angular(graus)' and 'Intensidade_rel_(%)' columns from
    comma-decimal strings (as exported by the acquisition software) into
    numeric floats, then optionally plots the cleaned data. This
    combines the "read", "clean", and "visualize" steps of the analysis
    pipeline into a single convenience function.

    Args:
        corrida_caminho (str or pathlib.Path): Path to a tab-separated
            run file (e.g. 'experimental_data/corrida7.txt') containing
            'Posição_Angular(graus)' and 'Intensidade_rel_(%)' columns
            with comma decimal separators.
        visualizar (bool): If True, show a scatter plot of the cleaned
            data via `visualizar_dados`. Defaults to True.

    Returns:
        pandas.DataFrame: The cleaned run, with 'Posição_Angular(graus)'
        and 'Intensidade_rel_(%)' as numeric (float) columns.
    """
    corrida_bruto = pd.read_csv(corrida_caminho, sep='\t')
    
    corrida_limpo = corrida_bruto.copy()
    corrida_limpo['Posição_Angular(graus)'] = corrida_bruto['Posição_Angular(graus)'].str.replace(",", ".", case=False, regex=False)
    corrida_limpo['Intensidade_rel_(%)'] = corrida_bruto['Intensidade_rel_(%)'].str.replace(",", ".", case=False, regex=False)

    corrida_limpo['Posição_Angular(graus)'] = pd.to_numeric(corrida_limpo['Posição_Angular(graus)'])
    corrida_limpo['Intensidade_rel_(%)'] = pd.to_numeric(corrida_limpo['Intensidade_rel_(%)'])

    if visualizar:
        visualizar_dados(corrida_limpo)

    return corrida_limpo
