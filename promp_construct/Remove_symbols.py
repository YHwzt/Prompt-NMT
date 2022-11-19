

def process_laguage(conent):
    train_data = []
    for word in conent:
        word = re.sub(r'[{}]+'.format(punctuation),' ',word)
        train_data.append(word)
    return train_data