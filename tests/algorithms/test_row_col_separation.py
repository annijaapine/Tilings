from itertools import product

import pytest

from permuta import Perm
from tilings import GriddedPerm, Tiling
from tilings.algorithms.row_col_separation import (
    Graph,
    RowColSeparation,
    _RowColSeparationSingleApplication,
)

# ----------------------------------------------------------------------------
#           Test for the Graph class
# ----------------------------------------------------------------------------


@pytest.fixture
def matrix():
    return [[1, 2, 3], [4, 5, 6], [7, 8, 9]]


@pytest.fixture
def matrix2():
    m = [
        [0, 1, 0, 1, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0],
        [0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0],
    ]
    return m


@pytest.fixture
def graph_with_matrix(matrix):
    G = Graph(range(3), matrix=matrix)
    return G


@pytest.fixture
def graph1(matrix2):
    g = Graph(range(5), matrix=matrix2)
    return g


@pytest.fixture
def graph2():
    m = [[0, 0, 1, 0], [1, 0, 1, 1], [1, 0, 0, 1], [0, 0, 1, 0]]
    g = Graph(range(4), matrix=m)
    return g


@pytest.fixture
def graph3():
    m = [[0, 1, 1], [0, 0, 0], [0, 0, 0]]
    g = Graph(range(3), matrix=m)
    return g


@pytest.fixture
def empty_graph():
    return Graph([], [])


def test_init_graph(matrix2):
    G = Graph("abcde", matrix=matrix2)
    assert G._matrix == matrix2
    assert G._vertex_labels == [set(c) for c in "abcde"]
    assert G._vertex_weights == [1 for _ in range(5)]
    assert not G._reduced
    assert not G._is_acyclic


def test_num_vertices(graph_with_matrix):
    assert graph_with_matrix.num_vertices == 3


def test_add_matrix_rows1(graph_with_matrix):
    graph_with_matrix._add_matrix_rows(0, 1)
    assert graph_with_matrix._matrix == [[5, 7, 9], [7, 8, 9]]


def test_add_matrix_rows2(graph_with_matrix):
    graph_with_matrix._add_matrix_rows(0, 2)
    assert graph_with_matrix._matrix == [[8, 10, 12], [4, 5, 6]]


def test_add_matrix_rows3(graph_with_matrix):
    graph_with_matrix._add_matrix_rows(1, 2)
    assert graph_with_matrix._matrix == [[1, 2, 3], [11, 13, 15]]


def test_add_matrix_columns1(graph_with_matrix):
    graph_with_matrix._add_matrix_columns(0, 1)
    assert graph_with_matrix._matrix == [[3, 3], [9, 6], [15, 9]]


def test_add_matrix_columns2(graph_with_matrix):
    graph_with_matrix._add_matrix_columns(0, 2)
    assert graph_with_matrix._matrix == [[4, 2], [10, 5], [16, 8]]


def test_add_matrix_columns3(graph_with_matrix):
    graph_with_matrix._add_matrix_columns(1, 2)
    assert graph_with_matrix._matrix == [[1, 5], [4, 11], [7, 17]]


def test_merge_vertices(graph1, graph2):
    graph1._merge_vertices(2, 4)
    assert graph1.num_vertices == 4
    assert graph1._vertex_labels == [{0}, {1}, {2, 4}, {3}]
    assert graph1._vertex_weights == [1, 1, 2, 1]
    assert graph1._matrix == [
        [0, 1, 0, 1],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 1],
    ]
    graph1._merge_vertices(0, 2)
    assert graph1.num_vertices == 3
    assert graph1._vertex_labels == [{0, 2, 4}, {1}, {3}]
    assert graph1._vertex_weights == [3, 1, 1]
    assert graph1._matrix == [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 1],
    ]
    graph2._merge_vertices(0, 3)
    assert graph2.num_vertices == 3
    assert graph2._vertex_labels == [{0, 3}, {1}, {2}]
    assert graph2._vertex_weights == [2, 1, 1]
    assert graph2._matrix == [
        [0, 0, 2],
        [2, 0, 1],
        [2, 0, 0],
    ]


def test_delete_edge_if_smaller(graph_with_matrix):
    graph_with_matrix._delete_edge_if_small(0, 1, 1)
    assert graph_with_matrix._matrix[0][1] == 2
    graph_with_matrix._delete_edge_if_small(0, 1, 2)
    assert graph_with_matrix._matrix[0][1] == 2
    graph_with_matrix._delete_edge_if_small(0, 1, 3)
    assert graph_with_matrix._matrix[0][1] == 0
    assert graph_with_matrix._matrix == [[1, 0, 3], [4, 5, 6], [7, 8, 9]]


def test_trim_edges(graph_with_matrix):
    graph_with_matrix._vertex_weights[1] = 3
    graph_with_matrix._trim_edges(1)
    assert graph_with_matrix._matrix == [
        [1, 0, 3],
        [4, 0, 6],
        [7, 8, 9],
    ]


def test_find_non_edges(graph2, empty_graph):
    assert set(graph2.find_non_edge()) == {0, 3}
    assert empty_graph.find_non_edge() is None


def test_reduce(graph1, graph2):
    graph2.reduce()
    assert graph2._matrix == [[0, 0, 2], [2, 0, 1], [2, 0, 0]]
    # Test that making it twice does nothing
    graph2.reduce()
    assert graph2._matrix == [[0, 0, 2], [2, 0, 1], [2, 0, 0]]
    graph1.reduce()
    assert graph1._matrix == [[0]]
    assert graph1._reduced


def test_is_acyclic(graph1, graph2, graph3, empty_graph):
    graph2.reduce()
    assert not graph2.is_acyclic()
    for g in graph2.break_cycle_in_all_ways([(0, 2), (2, 0)]):
        g.reduce()
        assert g.is_acyclic()
    graph1.reduce()
    assert graph1.is_acyclic()
    graph3.reduce()
    assert graph3.is_acyclic()
    empty_graph.reduce()
    assert empty_graph.is_acyclic()
    g = Graph(range(4), [[0, 0, 1, 1], [1, 0, 0, 1], [0, 1, 0, 1], [0, 0, 0, 0]])
    g.reduce()
    assert not g.is_acyclic()


def test_find_cyle(graph1, graph2):
    graph2.reduce()
    assert set(graph2.find_cycle()) == set([(0, 2), (2, 0)])
    graph1.reduce()
    assert graph1.find_cycle() is None
    three_cycle = Graph(range(3), [[0, 1, 0], [0, 0, 1], [1, 0, 0]])
    three_cycle.reduce()
    assert set(three_cycle.find_cycle()) == set([(0, 1), (1, 2), (2, 0)])


def test_break_cycle_in_all_ways(graph2):
    graph2.reduce()
    childs = list(graph2.break_cycle_in_all_ways([(0, 2), (2, 0)]))
    assert len(childs) == 2
    g = childs[0]
    assert g._matrix == [[0, 0, 0], [2, 0, 1], [2, 0, 0]]
    g = childs[1]
    assert g._matrix == [[0, 0, 2], [2, 0, 1], [0, 0, 0]]
    assert g._vertex_labels == graph2._vertex_labels
    assert g._vertex_weights == graph2._vertex_weights
    # Test that changes on g does not affect graph2
    g._matrix[0][1] = 10
    assert graph2._matrix[0][1] == 0
    g._matrix[0] = None
    assert graph2._matrix[0] is not None
    g._vertex_labels[0].add(10)
    assert graph2._vertex_labels[0] == set([0, 3])
    g._vertex_labels[0] = None
    assert graph2._vertex_labels[0] == set([0, 3])
    g._vertex_weights[1] = 10
    assert graph2._vertex_weights[1] == 1


def test_length3_cycle():
    g = Graph([1, 2, 3, 4], [[0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, 0], [1, 1, 1, 0]])
    cycle = set([(0, 1), (1, 2), (2, 0)])
    assert set(g._length3_cycle(0, 1, 2)) == cycle
    assert set(g._length3_cycle(0, 2, 1)) == cycle
    assert set(g._length3_cycle(1, 0, 2)) == cycle
    assert set(g._length3_cycle(1, 2, 0)) == cycle
    assert set(g._length3_cycle(2, 0, 1)) == cycle
    assert set(g._length3_cycle(2, 1, 0)) == cycle


def test_vertex_order(graph2, graph3):
    graph2.reduce()
    vertices = graph2._vertex_labels
    childs = list(graph2.break_cycle_in_all_ways([(0, 2), (2, 0)]))
    g = childs[0]
    g.reduce()
    assert g.vertex_order() == [vertices[1], vertices[2], vertices[0]]
    g = childs[1]
    g.reduce()
    assert g.vertex_order() == [vertices[1], vertices[0], vertices[2]]

    print(graph3)
    graph3.reduce()
    assert graph3.vertex_order() == [set([0]), set([1, 2])]


def test_le(graph2, graph3):
    assert graph2 < graph3
    assert graph2 <= graph3


# ----------------------------------------------------------------------------
#           Test for the _RowColSeparationSingleApplication class
# ----------------------------------------------------------------------------


@pytest.fixture
def not_separable_tilings():
    t1 = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1, 2)), ((0, 0),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((1, 0),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((2, 0),) * 3),
            GriddedPerm(Perm((0, 1)), ((0, 0), (1, 0))),
            GriddedPerm(Perm((0, 1)), ((1, 0), (2, 0))),
        ]
    )
    t2 = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1, 2)), ((0, 0),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((1, 0),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((2, 0),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((3, 0),) * 3),
            GriddedPerm(Perm((0, 1)), ((0, 0), (1, 0))),
            GriddedPerm(Perm((0, 1)), ((0, 0), (2, 0))),
            GriddedPerm(Perm((0, 1)), ((1, 0), (2, 0))),
            GriddedPerm(Perm((0, 1)), ((2, 0), (3, 0))),
        ]
    )
    t3 = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1, 2)), ((0, 0),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((1, 0),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((2, 0),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((3, 0),) * 3),
            GriddedPerm(Perm((0, 1)), ((0, 0), (2, 0))),
            GriddedPerm(Perm((0, 1)), ((0, 0), (3, 0))),
            GriddedPerm(Perm((1, 0)), ((1, 0), (2, 0))),
            GriddedPerm(Perm((0, 1)), ((1, 0), (3, 0))),
        ]
    )
    t4 = Tiling(
        obstructions=(
            GriddedPerm(Perm((0,)), ((1, 1),)),
            GriddedPerm(Perm((0,)), ((1, 2),)),
            GriddedPerm(Perm((0, 1)), ((0, 0), (0, 0))),
            GriddedPerm(Perm((0, 1)), ((0, 0), (0, 1))),
            GriddedPerm(Perm((0, 1)), ((0, 1), (0, 1))),
            GriddedPerm(Perm((0, 1)), ((0, 1), (0, 2))),
            GriddedPerm(Perm((0, 1)), ((0, 2), (0, 2))),
            GriddedPerm(Perm((0, 1)), ((1, 0), (1, 0))),
            GriddedPerm(Perm((1, 0)), ((0, 2), (0, 0))),
        ),
        requirements=((GriddedPerm(Perm((0,)), ((0, 1),)),),),
    )
    return [t1, t2, t3, t4]


@pytest.fixture
def separable_tiling1():
    t1 = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1, 2)), ((0, 0),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((1, 0),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((2, 0),) * 3),
            GriddedPerm(Perm((0, 1)), ((0, 0), (1, 0))),
            GriddedPerm(Perm((0, 1)), ((1, 0), (2, 0))),
            GriddedPerm(Perm((0, 1)), ((0, 0), (2, 0))),
        ]
    )
    return t1


@pytest.fixture
def separable_tiling2():
    t2 = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1, 2)), ((0, 0),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((1, 0),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((2, 0),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((3, 0),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((0, 1),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((1, 1),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((2, 1),) * 3),
            GriddedPerm(Perm((0,)), ((3, 1),)),
            GriddedPerm(Perm((0, 1)), ((0, 0), (0, 1))),
            GriddedPerm(Perm((0, 1)), ((0, 0), (1, 0))),
            GriddedPerm(Perm((0, 1)), ((0, 0), (2, 0))),
            GriddedPerm(Perm((0, 1)), ((0, 0), (3, 0))),
            GriddedPerm(Perm((0, 1)), ((1, 0), (2, 0))),
            GriddedPerm(Perm((0, 1)), ((2, 0), (3, 0))),
            GriddedPerm(Perm((0, 1)), ((0, 1), (1, 1))),
            GriddedPerm(Perm((0, 1)), ((0, 1), (2, 1))),
            GriddedPerm(Perm((0, 1)), ((0, 1), (3, 1))),
            GriddedPerm(Perm((0, 1)), ((1, 1), (2, 1))),
            GriddedPerm(Perm((0, 1)), ((2, 1), (3, 1))),
        ]
    )
    return t2


@pytest.fixture
def separable_tiling3():
    t3 = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1, 2)), ((0, 0),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((1, 0),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((2, 0),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((3, 0),) * 3),
            GriddedPerm(Perm((0, 1)), ((0, 0), (2, 0))),
            GriddedPerm(Perm((0, 1)), ((0, 0), (3, 0))),
            GriddedPerm(Perm((0, 1)), ((1, 0), (2, 0))),
            GriddedPerm(Perm((0, 1)), ((1, 0), (3, 0))),
        ]
    )
    return t3


@pytest.fixture
def separable_tiling4():
    return Tiling(
        obstructions=(
            GriddedPerm(Perm((0,)), ((1, 1),)),
            GriddedPerm(Perm((0,)), ((1, 2),)),
            GriddedPerm(Perm((0, 1)), ((0, 0), (0, 0))),
            GriddedPerm(Perm((0, 1)), ((0, 0), (0, 1))),
            GriddedPerm(Perm((0, 1)), ((0, 1), (0, 1))),
            GriddedPerm(Perm((0, 1)), ((0, 1), (0, 2))),
            GriddedPerm(Perm((0, 1)), ((0, 2), (0, 2))),
            GriddedPerm(Perm((0, 1)), ((1, 0), (1, 0))),
            GriddedPerm(Perm((1, 0)), ((0, 2), (0, 0))),
            GriddedPerm(Perm((0, 1)), ((0, 0), (0, 2))),
        ),
        requirements=((GriddedPerm(Perm((0,)), ((0, 1),)),),),
    )


def assert_matrix_entry_is(rcs, matrix, cell1, cell2, value):
    i1 = rcs.cell_idx(cell1)
    i2 = rcs.cell_idx(cell2)
    if matrix[i1][i2] != value:
        m = "Value matrix[{}][{}] is {}, not {}".format(
            cell1, cell2, matrix[i1][i2], value
        )
        raise AssertionError(m)


def test_init(separable_tiling2):
    rcs = _RowColSeparationSingleApplication(separable_tiling2)
    assert rcs._tiling == separable_tiling2
    assert len(rcs._active_cells) == 7
    assert (3, 1) not in rcs._active_cells


def test_cell_idx(separable_tiling2):
    rcs = _RowColSeparationSingleApplication(separable_tiling2)
    for c in separable_tiling2.active_cells:
        assert c == rcs.cell_at_idx(rcs.cell_idx(c))


def test_cell_at_idx(separable_tiling2):
    rcs = _RowColSeparationSingleApplication(separable_tiling2)
    for i in range(len(separable_tiling2.active_cells)):
        assert i == rcs.cell_idx(rcs.cell_at_idx(i))


def test_basic_matrix(separable_tiling2):
    rcs = _RowColSeparationSingleApplication(separable_tiling2)
    # Row basic matrix
    m = rcs._basic_matrix(True)
    for c1, c2 in product(separable_tiling2.active_cells, repeat=2):
        if c1[1] < c2[1]:
            assert_matrix_entry_is(rcs, m, c1, c2, 1)
        else:
            assert_matrix_entry_is(rcs, m, c1, c2, 0)
    # Column basic matrix
    m = rcs._basic_matrix(False)
    for c1, c2 in product(separable_tiling2.active_cells, repeat=2):
        if c1[0] < c2[0]:
            assert_matrix_entry_is(rcs, m, c1, c2, 1)
        else:
            assert_matrix_entry_is(rcs, m, c1, c2, 0)


def test_cell_order(separable_tiling1):
    rcs = _RowColSeparationSingleApplication(separable_tiling1)
    ob = GriddedPerm(Perm((0, 1)), ((0, 0), (0, 1)))
    assert rcs._col_cell_order(ob) == ((0, 1), (0, 0))
    ob = GriddedPerm(Perm((1, 0)), ((0, 1), (0, 0)))
    assert rcs._col_cell_order(ob) == ((0, 0), (0, 1))
    ob = GriddedPerm(Perm((0, 1)), ((0, 0), (1, 0)))
    assert rcs._row_cell_order(ob) == ((1, 0), (0, 0))
    ob = GriddedPerm(Perm((1, 0)), ((0, 0), (1, 0)))
    assert rcs._row_cell_order(ob) == ((0, 0), (1, 0))


def test_complete_inequalities_matrices(separable_tiling2):
    rcs = _RowColSeparationSingleApplication(separable_tiling2)
    row_m, col_m = rcs._complete_ineq_matrices()
    # Row basic matrix
    ob_ineq = [
        ((1, 0), (0, 0)),
        ((2, 0), (0, 0)),
        ((3, 0), (0, 0)),
        ((1, 1), (0, 1)),
        ((2, 1), (0, 1)),
        ((2, 0), (1, 0)),
        ((2, 1), (1, 1)),
        ((3, 0), (2, 0)),
    ]
    for c1, c2 in product(separable_tiling2.active_cells, repeat=2):
        if c1[1] < c2[1] or (c1, c2) in ob_ineq:
            print(1, c1, c2)
            assert_matrix_entry_is(rcs, row_m, c1, c2, 1)
        else:
            print(0, c1, c2)
            assert_matrix_entry_is(rcs, row_m, c1, c2, 0)
    assert rcs._ineq_matrices == (row_m, col_m)
    # Column basic matrix
    ob_ineq = [((0, 1), (0, 0))]
    for c1, c2 in product(separable_tiling2.active_cells, repeat=2):
        if c1[0] < c2[0] or (c1, c2) in ob_ineq:
            assert_matrix_entry_is(rcs, col_m, c1, c2, 1)
        else:
            assert_matrix_entry_is(rcs, col_m, c1, c2, 0)


def test_row_ineq_graph(separable_tiling2):
    rcs = _RowColSeparationSingleApplication(separable_tiling2)
    assert rcs.row_ineq_graph()._matrix == rcs._complete_ineq_matrices()[0]


def test_col_ineq_graph(separable_tiling2):
    rcs = _RowColSeparationSingleApplication(separable_tiling2)
    assert rcs.col_ineq_graph()._matrix == rcs._complete_ineq_matrices()[1]


def test_all_order():
    t = Tiling(obstructions=[GriddedPerm(Perm((0, 1)), ((0, 0), (1, 0)))])
    rcs = _RowColSeparationSingleApplication(t)
    assert list(rcs._all_order(rcs.row_ineq_graph())) == [[{(1, 0)}, {(0, 0)}]]
    assert list(rcs._all_order(rcs.col_ineq_graph())) == [[{(0, 0)}, {(1, 0)}]]
    t = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1)), ((0, 0), (1, 0))),
            GriddedPerm(Perm((1, 0)), ((0, 0), (1, 0))),
        ]
    )
    rcs = _RowColSeparationSingleApplication(t)
    assert sorted(rcs._all_order(rcs.row_ineq_graph())) == [
        [{(1, 0)}, {(0, 0)}],
        [{(0, 0)}, {(1, 0)}],
    ]
    assert list(rcs._all_order(rcs.col_ineq_graph())) == [[{(0, 0)}, {(1, 0)}]]


def test_maximal_order():
    t = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1)), ((0, 0), (1, 0))),
            GriddedPerm(Perm((1, 0)), ((0, 0), (1, 0))),
        ]
    )
    rcs = _RowColSeparationSingleApplication(t)
    possible_order = [
        [{(1, 0)}, {(0, 0)}],
        [{(0, 0)}, {(1, 0)}],
    ]
    assert sorted(rcs._maximal_order(rcs.row_ineq_graph())) in possible_order
    assert rcs.max_row_order in possible_order
    assert list(rcs._maximal_order(rcs.col_ineq_graph())) == [{(0, 0)}, {(1, 0)}]
    assert rcs.max_col_order == [{(0, 0)}, {(1, 0)}]


def test_separates_tiling():
    t = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1)), ((0, 0), (1, 0))),
            GriddedPerm(Perm((2, 0, 1)), ((0, 0), (1, 0), (1, 0))),
            GriddedPerm(Perm((2, 0, 1)), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm(Perm((2, 0, 1)), ((1, 0), (1, 0), (1, 0))),
        ],
        requirements=[[GriddedPerm(Perm((0,)), ((1, 0),))]],
    )
    print(t)
    rcs = _RowColSeparationSingleApplication(t)
    row_order = [{(1, 0)}, {(0, 0)}]
    col_order = [{(0, 0)}, {(1, 0)}]
    sep_t = rcs._separates_tiling(row_order, col_order)
    print(sep_t)
    assert sep_t == Tiling(
        obstructions=[
            GriddedPerm(Perm((2, 0, 1)), ((0, 1), (1, 0), (1, 0))),
            GriddedPerm(Perm((2, 0, 1)), ((0, 1), (0, 1), (0, 1))),
            GriddedPerm(Perm((2, 0, 1)), ((1, 0), (1, 0), (1, 0))),
        ],
        requirements=[[GriddedPerm(Perm((0,)), ((1, 0),))]],
    )


def test_map_gridded_perm(separable_tiling1):
    rcs = _RowColSeparationSingleApplication(separable_tiling1)
    ob = GriddedPerm(Perm((0, 1, 2)), ((0, 0), (1, 0), (1, 0)))
    cell_map = {(0, 0): (0, 0), (1, 0): (1, 1)}
    assert rcs._map_gridded_perm(cell_map, ob) == GriddedPerm(
        Perm((0, 1, 2)), ((0, 0), (1, 1), (1, 1))
    )
    ob = GriddedPerm(Perm((0, 1, 2)), ((0, 0), (1, 0), (1, 0)))
    assert rcs._map_gridded_perm(cell_map, ob) == GriddedPerm(
        Perm((0, 1, 2)), ((0, 0), (1, 1), (1, 1))
    )


def test_all_separation():
    t = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1)), ((0, 0),) * 2),
            GriddedPerm(Perm((0, 1)), ((1, 0),) * 2),
            GriddedPerm(Perm((0, 1)), ((0, 0), (1, 0))),
            GriddedPerm(Perm((1, 0)), ((0, 0), (1, 0))),
        ]
    )
    assert len(list(_RowColSeparationSingleApplication(t).all_separated_tiling())) == 2
    assert (
        len(
            list(
                _RowColSeparationSingleApplication(t).all_separated_tiling(
                    only_max=False
                )
            )
        )
        == 2
    )


# ----------------------------------------------------------------------------
#           Test for the RowColSeparation class
# ----------------------------------------------------------------------------


def test_separated_tiling(
    not_separable_tilings,
    separable_tiling1,
    separable_tiling2,
    separable_tiling3,
    separable_tiling4,
):
    t = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1)), ((0, 0),) * 2),
            GriddedPerm(Perm((0, 1)), ((1, 0),) * 2),
            GriddedPerm(Perm((0, 1)), ((0, 0), (1, 0))),
        ]
    )
    rcs = RowColSeparation(t)
    print(t)
    print(rcs.separated_tiling())
    assert rcs.separated_tiling() == Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1)), ((0, 1),) * 2),
            GriddedPerm(Perm((0, 1)), ((1, 0),) * 2),
        ]
    )
    for t in not_separable_tilings:
        rcs = RowColSeparation(t)
        assert t == rcs.separated_tiling()
    t1_sep = Tiling(
        obstructions=(
            GriddedPerm(Perm((0,)), ((0, 0),)),
            GriddedPerm(Perm((0,)), ((0, 1),)),
            GriddedPerm(Perm((0,)), ((1, 0),)),
            GriddedPerm(Perm((0,)), ((1, 2),)),
            GriddedPerm(Perm((0,)), ((2, 1),)),
            GriddedPerm(Perm((0,)), ((2, 2),)),
            GriddedPerm(Perm((0, 1, 2)), ((0, 2), (0, 2), (0, 2))),
            GriddedPerm(Perm((0, 1, 2)), ((1, 1), (1, 1), (1, 1))),
            GriddedPerm(Perm((0, 1, 2)), ((2, 0), (2, 0), (2, 0))),
        ),
        requirements=(),
    )
    t2_sep = Tiling(
        obstructions=(
            GriddedPerm(Perm((0,)), ((0, 0),)),
            GriddedPerm(Perm((0,)), ((0, 1),)),
            GriddedPerm(Perm((0,)), ((0, 2),)),
            GriddedPerm(Perm((0,)), ((0, 3),)),
            GriddedPerm(Perm((0,)), ((1, 0),)),
            GriddedPerm(Perm((0,)), ((1, 2),)),
            GriddedPerm(Perm((0,)), ((1, 3),)),
            GriddedPerm(Perm((0,)), ((1, 4),)),
            GriddedPerm(Perm((0,)), ((2, 1),)),
            GriddedPerm(Perm((0,)), ((2, 2),)),
            GriddedPerm(Perm((0,)), ((2, 4),)),
            GriddedPerm(Perm((0,)), ((3, 1),)),
            GriddedPerm(Perm((0,)), ((3, 3),)),
            GriddedPerm(Perm((0,)), ((3, 4),)),
            GriddedPerm(Perm((0,)), ((4, 1),)),
            GriddedPerm(Perm((0,)), ((4, 2),)),
            GriddedPerm(Perm((0,)), ((4, 3),)),
            GriddedPerm(Perm((0,)), ((4, 4),)),
            GriddedPerm(Perm((0, 1)), ((2, 0), (3, 0))),
            GriddedPerm(Perm((0, 1)), ((3, 0), (4, 0))),
            GriddedPerm(Perm((0, 1, 2)), ((0, 4), (0, 4), (0, 4))),
            GriddedPerm(Perm((0, 1, 2)), ((1, 1), (1, 1), (1, 1))),
            GriddedPerm(Perm((0, 1, 2)), ((2, 0), (2, 0), (2, 0))),
            GriddedPerm(Perm((0, 1, 2)), ((2, 3), (2, 3), (2, 3))),
            GriddedPerm(Perm((0, 1, 2)), ((3, 0), (3, 0), (3, 0))),
            GriddedPerm(Perm((0, 1, 2)), ((3, 2), (3, 2), (3, 2))),
            GriddedPerm(Perm((0, 1, 2)), ((4, 0), (4, 0), (4, 0))),
        ),
        requirements=(),
    )
    t3_sep = Tiling(
        obstructions=(
            GriddedPerm(Perm((0,)), ((0, 0),)),
            GriddedPerm(Perm((0,)), ((1, 0),)),
            GriddedPerm(Perm((0,)), ((2, 1),)),
            GriddedPerm(Perm((0,)), ((3, 1),)),
            GriddedPerm(Perm((0, 1, 2)), ((0, 1), (0, 1), (0, 1))),
            GriddedPerm(Perm((0, 1, 2)), ((1, 1), (1, 1), (1, 1))),
            GriddedPerm(Perm((0, 1, 2)), ((2, 0), (2, 0), (2, 0))),
            GriddedPerm(Perm((0, 1, 2)), ((3, 0), (3, 0), (3, 0))),
        ),
        requirements=(),
    )
    t4_sep = Tiling(
        obstructions=(
            GriddedPerm(Perm((0, 1)), ((0, 2),) * 2),
            GriddedPerm(Perm((0, 1)), ((1, 1),) * 2),
            GriddedPerm(Perm((0, 1)), ((2, 0),) * 2),
            GriddedPerm(Perm((0, 1)), ((3, 0),) * 2),
            GriddedPerm(Perm((1, 0)), ((0, 2), (2, 0))),
        ),
        requirements=((GriddedPerm(Perm((0,)), ((1, 1),)),),),
    )
    assert RowColSeparation(separable_tiling1).separated_tiling() == t1_sep
    assert RowColSeparation(separable_tiling2).separated_tiling() == t2_sep
    assert RowColSeparation(separable_tiling3).separated_tiling() == t3_sep
    assert RowColSeparation(separable_tiling4).separated_tiling() == t4_sep
    # Test for the empty tiling
    empty_tiling = Tiling(obstructions=[GriddedPerm(Perm((0,)), ((0, 0),))])
    assert RowColSeparation(empty_tiling).separated_tiling() == empty_tiling


def test_separable(
    not_separable_tilings, separable_tiling1, separable_tiling2, separable_tiling3
):
    for t in not_separable_tilings:
        rcs = RowColSeparation(t)
        assert not rcs.separable()
    for t in [separable_tiling1, separable_tiling2, separable_tiling3]:
        rcs = RowColSeparation(t)
        assert rcs.separable()


def test_multiple_separation():
    """
    Test that the row column separation is idempotent. This tilings needs two
    pass of the algorithm to stabilize.
    """
    t = Tiling(
        obstructions=(
            GriddedPerm(Perm((0,)), ((0, 0),)),
            GriddedPerm(Perm((0,)), ((0, 1),)),
            GriddedPerm(Perm((0,)), ((0, 3),)),
            GriddedPerm(Perm((0,)), ((1, 0),)),
            GriddedPerm(Perm((0,)), ((1, 2),)),
            GriddedPerm(Perm((0,)), ((1, 3),)),
            GriddedPerm(Perm((0,)), ((1, 4),)),
            GriddedPerm(Perm((0,)), ((2, 1),)),
            GriddedPerm(Perm((0,)), ((2, 3),)),
            GriddedPerm(Perm((0,)), ((3, 0),)),
            GriddedPerm(Perm((0,)), ((3, 1),)),
            GriddedPerm(Perm((0,)), ((3, 2),)),
            GriddedPerm(Perm((0,)), ((3, 4),)),
            GriddedPerm(Perm((0,)), ((4, 1),)),
            GriddedPerm(Perm((0,)), ((4, 3),)),
            GriddedPerm(Perm((0, 1)), ((0, 2), (0, 2))),
            GriddedPerm(Perm((0, 1)), ((0, 2), (2, 2))),
            GriddedPerm(Perm((0, 1)), ((0, 4), (4, 4))),
            GriddedPerm(Perm((0, 1)), ((1, 1), (1, 1))),
            GriddedPerm(Perm((0, 1)), ((2, 0), (2, 0))),
            GriddedPerm(Perm((0, 1)), ((2, 2), (2, 2))),
            GriddedPerm(Perm((0, 1)), ((2, 2), (2, 4))),
            GriddedPerm(Perm((0, 1)), ((2, 4), (2, 4))),
            GriddedPerm(Perm((0, 1)), ((2, 4), (4, 4))),
            GriddedPerm(Perm((0, 1)), ((3, 3), (3, 3))),
            GriddedPerm(Perm((0, 1)), ((4, 0), (4, 4))),
            GriddedPerm(Perm((0, 1)), ((4, 2), (4, 2))),
            GriddedPerm(Perm((0, 1)), ((4, 2), (4, 4))),
            GriddedPerm(Perm((1, 0)), ((0, 2), (2, 2))),
            GriddedPerm(Perm((1, 0)), ((1, 1), (1, 1))),
            GriddedPerm(Perm((1, 0)), ((2, 2), (2, 0))),
            GriddedPerm(Perm((1, 0)), ((2, 2), (2, 2))),
            GriddedPerm(Perm((1, 0)), ((2, 2), (4, 2))),
            GriddedPerm(Perm((1, 0)), ((2, 4), (2, 2))),
            GriddedPerm(Perm((1, 0)), ((2, 4), (4, 4))),
            GriddedPerm(Perm((1, 0)), ((3, 3), (3, 3))),
            GriddedPerm(Perm((1, 0)), ((4, 4), (4, 2))),
            GriddedPerm(Perm((0, 1, 2)), ((0, 2), (0, 4), (0, 4))),
            GriddedPerm(Perm((0, 1, 2)), ((0, 2), (0, 4), (2, 4))),
            GriddedPerm(Perm((0, 1, 2)), ((0, 4), (0, 4), (0, 4))),
            GriddedPerm(Perm((0, 1, 2)), ((0, 4), (0, 4), (2, 4))),
            GriddedPerm(Perm((0, 1, 2)), ((2, 0), (4, 0), (4, 0))),
            GriddedPerm(Perm((0, 1, 2)), ((2, 0), (4, 0), (4, 2))),
            GriddedPerm(Perm((0, 1, 2)), ((4, 0), (4, 0), (4, 2))),
            GriddedPerm(Perm((0, 2, 1)), ((0, 2), (0, 4), (4, 4))),
            GriddedPerm(Perm((0, 2, 1)), ((2, 0), (2, 2), (4, 0))),
            GriddedPerm(Perm((0, 2, 1)), ((2, 0), (4, 4), (4, 0))),
            GriddedPerm(Perm((1, 0, 2)), ((2, 2), (4, 0), (4, 2))),
            GriddedPerm(Perm((1, 0, 2)), ((4, 4), (4, 4), (4, 4))),
            GriddedPerm(Perm((1, 2, 0)), ((4, 4), (4, 4), (4, 4))),
            GriddedPerm(Perm((2, 0, 1)), ((4, 4), (4, 4), (4, 4))),
            GriddedPerm(Perm((0, 2, 1, 3)), ((4, 0), (4, 0), (4, 0), (4, 0))),
            GriddedPerm(Perm((0, 2, 3, 1)), ((4, 0), (4, 0), (4, 0), (4, 0))),
            GriddedPerm(Perm((0, 3, 1, 2)), ((4, 0), (4, 0), (4, 0), (4, 0))),
            GriddedPerm(Perm((0, 3, 1, 2)), ((4, 0), (4, 2), (4, 0), (4, 0))),
            GriddedPerm(Perm((1, 2, 0, 3)), ((4, 0), (4, 0), (4, 0), (4, 0))),
            GriddedPerm(Perm((2, 0, 1, 3)), ((2, 0), (4, 0), (4, 0), (4, 0))),
            GriddedPerm(Perm((2, 0, 1, 3)), ((4, 0), (4, 0), (4, 0), (4, 0))),
        ),
        requirements=(
            (GriddedPerm(Perm((0,)), ((1, 1),)),),
            (GriddedPerm(Perm((0,)), ((2, 2),)),),
            (GriddedPerm(Perm((0,)), ((3, 3),)),),
        ),
    )
    rcs = RowColSeparation(t)
    seprated_tiling = rcs.separated_tiling()
    expected_tiling = Tiling(
        obstructions=(
            GriddedPerm(Perm((0,)), ((0, 0),)),
            GriddedPerm(Perm((0,)), ((0, 1),)),
            GriddedPerm(Perm((0,)), ((0, 2),)),
            GriddedPerm(Perm((0,)), ((0, 3),)),
            GriddedPerm(Perm((0,)), ((0, 4),)),
            GriddedPerm(Perm((0,)), ((0, 5),)),
            GriddedPerm(Perm((0,)), ((0, 6),)),
            GriddedPerm(Perm((0,)), ((1, 0),)),
            GriddedPerm(Perm((0,)), ((1, 1),)),
            GriddedPerm(Perm((0,)), ((1, 3),)),
            GriddedPerm(Perm((0,)), ((1, 4),)),
            GriddedPerm(Perm((0,)), ((1, 5),)),
            GriddedPerm(Perm((0,)), ((1, 6),)),
            GriddedPerm(Perm((0,)), ((1, 7),)),
            GriddedPerm(Perm((0,)), ((2, 0),)),
            GriddedPerm(Perm((0,)), ((2, 2),)),
            GriddedPerm(Perm((0,)), ((2, 3),)),
            GriddedPerm(Perm((0,)), ((2, 4),)),
            GriddedPerm(Perm((0,)), ((2, 5),)),
            GriddedPerm(Perm((0,)), ((2, 6),)),
            GriddedPerm(Perm((0,)), ((2, 7),)),
            GriddedPerm(Perm((0,)), ((3, 0),)),
            GriddedPerm(Perm((0,)), ((3, 1),)),
            GriddedPerm(Perm((0,)), ((3, 2),)),
            GriddedPerm(Perm((0,)), ((3, 4),)),
            GriddedPerm(Perm((0,)), ((3, 5),)),
            GriddedPerm(Perm((0,)), ((3, 6),)),
            GriddedPerm(Perm((0,)), ((3, 7),)),
            GriddedPerm(Perm((0,)), ((4, 0),)),
            GriddedPerm(Perm((0,)), ((4, 1),)),
            GriddedPerm(Perm((0,)), ((4, 2),)),
            GriddedPerm(Perm((0,)), ((4, 3),)),
            GriddedPerm(Perm((0,)), ((4, 4),)),
            GriddedPerm(Perm((0,)), ((4, 6),)),
            GriddedPerm(Perm((0,)), ((4, 7),)),
            GriddedPerm(Perm((0,)), ((5, 0),)),
            GriddedPerm(Perm((0,)), ((5, 1),)),
            GriddedPerm(Perm((0,)), ((5, 2),)),
            GriddedPerm(Perm((0,)), ((5, 3),)),
            GriddedPerm(Perm((0,)), ((5, 4),)),
            GriddedPerm(Perm((0,)), ((5, 5),)),
            GriddedPerm(Perm((0,)), ((5, 7),)),
            GriddedPerm(Perm((0,)), ((6, 0),)),
            GriddedPerm(Perm((0,)), ((6, 1),)),
            GriddedPerm(Perm((0,)), ((6, 2),)),
            GriddedPerm(Perm((0,)), ((6, 3),)),
            GriddedPerm(Perm((0,)), ((6, 5),)),
            GriddedPerm(Perm((0,)), ((6, 6),)),
            GriddedPerm(Perm((0,)), ((6, 7),)),
            GriddedPerm(Perm((0,)), ((7, 1),)),
            GriddedPerm(Perm((0,)), ((7, 2),)),
            GriddedPerm(Perm((0,)), ((7, 3),)),
            GriddedPerm(Perm((0,)), ((7, 4),)),
            GriddedPerm(Perm((0,)), ((7, 5),)),
            GriddedPerm(Perm((0,)), ((7, 6),)),
            GriddedPerm(Perm((0,)), ((7, 7),)),
            GriddedPerm(Perm((0, 1)), ((1, 2), (1, 2))),
            GriddedPerm(Perm((0, 1)), ((2, 1), (2, 1))),
            GriddedPerm(Perm((0, 1)), ((3, 3), (3, 3))),
            GriddedPerm(Perm((0, 1)), ((4, 5), (4, 5))),
            GriddedPerm(Perm((0, 1)), ((6, 4), (6, 4))),
            GriddedPerm(Perm((1, 0)), ((1, 2), (1, 2))),
            GriddedPerm(Perm((1, 0)), ((3, 3), (3, 3))),
            GriddedPerm(Perm((1, 0)), ((4, 5), (4, 5))),
            GriddedPerm(Perm((1, 0)), ((5, 6), (6, 4))),
            GriddedPerm(Perm((0, 1, 2)), ((0, 7), (0, 7), (0, 7))),
            GriddedPerm(Perm((1, 0, 2)), ((5, 6), (5, 6), (5, 6))),
            GriddedPerm(Perm((1, 2, 0)), ((5, 6), (5, 6), (5, 6))),
            GriddedPerm(Perm((2, 0, 1)), ((5, 6), (5, 6), (5, 6))),
            GriddedPerm(Perm((0, 2, 1, 3)), ((7, 0), (7, 0), (7, 0), (7, 0))),
            GriddedPerm(Perm((0, 2, 3, 1)), ((7, 0), (7, 0), (7, 0), (7, 0))),
            GriddedPerm(Perm((0, 3, 1, 2)), ((7, 0), (7, 0), (7, 0), (7, 0))),
            GriddedPerm(Perm((1, 2, 0, 3)), ((7, 0), (7, 0), (7, 0), (7, 0))),
            GriddedPerm(Perm((2, 0, 1, 3)), ((7, 0), (7, 0), (7, 0), (7, 0))),
        ),
        requirements=(
            (GriddedPerm(Perm((0,)), ((1, 2),)),),
            (GriddedPerm(Perm((0,)), ((3, 3),)),),
            (GriddedPerm(Perm((0,)), ((4, 5),)),),
        ),
    )
    assert seprated_tiling == expected_tiling


def test_backmap():
    t = Tiling(
        obstructions=(
            GriddedPerm(Perm((0,)), ((0, 0),)),
            GriddedPerm(Perm((0, 1)), ((0, 1), (0, 1))),
            GriddedPerm(Perm((0, 1)), ((0, 2), (0, 2))),
            GriddedPerm(Perm((0, 1)), ((0, 2), (1, 2))),
            GriddedPerm(Perm((0, 1)), ((1, 0), (1, 2))),
            GriddedPerm(Perm((0, 1)), ((1, 1), (1, 2))),
            GriddedPerm(Perm((0, 1)), ((1, 2), (1, 2))),
            GriddedPerm(Perm((1, 0)), ((0, 2), (1, 2))),
            GriddedPerm(Perm((1, 0)), ((1, 1), (1, 1))),
            GriddedPerm(Perm((1, 0)), ((1, 2), (1, 2))),
            GriddedPerm(Perm((0, 2, 1)), ((0, 1), (0, 2), (0, 2))),
            GriddedPerm(Perm((0, 2, 1)), ((1, 0), (1, 0), (1, 0))),
            GriddedPerm(Perm((0, 2, 1)), ((1, 0), (1, 1), (1, 0))),
            GriddedPerm(Perm((1, 2, 0)), ((0, 1), (0, 2), (1, 1))),
            GriddedPerm(Perm((1, 2, 0)), ((0, 1), (1, 2), (1, 1))),
            GriddedPerm(Perm((1, 2, 0)), ((1, 0), (1, 0), (1, 0))),
            GriddedPerm(Perm((2, 0, 1)), ((0, 2), (0, 1), (0, 2))),
            GriddedPerm(Perm((2, 0, 1)), ((1, 1), (1, 0), (1, 0))),
            GriddedPerm(Perm((2, 0, 1)), ((1, 2), (1, 0), (1, 0))),
            GriddedPerm(Perm((2, 1, 0)), ((0, 1), (1, 1), (1, 0))),
            GriddedPerm(Perm((2, 1, 0)), ((0, 2), (1, 1), (1, 0))),
            GriddedPerm(Perm((2, 1, 0)), ((1, 2), (1, 1), (1, 0))),
            GriddedPerm(Perm((2, 3, 0, 1)), ((0, 1), (0, 2), (1, 0), (1, 0))),
        ),
        requirements=((GriddedPerm(Perm((0,)), ((1, 2),)),),),
        assumptions=(),
    )
    cellmap1 = {
        (0, 1): (0, 1),
        (1, 0): (2, 0),
        (1, 1): (2, 1),
        (1, 2): (1, 2),
    }
    cellmap2 = {
        (0, 1): (0, 1),
        (1, 2): (1, 3),
        (2, 0): (2, 0),
        (2, 1): (3, 2),
    }
    final_cell_map = {
        (0, 1): (0, 1),
        (1, 0): (2, 0),
        (1, 1): (3, 2),
        (1, 2): (1, 3),
    }
    rcs1 = _RowColSeparationSingleApplication(t)
    t1 = rcs1.separated_tiling()
    assert rcs1.get_cell_map() == cellmap1
    rcs2 = _RowColSeparationSingleApplication(t1)
    t2 = rcs2.separated_tiling()
    assert rcs2.get_cell_map() == cellmap2
    rcs = RowColSeparation(t)
    assert rcs.separated_tiling() == t2
    assert RowColSeparation(t).get_cell_map() == final_cell_map


def test_backmap2():
    t = Tiling(
        obstructions=(
            GriddedPerm(Perm((0, 1)), ((0, 0), (1, 2))),
            GriddedPerm(Perm((0, 1)), ((0, 0), (2, 2))),
            GriddedPerm(Perm((0, 1)), ((0, 2), (0, 2))),
            GriddedPerm(Perm((0, 1)), ((1, 0), (2, 0))),
            GriddedPerm(Perm((0, 1)), ((1, 1), (1, 1))),
            GriddedPerm(Perm((0, 1)), ((2, 0), (2, 0))),
            GriddedPerm(Perm((1, 0)), ((0, 0), (0, 0))),
            GriddedPerm(Perm((1, 0)), ((0, 0), (1, 0))),
            GriddedPerm(Perm((1, 0)), ((0, 0), (2, 0))),
            GriddedPerm(Perm((1, 0)), ((0, 2), (1, 2))),
            GriddedPerm(Perm((1, 0)), ((1, 0), (2, 0))),
            GriddedPerm(Perm((1, 0)), ((1, 1), (1, 0))),
            GriddedPerm(Perm((1, 0)), ((1, 2), (1, 0))),
            GriddedPerm(Perm((1, 0)), ((1, 2), (1, 2))),
            GriddedPerm(Perm((1, 0)), ((1, 2), (2, 2))),
            GriddedPerm(Perm((1, 0)), ((2, 2), (2, 2))),
            GriddedPerm(Perm((0, 1, 2)), ((1, 0), (1, 1), (1, 2))),
            GriddedPerm(Perm((0, 1, 2)), ((1, 0), (1, 1), (2, 2))),
            GriddedPerm(Perm((0, 1, 2)), ((1, 0), (1, 2), (1, 2))),
            GriddedPerm(Perm((0, 1, 2)), ((1, 0), (1, 2), (2, 2))),
            GriddedPerm(Perm((0, 2, 1)), ((0, 0), (1, 0), (1, 0))),
            GriddedPerm(Perm((0, 2, 1)), ((1, 0), (1, 0), (1, 0))),
            GriddedPerm(Perm((1, 0, 2)), ((1, 0), (1, 0), (1, 1))),
            GriddedPerm(Perm((1, 0, 2)), ((1, 0), (1, 0), (1, 2))),
            GriddedPerm(Perm((1, 2, 0)), ((1, 0), (1, 0), (1, 0))),
            GriddedPerm(Perm((2, 0, 1)), ((1, 0), (1, 0), (1, 0))),
            GriddedPerm(Perm((2, 1, 0)), ((0, 2), (2, 2), (2, 0))),
        ),
        requirements=((GriddedPerm(Perm((0,)), ((1, 0),)),),),
    )
    cellmap1 = {
        (0, 0): (0, 0),
        (0, 2): (0, 3),
        (1, 0): (1, 1),
        (1, 1): (2, 2),
        (1, 2): (2, 3),
        (2, 2): (3, 3),
    }
    cellmap2 = {
        (0, 0): (0, 0),
        (0, 3): (0, 3),
        (1, 1): (1, 1),
        (2, 2): (3, 2),
        (2, 3): (2, 4),
        (3, 3): (4, 3),
    }
    final_cell_map = {
        (0, 0): (0, 0),
        (0, 2): (0, 3),
        (1, 0): (1, 1),
        (1, 1): (3, 2),
        (1, 2): (2, 4),
        (2, 2): (4, 3),
    }
    print(t)
    rcs1 = _RowColSeparationSingleApplication(t)
    t1 = rcs1.separated_tiling()
    print(t1)
    assert rcs1.get_cell_map() == cellmap1
    rcs2 = _RowColSeparationSingleApplication(t1)
    t2 = rcs2.separated_tiling()
    print(t2)
    assert rcs2.get_cell_map() == cellmap2
    rcs = RowColSeparation(t)
    assert rcs.separated_tiling() == t2
    assert RowColSeparation(t).get_cell_map() == final_cell_map


def test_backmap3():
    t = Tiling(
        obstructions=(
            GriddedPerm(Perm((0, 1)), ((0, 0), (0, 0))),
            GriddedPerm(Perm((0, 1)), ((0, 0), (0, 1))),
            GriddedPerm(Perm((0, 1)), ((0, 0), (0, 2))),
            GriddedPerm(Perm((0, 1)), ((0, 0), (1, 1))),
            GriddedPerm(Perm((0, 1)), ((0, 0), (2, 0))),
            GriddedPerm(Perm((0, 1)), ((0, 0), (2, 2))),
            GriddedPerm(Perm((0, 1)), ((0, 1), (0, 2))),
            GriddedPerm(Perm((0, 1)), ((0, 1), (1, 1))),
            GriddedPerm(Perm((0, 1)), ((0, 2), (0, 2))),
            GriddedPerm(Perm((0, 1)), ((1, 1), (1, 1))),
            GriddedPerm(Perm((0, 1)), ((1, 1), (2, 1))),
            GriddedPerm(Perm((0, 1)), ((2, 0), (2, 0))),
            GriddedPerm(Perm((1, 0)), ((0, 0), (2, 0))),
            GriddedPerm(Perm((1, 0)), ((0, 1), (0, 0))),
            GriddedPerm(Perm((1, 0)), ((0, 1), (2, 1))),
            GriddedPerm(Perm((1, 0)), ((0, 2), (0, 0))),
            GriddedPerm(Perm((1, 0)), ((0, 2), (0, 1))),
            GriddedPerm(Perm((1, 0)), ((1, 1), (2, 1))),
            GriddedPerm(Perm((1, 0)), ((2, 1), (2, 0))),
            GriddedPerm(Perm((1, 0)), ((2, 1), (2, 1))),
            GriddedPerm(Perm((1, 0)), ((2, 2), (2, 1))),
            GriddedPerm(Perm((0, 1, 2)), ((0, 1), (0, 1), (2, 1))),
            GriddedPerm(Perm((0, 1, 2)), ((0, 1), (2, 1), (2, 2))),
            GriddedPerm(Perm((0, 2, 1)), ((0, 1), (0, 1), (0, 1))),
            GriddedPerm(Perm((0, 2, 1)), ((0, 1), (2, 2), (2, 2))),
            GriddedPerm(Perm((0, 2, 1)), ((2, 1), (2, 2), (2, 2))),
            GriddedPerm(Perm((0, 2, 1)), ((2, 2), (2, 2), (2, 2))),
            GriddedPerm(Perm((1, 0, 2)), ((2, 2), (2, 2), (2, 2))),
            GriddedPerm(Perm((1, 2, 0)), ((0, 2), (2, 2), (2, 2))),
            GriddedPerm(Perm((1, 2, 0)), ((2, 2), (2, 2), (2, 2))),
            GriddedPerm(Perm((2, 0, 1)), ((0, 1), (0, 1), (0, 1))),
            GriddedPerm(Perm((2, 0, 1)), ((2, 2), (2, 0), (2, 2))),
            GriddedPerm(Perm((2, 0, 1)), ((2, 2), (2, 2), (2, 2))),
            GriddedPerm(Perm((2, 1, 0)), ((0, 2), (2, 2), (2, 0))),
            GriddedPerm(Perm((2, 1, 0)), ((0, 2), (2, 2), (2, 2))),
            GriddedPerm(Perm((2, 1, 0)), ((2, 2), (2, 2), (2, 0))),
            GriddedPerm(Perm((2, 1, 0)), ((2, 2), (2, 2), (2, 2))),
        ),
        requirements=((GriddedPerm(Perm((0,)), ((2, 1),)),),),
    )
    cellmap1 = {
        (0, 0): (2, 0),
        (0, 1): (0, 2),
        (0, 2): (1, 4),
        (2, 0): (3, 1),
        (2, 1): (3, 3),
        (2, 2): (3, 4),
    }
    print(t)
    rcs1 = _RowColSeparationSingleApplication(t)
    t1 = rcs1.separated_tiling()
    print(t1)
    assert rcs1.get_cell_map() == cellmap1
    rcs = RowColSeparation(t)
    assert rcs.separated_tiling() == t1
    assert rcs.get_cell_map() == cellmap1
