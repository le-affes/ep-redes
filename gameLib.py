from enum import Enum
import time
from typing import List
import os


# Definindo o enum MessageType
class MessageType(Enum):
    POSITION = 1
    ATTACK = 2
    ATTACK_RESULT = 3
    GAME_RESULT = 4
    NAME = 5
    DEFENSE = 6
    DEFENSE_RESULT = 7
    INVALID_POSITION = 8
    PRINT_GAME = 9


tamanho_tabuleiro = 5
navios = 3


def printTabuleiro(tabuleiro: List[List[str]]) -> str:
    resultado = "\n "
    linhas = len(tabuleiro)
    colunas = len(tabuleiro[0])

    # Adicionar o cabeçalho com os índices das colunas
    resultado += "  "  # Espaço para alinhar os índices das colunas
    for j in range(1, colunas + 1):
        resultado += f"{j}   "  # 3 espaços após o número da coluna
    resultado += "\n"

    # Adicionar o conteúdo do tabuleiro com o índice das linhas
    for i in range(linhas):
        resultado += f"{i + 1}  "  # Índice da linha
        for j in range(colunas):
            resultado += tabuleiro[i][j]
            if (
                j < colunas - 1
            ):  # Adiciona 3 espaços entre os elementos, mas não após o último
                resultado += "   "
        if i < linhas - 1:  # Apenas adiciona uma nova linha se não for a última linha
            resultado += "\n"
    resultado += "\n"
    return resultado


def limpar_tela():
    # Detecta o sistema operacional e executa o comando apropriado
    if os.name == "nt":  # Se for Windows
        os.system("cls")
    else:  # Se for Linux ou macOS
        os.system("clear")


# Mensagem de coordenada
def sendCoordinate(initialMessage: str):
    while True:
        try:
            coordenadas = input(initialMessage)
            posicao = coordenadas.split(",")
            x, y = int(posicao[0]), int(posicao[1])
            if x > tamanho_tabuleiro or y > tamanho_tabuleiro or y < 0 or x < 0:
                print("Entrada inválida!")
                time.sleep(2)
                continue

        except:
            print("Entrada inválida!")
            time.sleep(2)
            continue

        return str((x - 1, y - 1)).encode()


def receiveCoordinate(message: str):
    tupla_str = message.strip("()")
    x_str, y_str = tupla_str.split(", ")
    return (int(x_str), int(y_str))


def sendAttackMessage():
    while True:
        coordenadas = input("Informe o alvo (linha,coluna): ")
        try:
            ataque_x, ataque_y = map(int, coordenadas.split(","))
            if ataque_x > tamanho_tabuleiro or ataque_y > tamanho_tabuleiro:
                print("Entrada inválida!")
                time.sleep(2)

        except:
            print("Entrada inválida!")
            time.sleep(2)
            continue

        return (ataque_x, ataque_y)
