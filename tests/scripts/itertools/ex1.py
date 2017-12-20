# coding: utf-8


from pyccel.stdlib.parallel.openmp import omp_get_thread_num

#$ header class StopIteration(public, hide)
#$ header method __init__(StopIteration)
#$ header method __del__(StopIteration)
class StopIteration(object):

    def __init__(self):
        pass

    def __del__(self):
        pass

#$ header class List(public, hide)
#$ header method __init__(List, str, str)
#$ header method __del__(List)
class List(object):

    def __init__(self, a, b):
        self._a = a
        self._b = b

    def __del__(self):
        pass

#$ header class Range(public, iterable, openmp)
#$ header method __init__(Range, int, int, int, bool, int, str [:], str [:], str [:])
#$ header method __del__(Range)
#$ header method __iter__(Range)
#$ header method __next__(Range)
class Range(object):

    def __init__(self, start, stop, step, nowait=True, collapse=None,
                 private=['i'], firstprivate=['i'], lastprivate=['i']):

        self.start = start
        self.stop  = stop
        self.step  = step

        self._ordered      = None
        self._private      = private
        self._firstprivate = firstprivate
        self._lastprivate  = lastprivate
        self._linear       = None
        self._reduction    = None
        self._schedule     = None
        self._collapse     = collapse
        self._nowait       = nowait

        self.i = start

    def __del__(self):
        print('> free')

    def __iter__(self):
        self.i = 0

    def __next__(self):
        if (self.i < self.stop):
            i = self.i
            self.i = self.i + 1
        else:
            raise StopIteration()

p = Range(-2,3,1)

#$ omp parallel
for i in p:
    idx = omp_get_thread_num()
    print("> thread id : ", idx, " working on ", i)
#$ omp end parallel
