import numpy as np

class Graph:
    def __init__(self,gdict=None):
        if gdict is None:
             gdict = {}
        self.gdict = gdict
        self.nodes = list(gdict.keys())
        self.adj = self.get_adjacency()

    def edges(self):
        return self.findedges()

# Find the distinct list of edges
    def findedges(self):
        edgename = []
        for vrtx in self.gdict:
            for nxtvrtx in self.gdict[vrtx]:
                if {nxtvrtx, vrtx} not in edgename:
                    edgename.append({vrtx, nxtvrtx})
        return edgename

    def get_adjacency(self):
        size = len(self.nodes)
        adj = np.zeros((size, size))
        for i in range(size):
            for j in range(size):
                if self.nodes[j] in self.gdict[self.nodes[i]]:
                    adj[i, j] = 1
        return adj

class TonnetzGraph(Graph):
    def __init__(self, T=[3, 4, 5], PC=None):
        self.T = T
        if PC:
            self.PC = PC
        else:
            self.PC = list(range(12))
        self.relations = self.get_complementary()
        self.rel_type = {t : (t, 12-t) for t in self.T}
        super(TonnetzGraph, self).__init__(gdict=self.create_graph())

    def get_complementary(self):
        return self.T + [12-t for t in self.T]

    def create_graph(self):
        connections = dict()
        for pc in self.PC:
            connections[pc] = list(map(lambda x : (x+pc)%12, self.relations))
        return connections


class SpinnenGraph(Graph):
    def __init__(self):
        self.relations = ["P", "L", "R"]
        self.PC = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        self.PCN = dict(zip(self.PC, ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "G#", "A", "Bb", "B"]))
        self.types = ["m", "M"]
        super(SpinnenGraph, self).__init__(gdict=self.create_graph())

    def operation(self, base, op, t):
        if op == "P":
            return self.PCN[base%12] + self.inv(t)
        elif op == "L":
            n = self.fetch_move("L", t)
            return self.PCN[(base + n) % 12] + self.inv(t)
        elif op == "R":
            n = self.fetch_move("R", t)
            return self.PCN[(base + n) % 12] + self.inv(t)
        else:
            raise ValueError("Operation {} is not recognised".format(op))

    def fetch_move(self, op, t):
        if op == "L":
            if t == "M":
                return 4
            else :
                return 8
        else:
            if t == "M":
                return 9
            else:
                return 3

    def inv(self, t):
        if t == "m":
            return "M"
        elif t == "M":
            return "m"
        else :
            raise ValueError("Type {} is not recognised".format(t))

    def create_graph(self):
        connections = dict()
        for pc in self.PC:
            for t in self.types:
                connections[self.PCN[pc]+t] = list(map(lambda x: self.operation(pc, x, t), self.relations))
        return connections


if __name__=="__main__":
    from hamiltonian_path import *
    g = TonnetzGraph()
    print(g.nodes)
    sg = SpinnenGraph()
    print(sg.nodes)
    cycle = hamCycle(sg)
    print(cycle)