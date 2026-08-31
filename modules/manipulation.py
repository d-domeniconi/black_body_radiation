import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import CubicSpline
from matplotlib.collections import LineCollection
import matplotlib as mpl
from matplotlib.colors import LinearSegmentedColormap

def dominio(corrida, 
            angulo_min=0, 
            angulo_max=360, 
            intensidade_min=0,
            intensidade_max=100,
            visualizar=True):
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
    theta_rad = np.deg2rad(theta)
    n = ( ( 2*np.sin(1.3439-theta_rad)/(3**0.5) + (1/2) ) ** 2 + (3/4) ) ** 0.5
    lambida = ( A / (n - B) ) ** 0.5
    return lambida

def transformacao_de_eixo(corrida, visualizar=True):
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
    corrida_filtrada = dominio(corrida, angulo_min, angulo_max, intensidade_min, intensidade_max, visualizar=visualizar)
    corrida_transformada = transformacao_de_eixo(corrida_filtrada, visualizar=visualizar)
    return corrida_transformada