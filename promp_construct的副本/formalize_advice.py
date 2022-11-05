# 预先定义的提示符,用于 orginizing advices
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

ad_lines = [l.strip() for l in open("./all.advices").readlines()]
txt_lines = [l.strip().split("\t") for l in open("./all.merge").readlines()]
SET='</SEP>'

def _sort_advice(line):
# for line in ad_lines:
    ads = line.split("\t")
    align = []
    tforce = []
    order = []
    for ad in ads:
        # filter out
        if "</AB> ." in ad or "</TE> ." in ad:
            continue
        
        # formalize
        if "</A" in ad:
            align.append(ad)
        if "</T" in ad:
            tforce.append(ad)
        if "</R" in ad:
            order.append(ad)

    

    align = "\t".join(align) 
    order = "\t".join(order)
    tforce = "\t".join(tforce)
    return (align, order, tforce)
    # ad = "%s</SEP>%s</SEP>%s" % (align, tforce, order)
    # print(ad)

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

for ad,txt in zip(ad_lines,txt_lines):
    align, order, _ = _sort_advice(ad)


# first align

# then reorder

# then target force