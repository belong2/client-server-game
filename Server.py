# Source          : https://www.youtube.com/watch?v=3QiPPX-KeSc
# Source Accessed : 2023/12/03
# Last Modified   : 2023/12/07

import socket
import threading
import sys
import signal
import dotenv
from TicTacToe import TicTacToe

"""
GLOBAL VARIABLES:
  conn
"""

ENV = dotenv.dotenv_values(".env")
PORT = int(ENV.get("PORT")); SERVER = ENV.get("SERVER")
ADDR = (SERVER, PORT)
HEADER_SIZE = 33
OUTBOUND_MESSAGE_HEADER = "YOU: "
INBOUND_MESSAGE_HEADER = "CLIENT: "

END_TRANSMISSION = "/q"
TICTACTOE_TRANSMISSION = ("!TICTACTOE", "!TIC-TAC-TOE")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.settimeout(0.5)
server.bind(ADDR)

# *************************************************************************************
# *************************************************************************************

def interrupt_handler(signum, frame):
  """
  Custom SIGINT handler. Closes connections
  and shuts down server.
  """
  signal.signal(signal.SIGINT, signal.SIG_IGN)
  print(f"Interrupt signaled: Num = {signum}. Exiting program...\n")
  print(frame)
  try:
    conn.close()
  except():
    pass
  server.close()
  sys.exit(1)

def tictactoe(conn:socket.socket):
  """
  Starts the tic-tac-toe game
  """
  tictactoe = TicTacToe(conn, HEADER_SIZE)
  tictactoe.start_game()

def receive_data(conn:socket.socket,):
  """
  Receives data from client and displays to stdout.
  """
  while True:
    bytesHeader:bytes = bytes("", "ascii")
    try:
      bytesHeader = conn.recv(HEADER_SIZE)                # Receive msg length
    except(ConnectionAbortedError):
      return 0
    except(ConnectionResetError):
      return 0
    if len(bytesHeader) > 0:
      msgLenBytes = bytesHeader[0:32]
      waitFlag = bytesHeader[32]
      msgLen = int(bytes.decode(msgLenBytes, "ascii"))
      dataBytes = conn.recv(msgLen)                             # Receive data
      data = bytes.decode(dataBytes, "ascii")

      if data == END_TRANSMISSION:
        return 0
      
      print(INBOUND_MESSAGE_HEADER, data, sep=None)

      if data.upper() in TICTACTOE_TRANSMISSION:
        tictactoe(conn)
      return 1

def send_data(conn:socket.socket):
  """
  Sends data to client.
  """
  restart = True
  while restart:
    restart = False
    message = input("Enter a message: ")

    if message:
      msgBytes = str.encode(message, "ascii")
      msgLen = len(msgBytes)
      msgLenAsBytes = str.encode(str(msgLen), "ascii")
      if len(msgLenAsBytes) > HEADER_SIZE:
        print("Message is too long!")
        restart = True
      else: 
        msgLenAsBytes = msgLenAsBytes + b' ' * (HEADER_SIZE - len(msgLenAsBytes))
        conn.send(msgLenAsBytes + msgBytes)
        print(OUTBOUND_MESSAGE_HEADER, message, sep=None)
        if message == END_TRANSMISSION: return 0

        return 1

def respond_client(conn:socket.socket, addr):
  """
  Responds to client.
  """
  tid = threading.current_thread().ident
  print(f"New connection from {addr}. TID = {tid}", end=" \n")

  while True:
    if not receive_data(conn):
      break
    if not send_data(conn):
      break

  print("Closing connection!")

  conn.close()
  return 0

def start_server():
  """
  Starts the server.\n
  The server will listen on the port specified
  by "PORT" and at the IP address specified by
  "SERVER". When a connection is started a
  new thread will be created and the connection
  will be passed as argument to the function
  "respond_client".
  """
  server.listen()
  print(
    f"Server started listening on port = {PORT} " +
    f"at address = {SERVER}"
  )
  while True:
    try:
      global conn
      conn, addr = server.accept()          # Accept Connection
      # Fork
      thread = threading.Thread(target=respond_client, args=(conn, addr))
      thread.start()
      print("Connection Accepted! TID = ", thread.ident, end=" \n")
    except(TimeoutError):
      pass

if __name__ == "__main__":
  signal.signal(signal.SIGINT, interrupt_handler)
  start_server()
