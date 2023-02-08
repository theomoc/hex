import socket
from random import choice
from time import sleep
from copy import deepcopy
from math import inf


class Agent48():
    """This class describes the default Hex agent. It will randomly send a
    valid move at each turn, and it will choose to swap with a 50% chance.
    """

    HOST = "127.0.0.1"
    PORT = 1234

    def __init__(self, board_size=11):
        self.s = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
        )

        self.s.connect((self.HOST, self.PORT))

        self.board_size = board_size
        self.board = []
        self.colour = ""
        self.turn_count = 0
        self.swap_moves = [(2,2),(2,3),(2,4),(2,5),(2,8),(2,9),(2,10),
                           (3,2),(3,3),(3,4),(3,5),(3,6),(3,7),(3,8),(3,9),(3,10),
                           (4,2),(4,3),(4,4),(4,5),(4,6),(4,7),(4,8),(4,9),(4,10),
                           (5,2),(5,3),(5,4),(5,5),(5,6),(5,7),(5,8),(5,9),(5,10),
                           (6,2),(6,3),(6,4),(6,5),(6,6),(6,7),(6,8),(6,9),(6,10),
                           (7,2),(7,3),(7,4),(7,5),(7,6),(7,7),(7,8),(7,9),(7,10),
                           (8,2),(8,3),(8,4),(8,5),(8,6),(8,7),(8,8),(8,9),(8,10),
                           (9,2),(9,3),(9,4),(9,5),(9,6),(9,7),(9,8),(9,9),(9,10),
                           (10,2),(10,3),(10,4),(10,5),(10,8),(10,9),(10,10)]
        self.decent_moves = [(0,2),(0,3),(0,5),(0,6),(0,7),(0,8),(0,10),(10, 0),(10, 2),(10, 3),(10, 4),(10, 5),(10, 7),(10, 8)]

    def run(self):
        """Reads data until it receives an END message or the socket closes."""

        while True:
            data = self.s.recv(1024)
            if not data:
                break
            # print(f"{self.colour} {data.decode('utf-8')}", end="")
            if (self.interpret_data(data)):
                break

        # print(f"Naive agent {self.colour} terminated")

    def interpret_data(self, data):
        """Checks the type of message and responds accordingly. Returns True
        if the game ended, False otherwise.
        """

        messages = data.decode("utf-8").strip().split("\n")
        messages = [x.split(";") for x in messages]
        # print(messages)
        for s in messages:
            if s[0] == "START":
                self.board_size = int(s[1])
                self.colour = s[2]
                self.board = [
                    [0]*self.board_size for i in range(self.board_size)]

                if self.colour == "R":
                    self.make_move()

            elif s[0] == "END":
                return True

            elif s[0] == "CHANGE":
                if s[3] == "END":
                    return True

                elif s[1] == "SWAP":
                    self.colour = self.opp_colour()
                    if s[3] == self.colour:
                        self.make_move()

                elif s[3] == self.colour: # the case when we have 'CHANGE ACTION BOARD TURN', where ACTION = MOVE/END. If END, return false. BOARD = state of board, represented as a matrix. TURN = colour that makes the next move
                    action = [int(x) for x in s[1].split(",")] # action = [row, col] is where we want to place a piece
                    self.board[action[0]][action[1]] = self.opp_colour() # the 0 that used to be in that position will now be R/B, depending on our colour

                    self.make_move()

        return False
   
    def make_move(self):
        """Makes a random move from the available pool of choices. If it can
        swap, chooses to do so 50% of the time.
        """
        # print(f"{self.colour} making move")
        if self.turn_count == 0:
            if self.colour == "R":
                move = choice(self.decent_moves)
                self.s.sendall(bytes(f"{move[0]},{move[1]}\n", "utf-8"))
                self.board[move[0]][move[1]] = self.colour
            elif self.colour == "B":
                first_move = self.get_first_move_coord
                if first_move in self.swap_moves or first_move in self.decent_moves:
                    self.s.sendall(bytes("SWAP\n", "utf-8"))
                else:
                    move = choice(self.decent_moves)
                    self.s.sendall(bytes(f"{move[0]},{move[1]}\n", "utf-8"))
                    self.board[move[0]][move[1]] = self.colour

        else:
            move = self.minimax(3)
            self.s.sendall(bytes(f"{move[0]},{move[1]}\n", "utf-8"))
            self.board[move[0]][move[1]] = self.colour

        self.turn_count += 1

    def opp_colour(self):
        """Returns the char representation of the colour opposite to the
        current one.
        """
        if self.colour == "R":
            return "B"
        elif self.colour == "B":
            return "R"
        else:
            return "None"

    def get_first_move_coord(self):
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.board[i][j] == "R":
                    return (i, j)
            
    def get_moves(self, board):
        moves = []

        for i in range(self.board_size):
            for j in range(self.board_size):
                if board[i][j] == 0:
                    moves.append([i, j])

        return moves

    def ab_value(self, depth, a, b, board, colour, legal_moves):
        if (depth == 0):
            return self.heuristic(board)		#sends the last move made and the player who made it

        elif (colour == self.colour):       					#node is minimising
            best = inf

            for move in legal_moves:
                test_board = deepcopy(board) 					#copy board into another variable
                test_board[move[0]][move[1]] = colour 			#make move on copied board
                updated_moves = legal_moves.copy()
                updated_moves.remove(move)
                best = min(best, self.ab_value(depth-1, a, b, test_board, self.opp_colour, updated_moves))
                b = min(b, best)
                
                if (b <= a):
                    break
                
            return best
        
        else:       					#node is maximising
            best = -inf

            for move in legal_moves:
                test_board = deepcopy(board) 					#copy board into another variable
                test_board[move[0]][move[1]] = colour 			#make move on copied board
                updated_moves = legal_moves.copy()
                updated_moves.remove(move)
                best = max(best, self.ab_value(depth-1, a, b, test_board, self.colour, updated_moves))
                a = max(a, best)

                if (b <= a):
                    break
                
            return best

    def minimax(self, depth):
        legal_moves = self.get_moves(self.board)
        min_val = inf
        best_move = []

        for move in legal_moves:
            test_board = deepcopy(self.board) 				#copy board into another variable
            test_board[move[0]][move[1]] = self.colour 			#make move on copied board
            minimax_result = self.ab_value(depth, inf, -inf, test_board, self.opp_colour(), legal_moves)

            if (minimax_result < min_val):
                min_val = minimax_result
                best_move = move
                    
        return best_move

    def heuristic(self, board):					#changed to take colour
        agent_stones = self.get_stones(self.colour, board)				#changed to parameter colour
        opp_stones = self.get_stones(self.opp_colour, board)

        diff = self.djikstra(agent_stones, self.colour, board) - self.djikstra(opp_stones, self.opp_colour, board)

        return diff

    def get_stones(self, colour, board):
        stones = []

        for i in range(self.board_size):
                for j in range(self.board_size):
                    if board[i][j] == colour:
                        neighbours = self.get_neighbours([i,j])

                        if not any(hex in stones for hex in neighbours):
                            stones.append([i,j])

        return stones

    def get_neighbours(self, hex):  # Returns adjacent hexes
        x = hex[1]
        y = hex[0]

        # Corner Inputs
        if y == 0 and x == 0:
            return [[0,1], [1,0]]
        elif y == 0 and x == self.board_size-1:
            return [[0,self.board_size-2], [1,self.board_size-1], [1,self.board_size-2]]
        elif y == self.board_size-1 and x == 0:
            return [[self.board_size-2,0], [self.board_size-2,1], [self.board_size-1,1]]
        elif y == self.board_size-1 and x == self.board_size-1:
            return [[self.board_size-2,self.board_size-1], [self.board_size-1,self.board_size-2]]

        # Sides Inputs
        elif y == 0:
            return [[0,x-1], [0,x+1], [1,x-1], [1,x]]
        elif y == self.board_size-1:
            return [[self.board_size-1,x-1], [self.board_size-1,x+1], [self.board_size-2,x], [self.board_size-2,x+1]]
        elif x == 0:
            return [[y-1,0], [y+1,0], [y-1,1], [y,1]]
        elif x == self.board_size-1:
            return [[y-1,self.board_size-1], [y+1,self.board_size-1], [y,self.board_size-2], [y+1,self.board_size-2]]
        
        # All Other Hex Inputs
        else:
            return [[y-1,x], [y-1,x+1], [y,x-1], [y,x+1], [y+1,x-1], [y+1,x]]            

    def djikstra(self, stones, colour, board):
        min_chains = []
        min_chain = 0

        for stone in stones:
            graph = [[inf for column in range(self.board_size)]
                      for row in range(self.board_size)]
            graph[stone[0]][stone[1]] = 0
            graph = self.djikstra_recursive(colour, stone, graph, board)
            
            if colour == "R":
                min_chain = min(graph[0]) + min(graph[self.board_size-1])
            
            else:
                left_min = inf
                right_min = inf

                for row in graph:
                    if row[0] < left_min:
                        left_min = row[0]
                    if row[self.board_size-1] < right_min:
                        right_min = row[self.board_size-1]
                min_chain = left_min + right_min
            
            min_chains.append(min_chain)
        
        return min(min_chains)

        
    def djikstra_recursive(self, colour, hex, graph, board):
        neighbours = self.get_neighbours(hex)

        for neighbour in neighbours:
            if board[neighbour[0]][neighbour[1]] == colour and graph[hex[0]][hex[1]] < graph[neighbour[0]][neighbour[1]]:
                graph[neighbour[0]][neighbour[1]] = graph[hex[0]][hex[1]]
                graph = self.djikstra_recursive(colour, neighbour, graph, board)

            elif board[neighbour[0]][neighbour[1]] == 0 and graph[hex[0]][hex[1]] + 1 < graph[neighbour[0]][neighbour[1]]:
                graph[neighbour[0]][neighbour[1]] = graph[hex[0]][hex[1]] + 1
                graph = self.djikstra_recursive(colour, neighbour, graph, board)
        
        return graph

if (__name__ == "__main__"):
    agent = Agent48()
    agent.run()