import pytest

from permuta import Perm
from tilings import GriddedPerm, Tiling


@pytest.fixture
def simple_trans_row():
    return Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1)), [(0, 0), (1, 0)]),
            GriddedPerm(Perm((0, 1)), [(1, 0), (2, 0)]),
        ],
        requirements=[[GriddedPerm(Perm((0,)), [(1, 0)])]],
    )


@pytest.fixture
def simple_trans_col():
    return Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1)), [(0, 0), (0, 1)]),
            GriddedPerm(Perm((0, 1)), [(0, 1), (0, 2)]),
        ],
        requirements=[[GriddedPerm(Perm((0,)), [(0, 1)])]],
    )


@pytest.fixture
def simple_trans_row_len2():
    return Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1)), [(0, 0), (1, 0)]),
            GriddedPerm(Perm((0, 1)), [(1, 0), (2, 0)]),
            GriddedPerm(Perm((0, 1)), [(2, 0), (3, 0)]),
        ],
        requirements=[
            [GriddedPerm(Perm((0,)), [(1, 0)])],
            [GriddedPerm(Perm((0,)), [(2, 0)])],
        ],
    )


@pytest.fixture
def simple_trans_row_len3():
    return Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1)), [(0, 0), (1, 0)]),
            GriddedPerm(Perm((0, 1)), [(1, 0), (2, 0)]),
            GriddedPerm(Perm((0, 1)), [(2, 0), (3, 0)]),
            GriddedPerm(Perm((0, 1)), [(3, 0), (4, 0)]),
        ],
        requirements=[
            [GriddedPerm(Perm((0,)), [(1, 0)])],
            [GriddedPerm(Perm((0,)), [(2, 0)])],
            [GriddedPerm(Perm((0,)), [(3, 0)])],
        ],
    )
