import abc
from itertools import chain, product

from comb_spec_searcher import InferralRule
from permuta import Perm, PermSet
from tilings import Obstruction


class ObstructionInferral(abc.ABC):
    """
    Algorithm to compute the tiling created by adding all obstructions from
    `self.potential_new_obs()` that can be added to the tiling.
    """
    def __init__(self, tiling):
        self._tiling = tiling

    @abc.abstractmethod
    def potential_new_obs(self):
        """
        Return an iterable of new obstruction that should be added to the
        tiling if possible
        """
        pass

    def new_obs(self):
        """
        Returns the list of new obstruction that can be added to the tiling.
        """
        if hasattr(self, '_new_obs'):
            return self._new_obs
        newobs = []
        merged_tiling = self._tiling.merge()
        for ob in sorted(self.potential_new_obs(), key=len):
            if self.can_add_obstruction(ob, merged_tiling):
                newobs.append(ob)
                merged_tiling = merged_tiling.__class__(
                    obstructions=chain(merged_tiling.obstructions, (ob,)),
                    requirements=merged_tiling.requirements,
                    remove_empty=False)
        self._new_obs = newobs
        return self._new_obs

    @staticmethod
    def can_add_obstruction(obstruction, tiling):
        """Return true if obstruction can be added to tiling."""
        return (tiling.add_requirement(obstruction.patt, obstruction.pos)
                .merge().is_empty())

    def obstruction_inferral(self):
        """
        Return the tiling with the new obstructions.
        """
        obs = chain(self._tiling.obstructions, self.new_obs())
        reqs = self._tiling.requirements
        return self._tiling.__class__(obs, reqs)

    def formal_step(self):
        """ Return a string describing the operation performed. """
        return "Added the obstructions {}.".format(self.new_obs())

    def rule(self):
        """
        Return a comb_spec_searcher Rule for the new tiling.

        If no new obstruction is added, returns None.
        """
        if self.new_obs():
            return InferralRule(self.formal_step(),
                                self.obstruction_inferral())


class SubobstructionInferral(ObstructionInferral):
    """
    Algorithm to compute the tiling created by adding all
    subobstructions which can be added.
    """

    def potential_new_obs(self):
        """
        Return the set of all subobstructions of the tiling.
        """
        subobs = set()
        for ob in self._tiling.obstructions:
            subobs.update(ob.all_subperms())
        subobs.remove(Obstruction(Perm(), []))
        return subobs


class AllObstructionInferral(ObstructionInferral):
    """
    Algorithm to compute the tiling created by adding all
    obstruction of given length which can be added.
    """
    def __init__(self, tiling, obstrucion_length):
        super().__init__(tiling)
        self._obs_len = obstrucion_length

    @property
    def obstrucion_length(self):
        return self._obs_len

    def avoids_obstructions(self, gp):
        """
        Return True if the gridded perm `gp` does not contains any obstruction
        of the tiling.
        """
        return all(ob not in gp for ob in self._tiling.obstructions)

    def not_required(self, gp):
        """
        Returns True if the gridded perm `gp` is not required by any
        requirement list of the tiling.
        """
        return all(any(gp not in req for req in req_list)
                   for req_list in self._tiling.requirements)

    def potential_new_obs(self):
        """
        Iterator over all possible obstruction of `self.obstruction_length`.
        """
        active = self._tiling.active_cells
        n = self._obs_len
        all_gp = (Obstruction(patt, pos) for patt, pos in
                  product(PermSet(n), product(active, repeat=n)))
        pot_obs = all_gp
        pot_obs = (gp for gp in all_gp if
                   not gp.contradictory() and
                   self.avoids_obstructions(gp) and
                   self.not_required(gp))
        return pot_obs


class EmptyCellInferral(AllObstructionInferral):
    """
    Try to add a point obstruction to all the active non positive cell
    """
    def __init__(self, tiling):
        super().__init__(tiling, 1)

    def empty_cells(self):
        """
        Return an iterator over all cell that where discovered to be empty.
        """
        return (ob.pos[0] for ob in self.new_obs())

    def formal_step(self):
        """ Return a string describing the operation performed. """
        empty_cells_str = ", ".join(map(str, self.empty_cells()))
        return "The cells {} are empty.".format(empty_cells_str)
