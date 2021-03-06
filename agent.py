import game as gm
import random
import math
import mctsnode
from copy import deepcopy

class Agent:
    def __init__(self, color, type):
        self.color = color
        self.type = type

        self.decisionFunction = None
        if self.type == "random":
            self.decisionFunction = self.random
        elif self.type == "negamax":
            self.decisionFunction = self.minimax
        elif self.type == "human":
            self.decisionFunction = self.human
        elif self.type == "montecarlo":
            self.decisionFunction = self.mcts

        self.maxDepth = 4
        self.maxTrials = 400

    def random(self, gameState):
        # Pick random move
        pick = random.randint(0, len(gameState.legalMoves) - 1)
        pick = gameState.legalMoves[pick]
        return gameState.nodes[pick].id

    def human(self, gameState):
        # Controlled by human
        while True:
            try:
                move = int(input('Please enter a ' + self.color + " move: "))
                if move in gameState.legalMoves:
                    return move
                elif move > len(gameState.nodes) or move < 0:
                    print("   Error: this space does not exist on this board")
                    continue
                else:
                    print("   Error: this space is already taken")
                    continue
            except ValueError:
                print("   Error: please input a positive integer")
                continue

    def minimax(self, gameState):
        bestMove = self.negamax(gameState, self.maxDepth, -math.inf, math.inf, self.color, None)
        return bestMove
    def negamax(self, gameState, depth, alpha, beta, color, move):
        if move != None:
            initialVal = self.evaluateGameState(gameState, color, move)
            if math.isinf(initialVal) or depth == 0:
                return initialVal

        value = -math.inf
        bestMove = gameState.legalMoves[0]
        for i in gameState.legalMoves:
            currentGameState = deepcopy(gameState)
            currentGameState.processMove(i, color)

            oppositeColor = "white" if color == "black" else "black"
            oppositeVal = self.negamax(currentGameState, depth - 1, -beta, -alpha, oppositeColor, i)
            childVal = -oppositeVal
            bestMove = i if childVal > value else bestMove
            value = max(value, childVal)
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        if depth == self.maxDepth:
            return bestMove
        return value

    def evaluateGameState(self, gameState, color, move):
        winner = gameState.findWinner(move)
        if winner == color:
            return math.inf
        elif winner == "none":
            score = 0
            for i in gameState.nodes:
                score += len(i.circuitNeighbors[color])
            return score
        return -math.inf



    def mcts(self, gameState):
        root = mctsnode.Node(deepcopy(gameState), self.color, None, None)
        root.expand_node()

        trials = 0
        while trials < self.maxTrials:
            # Selection and Expansion
            pick = root
            while len(pick.children) > 0:
                bestScore, bestChild = 0, pick.children[0]
                for child in pick.children:
                    res = (child.wins/2 + 1) / (child.trials + 2) # Priority formula
                    if res > bestScore:
                        bestScore = res
                        bestChild = child
                pick = bestChild
                #pick = random.choice(pick.children)
            pick.expand_node()

            # Simulation
            winner = pick.simulate()


            # Backpropagation
            while pick.parent is not None:
                pick.trials += 1
                if winner != pick.color:
                    pick.wins += 1
                pick = pick.parent
            trials += 1

        bestWinPercentage, bestMove = 0, 0
        for child in root.children:
            winpercent = child.wins / child.trials if child.trials != 0 else 0
            print(child.wins, child.trials)
            if winpercent > bestWinPercentage:
                bestMove, bestWinPercentage = child.move, winpercent
        return bestMove
