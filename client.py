import socket
import re
import threading
import enum

class Choices(enum.Enum):
    ROCK = 1
    PAPER = 2
    SCISSORS = 3

class Client:
    HOST = 1
    CLIENT = 2
    BUFFER = 128
    WAIT_CLIENT_CHOICE_MESSAGE = "What will be your..."
    
    def __init__(self):
        self.get_client_type()
        self.init_client_sock()
        threading.Thread(target=self.threaded_communication).start()
        
    def get_client_type(self):
        try:
            answer = input(f"({Client.HOST})host, ({Client.CLIENT})connect\n")
            answer = int(answer)
        except ValueError:
            print("Incorrect input. Please enter a number")
        while answer not in (Client.HOST, Client.CLIENT):
            print("Incorrect client type. Try again")
            try:
                answer = input(f"({Client.HOST})host, ({Client.CLIENT})connect\n")
                answer = int(answer)
            except ValueError:
                print("Incorrect input. Please enter a number")
        self.type = answer

    def init_client_sock(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.type == Client.HOST:
            self.sock.bind(('', 55555))
            self.sock.listen(1)
            print("You are a host. Waiting for client")
        elif self.type == Client.CLIENT:
            self.connect()
    
    def connect(self):
        ip = input("Input ip addr of host\n")
        while re.match("[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", ip) is None:
            print("Incorrect ip addr. Try again")
            ip = input("Input ip addr of host\n")
        try:
            self.sock.connect((ip, 55555))
        except socket.error:
            print("Unable to connect to the host. Try another\n")
            self.connect()

    def threaded_communication(self):
        if self.type == self.HOST:
            while True:
                conn, addr = self.sock.accept()
                conn.send("You are connected. Let's start".encode())
                while True:
                    try:
                        print("Your choice")
                        conn.send("My choice will be...".encode())
                        choice = self.get_choice()

                        conn.send(Client.WAIT_CLIENT_CHOICE_MESSAGE.encode())
                        print("Waiting for opponent choice")
                        client_choice = int(conn.recv(Client.BUFFER).decode())
                        if not client_choice:
                            break
                        else:
                            if choice == client_choice:
                                print("Draw")
                                conn.send("Draw".encode())
                            elif (choice, client_choice) in [(Choices.ROCK.value, Choices.SCISSORS.value), 
                                                             (Choices.SCISSORS.value, Choices.PAPER.value),
                                                             (Choices.PAPER.value, Choices.ROCK.value)]:
                                print("You won")
                                conn.send("I won".encode())
                            else:
                                print("You lost")
                                conn.send("You won".encode())
                    except socket.error:
                        print("Client disconnected")
                        break
        elif self.type == self.CLIENT:
            while True:
                message = self.sock.recv(Client.BUFFER).decode()
                print(message)
                if message == Client.WAIT_CLIENT_CHOICE_MESSAGE:
                    choice = self.get_choice()
                    self.sock.send(str(choice).encode())

    def get_choice(self):
        try:
            choice = input(f"({Choices.ROCK.value})Rock, ({Choices.PAPER.value})Paper, ({Choices.SCISSORS.value})Scissors\n")
            choice = int(choice)
        except ValueError:
            print("Incorrect input. Please enter a number")
        while choice not in (Choices.ROCK.value, Choices.PAPER.value, Choices.SCISSORS.value):
            print("Incorrect choice. Try Again")
            try:
                choice = int(input(f"({Choices.ROCK.value})Rock, ({Choices.PAPER.value})Paper, ({Choices.SCISSORS.value})Scissors\n"))
            except ValueError:
                print("Incorrect input. Please enter a number")
        return choice
    
if __name__ == "__main__":
    Client()