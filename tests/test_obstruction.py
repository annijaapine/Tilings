import pytest

from grids_two import Obstruction
from permuta import Perm
from permuta.misc import DIR_EAST, DIR_NORTH, DIR_SOUTH, DIR_WEST, DIR_NONE


@pytest.fixture
def simpleob():
    return Obstruction(Perm((1, 0, 3, 2)),
                       ((0, 0), (0, 0), (2, 2), (2, 1)))


@pytest.fixture
def singlecellob():
    return Obstruction.single_cell(Perm((1, 0, 3, 2)), (2, 2))


@pytest.fixture
def everycellob():
    return Obstruction(Perm((0, 3, 6, 1, 4, 7, 2, 5, 8)),
                       ((0, 0), (0, 1), (0, 2),
                        (1, 0), (1, 1), (1, 2),
                        (2, 0), (2, 1), (2, 2)))


@pytest.fixture
def typicalob():
    return Obstruction(Perm((1, 0, 2, 4, 3)),
                       ((0, 0), (0, 0), (1, 0), (1, 1), (1, 1)))


@pytest.fixture
def isolatedob():
    return Obstruction(Perm((0, 1, 2)),
                       ((0, 0), (1, 1), (2, 2)))


def test_spans_cell(simpleob):
    assert simpleob.spans_cell((1, 1))
    assert simpleob.spans_cell((0, 2))
    assert simpleob.spans_cell((2, 2))

    assert not simpleob.spans_cell((3, 2))
    assert not simpleob.spans_cell((0, 3))


def test_occupies_cell(simpleob):
    assert simpleob.occupies((0, 0))
    assert simpleob.occupies((2, 1))
    assert simpleob.occupies((2, 2))

    assert not simpleob.occupies((0, 1))
    assert not simpleob.occupies((3, 1))
    assert not simpleob.occupies((2, 0))


def test_occurrences_in(simpleob):
    ob = Obstruction(Perm((0, 2, 1)), ((0, 0), (2, 2), (2, 1)))
    assert list(ob.occurrences_in(simpleob)) == [(0, 2, 3), (1, 2, 3)]

    ob = Obstruction(Perm((1, 0, 2)), ((0, 0), (0, 0), (2, 1)))
    assert list(ob.occurrences_in(simpleob)) == [(0, 1, 3)]

    ob = Obstruction(Perm((1, 0, 2)), ((0, 0), (0, 0), (2, 2)))
    assert list(ob.occurrences_in(simpleob)) == [(0, 1, 2)]

    ob = Obstruction(Perm((0, 1, 2)), ((0, 0), (2, 2), (2, 1)))
    assert not any(ob.occurrences_in(simpleob))

    ob = Obstruction(Perm((1, 0, 2)), ((0, 0), (2, 2), (2, 2)))
    assert not ob.occurs_in(simpleob)


def test_remove_cells(simpleob):
    assert (simpleob.remove_cells([(0, 0)]) ==
            Obstruction(Perm((1, 0)), ((2, 2), (2, 1))))
    assert (simpleob.remove_cells([(0, 0), (2, 2)]) ==
            Obstruction(Perm((0,)), ((2, 1),)))
    assert simpleob.remove_cells([(0, 1), (1, 2)]) == simpleob


def test_points_in_cell(simpleob):
    assert list(simpleob.points_in_cell((0, 0))) == [0, 1]
    assert list(simpleob.points_in_cell((0, 1))) == []


def test_isolated_cells(simpleob, isolatedob):
    assert list(simpleob.isolated_cells()) == []
    assert list(isolatedob.isolated_cells()) == [(0, 0), (1, 1), (2, 2)]


def test_forced_point_index(singlecellob):
    assert singlecellob.forced_point_index((1, 1), DIR_SOUTH) is None
    assert singlecellob.forced_point_index((2, 2), DIR_WEST) == 0
    assert singlecellob.forced_point_index((2, 2), DIR_SOUTH) == 1
    assert singlecellob.forced_point_index((2, 2), DIR_NORTH) == 2
    assert singlecellob.forced_point_index((2, 2), DIR_EAST) == 3


def test_get_rowcol(everycellob):
    assert list(everycellob.get_points_row(1)) == [(1, 3), (4, 4), (7, 5)]
    assert list(everycellob.get_points_col(1)) == [(3, 1), (4, 4), (5, 7)]
    assert list(everycellob.get_points_above_row(2)) == []
    assert list(everycellob.get_points_below_row(2)) == [(0, 0), (1, 3),
                                                         (3, 1), (4, 4),
                                                         (6, 2), (7, 5)]
    assert (list(everycellob.get_points_right_col(1)) ==
            [(6, 2), (7, 5), (8, 8)])
    assert list(everycellob.get_points_left_col(1)) == [(0, 0), (1, 3), (2, 6)]


def test_get_bounding_box(typicalob):
    assert typicalob.get_bounding_box((1, 0)) == (2, 5, 0, 3)
    assert typicalob.get_bounding_box((2, 2)) == (5, 5, 5, 5)


def test_stretch_obstruction(typicalob):
    assert (typicalob.stretch_obstruction((2, 1)) ==
            Obstruction(Perm((1, 0, 2, 4, 3)),
                        ((0, 2), (0, 0), (3, 2), (3, 3), (3, 3))))
    assert (typicalob.stretch_obstruction((3, 2)) ==
            Obstruction(Perm((1, 0, 2, 4, 3)),
                        ((0, 0), (0, 0), (1, 2), (3, 3), (3, 3))))
    assert (typicalob.stretch_obstruction((4, 0)) ==
            Obstruction(Perm((1, 0, 2, 4, 3)),
                        ((0, 2), (0, 2), (1, 2), (1, 3), (3, 3))))


def test_place_point(typicalob):
    ob12 = Obstruction.single_cell(Perm((0, 1)), (0, 0))
    assert (list(ob12.place_point((0, 0), DIR_NORTH, skip_redundant=True)) ==
            [Obstruction(Perm((0,)), ((0, 0),)),
             Obstruction(Perm((0, 1)), ((2, 0), (2, 0)))])
    assert (list(ob12.place_point((0, 0), DIR_EAST, skip_redundant=True)) ==
            [Obstruction(Perm((0,)), ((0, 0),)),
             Obstruction(Perm((0, 1)), ((0, 2), (0, 2)))])
    assert (list(ob12.place_point((0, 0), DIR_SOUTH, skip_redundant=True)) ==
            [Obstruction(Perm((0,)), ((2, 2),)),
             Obstruction(Perm((0, 1)), ((0, 2), (0, 2)))])
    assert (list(ob12.place_point((0, 0), DIR_WEST, skip_redundant=True)) ==
            [Obstruction(Perm((0,)), ((2, 2),)),
             Obstruction(Perm((0, 1)), ((2, 0), (2, 0)))])

    assert (list(typicalob.place_point((0, 1), DIR_WEST, skip_redundant=True))
            == [Obstruction(Perm((1, 0, 2, 4, 3)),
                            ((2, 0), (2, 0), (3, 0), (3, 3), (3, 3))),
                Obstruction(Perm((1, 0, 2, 4, 3)),
                            ((2, 0), (2, 0), (3, 0), (3, 3), (3, 1))),
                Obstruction(Perm((1, 0, 2, 4, 3)),
                            ((2, 0), (2, 0), (3, 0), (3, 1), (3, 1))),
                Obstruction(Perm((1, 0, 2, 4, 3)),
                            ((0, 0), (2, 0), (3, 0), (3, 3), (3, 3))),
                Obstruction(Perm((1, 0, 2, 4, 3)),
                            ((0, 0), (2, 0), (3, 0), (3, 3), (3, 1))),
                Obstruction(Perm((1, 0, 2, 4, 3)),
                            ((0, 0), (2, 0), (3, 0), (3, 1), (3, 1))),
                Obstruction(Perm((1, 0, 2, 4, 3)),
                            ((0, 0), (0, 0), (3, 0), (3, 3), (3, 3))),
                Obstruction(Perm((1, 0, 2, 4, 3)),
                            ((0, 0), (0, 0), (3, 0), (3, 3), (3, 1))),
                Obstruction(Perm((1, 0, 2, 4, 3)),
                            ((0, 0), (0, 0), (3, 0), (3, 1), (3, 1)))])
    assert (list(Obstruction(Perm((2, 1, 0, 4, 3)),
                             ((0, 1), (0, 1), (1, 0), (2, 1), (2, 1))
                             ).place_point(
                                 (2, 1), DIR_SOUTH, skip_redundant=True)) ==
            [Obstruction(Perm((2, 1, 0, 3)),
                         ((0, 1), (0, 1), (1, 0), (2, 3))),
             Obstruction(Perm((2, 1, 0, 4, 3)),
                         ((0, 3), (0, 3), (1, 0), (4, 3), (4, 3))),
             Obstruction(Perm((2, 1, 0, 4, 3)),
                         ((0, 3), (0, 1), (1, 0), (4, 3), (4, 3))),
             Obstruction(Perm((2, 1, 0, 4, 3)),
                         ((0, 1), (0, 1), (1, 0), (4, 3), (4, 3)))])

    def minimize(obba):
        obba = sorted(obba)
        res = list()
        last = None
        for ob in obba:
            if ob == last:
                continue
            add = True
            for m in res:
                if m in ob:
                    add = False
                    break
            if add:
                res.append(ob)
        return res

    obs = minimize(Obstruction.single_cell(
        Perm((0, 1, 2)), (0, 0)).place_point((0, 0), DIR_NONE))
    assert (obs == [Obstruction(Perm((0, 1)), ((0, 0), (0, 0))),
                    Obstruction(Perm((0, 1)), ((0, 0), (2, 2))),
                    Obstruction(Perm((0, 1)), ((2, 2), (2, 2))),
                    Obstruction(Perm((0, 1, 2)), ((0, 0), (0, 2), (0, 2))),
                    Obstruction(Perm((0, 1, 2)), ((0, 0), (2, 0), (2, 0))),
                    Obstruction(Perm((0, 1, 2)), ((0, 2), (0, 2), (0, 2))),
                    Obstruction(Perm((0, 1, 2)), ((0, 2), (0, 2), (2, 2))),
                    Obstruction(Perm((0, 1, 2)), ((2, 0), (2, 0), (2, 0))),
                    Obstruction(Perm((0, 1, 2)), ((2, 0), (2, 0), (2, 2)))])


def test_is_point_obstr(typicalob, singlecellob):
    assert typicalob.is_point_obstr() is None
    assert singlecellob.is_point_obstr() is None
    assert Obstruction(Perm((0,)), ((0, 0),)).is_point_obstr() == (0, 0)
    assert Obstruction(Perm((0,)), ((3, 2),)).is_point_obstr() == (3, 2)
    assert Obstruction(Perm((0,)), ((100, 10),)).is_point_obstr() == (100, 10)


def test_is_single_cell(typicalob, simpleob, singlecellob):
    assert typicalob.is_single_cell() is None
    assert simpleob.is_single_cell() is None
    assert singlecellob.is_single_cell() == (2, 2)


def test_insert_point():
    ob = Obstruction(Perm((0, 4, 1, 2, 3, 5)),
                     [(0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (2, 2)])
    assert list(ob.insert_point((1, 1))) == [
        Obstruction(Perm((0, 5, 1, 2, 3, 4, 6)),
                    ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2))),
        Obstruction(Perm((0, 5, 1, 3, 2, 4, 6)),
                    ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2))),
        Obstruction(Perm((0, 5, 1, 4, 2, 3, 6)),
                    ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2))),
        Obstruction(Perm((0, 4, 1, 5, 2, 3, 6)),
                    ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2))),
        Obstruction(Perm((0, 5, 1, 3, 2, 4, 6)),
                    ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2))),
        Obstruction(Perm((0, 5, 1, 2, 3, 4, 6)),
                    ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2))),
        Obstruction(Perm((0, 5, 1, 2, 4, 3, 6)),
                    ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2))),
        Obstruction(Perm((0, 4, 1, 2, 5, 3, 6)),
                    ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2))),
        Obstruction(Perm((0, 5, 1, 3, 4, 2, 6)),
                    ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2))),
        Obstruction(Perm((0, 5, 1, 2, 4, 3, 6)),
                    ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2))),
        Obstruction(Perm((0, 5, 1, 2, 3, 4, 6)),
                    ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2))),
        Obstruction(Perm((0, 4, 1, 2, 3, 5, 6)),
                    ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2)))]


def test_compression(simpleob, singlecellob, everycellob, typicalob,
                     isolatedob):
    patthash = {Perm((1, 0, 3, 2)): 0,
                Perm((0, 3, 6, 1, 4, 7, 2, 5, 8)): 1,
                Perm((1, 0, 2, 4, 3)): 4,
                Perm((0, 1, 2)): 17}
    revhash = {0: Perm((1, 0, 3, 2)),
               1: Perm((0, 3, 6, 1, 4, 7, 2, 5, 8)),
               4: Perm((1, 0, 2, 4, 3)),
               17: Perm((0, 1, 2))}

    assert (Obstruction.decompress(simpleob.compress(patthash), revhash)
            == simpleob)
    assert (Obstruction.decompress(singlecellob.compress(patthash), revhash)
            == singlecellob)
    assert (Obstruction.decompress(everycellob.compress(patthash), revhash)
            == everycellob)
    assert (Obstruction.decompress(typicalob.compress(patthash), revhash)
            == typicalob)
    assert (Obstruction.decompress(isolatedob.compress(patthash), revhash)
            == isolatedob)
