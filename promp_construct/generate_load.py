from extract import phrase_extraction
import pickle
import argparse


# 生成AB,AM类型提示
def _phrase2advice(phrases):
    advices = []
    for p in phrases:
        ad = "%s %s %s %s" % (ABEGIN, p[2], AMID, p[3])
        advices.append(ad)
    return advices


# # 生成空的对齐提示
# def _generate_null_alignment_advice(align, en, fr):
#     en = en.split()
#     fr = fr.split()
#     aligned_en = [a[0] for a in align]
#     aligned_fr = [a[1] for a in align]
#
#     def _find_null_span(sent, aligned):
#         spans = []
#         span = []
#         for i in range(len(sent)):
#             if i not in aligned:
#                 span.append((sent[i]))
#             else:
#                 if len(span) > 1:
#                     spans.append(" ".join(span))
#                 span = []
#         return spans
#
#     en_spans = _find_null_span(en, aligned_en)
#     fr_spans = _find_null_span(fr, aligned_fr)
#
#     advices = []
#     for espan in en_spans:
#         ad = "%s %s %s %s" % (ABEGIN, NULL, AMID, espan)
#         advices.append(ad)
#     for fspan in fr_spans:
#         ad = "%s %s %s %s" % (ABEGIN, NULL, AMID, fspan)
#         advices.append(ad)
#     return advices


# 生成TB TI TE类型提词器
def _generate_target_force_advice(phrases, tgt_len):
    target_phrases = [(a[1], a[3]) for a in phrases]
    advices = []
    for p in target_phrases:
        if p[0][0] == 0:
            advices.append("%s %s" % (TBEGINWITH, p[1]))
        elif p[0][1] == tgt_len:
            advices.append("%s %s" % (TENDWITH, p[1]))
        else:
            advices.append("%s %s" % (TINCULDE, p[1]))
    return advices


# 生成RB RM类型提示
def _generate_reorder_advice(phrases, min_len=2):
    legal_phs = []
    for ph in phrases:
        sspan, tspan, _, _ = ph
        # at least one phrase longer than min length
        if sspan[1] - sspan[0] >= min_len or tspan[1] - tspan[0] >= min_len:
            legal_phs.append(ph)
    num_phs = len(legal_phs)
    reorder_ads = []
    for i in range(num_phs - 1):
        for j in range(i + 1, num_phs):
            ph1sspan, ph1tspan, ph1stext, ph1ttext = legal_phs[i]
            ph2sspan, ph2tspan, ph2stext, ph2ttext = legal_phs[j]
            # 找到 reorder 类型单词的映射
            if ph1sspan[1] < ph2sspan[0] and ph2tspan[1] < ph1tspan[0]:
                ad = "%s %s %s %s" % (REORDERBEGIN, ph1stext, REORDERMID, ph2stext)
                reorder_ads.append(ad)
            if ph1sspan[0] > ph2sspan[1] and ph2tspan[0] > ph1tspan[1]:
                ad = "%s %s %s %s" % (REORDERBEGIN, ph2stext, REORDERMID, ph1stext)
                reorder_ads.append(ad)

    return reorder_ads


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
align_lines = [l.strip() for l in open(args.align_path).readlines()]
REVERSE = args.reverse

MATRAT = 0.35  # 短语长度/句子长度的最大比例
MAXLEN = 10  # 最大短语长度

# 预先定义的提示符，用于组织提词器
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
# MONOTONIC = "</MONO>"
# 首先，需要找到对齐的段
# 通过搜索和删除

# 加载词表，转为实例对象
ph_save_path = "phrases" if not REVERSE else "phrases.r"
with open(ph_save_path, "rb") as fp:  # Unpickling
    phrases = pickle.load(fp)

advices = []
for text, phs in zip(text_lines, phrases):
    ads = []
    if not REVERSE:
        src, tgt = text.split("\t")
    else:
        tgt, src = text.split("\t")

    # Align force
    # normal alignment
    ads += _phrase2advice(phs)
    # Target force
    ads += _generate_target_force_advice(phs, len(tgt.split()))
    # Reordering
    ads += _generate_reorder_advice(phs, min_len=2)
    print("\t".join(ads))
    ads = "\t".join(ads)
    advices.append(ads)
with open("test.advices", 'w') as f:
    f.write("\n".join(advices))
