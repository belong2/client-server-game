# Source          : https://www.youtube.com/watch?v=3QiPPX-KeSc
# Source Accessed : 2023/12/03
# Last Modified   : 2023/12/07

import socket
import dotenv

ENV = dotenv.dotenv_values(".env")
PORT = int(ENV.get("PORT")); SERVER = ENV.get("SERVER")
ADDR = (SERVER, PORT)
HEADER_SIZE = 33
OUTBOUND_MESSAGE_HEADER = "YOU: "
INBOUND_MESSAGE_HEADER = "SERVER: "

END_TRANSMISSION = "/q"
TICTACTOE_TRANSMISSION = ("!TICTACTOE", "!TIC-TAC-TOE")

def tictactoe(conn:socket.socket):
  """
  Manages the tic-tac-toe for the client.
  """
  playing = True
  while playing:
    wait = receive_message(conn, game=True)
    if wait < 0:
      break
    if wait: continue

    send_message(conn, game=True)

  return 0

def receive_message(client:socket.socket, game=False):
  """
  Receives a message from the server.
  """
  while True:
    bytesHeader = bytes("", "ascii")
    wait = False
    try:
      bytesHeader = client.recv(HEADER_SIZE)
    except(ConnectionAbortedError):
      return 0
    except(ConnectionResetError):
      return 0
    if len(bytesHeader) > 0:
      msgLenBytes = bytesHeader[0:32]
      waitFlag = bytesHeader[32]
      waitFlag = chr(waitFlag)
      if waitFlag == "1":
        wait = True
      msgLen = int(bytes.decode(msgLenBytes, "ascii"))
      dataBytes = client.recv(msgLen)                             # Receive data
      data = bytes.decode(dataBytes, "ascii")

      if data == END_TRANSMISSION:
        return 0

      if game:
        if data == "[exit]":
          return -1
        print(data, end="")
        if wait:
          return 1
        else:
          return 0
      else:
        print(INBOUND_MESSAGE_HEADER, data, sep=None)
        return 1

def send_message(client:socket.socket, game=False):
  """
  Sends a message to the server.
  """
  restart = True
  msg = ""
  while restart:
    restart = False
    if not game:
      print("Enter \"!TICTACTOE\" to play a game!")
      msg = input("Enter a message: ")
    else:
      msg = input()

    if not msg:
      msg = "\n"

    if msg:
      msgBytes = str.encode(str(msg), "ascii")
      numBytes = len(msgBytes)
      numBytesAsBytes = str.encode(str(numBytes), "ascii")
      if len(numBytesAsBytes) > HEADER_SIZE:
        print("Message is too long!")
        restart = True
      else: 
        numBytesAsBytes = numBytesAsBytes + b' ' * (HEADER_SIZE - len(numBytesAsBytes))
        client.send(numBytesAsBytes + msgBytes)
        if not game:
          print(OUTBOUND_MESSAGE_HEADER, msg, sep=None)
        if msg == END_TRANSMISSION: return 0
        if msg.upper() in TICTACTOE_TRANSMISSION: tictactoe(client)

        return 1

if __name__ == "__main__":
  client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  # client.settimeout(0.5)
  client.connect(ADDR)
  print("Successfully connected to the server!")
  print("Send '/q' to cance the connection.")

  while True:
    if not send_message(client):
      break
    if not receive_message(client):
      break

  print("Closing connection!")

  client.close()
