# TODO: Docstring
# TODO: Make python2.7 compatible once permuta is


from copy import deepcopy
from itertools import product
from permuta import Perm
from permuta import PermSet
from permuta.misc import ordered_set_partitions, flatten
from permuta.descriptors import Descriptor
from permuta._perm_set.unbounded.described import PermSetDescribed


__all__ = ("Tile", "Tiling")


class Tile(object):
    "An enum used to represent different tiles in tilings"
    #INPUT_SET = X = "Input set"
    ALL = UNIVERSE = PermSet()
    POINT = P = PermSet([Perm()])  # pylint: disable=invalid-name
    INCREASING = PermSet.avoiding(Perm((1, 0)))
    DECREASING = PermSet.avoiding(Perm((0, 1)))


class Tiling(dict):
    def __init__(self, tiles=()):
        # Inefficient AF?
        super(Tiling, self).__init__(tiles)
        self._max_i = max(i for (i, _) in self) + 1 if self else 1
        self._max_j = max(j for (_, j) in self) + 1 if self else 1
        #for key, value in iteritems(tiles):
        #    print(key, value)


    def __hash__(self):
        # TODO: Hash without using sum?
        return sum(hash((key, value)) for (key, value) in iteritems(self))

    def __repr__(self):
        return "<A tiling with {} non-empty tiles>".format(len(self))

    def __str__(self):
        n = self._max_i
        m = self._max_j
        arr = [ [ ' ' for j in range(2*m+1) ] for i in range(2*n+1) ]
        labels = {}

        for i in range(2*n+1):
            for j in range(2*m+1):
                a = i % 2 == 0
                b = j % 2 == 0
                if a and b:
                    arr[i][j] = '+'
                elif a:
                    arr[i][j] = '-'
                elif b:
                    arr[i][j] = '|'

        for i,j in self:
            #if type(self[(i,j)]) is Tile.INPUT_SET:
            #    arr[2*i+1][2*j+1] = 'X'
            #elif type(self[(i,j)]) is Tile.POINT:
            #    arr[2*i+1][2*j+1] = 'o'
            if type(self[(i,j)]) is Tile.POINT:
                arr[2*i+1][2*j+1] = 'o'
            else:
                if self[(i,j)] not in labels:
                    labels[self[(i,j)]] = str(len(labels) + 1)

                arr[2*i+1][2*j+1] = labels[self[(i,j)]]

        out = '\n'.join( ''.join(row) for row in arr )

        for k, v in sorted(labels.items(), key=lambda x: x[1]):
            out += '\n{}: {!s}'.format(v, k)

        return out


#
# Please ignore the code below, will be used later
#


POINT_PERM_SET = PermSet(Perm(0,))


class GeneratingRule(Descriptor):
    """
    When we implement generating_function, this is probably what it will
    look like (this will not handle inputs in same row/col):
    def generating_function(self):
        gf = 1
        for row in self.rule:
            for s in row:
                gf *= s.generating_function()
        gf += 1
        return gf
    """
    def __init__(self, rule):
        # Store rules in a dictionary (check if list and convert), throw out None tiles
        # TODO: store rules as a 2d array, and benchmark
        if isinstance(rule, list):
            self.rule = {(i, j): rule[i][j]
                         for i in range(len(rule))
                         for j in range(len(rule[i]))
                         if rule[i][j] is not None}
        else:
            self.rule = {(i, j): s
                         for ((i,j), s) in rule.items()
                         if s is not None}

    def __eq__(self, other):
        return isinstance(other, Tiling) and self.rule == other.rule

    def __hash__(self):
        # TODO: Hash without using sum?
        return sum(hash((k, v)) for k, v in self.rule.items())

    def __repr__(self):
        return "<A descriptor subclass object>"

    def __str__(self):
        n = max( i for i,j in self.rule )+1 if self.rule else 1
        m = max( j for i,j in self.rule )+1 if self.rule else 1
        arr = [ [ ' ' for j in range(2*m+1) ] for i in range(2*n+1) ]
        labels = {}

        for i in range(2*n+1):
            for j in range(2*m+1):
                a = i % 2 == 0
                b = j % 2 == 0
                if a and b:
                    arr[i][j] = '+'
                elif a:
                    arr[i][j] = '-'
                elif b:
                    arr[i][j] = '|'

        for i,j in self.rule:
            #if type(self.rule[(i,j)]) is InputPermutationSet:
            if type(self.rule[(i,j)]) is self:
                arr[2*i+1][2*j+1] = 'X'
            elif type(self.rule[(i,j)]) is POINT_PERM_SET:
                arr[2*i+1][2*j+1] = 'o'
            else:
                if self.rule[(i,j)] not in labels:
                    labels[self.rule[(i,j)]] = str(len(labels) + 1)

                arr[2*i+1][2*j+1] = labels[self.rule[(i,j)]]

        out = '\n'.join( ''.join(row) for row in arr )

        for k, v in sorted(labels.items(), key=lambda x: x[1]):
            out += '\n' + '%s: %s' % (v, k.description)

        return out


class GeneratingSet(PermSetDescribed):
    """A permutation set containing all permutations generated by a generating rule."""

    def __init__(self, descriptor):
        PermSetDescribed.__init__(self, descriptor)
        self.rule = descriptor.rule  # TODO: Don't be so hacky

    def __contains__(self, item):
        raise NotImplementedError

    def __getitem__(self, key):
        raise NotImplementedError

    def of_length(self, n):
    #def generate_of_length(self, n, input):

        rule = list(self.rule.items())
        h = max( k[0] for k,v in rule ) + 1 if rule else 1
        w = max( k[1] for k,v in rule ) + 1 if rule else 1

        #def permute(arr, perm):
        #    res = [None] * len(arr)
        #    for i in range(len(arr)):
        #        res[i] = arr[perm[i] - 1]
        #    return res

        def count_assignments(at, left):

            if at == len(rule):
                if left == 0:
                    yield []
            elif type(rule[at][1]) is POINT_PERM_SET:
                # this doesn't need to be handled separately,
                # it's just an optimization
                if left > 0:
                    for ass in count_assignments(at + 1, left - 1):
                        yield [1] + ass
            else:
                for cur in range(left+1):
                    for ass in count_assignments(at + 1, left - cur):
                        yield [cur] + ass

        for count_ass in count_assignments(0, n):

            cntz = [ [ 0 for j in range(w) ] for i in range(h) ]

            for i, k in enumerate(count_ass):
                cntz[rule[i][0][0]][rule[i][0][1]] = k

            rowcnt = [ sum( cntz[row][col] for col in range(w) ) for row in range(h) ]
            colcnt = [ sum( cntz[row][col] for row in range(h) ) for col in range(w) ]

            for colpart in product(*[ ordered_set_partitions(range(colcnt[col]), [ cntz[row][col] for row in range(h) ]) for col in range(w) ]):
                scolpart = [ [ sorted(colpart[i][j]) for j in range(h) ] for i in range(w) ]
                for rowpart in product(*[ ordered_set_partitions(range(rowcnt[row]), [ cntz[row][col] for col in range(w) ]) for row in range(h) ]):
                    srowpart = [ [ sorted(rowpart[i][j]) for j in range(w) ] for i in range(h) ]
                    for perm_ass in product(*[ s[1].of_length(cnt) if s[1] is not Tile.P else s[1][0] for cnt, s in zip(count_ass, rule) ]):
                    #for perm_ass in product(*[ s[1].of_length(cnt) for cnt, s in zip(count_ass, rule) ]):
                    #for perm_ass in product(*[ s[1].generate_of_length(cnt, input) for cnt, s in zip(count_ass, rule) ]):
                        arr = [ [ [] for j in range(w) ] for i in range(h) ]

                        for i, perm in enumerate(perm_ass):
                            arr[rule[i][0][0]][rule[i][0][1]] = perm

                        res = [ [None]*colcnt[col] for col in range(w) ]

                        cumul = 0
                        #cumul = 1
                        for row in range(h-1,-1,-1):
                            for col in range(w):
                                for idx, val in zip(scolpart[col][row], arr[row][col].apply(srowpart[row][col])):
                                #for idx, val in zip(scolpart[col][row], permute(srowpart[row][col], arr[row][col])):
                                    res[col][idx] = cumul + val

                            cumul += rowcnt[row]

                        yield Perm(flatten(res))
                        #yield Perm(element - 1 for element in flatten(res))


    def to_static(self, max_n, input, description=None):

        inp = deepcopy(input)

        for n in range(max_n+1):
            for perm in self.generate_of_length(n, inp):
                inp.setdefault(n, [])
                inp[n].append(perm)

        try:
            gf = self.generating_function()
        except NotImplementedError:
            gf = None

        perms = [ p for ps in inp.values() for p in ps ]
        return PermSet(perms)
        #return StaticPermutationSet(perms, gf, description if description is not None else self.description)
