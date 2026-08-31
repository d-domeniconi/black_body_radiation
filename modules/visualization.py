import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import CubicSpline
from matplotlib.collections import LineCollection
import matplotlib as mpl
from matplotlib.colors import LinearSegmentedColormap

def visualizar_dados(corrida):
    plt.figure(figsize=(17, 6))
    plt.scatter(corrida["Posição_Angular(graus)"], corrida["Intensidade_rel_(%)"], color="blue", label="Dados experimentais",marker='o',s=8)
    plt.xlabel("Posição angular (°)")
    plt.ylabel("Intensidade rel.")
    plt.title("Intensidade relativa vs Posição angular")
    plt.grid()
    plt.show()
    return None

def lei_de_plank(corrida, spline=False, lim_inferior=None, lim_superior=None):

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
    corrida_bruto = pd.read_csv(corrida_caminho, sep='\t')
    
    corrida_limpo = corrida_bruto.copy()
    corrida_limpo['Posição_Angular(graus)'] = corrida_bruto['Posição_Angular(graus)'].str.replace(",", ".", case=False, regex=False)
    corrida_limpo['Intensidade_rel_(%)'] = corrida_bruto['Intensidade_rel_(%)'].str.replace(",", ".", case=False, regex=False)

    corrida_limpo['Posição_Angular(graus)'] = pd.to_numeric(corrida_limpo['Posição_Angular(graus)'])
    corrida_limpo['Intensidade_rel_(%)'] = pd.to_numeric(corrida_limpo['Intensidade_rel_(%)'])

    if visualizar:
        visualizar_dados(corrida_limpo)

    return corrida_limpo