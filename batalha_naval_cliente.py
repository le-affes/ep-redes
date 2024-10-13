import socket
import threading
from gameLib import *


class ClienteBatalhaNaval:
    def __init__(self):
        self.host = socket.gethostname()
        self.port = 55555
        self.cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cliente.connect((self.host, self.port))

    def receber_mensagens(self):
        while True:
            try:
                msg = self.cliente.recv(1024).decode()
                tipo, conteudo = msg.split(":", 1)
                tipo = MessageType(int(tipo.strip()))

                if tipo == MessageType.SHIP_QTD:
                    print(f"Quantidade de navios: {conteudo}")

                elif tipo == MessageType.POSITION:
                    self.cliente.send(sendCoordinate(conteudo))

                elif tipo == MessageType.ATTACK:
                    self.cliente.send(
                        sendCoordinate("Informe a posição de ataque (linha,coluna): ")
                    )

                elif tipo == MessageType.ATTACK_RESULT:
                    print(f"Resultado do ataque: {conteudo}")

                elif tipo == MessageType.DEFENSE_RESULT:
                    print(f"Resultado da defesa: {conteudo}")

                elif tipo == MessageType.GAME_RESULT:
                    print(f"Resultado do jogo: {conteudo}")
                    break

                elif tipo == MessageType.ENEMY_SHIPS:
                    print(f"Navios restantes do inimigo: {conteudo}")

                elif tipo == MessageType.NAME:
                    nome = input("Informe seu nome: ")
                    self.cliente.send(nome.encode())

                elif tipo == MessageType.DEFENSE:
                    self.cliente.send(
                        sendCoordinate(
                            "Em que posição deseja se defender? (linha,coluna): "
                        )
                    )
                
                elif tipo == MessageType.INVALID_POSITION:
                    print(conteudo)

                elif tipo == MessageType.PRINT_GAME:
                    print(conteudo)

            except:
                print("Conexão com o servidor perdida.")
                break

    def iniciar(self):
        # Thread para receber mensagens
        thread_receber = threading.Thread(target=self.receber_mensagens)
        thread_receber.start()
        thread_receber.join()


if __name__ == "__main__":
    cliente = ClienteBatalhaNaval()
    cliente.iniciar()
