
import random
from contextlib import contextmanager

class RandomShuffler(object):
    """Use random functions while keeping track of the random state to make it
    reproducible and deterministic."""

    def __init__(self, random_state=None):
        self._random_state = random_state
        if self._random_state is None:
            self._random_state = random.getstate()

    @contextmanager
    def use_internal_state(self):
        """Use a specific RNG state."""
        old_state = random.getstate()
        random.setstate(self._random_state)
        yield
        self._random_state = random.getstate()
        random.setstate(old_state)

    @property
    def random_state(self):
        return deepcopy(self._random_state)

    @random_state.setter
    def random_state(self, s):
        self._random_state = s

    def __call__(self, data):
        """Shuffle and return a new list."""
        with self.use_internal_state():
            return random.sample(data, len(data))
            
    def sample_ratio(self, th=0.35):
        with self.use_internal_state():
            return random.uniform(0, th)

def SampleAdvice(advice, random_shuffler):

    A, T, M = advice

    A = A.split("\t")
    T = T.split("\t")
    M = M.split("\t")

    # 3 types of advices
    # flip a coin a decide whether take it
    # for A advice, sample a ratio of them
    # for T advice, sample only on of them
    # for M advice, keep it
    def _sample(l, ratio, max_len):
        if random_shuffler is not None: # sample only in train mode
            l = random_shuffler(l)
            _f = random_shuffler.sample_ratio(th=1.0)
            _r = random_shuffler.sample_ratio(th=ratio)
            l = l[:round(_r*len(l))+1] if _f > 0.5 else []
            l = l[:max_len] if len(l)>max_len else l
        return l

    A = _sample(A, ratio=0.35, max_len=5)
    T = _sample(T, ratio=0.35, max_len=2)
    M = _sample(M, ratio=0.35, max_len=3)
    advice = "</SEP>".join(A + T + M)

    return advice



random_shuffler = RandomShuffler()



sets = ["/data/user/WzT/de_en_data/valid/valid1.advices", "/data/user/WzT/de_en_data/test/test1.advices"]
for s in sets:
    with open(s) as r, open(s+".sample", 'w') as w:
        raw_ads = [l.strip() for l in r.readlines()]
        sample_ads = []
        for ad in raw_ads:
            
            ad = ad.split("</SEP>")
            print(ad)
            sp_ad = SampleAdvice(ad, random_shuffler)
            w.write(sp_ad+"\n")


