import itertools as it
from logging import getLogger

import networkx as nx
import numpy as np
import pairlist as pl
import yaplotlib as yap
from cycless import cycles, simplex

from graphenator import firstshell


def to_graph(x, cell, bondlen=1.2):

    logger = getLogger()

    pairs = {(i, j): d for i, j, d in pl.pairs_iter(x, bondlen, cell, fractional=False)}

    g = nx.Graph(list(pairs))

    remove = []
    for tetra in simplex.tetrahedra_iter(g):
        subset = {}
        for i, j in it.combinations(tetra, 2):
            if (i, j) in pairs:
                subset[i, j] = pairs[i, j]
            else:
                subset[i, j] = pairs[j, i]
        keys = list(subset.keys())
        values = list(subset.values())
        longest = np.argmax(values)
        # print(keys)
        # print(values)
        # print(longest, subset[keys[longest]])

        remove.append(keys[longest])

    for edge in remove:
        g.remove_edge(*edge)

    return g


def cycle_hist(g):
    hist = [0] * 7
    for cycle in cycles.cycles_iter(g, maxsize=6):
        hist[len(cycle)] += 1
    return hist


def fix_graph(x, cell):
    logger = getLogger()

    rpeak = firstshell(x, cell)
    celli = np.linalg.inv(cell)

    g = to_graph(x, cell, rpeak * 1.33)

    logger.info(cycle_hist(g))

    newedges = []
    for cycle in cycles.cycles_iter(g, maxsize=6):
        assert len(cycle) in (3, 4)

        if len(cycle) == 4:
            # connect the shorter diagonal
            d1 = x[cycle[2]] - x[cycle[0]]
            d1 -= np.floor(d1 @ celli + 0.5) @ cell
            d2 = x[cycle[3]] - x[cycle[1]]
            d2 -= np.floor(d2 @ celli + 0.5) @ cell

            if d1 @ d1 > d2 @ d2:
                newedges.append((cycle[1], cycle[3]))
            else:
                newedges.append((cycle[0], cycle[2]))

    for edge in newedges:
        g.add_edge(*edge)

    print(cycle_hist(g))
    return g


def dualize(x, cell, g):
    celli = np.linalg.inv(cell)
    tripos = []
    edgeowners = dict()
    adj = nx.Graph()
    for o, tri in enumerate(simplex.triangles_iter(g)):
        d = x[list(tri)] - x[tri[0]]
        d -= np.floor(d @ celli + 0.5) @ cell
        c = np.mean(d, axis=0) + x[tri[0]]
        tripos.append(c)

        i, j, k = tri
        if (i, j) in edgeowners:
            adj.add_edge(o, edgeowners[i, j])
        edgeowners[i, j] = o
        edgeowners[j, i] = o

        if (j, k) in edgeowners:
            adj.add_edge(o, edgeowners[j, k])
        edgeowners[j, k] = o
        edgeowners[k, j] = o

        if (i, k) in edgeowners:
            adj.add_edge(o, edgeowners[i, k])
        edgeowners[i, k] = o
        edgeowners[k, i] = o

    return np.array(tripos), adj


def force(x, cell, g):
    celli = np.linalg.inv(cell)
    N = x.shape[0]
    F = np.zeros_like(x)
    E = 0
    for i, j in g.edges():
        d = x[i] - x[j]
        d -= np.floor(d @ celli + 0.5) @ cell
        r = np.linalg.norm(d)
        e = d / r
        F[i] -= e * r
        F[j] += e * r
        E += r**2 / 2
    return F, E


def snapshot(x, cell, g):

    # logger = getLogger()

    celli = np.linalg.inv(cell)

    frame = ""

    frame += yap.SetPalette(7, 128, 255, 128)
    frame += yap.Layer(1)
    frame += yap.Color(0)
    c = (cell[0] + cell[1] + cell[2]) / 2
    frame += yap.Line(cell[0, :] - c, -c)
    frame += yap.Line(cell[1, :] - c, -c)
    frame += yap.Line(cell[2, :] - c, -c)

    frame += yap.Size(0.2)
    for pos in x:
        frame += yap.Circle(pos)

    for cycle in cycles.cycles_iter(g, maxsize=8):
        cycle = list(cycle)
        d = x[cycle] - x[cycle[0]]
        d -= np.floor(d @ celli + 0.5) @ cell
        c = np.mean(d, axis=0) + x[cycle[0]]
        dc = np.floor(c @ celli + 0.5) @ cell
        d = d + x[cycle[0]] - dc
        frame += yap.Layer(len(cycle))
        frame += yap.Color(len(cycle))
        frame += yap.Polygon(d)

    frame += yap.NewPage()

    return frame


def quench(x, cell, g: nx.Graph, dt=0.01, file=None):
    logger = getLogger()
    for loop in range(100):
        F, E = force(x, cell, g)
        logger.info(E)
        x += F * dt
        rpeak = firstshell(x, cell)
        if file is not None:
            file.write(snapshot(x, cell, g))
    return x
