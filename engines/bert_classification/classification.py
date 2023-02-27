import time
import os
from contextlib import redirect_stdout
import numpy as np
import pandas as pd
from tensorflow import keras
import jieba
import keras_nlp
from transformers import BertTokenizerFast
# os.environ["CUDA_VISIBLE_DEVICES"] = "-1"


class CustomerCallback(keras.callbacks.Callback):
    def __init__(self, logpath):
        if os.path.exists(logpath): os.remove(logpath)
        self.logpath = logpath

    def on_epoch_end(self, epoch, logs=None):
        with open(self.logpath, "a") as w:
            with redirect_stdout(w):
                if (int(epoch) % 1) == 0:
                    print("Epoch: {:>3} | Loss: ".format(epoch) + f"{logs['loss']:.4e}" +
                          " | sparse_categorical_accuracy: " + f"{logs['sparse_categorical_accuracy']:.4e}" +
                          " | Valid loss: " + f"{logs['val_loss']:.4e}" +
                          " | val_sparse_categorical_accuracy: " + f"{logs['val_sparse_categorical_accuracy']:.4e}"
                          )
                w.write("\n")


class Classification:
    def __init__(self, modelpath=None, datapath=None):
        if datapath is None:
            # 以字符分割的 tokenizer
            self.word_index = {}
            with open(modelpath + "/new_word_counts.txt", "r",
                      encoding="utf-8") as r:
                for w in r.readlines():
                    l = w.split("\t")
                    try:
                        self.word_index[l[0]] = int(l[1].strip("\n"))
                    except:
                        continue

            # 三级类目id与模型预测id映射关系
            self.idx_cate = {}
            with open(modelpath + "/new_index_cate.txt", "r",
                      encoding="utf-8") as r:
                for line in r.readlines():
                    l = line.split(",")
                    self.idx_cate[int(l[0])] = int(l[1].strip("\n"))

            # 预测1级类目模型
            self.transformer_model = keras.models.load_model(modelpath)

            self.cateId2name = {17799: "品牌设计", 17900: "空间设计服务", 17853: "影音视频服务",
                                2107: "知识产权", 18097: "软件开发", 18075: "网站建设服务", 16134: "八戒国际",
                                18083: "移动端开发", 9: "工程设计", 18139: "硬件开发", 17918: "UI设计",
                                17941: "策划", 17988: "营销传播", 18200: "VR/AR/MR", 17884: "工业设计与制造",
                                17825: "动漫游戏设计", 18034: "写作和内容", 18208: "区块链", 18123: "SaaS服务",
                                5788: "法律服务", 18216: "人工智能", 5787: "工商财税", 18262: "企业咨询",
                                18157: "技术服务", 18052: "翻译服务", 3128: "人力资源", 18338: "印刷服务",
                                18235: "企业后勤服务", 4794: "科技研究开发", 18249: "企业培训", 4788: "科技咨询"}
        else:
            self.tokenizer = BertTokenizerFast.from_pretrained("../models/bert-base-chinese")  # 以字符分割的 tokenizer
            self.df = pd.read_csv(datapath, sep="\t", quoting=3).head()
            self.MAX_SENT_LENGTH = 500

    def compute(self, sentence):
        X = [self.word_index[x] if x in self.word_index else 1 for x in jieba.cut(sentence)]
        X = keras.preprocessing.sequence.pad_sequences([X], maxlen=150, padding="post", truncating="post")
        Y = self.transformer_model.predict(X)

        # 去除一级类目：遍历最大值的索引，看该索引下的类目是否在 data_d 中
        Y = self.idx_cate[list(Y[0]).index(max(Y[0]))]

        return self.cateId2name[Y]

    def train_model(self, maxlen, vocab_size, num_class, embed_dim=128, num_heads=3, ff_dim=1024):
        inputs = keras.layers.Input(shape=(maxlen,))
        embedding_layer = keras_nlp.layers.TokenAndPositionEmbedding(sequence_length=maxlen,
                                                                     vocabulary_size=vocab_size,
                                                                     embedding_dim=embed_dim,
                                                                     mask_zero=True,)
        x = embedding_layer(inputs)
        encoder = keras_nlp.layers.TransformerEncoder(num_heads=num_heads, intermediate_dim=ff_dim)
        x = encoder(x)

        # bi_lstm = keras.layers.Bidirectional(keras.layers.GRU(128, return_sequences=True))(x)  # 显卡内存不足报错
        # avg_pool = keras.layers.GlobalAveragePooling1D()(bi_lstm)
        # max_pool = keras.layers.GlobalMaxPooling1D()(bi_lstm)
        # x = keras.layers.concatenate([avg_pool, max_pool])

        x = keras.layers.GlobalAveragePooling1D()(x)
        x = keras.layers.Dropout(0.25)(x)
        x = keras.layers.Dense(ff_dim, activation="relu")(x)
        x = keras.layers.Dropout(0.25)(x)
        outputs = keras.layers.Dense(num_class, activation="softmax")(x)
        model = keras.Model(inputs=inputs, outputs=outputs)
        model.summary()
        return model

    def train(self, text, label):
        self.df["vec"] = self.df[text].apply(lambda x:self.tokenizer(str.lower(x))["input_ids"][1:-1])

        word_freq_idx = {}

        # 建模
        self.df["title_vec"] = self.df[text].apply(
            lambda x: [word_freq_idx[w] if w in word_freq_idx else 1 for w in x.split(" ")])
        data = self.df.merge(self.df[label].drop_duplicates().reset_index(drop=True).reset_index(), how="left",
                          on=label)
        X = keras.preprocessing.sequence.pad_sequences(data["title_vec"].to_list(), maxlen=self.MAX_SENT_LENGTH,
                                                       padding="post", truncating="post")
        # Y = keras.utils.to_categorical(data["index"].to_list(), num_classes=self.NUM_CLASSES - 1)
        Y = np.array(data["index"])

        callbacks = [CustomerCallback("./log")]

        MAX_NB_WORDS = pd.read_csv("./new_word_counts.txt", names=["word", "idx"], sep="\t").shape[0] + 2
        NUM_CLASSES = len(self.df[label].drop_duplicates())
        model = self.train_model(self.MAX_SENT_LENGTH, MAX_NB_WORDS, NUM_CLASSES)

        model.compile(
            optimizer='adamax',
            loss=keras.losses.SparseCategoricalCrossentropy(),
            metrics=keras.metrics.SparseCategoricalAccuracy(),
        )
        model.fit(
            X, Y, batch_size=128, epochs=50, validation_split=0.3, callbacks=callbacks
        )

        return


def temp_predict():
    t1 = time.time()
    model = Classification("../models/total_category1_score_new_0.5")
    t2 = time.time()

    print("加载时长：" + str(t2 - t1))
    sentence = "需要一个拥有虚拟现实技术的装备"
    result = model.compute(sentence)
    t3 = time.time()

    print("预测时长：" + str(t3 - t2))
    print(result)


def temp_train():
    t1 = time.time()
    model = Classification(modelpath=None, datapath="../datasets/job_detail_file.txt")
    t2 = time.time()
    print("加载时长：" + str(t2 - t1))
    model.train("title", "category3id")
    t3 = time.time()

    print("预测时长：" + str(t3 - t2))


if __name__ == '__main__':
    # temp_predict()
    temp_train()