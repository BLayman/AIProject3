import matplotlib

import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt

class ResultCounter:
    def __init__(self, numRounds):
        self.numRounds = numRounds
        self.wumpusDeaths = 0
        self.wins = 0
        self.pitDeaths = 0
        self.scores = []
        self.moves = []
    def addResults(self, results):
        if results[2] == 'Win':
            self.wins += 1
        if results[2] == 'Wumpus':
            self.wumpusDeaths +=1
        if results[2] == 'Pit':
            self.pitDeaths += 1
        self.scores.append(results[0])
        self.moves.append(results[1])
    def graphEndStats(self):
        reasons = ('Wins', 'Wumpus Deaths', 'Pit Deaths')
        y_pos = np.arange(len(reasons))
        counts = [self.wins, self.wumpusDeaths, self.pitDeaths]

        plt.bar(y_pos, counts, align='center', alpha=0.5)
        plt.xticks(y_pos, reasons)
        plt.ylabel('Number Of Games Ended By Reason')
        plt.title('Reason Game Ended')

        plt.show()
    def graphPointsHist(self):
        histValues, histEdges = np.histogram(self.scores)

        y_pos = np.arange(len(histEdges))

        plt.bar(y_pos, histEdges, align='center', alpha=0.5)
        plt.xticks(y_pos, histValues)
        plt.ylabel('some hist y')
        plt.title('some hist x')
        plt.show()

    def graphCellHist(self):
        pass
