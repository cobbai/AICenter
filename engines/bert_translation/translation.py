#encoding=utf-8
import time
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from optimum.bettertransformer import BetterTransformer
import tensorflow as tf


class TextTranslation:
    def __init__(self, modelpath):
        self.model_file = modelpath  # max_length=512

        """
        Encoder
            WordEmbedding(65001, 512)
            PositionEmbedding(512, 512)
            QKV(512, 512)
            fc1(512, 2048)
            fc2(2048, 512)
        Decoder
            WordEmbedding(65001, 512)
            PositionEmbedding(512, 512)
            QKV(512, 512)
            fc1(512, 2048)
            fc2(2048, 512)
        Linear(512, 65001)
        """
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_file)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_file)
        if len(tf.config.list_physical_devices('GPU')) != 0:
            self.translation = pipeline("translation", model=self.model, tokenizer=self.tokenizer, device=0)
        else:
            self.translation = pipeline("translation", model=self.model, tokenizer=self.tokenizer)

    def translate(self, sentence):
        return self.translation(sentence)


def temp_test1():
    t1 = time.time()
    model_zh_en = TextTranslation("../models/Helsinki-NLP/opus-mt-zh-en")
    t2 = time.time()
    print("加载时长：" + str(t2 - t1))
    sentence = "选择一些句子对A与B，其中50%的数据B是A的下一条句子，剩余50%的数据B是语料库中随机选择的，学习其中的相关性，添加这样的预训练的目的是目前很多NLP的任务比如QA和NLI都需要理解两个句子之间的关系，从而能让预训练的模型更好的适应这样的任务"
    result = model_zh_en.translate(sentence)
    t3 = time.time()
    print("预测时长：" + str(t3 - t2))
    print(result)


def temp_test2():
    t1 = time.time()
    model_en_zh = TextTranslation("../models/Helsinki-NLP/opus-mt-en-zh")
    t2 = time.time()
    print("加载时长：" + str(t2 - t1))
    sentence = "The message port closed"
    result = model_en_zh.translate(sentence)
    t3 = time.time()
    print("预测时长：" + str(t3 - t2))
    print(result)


def temp():
    import tensorflow as tf
    t = time.time()
    modelpath = "../models/Helsinki-NLP/opus-mt-zh-en"
    tokenizer = AutoTokenizer.from_pretrained(modelpath)
    model = AutoModelForSeq2SeqLM.from_pretrained(modelpath)
    print(model)  # 模型结构
    print(model.config)  # 模型参数配置

    def visualize_children(object, level=0):
        print(str(level) + "--" + type(object).__name__)
        try:
            for child in object.children(): visualize_children(child, level + 1)
        except:
            pass

    # visualize_children(model)

    print(time.time() - t)


if __name__ == '__main__':
    # temp_test1()
    temp_test2()
    # temp()
