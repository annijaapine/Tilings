import heapq
from itertools import combinations, product
from operator import xor

from comb_spec_searcher import InferralRule


class Graph(object):
    """
    A weighted directed graph implemented with an adjacency matrix.

    The graph is made such that it is easy to merge to vertices. Merging
    vertices collapse to vertices together such that
        - The weight of the new vertex is the sum of the weights
        - The weight of the edges is the sum of the weight of the edges that
        went to any of the merged vertices before the merge.


    The graph supports 2 operations
        - `reduce`: who merge two vertices that were not connected by an edges
        and repeat as long as possible.
        - `break_cycle_in_all_ways`: Take a cycle in the graph and return a
        copy of the graph with a removed edges for each edges in the cycle.

    Moreover, one can also ask:
        - if the graph is acyclic with `is_acyclic`
        - for a cycle of the graph with `find_cycle`
        - For the vertex order implied by a reduced acyclic graph
    """

    def __init__(self, vertices, matrix=None):
        self._vertex_labels = [set([v]) for v in vertices]
        self._vertex_weights = [1 for _ in self._vertex_labels]
        self._matrix = matrix
        assert len(matrix) == len(self._vertex_labels)
        assert all(len(row) == len(self._matrix) for row in matrix)
        self._reduced = False
        self._is_acyclic = False

    @property
    def num_vertices(self):
        """
        The number of vertices of the graph
        """
        return len(self._vertex_weights)

    def _merge_vertices(self, v1, v2):
        """
        Merge the two vertices.

        Vertex and edges are merged and the weight are added. Then edges with a
        weight that is to small are discarded.
        """
        v2_label = self._vertex_labels.pop(v2)
        self._vertex_labels[v1].update(v2_label)
        v2_weight = self._vertex_weights.pop(v2)
        self._vertex_weights[v1] += v2_weight
        self._add_matrix_rows(v1, v2)
        self._add_matrix_columns(v1, v2)
        self._trim_edges(v1)

    def reduce(self):
        if self._reduced:
            return
        non_edge = self.find_non_edge()
        while non_edge:
            self._merge_vertices(non_edge[0], non_edge[1])
            non_edge = self.find_non_edge()
        self._reduced = True

    def find_non_edge(self):
        """
        Return a non-edge of the graph.

        A non edges is a pair of vertices `(v1, v2)` such that neither
        `(v1, v2)` or `(v2, v1)` is an edge in the graph.
        """
        for v1, v2 in combinations(range(self.num_vertices), 2):
            if not self._is_edge(v1, v2) and not self._is_edge(v2, v1):
                return (v1, v2)

    def is_acyclic(self):
        """
        Check if the graph is acyclic.

        To perform that check, the graph must first be reduced with the
        `reduce` method.
        """
        assert self._reduced, "Graph must first be reduced"
        if self._is_acyclic or self.num_vertices == 0:
            return True
        for row in self._matrix:
            if row.count(0) == self.num_vertices:
                self._is_acyclic = True
                return True
        return False

    def find_cycle(self):
        """
        Return the edges of a cycle of the graphs. The graphs first need to be
        reduced

        If a cycle of length 3 is return it means that no cycle of length 2
        exist.

        If the graph is acyclic, returns None.

        NOTE:

            One can prove that if a reduced graph is not acyclic it has either
            a cycle of length 2 or 3.
        """
        assert self._reduced, "Graph must first be reduced"
        for v1, v2 in combinations(range(self.num_vertices), 2):
            if self._is_edge(v1, v2) and self._is_edge(v2, v1):
                return ((v1, v2), (v2, v1))
        for v1, v2, v3 in combinations(range(self.num_vertices), 3):
            cycle = self._length3_cycle(v1, v2, v3)
            if cycle:
                return cycle
        self._is_acyclic = True
        return None

    def break_cycle_in_all_ways(self, edges):
        """
        Generator over Graph object obtained by removing one edge of the
        `edges` iterator.
        """
        for e in edges:
            new_graph = Graph.__new__(Graph)
            new_graph._vertex_labels = [vl.copy()
                                        for vl in self._vertex_labels]
            new_graph._vertex_weights = self._vertex_weights.copy()
            new_graph._matrix = [row.copy() for row in self._matrix]
            new_graph._matrix[e[0]][e[1]] = 0
            new_graph._reduced = False
            new_graph._is_acyclic = False
            yield new_graph

    def vertex_order(self):
        """
        Return the order of the vertex in a reduced acyclic graph.

        A reduced acyclic graph is an acyclic orientation of a complete graph.
        There it equivalent to an ordering of its vertices.

        To compute the vertex order, the graph must be reduced and acyclic.
        """
        assert self._reduced, "Graph must first be reduced"
        assert self.is_acyclic(), "Graph must be acyclic"
        vert_num_parent = [row.count(0) for row in self._matrix]
        return [
            p[1] for p in sorted(zip(vert_num_parent, self._vertex_labels))
        ]

    def _add_matrix_rows(self, row1_idx, row2_idx):
        """
        Deletes row 2 from the graph matrix and change row 1 to
        the sum of both row.
        """
        assert row1_idx != row2_idx
        row1 = self._matrix[row1_idx]
        row2 = self._matrix.pop(row2_idx)
        self._matrix[row1_idx] = list(map(sum, zip(row1, row2)))

    def _add_matrix_columns(self, col1_idx, col2_idx):
        """
        Deletes column 2 from the graph matrix and change column 1 to
        the sum of both column.
        """
        assert col1_idx != col2_idx
        for row in self._matrix:
            c2_value = row.pop(col2_idx)
            row[col1_idx] += c2_value

    def _trim_edges(self, vertex):
        """
        Remove all the edges that touch vertex that that have a weight which is
        too small.

        The weight of a vertex is too small if it is smaller than the product
        of the weights of the two vertex it connects.
        """
        v1 = vertex
        v1_weight = self._vertex_weights[v1]
        for v2 in range(self.num_vertices):
            v2_weight = self._vertex_weights[v2]
            weight_prod = v1_weight * v2_weight
            self._delete_edge_if_small(v1, v2, weight_prod)
            self._delete_edge_if_small(v2, v1, weight_prod)

    def _delete_edge_if_small(self, head, tail, cap):
        """
        Delete the edges that goes from head to tail if its weight is lower
        than the cap.
        """
        weight = self._matrix[head][tail]
        if weight < cap:
            self._matrix[head][tail] = 0

    def _is_edge(self, v1, v2):
        return self._matrix[v1][v2] != 0

    def _length3_cycle(self, v1, v2, v3):
        """
        Return the edges of a length 3 cycle containing the three vertices if
        such a cycle exist. Otherwise return None
        """
        def is_cycle(edges):
            return all(self._is_edge(*e) for e in edges)
        orientation1 = ((v1, v2), (v2, v3), (v3, v1))
        if is_cycle(orientation1):
            return orientation1
        orientation2 = ((v1, v3), (v3, v2), (v2, v1))
        if is_cycle(orientation2):
            return orientation2

    def __repr__(self):
        s = 'Graph over the vertices {}\n'.format(self._vertex_labels)
        s += 'Vertex weight is {}\n'.format(self._vertex_weights)
        for row in self._matrix:
            s += '{}\n'.format(row)
        return s

    def __lt__(self, other):
        """
        A graph is 'smaller if it as more vertices.
        Useful for the priority queue
        """
        return self.num_vertices > other.num_vertices

    def __le__(self, other):
        """
        A graph is 'smaller if it as more vertices.
        Useful for the priority queue
        """
        return self.num_vertices >= other.num_vertices


class RowColSeparation(object):
    def __init__(self, tiling):
        self._tiling = tiling
        self._active_cells = tuple(sorted(tiling.active_cells))

    def cell_at_idx(self, idx):
        """Return the cell at index `idx`."""
        return self._active_cells[idx]

    def cell_idx(self, cell):
        """Return the index of the cell"""
        return self._active_cells.index(cell)

    def _basic_matrix(self, row):
        """
        Compute the basic matrix of inequalities based only on difference in
        row and columns. If `row` is True return the matrix for the row,
        otherwise return if for the columns.
        """
        idx = 1 if row else 0
        num_cell = len(self._active_cells)
        m = []
        for c1 in self._active_cells:
            row = [1 if c1[idx] < c2[idx] else 0 for c2 in self._active_cells]
            m.append(row)
        return m

    @staticmethod
    def _row_cell_order(ob):
        """
        Return the order of the two cells of a length 2 obstruction localized
        in a row.


        A cell `c1` is smaller than cell `c2` if all the points in `c1` are
        lower than all the point in `c2`.

        OUTPUT:
            A tuple (smaller_cell, bigger_cell)
        """
        assert len(ob) == 2, "Obstruction must be of length 2"
        c1, c2 = ob.pos
        assert c1[1] == c2[1], "Obstruction not a row obstruction"
        assert c1[0] != c2[0], "Obstruction is single cell"
        if ob.patt[0] == 0:
            return c2, c1
        else:
            return c1, c2

    @staticmethod
    def _col_cell_order(ob):
        """
        Return the order of the two cells of a length 2 obstruction.

        A cell `c1` is smaller than a cell `c2` if all the points in `c1` must
        be on the left all points in `c2`.

        OUTPUT:
            A tuple (smaller_cell, bigger_cell)
        """
        assert len(ob) == 2, "Obstruction must be of length 2"
        c1, c2 = ob.pos
        assert c1[0] == c2[0], "Obstruction not a col obstruction"
        assert not c1[1] == c2[1], "Obstruction is single cell"
        return c2, c1

    def _add_ineq(self, ineq, matrix):
        """
        Add an inequalities to the matrix.

        The inequalities must a tuple (smaller_cell, bigger_cell).
        """
        small_c, big_c = ineq
        matrix[self.cell_idx(small_c)][self.cell_idx(big_c)] = 1

    def _complete_ineq_matrices(self):
        """
        Return the matrices of inequalities between the cells.

        OUTPUT:
            tuple `(row_matrix, col_matrix)`
        """
        if hasattr(self, '_ineq_matrices'):
            return self._ineq_matrices
        row_m = self._basic_matrix(row=True)
        col_m = self._basic_matrix(row=False)
        filtered_obs = (ob for ob in self._tiling.obstructions
                        if len(ob) == 2 and not ob.is_single_cell())
        for ob in filtered_obs:
            c1, c2 = ob.pos
            if c1[1] == c2[1]:
                ineq = self._row_cell_order(ob)
                self._add_ineq(ineq, row_m)
            elif c1[0] == c2[0]:
                ineq = self._col_cell_order(ob)
                self._add_ineq(ineq, col_m)
        self._ineq_matrices = row_m, col_m
        return self._ineq_matrices

    def row_ineq_graph(self):
        return Graph(self._active_cells, self._complete_ineq_matrices()[0])

    def col_ineq_graph(self):
        return Graph(self._active_cells, self._complete_ineq_matrices()[1])

    @staticmethod
    def _all_order(graph, only_max=False):
        """
        Generator of ordering of the active cells.

        One can get only the maximal separation by setting `only_max` to
        `True`.

        The order are yielded in decreasing order of size.
        """
        max_sep_seen = 0
        graph.reduce()
        heap = [graph]
        while heap and (not only_max or max_sep_seen <= graph.num_vertices):
            graph = heapq.heappop(heap)
            if graph.is_acyclic():
                yield graph.vertex_order()
            else:
                cycle = graph.find_cycle()
                for g in graph.break_cycle_in_all_ways(cycle):
                    g.reduce()
                    heapq.heappush(heap, g)

    @staticmethod
    def _maximal_order(graph):
        """ Returns a order that maximise separation. """
        return next(RowColSeparation._all_order(graph))

    def _separates_tiling(self, row_order, col_order):
        cell_map = self._get_cell_map(row_order, col_order)
        obs = self._map_obstructions(cell_map)
        reqs = self._map_requirements(cell_map)
        return self._tiling.__class__(obstructions=obs, requirements=reqs)

    @staticmethod
    def _get_cell_map(row_order, col_order):
        """
        Return the position of the according to the given row_order and
        col_order.
        """
        cell_map = dict()
        for i, row in enumerate(row_order):
            for cell in row:
                cell_map[cell] = (None, i)
        for i, col in enumerate(col_order):
            for cell in col:
                cell_map[cell] = (i, cell_map[cell][1])
        return cell_map

    def _map_obstructions(self, cell_map):
        """Map the obstruction of a tiling according to the cell map."""
        non_point_obs = (ob for ob in self._tiling.obstructions if len(ob) > 1)
        for ob in non_point_obs:
            ob = self._map_gridded_perm(cell_map, ob)
            if not ob.contradictory():
                yield ob

    def _map_requirements(self, cell_map):
        """Map the requirements of a tiling according to the cell map."""
        for req_list in self._tiling.requirements:
            yield [self._map_gridded_perm(cell_map, req) for req in req_list]

    @property
    def max_row_order(self):
        """A maximal order on the rows."""
        if hasattr(self, '_max_row_order'):
            return self._max_row_order
        self._max_row_order = self._maximal_order(self.row_ineq_graph())
        return self._max_row_order

    @property
    def max_col_order(self):
        """A maximal order on the columns."""
        if hasattr(self, '_max_col_order'):
            return self._max_col_order
        self._max_col_order = self._maximal_order(self.col_ineq_graph())
        return self._max_col_order

    @staticmethod
    def _map_gridded_perm(cell_map, gp):
        """
        Transform a gridded perm by mapping the position of the gridded perm
        according to the cell_map
        """
        pos = (cell_map[p] for p in gp.pos)
        gp = gp.__class__(gp.patt, pos)
        return gp

    def separable(self):
        """
        Test if the tiling is separable.

        A tiling is not separable the separation does not creates any new row
        or column.
        """
        ncol, nrow = self._tiling.dimensions
        return len(self.max_row_order) > nrow or len(self.max_col_order) > ncol

    def separated_tiling(self):
        """
        Return the one the possible maximal separation of the tiling.
        """
        return self._separates_tiling(self.max_row_order, self.max_col_order)

    def all_separated_tiling(self, only_max=False):
        """
        Generator over all the possibles separation of the tiling.

        One can only get the maximal one by setting `only_max=True`.

        NOTE: The same tiling might be returned many times.
        """
        orders = product(
            self._all_order(self.row_ineq_graph(), only_max=only_max),
            self._all_order(self.col_ineq_graph(), only_max=only_max),
        )
        for row_order, col_order in orders:
            yield self._separates_tiling(row_order, col_order)

    def formal_step(self):
        """
        Returns a string describing the operation that was performed.
        """
        return 'Row and column separation'

    def rule(self):
        """
        Return a comb_spec_searcher rule for the separation.

        If the tiling is not separable, returns None.
        """
        if self.separable():
            return InferralRule(self.formal_step(), self.separated_tiling())