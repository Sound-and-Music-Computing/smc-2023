# Hamiltonian Path Simple

def hamPath(g, sp=None, P=[]):
    """Find a hamiltonian path in a Tonnetz graph"""
    sp = g.nodes[0] if sp == None else sp
    path = None
    if not P:
        P.append(sp)
    if len(P) == len(g.nodes):
        return P
    for u in g.gdict[P[-1]]:
        if u not in P:
            path = hamPath(g, sp, P+[u])
        if path:
            return path


def hamCycle(g, sp=None, P=[]):
    """Find a hamiltonian cycle in a Tonnetz graph"""
    sp = g.nodes[0] if sp==None else sp
    path = None
    if not P:
        P.append(sp)
    if len(P) == len(g.nodes):
        if sp in g.gdict[P[-1]]:
            return P + [sp]
    for u in g.gdict[P[-1]]:
        if u not in P:
            path = hamCycle(g, sp, P+[u])
        if path:
            return path


def allHamCycles(g, sp=None, P=[], paths=[]):
    """Find all hamiltonian cycles in a Tonnetz graph"""
    sp = g.nodes[0] if sp == None else sp
    if P == []:
        P.append(sp)
    if len(P) == len(g.nodes):
        if sp in g.gdict[P[-1]]:
            paths.append(P + [sp])
            return paths
    for u in g.gdict[P[-1]]:
        if u not in P:
            paths = allHamCycles(g, sp, P+[u], paths)
    return paths


if __name__ =="__main__":
    from tonnetz_class import Graph
    gdict = {0: [1, 2, 3], 1: [0, 3], 2: [1, 3], 3: [0, 1, 2]}
    G = Graph(gdict)
    print(hamPath(G))
    print(hamCycle(G))
    print(len(allHamCycles(G)))

