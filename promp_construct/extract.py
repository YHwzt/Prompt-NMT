# -*- coding: utf-8 -*-
# Phrase Extraction Algorithm
# Original version from NLTK: http://goo.gl/ZLKexJ
# Authors: Liling Tan

def phrase_extraction(srctext, trgtext, alignment):

    def extract(f_start, f_end, e_start, e_end, greedy=False):
        if f_end < 0:  # 0-based indexing.
            return {}
        # 检查对齐点是否一致。
        for e,f in alignment:
            if ((f_start <= f <= f_end) and
               (e < e_start or e > e_end)):
                return {}


        phrases = set()
        # 不合并其他未对齐的 f
        if not greedy:
            src_phrase = " ".join(srctext[i] for i in range(e_start,e_end+1))
            trg_phrase = " ".join(trgtext[i] for i in range(f_start,f_end+1))
            phrases.add(((e_start, e_end+1), (f_start, f_end+1), src_phrase, trg_phrase))
            return phrases

        # 添加短语对（包括额外的未对齐 f）
        # 备注：如何解释“additional unaligned f”？
        fs = f_start
        # repeat-
        while True:
            fe = f_end
            # repeat-
            while True:
                # add phrase pair ([e_start, e_end], [fs, fe]) to set E
                # Need to +1 in range  to include the end-point.
                src_phrase = " ".join(srctext[i] for i in range(e_start,e_end+1))
                trg_phrase = " ".join(trgtext[i] for i in range(fs,fe+1))
                # Include more data for later ordering.
                phrases.add(((e_start, e_end+1), (f_start, f_end+1), src_phrase, trg_phrase))
                fe += 1 # fe++
                # -until fe aligned or out-of-bounds
                if fe in f_aligned or fe == trglen:
                    break
            fs -=1  # fe--
            # -until fs aligned or out-of- bounds
            if fs in f_aligned or fs < 0:
                break
        return phrases

    # Calculate no. of tokens in source and target texts.
    srctext = srctext.split()   # e
    trgtext = trgtext.split()   # f
    srclen = len(srctext)       # len(e)
    trglen = len(trgtext)       # len(f)
    # Keeps an index of which source/target words are aligned.
    e_aligned = [i for i,_ in alignment]
    f_aligned = [j for _,j in alignment]

    bp = set() # set of phrase pairs BP
    # for e start = 1 ... length(e) do
    # Index e_start from 0 to len(e) - 1
    for e_start in range(srclen):
        # for e end = e start ... length(e) do
        # Index e_end from e_start to len(e) - 1
        for e_end in range(e_start, srclen):
            # // find the minimally matching foreign phrase
            # (f start , f end ) = ( length(f), 0 )
            # f_start ∈ [0, len(f) - 1]; f_end ∈ [0, len(f) - 1]
            f_start, f_end = trglen-1 , -1  #  0-based indexing
            # for all (e,f) ∈ A do
            for e,f in alignment:
                # if e start ≤ e ≤ e end then
                if e_start <= e <= e_end:
                    f_start = min(f, f_start)
                    f_end = max(f, f_end)
            # add extract (f start , f end , e start , e end ) to set BP
            phrases = extract(f_start, f_end, e_start, e_end)
            if phrases:
                bp.update(phrases)
    return bp


# run doctests
if __name__ == "__main__":
    import doctest
    doctest.testmod()