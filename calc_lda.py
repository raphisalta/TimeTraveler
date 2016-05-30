from gensim import corpora, models, similarities
import logging
import mysql
import MeCab as mc
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
conn = mysql.MySQL('library') #使用するデータベース名
tagger = mc.Tagger()

def calc_lda(text):
    dictionary = corpora.Dictionary.load('deerwester.dict')
    corpus = corpora.MmCorpus('deerwester.mm')
    lda = models.LdaModel(corpus,id2word=dictionary, num_topics = 200)
    new_doc = txt_to_word(text)
    new_vec = dictionary.doc2bow(new_doc)
    print(lda[new_vec])

def make_dic():
    from collections import defaultdict
    frequency = defaultdict(int)
    import_corpora = open('db_corpora.txt','r')
    texts = []

    for doc in import_corpora.readlines(): # 文書ごとに単語をまとめる
        texts.append(doc.split())
    import_corpora.close()
    
    for text in texts: # 出現頻度をカウント
        for token in text:
            frequency[token] += 1

    texts = [[token for token in text if frequency[token] > 1] for text in texts]
    dictionary = corpora.Dictionary(texts)
    dictionary.save('deerwester.dict')
    corpus = [dictionary.doc2bow(text) for text in texts]
    corpora.MmCorpus.serialize('deerwester.mm', corpus)
    #print(dictionary.token2id)

# 単語のリストを学習し、入力単語と近い単語を上位10件まで表示
def print_word2vec(txt):
    from gensim.models import word2vec
    sentences = word2vec.Text8Corpus('db_corpora.txt')
    model = word2vec.Word2Vec(sentences, size=200)
    for w, d in model.most_similar(txt):
        print("%s\t%.4f"  % (w, d)) # wが単語、dが類似度

def txt_to_word(txt):
    wordList = [] 
    nounList = [] 
    cut = []
    wordList.append(tagger.parse(txt[0].strip()))
    cut.append(wordList[0].split()) # 名詞とその説明で分割する
    for i in range(len(cut[0])):
        if i%2==0 : continue # 単語の部分は飛ばし、品詞によって判断する
        part = cut[0][i].split(',')
        if (len(part) < 2) : continue # 空のリストの場合
        moji = part[0]
        kazu = cut[0][i].split(',')[1]
        if moji == '名詞' :
            if not(kazu == '数'):
                nounList.append(cut[0][i-1])      
    return nounList

def db_to_file():
    f = open('db_corpora.txt','w')
    texts = conn.select("Ja_News", "text","")
    for txt in texts:
        nounList = txt_to_word(txt)
        for i in range(len(nounList)):
            f.write(nounList[i] + " ")
        f.write('\n') #文書の終わりを示す改行コード
    f.close() 

if __name__ == '__main__':
    db_to_file()
    make_dic()
    #calc_lda('国連安保理の常任理事国ではない日本にとって、この首脳会議は、日本が世界政治に継続的に発言力を持つための最も重要な場である')
    #print_word2vec('会議') # word2vecのテスト
