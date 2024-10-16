import socket
import threading
from gameLib import *


class ClienteBatalhaNaval:
    def __init__(self):
        while True:
            try:
                entrada = input("Digite o endereço IP para se conectar. Para jogar em modo local apenas tecle 'Enter': ")
                if entrada == "":
                    self.host = socket.gethostname()  # Conexão local
                else:
                    self.host = entrada  # Conexão remota com IP especificado

                self.port = 55555
                self.cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                # Tentativa de conexão sem timeout
                self.cliente.connect((self.host, self.port))
                self.cliente.settimeout(5)

                print("Conectado ao servidor.")

                # Define um timeout para as operações após a conexão ser estabelecida
                self.cliente.settimeout(None)

                break
            
            except ConnectionRefusedError:
                print("Conexão recusada pelo servidor. O jogo pode já estar cheio ou em andamento.")
                self.cliente.close()
                continue
            except OSError as e:
                print(f"Erro de rede: {e}. Verifique o IP e a conexão.")
                self.cliente.close()
                continue
            except Exception as e:
                print(f"Erro ao conectar ao servidor: {e}. Tente novamente.")
                self.cliente.close()
                continue

    def receber_mensagens(self):
        while True:
            try:
                msg = self.cliente.recv(1024).decode()
                time.sleep(0.5)
                tipo, conteudo = msg.split(":", 1)
                tipo = MessageType(int(tipo.strip()))

                if tipo == MessageType.POSITION:
                    self.cliente.send(sendCoordinate(conteudo))
                    limpar_tela()

                elif tipo == MessageType.ATTACK:
                    self.cliente.send(
                        sendCoordinate("Informe a posição de ataque (linha,coluna): ")
                    )

                elif tipo == MessageType.ATTACK_RESULT:
                    print(f"Resultado do ataque: {conteudo}")
                    time.sleep(2)
                    limpar_tela()

                elif tipo == MessageType.DEFENSE_RESULT:
                    print(f"Resultado da defesa: {conteudo}")
                    time.sleep(2)
                    limpar_tela()

                elif tipo == MessageType.GAME_RESULT:
                    print(f"Resultado do jogo: {conteudo}")
                    break

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
                exit()
                break

    def iniciar(self):
        # Thread para receber mensagens
        thread_receber = threading.Thread(target=self.receber_mensagens)
        thread_receber.start()
        thread_receber.join()


if __name__ == "__main__":
    cliente = ClienteBatalhaNaval()
    cliente.iniciar()
