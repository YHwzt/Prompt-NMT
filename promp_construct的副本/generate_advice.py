from extract import phrase_extraction
import pickle
import argparse



# align_lines = [l.strip() for l in open("./train.align").readlines()]
# en_lines = [l.strip() for l in open("./train.en").readlines()]
# fr_lines = [l.strip() for l in open("./train.de").readlines()]

# args: text_file, align_file, reverse
parser = argparse.ArgumentParser()
parser.add_argument('--text-path', type=str, 
                    help='path to text file, merge en-fr')
parser.add_argument('--align-path', type=str, 
                    help='path to align file, direction en-fr')
parser.add_argument('--reverse', action='store_true',
                    help='return fr-en phrase table if true')

args = parser.parse_args()
text_lines = [l.strip() for l in open(args.text_path).readlines()]
# align_lines = [l.strip() for l in open(args.align_path).readlines()]
REVERSE = args.reverse


MATRAT = 0.35 # max ratio of phrase length / sentence length
MAXLEN = 10 # max phrase length


# Predefined token for orginizing advices
ABEGIN = "</AB>"
AMID = "</AM>"
NULL = "</NULL>"
# AEND = "</AE>"
TINCULDE = "</TI>"
TBEGINWITH = "</TB>"
TENDWITH = "</TE>"
# ORDER
REORDERBEGIN = "</RB>"
REORDERMID = "</RM>"
MONOTONIC = "</MONO>"
# firstly, need to find aligned segments
# by searching and removing

# parse align
def _parse_align(line, reverse=False):
    """
        Args:
            line: str;
            reverse: bool; src2tgt or tgt2src
        Return:
            align: dict;
    """
    A = line.split()
    k = 0 if not reverse else 1
    v = 1 - k
    align = [(int(a.split("-")[k]),int(a.split("-")[v])) for a in A]
    return align

# filter phrase
def _filter_phrase(phrases):
    filtered = []
    for p in phrases:
        et, ft, ep, fp = p
        elen = et[1] - et[0]
        flen = ft[1] - ft[0]
        if elen<MAXLEN and flen<MAXLEN:
            filtered.append(p)
    return filtered 

# aligned phrase to string
def _phrase2advice(phrases):
    advices = []
    for p in phrases:
        ad = "%s %s %s %s" % (ABEGIN,p[2],AMID,p[3])
        advices.append(ad)
    return advices

# find null 
def _generate_null_alignment_advice(align, en, fr):
    en = en.split()
    fr = fr.split()
    aligned_en = [a[0] for a in align]
    aligned_fr = [a[1] for a in align]

    def _find_null_span(sent, aligned):
        spans = []
        span = []
        for i in range(len(sent)):
            if i not in aligned:
                span.append((sent[i]))
            else:
                if len(span)>1:
                    spans.append(" ".join(span))
                span = []
        return spans

    en_spans = _find_null_span(en, aligned_en)
    fr_spans = _find_null_span(fr, aligned_fr)

    advices = []
    for espan in en_spans:
        ad = "%s %s %s %s" % (ABEGIN,NULL,AMID,espan)
        advices.append(ad)
    for fspan in fr_spans:
        ad = "%s %s %s %s" % (ABEGIN,NULL,AMID,fspan)
        advices.append(ad)    
    return advices
    
def _generate_target_force_advice(phrases, tgt_len):
    target_phrases = [(a[1],a[3]) for a in phrases]
    advices = []
    for p in target_phrases:
        if p[0][0] == 0:
            advices.append("%s %s" %(TBEGINWITH, p[1]))
        elif p[0][1] == tgt_len:
            advices.append("%s %s" %(TENDWITH, p[1]))
        else:
            advices.append("%s %s" %(TINCULDE, p[1]))
    return advices

def _generate_reorder_advice(phrases, min_len=2):
    legal_phs = []
    for ph in phrases:
        sspan, tspan, _, _ = ph
        if sspan[1] - sspan[0] >= min_len or tspan[1] - tspan[0] >= min_len: # at least one phrase longer than min length
            legal_phs.append(ph)
    num_phs = len(legal_phs)
    reorder_ads = []
    for i in range(num_phs-1):
        for j in range(i+1,num_phs):
            ph1sspan, ph1tspan, ph1stext, ph1ttext = legal_phs[i]
            ph2sspan, ph2tspan, ph2stext, ph2ttext = legal_phs[j]
            # find reorder phrase mapping
            if ph1sspan[1] < ph2sspan[0] and ph2tspan[1] < ph1tspan[0]:
                ad = "%s %s %s %s" % (REORDERBEGIN, ph1stext, REORDERMID, ph2stext)
                reorder_ads.append(ad)
            if ph1sspan[0] > ph2sspan[1] and ph2tspan[0] > ph1tspan[1]:
                ad = "%s %s %s %s" % (REORDERBEGIN, ph2stext, REORDERMID, ph1stext)
                reorder_ads.append(ad)

    return reorder_ads

# load
ph_save_path = "phrases" if not REVERSE else "phrases.r"
with open(ph_save_path, "rb") as fp:   #Pickling
    phrases = pickle.load(fp)


advices = []
for text,phs in zip(text_lines, phrases):
    ads = []
    if not REVERSE:
        src, tgt = text.split("\t")
    else:
        tgt, src = text.split("\t")

    # Align force
    # normal alignment
    ads += _phrase2advice(phs)
    # Target force
    ads  += _generate_target_force_advice(phs, len(tgt.split()))
    # Reordering
    ads += _generate_reorder_advice(phs, min_len=2)
    # print("\t".join(ads))
    ads = "\t".join(ads)
    advices.append(ads)
with open("all.advices", 'w') as f:
    f.write("\n".join(advices))





# all_phs = []
# for text,al in zip(text_lines, align_lines):
#     advices = []
#     if not REVERSE:
#         src, tgt = text.split("\t")
#     else:
#         tgt, src = text.split("\t")
#     align = _parse_align(al, reverse=REVERSE)
#     phrases = phrase_extraction(src, tgt, align)
#     all_phs.append(phrases)

#     phrases = _filter_phrase(phrases)

#     # Align force
#     # normal alignment
#     # advices += _phrase2advice(phrases)
#     # Target force
#     # advices  += _generate_target_force_advice(phrases, len(tgt.split()))
#     # Reordering
#     advices += _generate_reorder_advice(phrases, min_len=1)
#     print("\t".join(advices))



# # save
# ph_save_path = "phrases" if not REVERSE else "phrases.r"
# with open(ph_save_path, "wb") as fp:   #Pickling
#     pickle.dump(all_phs, fp)


# with open("train.phrases", "rb") as fp:   # Unpickling
#     all_phs = pickle.load(fp)
# # print(len(all_phs))
# # for en,fr,al in zip(en_lines, fr_lines, all_phs):
# for ph in all_phs:
#     ad = _generate_reorder_advice(ph)
#     print(ad)
#     xxx
#     if ad is not None:
#         print(ad)
#         xxx
