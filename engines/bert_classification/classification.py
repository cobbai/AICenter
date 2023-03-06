import time
import os
from contextlib import redirect_stdout
import numpy as np
import pandas as pd
from tensorflow import keras
import jieba
import keras_nlp
import string
from transformers import BertTokenizerFast
from queue import Queue
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


class CustomerCallbackRedis(keras.callbacks.Callback):
    def __init__(self, q):
        self.q = q

    def on_epoch_end(self, epoch, logs=None):
        if (int(epoch) % 1) == 0:
            mes = "Epoch: {:>3} | Loss: ".format(epoch) + f"{logs['loss']:.4e}" + " | sparse_categorical_accuracy: " + f"{logs['sparse_categorical_accuracy']:.4e}" + " | Valid loss: " + f"{logs['val_loss']:.4e}" + " | val_sparse_categorical_accuracy: " + f"{logs['val_sparse_categorical_accuracy']:.4e}"
            self.q.put(mes)


class Classification:
    def __init__(self, modelpath=None, datapath=None):
        self.MAX_SENT_LENGTH = 500
        self.vocab_size = 20000
        self.tokenizer = BertTokenizerFast.from_pretrained(modelpath + "bert-base-chinese")  # 以字符分割的 tokenizer
        self.modelpath = modelpath
        if datapath is None:
            self.cat_idx = pd.read_csv(modelpath + "temp/cat_idx", index_col=False)
            self.model = keras.models.load_model(modelpath + "keras_nlp_classification")
        else:
            self.df = pd.read_csv(datapath)

    def compute(self, sentence):
        X = self.tokenizer(str.lower(sentence))["input_ids"][1:-1]
        X = keras.preprocessing.sequence.pad_sequences([X], maxlen=self.MAX_SENT_LENGTH, padding="post", truncating="post")
        Y = self.model.predict(X)
        Y_list = list(Y[0])
        ans = Y_list.index(max(Y_list))
        return self.cat_idx[self.cat_idx["index"] == ans].iloc[0, -1]

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

    def jieba_tokenizer(self, text):
        word_freq = {}
        sentences = []
        punc = string.punctuation + "，。？！；“”：、‘’、》《【】（）@#￥%……&*{}=-+——·．／"
        for line in self.df[text]:
            temp = []
            for w in jieba.cut(line):
                w = str.lower(w)
                if w in punc or len(w) == 0 or str.isnumeric(w) or w == '' or w == ' ': continue
                word_freq[w] = word_freq.get(w, 0) + 1
                temp.append(w)
            sentences.append(temp)

        if os.path.exists("./new_word_counts.txt"): os.remove("./new_word_counts.txt")
        idx = 2
        word_id = {}
        with open("./new_word_counts.txt", "w", encoding="utf-8") as w:
            for word, freq in sorted(word_freq.items(), key=lambda x:-x[1]):
                w.write(str(idx) + "\t" + word + "\t" + str(freq) + "\n")
                word_id[word] = idx
                idx += 1
        vec = []
        for line in sentences:
            v = [word_id[x] if word_id[x] <= self.vocab_size else 1 for x in line]
            vec .append(v)
        self.df["vec"] = vec
        return

    def train(self, text, label, sample, epoch, q):
        self.df = self.df.sample(frac=sample).reset_index(drop=True)
        print("训练数据量：" + str(self.df.shape))
        # Bert分词
        self.df["vec"] = self.df[text].apply(lambda x:self.tokenizer(str.lower(x))["input_ids"][1:-1])

        # jieba分词
        # self.jieba_tokenizer(text)

        # 处理label索引
        cat_idx = self.df[label].drop_duplicates().reset_index(drop=True).reset_index()
        self.df = self.df.merge(cat_idx, how="left", on=label)

        # 建模
        X = keras.preprocessing.sequence.pad_sequences(self.df["vec"].to_list(), maxlen=self.MAX_SENT_LENGTH,
                                                       padding="post", truncating="post")
        # Y = keras.utils.to_categorical(data["index"].to_list(), num_classes=self.NUM_CLASSES - 1)
        Y = np.array(self.df["index"])

        callbacks = [CustomerCallbackRedis(q)]

        NUM_CLASSES = len(self.df[label].drop_duplicates())
        model = self.train_model(self.MAX_SENT_LENGTH, self.vocab_size, NUM_CLASSES)

        model.compile(
            optimizer='adamax',
            loss=keras.losses.SparseCategoricalCrossentropy(),
            metrics=keras.metrics.SparseCategoricalAccuracy(),
        )
        model.fit(
            X, Y, batch_size=128, epochs=epoch, validation_split=0.3, callbacks=callbacks
        )
        print("训练完成")
        model.save(self.modelpath + "temp")
        cat_idx.to_csv(self.modelpath + "temp/cat_idx", index=False, encoding="utf-8-sig")
        return "训练完成"


def temp_predict():
    t1 = time.time()
    model = Classification("../models/")
    t2 = time.time()

    print("加载时长：" + str(t2 - t1))
    sentence = "计算机相关专业本科以上学历，3年以上Java开发工作经验，具备较强的开发能力，注重代码质量，有良好的软件工程知识和编码规范意识"
    result = model.compute(sentence)
    t3 = time.time()

    print("预测时长：" + str(t3 - t2))
    print(result)


def temp_train():
    t1 = time.time()
    model = Classification(modelpath="../models/", datapath="../datasets/job_detail_file.txt")
    t2 = time.time()
    print("加载时长：" + str(t2 - t1))
    q = Queue()
    model.train("title", "category3id", 0.001, 3, q)
    t3 = time.time()
    print("训练结果日志队列：")
    while not q.empty():
        print(q.get())
    print("预测时长：" + str(t3 - t2))


if __name__ == '__main__':
    # temp_predict()
    temp_train()