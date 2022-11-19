from extract import phrase_extraction
import pickle
import argparse


# 对齐解析
def _parse_align(line, reverse=False):
    """
    按照源语言和目标语言或相反解析对齐文件
        Args:
            line: str;
            reverse: bool; src2tgt or tgt2src
        Return:
            align: dict;
    """
    A = line.split()
    k = 1 if reverse else 0
    v = 1 - k
    align = [(int(a.split("-")[k]), int(a.split("-")[v])) for a in A]
    return align


# 筛选词组短语,长度小于10保留
def _filter_phrase(phrases):
    filtered = []
    # 遍历词组
    for p in phrases:
        et, ft, ep, fp = p
        # 英语词组长度
        elen = et[1] - et[0]
        # 法语词组长度
        flen = ft[1] - ft[0]
        # MAXLEN为10
        if elen < MAXLEN and flen < MAXLEN:
            filtered.append(p)
    return filtered


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

MATRAT = 0.35  # max ratio of phrase length / sentence length
MAXLEN = 10  # max phrase length

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
# 首先，需要找到对齐的段
# 通过搜索和删除

all_phs = []
for text, al in zip(text_lines, align_lines):
    if not REVERSE:
        src, tgt = text.split("\t")
    else:
        tgt, src = text.split("\t")
    # 源语言和目标语言对齐解析
    align = _parse_align(al, reverse=REVERSE)
    # 抽取短语
    phrases = phrase_extraction(src, tgt, align)
    # 将每组短语添加到新列表
    all_phs.append(phrases)
    # 删除长度大于10的词组
    phrases = _filter_phrase(phrases)

# save
ph_save_path = "phrases" if not REVERSE else "phrases.r"
with open(ph_save_path, "wb") as fp:  # Pickling
    pickle.dump(all_phs, fp)

# with open("phrases.r", "rb") as fp:  # Unpickling
#     all_phs = pickle.load(fp)
# print(len(all_phs))
# print(all_phs)
