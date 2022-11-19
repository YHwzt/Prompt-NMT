import argparse


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

parser = argparse.ArgumentParser()
parser.add_argument('--ad_lines-path', type=str,
                    help='path to train.advices file')
parser.add_argument('--txt_lines-path', type=str,
                    help='path to all.merge file, direction align de en  三个文件一行以制表符隔开')

args = parser.parse_args()
ad_lines = [l.strip() for l in open(args.ad_lines_path).readlines()]
txt_lines = [l.strip().split("\t") for l in open(args.txt_lines_path).readlines()]


def _sort_advice(line):
    # for line in ad_lines:
    ads = line.split("\t")
    align = []
    tforce = []
    order = []
    # 将三种提示开头的放到三个了空列表当中
    for ad in ads:
        # filter out
        # if "</AB> ." in ad or "</TE> ." in ad:
        if "," in ad or "." in ad or "?" in ad or "!" in ad:
            continue
        # formalize
        if "</A" in ad:
            align.append(ad)
        if "</T" in ad:
            tforce.append(ad)
        if "</R" in ad:
            order.append(ad)
    # 将三个列表中的元素分隔开
    align = "\t".join(align)
    order = "\t".join(order)
    tforce = "\t".join(tforce)
    # ad = "%s</SEP>%s</SEP>%s" % (align, order, tforce)
    # print(ad)
    return (align, tforce, order)


def _find_opt_align(align, src):
    aligns = align.split("\t")
    cands = []
    # ids = range(len(src))
    remain = src
    # init fill
    for al in aligns:
        al = al.split()
        al = " ".join(al[1:al.index("</AM>")])
        if al in remain:
            remain = remain.replace(al, "")
            cands.append(al)

    return


# set = '</SEP></SEP>'

with open('testNew2.advices', 'w') as f:
    for ad, txt in zip(ad_lines, txt_lines):
        align, tforce, order = _sort_advice(ad)
        ad = "%s</SEP>%s</SEP>%s" % (align, tforce, order)
        print(ad)
        f.write(ad + "\n")
# first align

# then target force

# then reorder