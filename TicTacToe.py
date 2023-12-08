# Author        : Bradley Long
# Date Modified : 2023/12/07
# Date Created  : 2023/12/07

import socket

class TicTacToe:
  """
  
  """
  def __init__(self, conn:socket.socket = None, header:int = 32) -> None:
    """
    Sets up the game!
    """
    self.board = [
      [" " for x in range(3)] for x in range(3)
    ]
    self.player1 = "O"
    self.player2 = "X"
    self.currTurn = self.player1
    self.winner = ""
    self.conn = conn

    # Constants
    self.WIDTH = 31
    self.EXIT_SEQ = ("QUIT", "END", "EXIT")
    self.POSITIVEOPT = ("Y", "YES")
    self.NEGATIVEOPT = ("N", "NO")
    self.HEADER_SIZE = header
    self.POSSIBLE = [
      [(1, 1), (1, 2), (1, 3)],
      [(2, 1), (2, 2), (2, 3)],
      [(3, 1), (3, 2), (3, 3)],
      [(1, 1), (2, 1), (3, 1)],
      [(1, 2), (2, 2), (3, 2)],
      [(1, 3), (2, 3), (3, 3)],
      [(1, 1), (2, 2), (3, 3)],
      [(3, 1), (2, 2), (1, 3)],
    ]

    self.topBottomBorder = "  " + "*" * self.WIDTH

  # Public Methods
  def start_game(self) -> int:
    """
    Starts and manages the game.\n
    This method begins the game and manages the
    game. It will call a method to have the player
    make a move and will also call a method to
    determine if the game has been won or tied.\n
    NOTE: This method must check the value of
    self.winner after each call of _check_winner()
    .\n
    NOTE: The status variable is dynamic and thus
    has different meaning for each functions return
    code. A status of > 1 requires action, but the
    action can vary as seen below.
    """
    transmission = ""
    status = 0
    transmission += "Enter \"QUIT\", \"END\", OR \"EXIT\" at any time to quit the game.\n"
    if self.conn:
      self._transmit(transmission, wait=True)
    print(transmission, end="")
    transmission = ""

    status = self._ask_player_preference()
    if status > 0:      # Player chose to quit
      return 0
    # Check for a winner after each game cycle
    while not self.winner:
      status = self._make_move()
      if status > 0:    # Player chose to quit
        transmission += "Thanks for playing! Until next time!\n"
        if self.conn:
          self._transmit(transmission, wait=True)
          self._transmit(self.EXIT_SEQ[0], wait=False)
        print(transmission, end="")
        transmission = ""
        return 0
      status = self._check_winner()
      if status > 0: break        # No moves left. Possible tie.

    # Display the game results
    transmission += self.topBottomBorder + "\n"
    if self.winner:
      transmission += f"*** {self.winner} won the game! ***\n"
    else:
      transmission += "  *** The game was a tie! ***\n"
    transmission += self.topBottomBorder + "\n"
    self._transmit(transmission, wait=True)
    self._transmit("[exit]")
    print(transmission)
    return 0
  

  # Private Methods
  def _check_winner(self) -> int:
    """
    Checks if the game was won.\n
    This method will also determine if there are
    any empty position to keep playing and return
    1 if the game has resulted in a tie. Otherwise
    0 will be returned to indicate that there are
    still positions to play.\n
    NOTE: It is the responsibility of the calling
    method to determine if a winner has been assigned
    """
    empty_pos = False
    # Check all winning combinations
    for possible_set in self.POSSIBLE:
      move1 = possible_set[0]
      move2 = possible_set[1]
      move3 = possible_set[2]
      pos1 = self.board[move1[0]-1][move1[1]-1]
      pos2 = self.board[move2[0]-1][move2[1]-1]
      pos3 = self.board[move3[0]-1][move3[1]-1]

      # Determine if there are still empty positions
      if pos1 == " " or pos2 == " " or pos3 == " ":
        empty_pos = True
        continue

      # Determine if there is a winner
      if pos2 != pos1:
        continue 
      if pos3 != pos1:
        continue

      # Set winner
      self.winner = pos1

    # Notify that there are not positions left to play
    if not empty_pos:
      return 1
    # Or notify there are still positions to play
    return 0


  def _make_move(self) -> int:
    """
    This method implements a players move.\n
    This method will modify self.board to register
    player moves. The current player is registered
    with self.currTurn. The method makes use of
    _print_board() and _get_row_col to display
    information to the player and to get input
    from the user.
    NOTE: Currently this method only validates whether
    the player did not want to make the choice. If
    user input is not in self.NEGATIVEOPTS the function
    will move forward as though the player positively
    validated. 
    """
    transmission = ""
    row = -1
    col = -1
    affirm = self.NEGATIVEOPT[0]
    # Loop while the player has not affirmed their choice
    while affirm in self.NEGATIVEOPT:
      # Announce who's turn
      transmission = "\n" + f"  *** {self.currTurn}'s turn! ***\n" + "\n"
      if self.conn and self.currTurn == self.player1:
        self._transmit(transmission, wait=True)
      else:
        print(transmission, end="")
      transmission = ""

      # Show the board status
      self._print_board()
      transmission += "\n"
      if self.conn and self.currTurn == self.player1:
        self._transmit(transmission, wait=True)
      else:
        print(transmission, end="")
      transmission = ""

      # Get user inputs
      row = self._get_row_col("row")
      if row < 0:
        return 1
      col = self._get_row_col("column")
      if col < 0:
        return 1
      
      # Determine validity of input
      if self.board[row-1][col-1] == " ":
        self.board[row-1][col-1] = self.currTurn
        # Show the choice on the board and ask for user affirmation
        transmission += "\n"
        if self.conn and self.currTurn == self.player1:
          self._transmit(transmission, wait=True)
        else:
          print(transmission, end="")
        transmission = ""

        self._print_board()

        transmission += "\n"
        transmission += "  Does this move look okay? (y/n) "
        if self.conn and self.currTurn == self.player1:
          self._transmit(transmission, wait=False)
          affirm = self._receive().upper()
        else:
          print(transmission, end="")
          affirm = input().upper()
        transmission = ""

        if affirm in self.EXIT_SEQ:
          return 1          # User chose to quit. Return err code
        if affirm in self.NEGATIVEOPT:      # See NOTE in docstring
          self.board[row-1][col-1] = " "
      else:
        affirm = self.NEGATIVEOPT[0]
        transmission += "  This position has already been played!"
        transmission += "  Please choose a different position."
        if self.conn and self.currTurn == self.player1:
          self._transmit(transmission, wait=True)
        else:
          print(transmission)
        transmission = ""

    # Change players turn and send success code
    self._toggle_player()
    return 0


  def _toggle_player(self):
    """
    Toggles the current player.
    """
    if self.currTurn == self.player1:
      self.currTurn = self.player2
    else:
      self.currTurn = self.player1

    return 0


  def _get_row_col(self, pos):
    """
    Prompts the user for input.\n
    The caller should pass the string "row"
    or the string "column" to this function
    to modify the output to the user. This
    method includes validation to ensure
    the uesr's input is an integer between
    1 and 3 (inclusive).\n
    NOTE: The calling function must decrement
    the value returned by this function to
    receive the appropriate row or column
    index.
    """
    transmission = ""
    val = -1
    while val < 0:
        transmission += f"Please choose the {pos} where you would like to move: "
        if self.conn and self.currTurn == self.player1:
          self._transmit(transmission, wait=False)
          val = self._receive().upper()
        else:
          print(transmission, end="")
          val = input().upper()
        transmission = ""
        if val in self.EXIT_SEQ:
          return -1
        try:
          val = int(val)
        except(ValueError):
          val = -1

        if val < 1 or val > 3:
          val = -1
          transmission += f"Please enter a valid {pos} number (e.g. 1, 2, or 3)\n"
          if self.conn and self.currTurn == self.player1:
            self._transmit(transmission, wait=True)
          else:
            print(transmission, end="")
          transmission = ""

    return val


  def _print_board(self):
    """
    This function displays the current game
    status for the player.
    """
    transmission = ""

    transmission += self.topBottomBorder + "\n"
    widthLeft = self.WIDTH
    i = 1
    for row in self.board:
      transmission += str(i) + " " + "*"
      widthLeft -= 1
      spacing = (widthLeft-6) // 3
      spaces = " " * (spacing // 2)
      transmission += spaces
      transmission += row[0]
      transmission += spaces + "*"
      transmission += spaces
      transmission += row[1]
      transmission += spaces + "*"
      transmission += spaces
      transmission += row[2]
      transmission += spaces + "*"
      widthLeft -= (6 + len(spaces) * 6)
      transmission += ("*" * widthLeft) + "\n"
      widthLeft = self.WIDTH
      transmission += self.topBottomBorder + "\n"
      i += 1

    if self.conn and self.currTurn == self.player1:
      self._transmit(transmission, wait=True)
    else: print(transmission, end="")

  def _ask_player_preference(self):
    """
    This function determines whether the first
    player would like to play as "X" or "O".\n
    """
    transmission = ""
    pref = ""
    affirm = self.NEGATIVEOPT[0]
    # Loop while the player has not affirmed their choice
    while affirm in self.NEGATIVEOPT:
      affirm = ""
      # Loop while the user has not made a valid choice
      while pref.upper() not in ("X", "O"):
        transmission += "Please choose X or O...\n"
        transmission += "Prefer \"X\" or \"O\"? "
        if self.conn:
          self._transmit(transmission, wait=False)
          pref = self._receive().upper()
        else:
          print(transmission, end="")
          pref = input().upper()
        transmission = ""
        if pref in self.EXIT_SEQ:         # Return with err code
          return 1

      if pref == "X":
        self.player1 = "X"
        self.player2 = "O"
      else:
        self.player1 = "O"
        self.player2 = "X"
      pref = ""

      transmission += f"Player one will play as \"{self.player1}\"\n"
      transmission += f"Player two will play as \"{self.player2}\"\n"
      if self.conn:
        self._transmit(transmission, wait=True)
      else:
        print(transmission)
      transmission = ""

      # Loop while the user has not made a valid option
      while affirm not in self.POSITIVEOPT and affirm not in self.NEGATIVEOPT:
        transmission += "Does this sound okay? (y/n) "
        if self.conn:
          self._transmit(transmission, wait=False)
          affirm = self._receive().upper()
        else:
          print(transmission)
          affirm = input().upper()
        transmission = ""
        if affirm in self.EXIT_SEQ:     # Return with err code
          return 1
        
    return 0      # Return with success code.
  
  def _transmit(self, transmission, wait=False):
    msgBytes = str.encode(transmission, "ascii")
    msgLen = len(msgBytes)
    msgLenAsBytes = str.encode(str(msgLen), "ascii")
    msgLenAsBytes = msgLenAsBytes + b' ' * (self.HEADER_SIZE   - len(msgLenAsBytes))
    if wait:
      msgLenAsBytes = msgLenAsBytes[0:32] + bytes("1", "ascii")

    self.conn.send(msgLenAsBytes + msgBytes)

  def _receive(self):
    while True:
      msgHeader:bytes = bytes("", "ascii")
      try:
        msgHeader = self.conn.recv(self.HEADER_SIZE)                # Receive msg length
      except(ConnectionAbortedError):
        return 0
      except(ConnectionResetError):
        return 0
      if len(msgHeader) > 0:
        msgLenBytes = msgHeader[0:32]
        waitFlag = msgHeader[32]
        msgLen = int(bytes.decode(msgLenBytes, "ascii"))
        dataBytes = self.conn.recv(msgLen)                             # Receive data
        data = bytes.decode(dataBytes, "ascii")
        return data

if __name__ == "__main__":
  game = TicTacToe()
  game.start_game()
