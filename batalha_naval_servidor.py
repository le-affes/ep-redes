import socket
import threading
from gameLib import *


# Configurações do jogo


# Função para inicializar o tabuleiro
def inicializa_tabuleiro():
    return [["~" for _ in range(tamanho_tabuleiro)] for _ in range(tamanho_tabuleiro)]


# Função para verificar se o tiro acertou um navio
def verifica_tiro(tabuleiro, x, y):
    return tabuleiro[x][y] == "N"


# Função para validar se uma posição está dentro dos limites do tabuleiro
def posicao_valida(x, y):
    return 0 <= x < tamanho_tabuleiro and 0 <= y < tamanho_tabuleiro


# Classe para o servidor do jogo
class ServidorBatalhaNaval:
    def __init__(self):
        self.host = socket.gethostname()
        self.port = 55555
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(2)
        print("Aguardando jogadores...")

        self.jogadores = []
        self.tabuleiros = [inicializa_tabuleiro(), inicializa_tabuleiro()]
        self.nomes = ["", ""]

    def conectar_jogadores(self):
        while len(self.jogadores) < 2:
            cliente_socket, _ = self.server.accept()
            self.jogadores.append(cliente_socket)
            print(f"Jogador {len(self.jogadores)} conectado.")

        # Cria threads para cada jogador
        threads = [
            threading.Thread(target=self.inicializar_jogador, args=(0,)),
            threading.Thread(target=self.inicializar_jogador, args=(1,)),
        ]

        # Inicia as threads para nome e posicionamento de navios simultâneos
        for thread in threads:
            thread.start()

        # Aguarda as threads finalizarem
        for thread in threads:
            thread.join()

    def inicializar_jogador(self, jogador_index):
        # Solicitar nome
        self.jogadores[jogador_index].send(
            f"{MessageType.NAME.value}: Informe seu nome.".encode()
        )
        self.nomes[jogador_index] = self.jogadores[jogador_index].recv(1024).decode()
        print(f"Nome do Jogador {jogador_index + 1}: {self.nomes[jogador_index]}")

        # Enviar quantidade de navios
        self.jogadores[jogador_index].send(
            f"{MessageType.SHIP_QTD.value}: {navios}".encode()
        )

        # Posicionar navios

        i = 0
        while i < navios:
            self.jogadores[jogador_index].send(
                f"{MessageType.POSITION.value}: Posicione seus navios no formato 'linha,coluna'): ".encode()
            )

            msg = self.jogadores[jogador_index].recv(1024).decode()
            x, y = receiveCoordinate(msg)

            if self.tabuleiros[jogador_index][x][y] == "N":
                self.jogadores[jogador_index].send(
                    f"{MessageType.INVALID_POSITION.value}: Navio já existente! Selecione outra posição.".encode()
                )
                continue
            else:
                self.tabuleiros[jogador_index][x][y] = "N"
                # self.jogadores[jogador_index].send(
                #     f"{MessageType.PRINT_GAME.value}: {printTabuleiro(self.tabuleiros[jogador_index])}".encode()
                # )
                i += 1

    def iniciar_jogo(self):
        # Iniciar rodadas alternadas
        turno = 0
        while True:
            # self.jogadores[turno].send(
            #     f"{MessageType.PRINT_GAME.value}: {printTabuleiro(self.tabuleiros[turno])}".encode()
            # )
            # Jogador atual faz o ataque
            self.jogadores[turno].send(
                f"{MessageType.ATTACK.value}: Seu turno! Informe o alvo no formato 'linha,coluna'.".encode()
            )
            msg = self.jogadores[turno].recv(1024).decode()
            ataque_x, ataque_y = receiveCoordinate(msg)

            # Jogador oponente escolhe uma posição para se defender
            oponente = 1 - turno
            if sum(row.count("N") for row in self.tabuleiros[oponente]) > 1:
                self.jogadores[oponente].send(
                    f"{MessageType.DEFENSE.value}: Em que posição deseja se defender? (linha,coluna)".encode()
                )
                msg = self.jogadores[oponente].recv(1024).decode()
                defesa_x, defesa_y = receiveCoordinate(msg)

                # Verificar se a defesa coincide com o ataque
                if ataque_x == defesa_x and ataque_y == defesa_y:
                    # Ataque anulado
                    self.jogadores[turno].send(
                        f"{MessageType.ATTACK_RESULT.value}: Seu ataque foi defendido.".encode()
                    )
                    self.jogadores[oponente].send(
                        f"{MessageType.DEFENSE_RESULT.value}: Você defendeu o ataque!".encode()
                    )
                    # O turno muda para o defensor, que agora ataca
                    turno = oponente
                    continue  # Passa para o próximo ataque

            # Ataque é válido
            if verifica_tiro(self.tabuleiros[oponente], ataque_x, ataque_y):
                self.tabuleiros[oponente][ataque_x][ataque_y] = "X"
                self.jogadores[turno].send(
                    f"{MessageType.ATTACK_RESULT.value}: Acertou um navio!".encode()
                )
                self.jogadores[oponente].send(
                    f"{MessageType.ATTACK_RESULT.value}: Um dos seus navios foi atingido!".encode()
                )

                # Checar se o oponente perdeu
                if all(
                    cell != "N" for row in self.tabuleiros[oponente] for cell in row
                ):
                    self.jogadores[turno].send(
                        f"{MessageType.GAME_RESULT.value}: Você venceu!".encode()
                    )
                    self.jogadores[oponente].send(
                        f"{MessageType.GAME_RESULT.value}: Você perdeu!".encode()
                    )
                    break
            else:
                # Ataque falhou
                self.jogadores[turno].send(
                    f"{MessageType.ATTACK_RESULT.value}: Você errou!".encode()
                )
                self.jogadores[oponente].send(
                    f"{MessageType.ATTACK_RESULT.value}: Seu oponente errou!".encode()
                )

            # Enviar o número de navios restantes do oponente
            navios_restantes = sum(row.count("N") for row in self.tabuleiros[oponente])
            self.jogadores[turno].send(
                f"{MessageType.ENEMY_SHIPS.value}: O inimigo ainda tem {navios_restantes} navios.".encode()
            )

            # Alterna turno
            turno = oponente

    def iniciar(self):
        # Conecta jogadores e inicia suas threads de inicialização
        self.conectar_jogadores()

        # Inicia o jogo em uma thread separada
        jogo_thread = threading.Thread(target=self.iniciar_jogo)
        jogo_thread.start()
        jogo_thread.join()


if __name__ == "__main__":
    servidor = ServidorBatalhaNaval()
    servidor.iniciar()
