import time
import tensorflow as tf
from transformers import pipeline, BertTokenizerFast, AutoModelForTokenClassification


class NamedEntityRecognition:
    def __init__(self, tokenpath, modelpath):
        self.model_file = modelpath
        # 以字符分割的 tokenizer
        self.tokenizer = BertTokenizerFast.from_pretrained(tokenpath)
        self.model = AutoModelForTokenClassification.from_pretrained(self.model_file)
        # print(self.model)
        # print(self.model.config)
        self.id2label = self.model.config.id2label
        if len(tf.config.list_physical_devices('GPU')) != 0:
            self.pipeline = pipeline("ner", model=self.model, tokenizer=self.tokenizer, device=0)
        else:
            self.pipeline = pipeline("ner", model=self.model, tokenizer=self.tokenizer)

    def compute(self, sentence):
        result = self.pipeline(sentence)
        ans = {}
        str = ""
        for item in result:
            print(item)
            label = item["entity"].split("-")

            if label[0] == "B":
                str = item["word"]
            elif label[0] == "I":
                str += item["word"]
            elif label[0] == "E":
                str += item["word"]
                ans[str] = str + "(" + label[1] + ")"
            elif label[0] == "S":
                str = item["word"]
                ans[str] = str + "(" + label[1] + ")"
        return ans

    def compute_pos(self, sentence):
        result = self.pipeline(sentence)
        ans = {}
        str = ""
        before = ""
        for item in result:
            print(item)

            # 开头第一个字符
            if before == "":
                before = item["entity"]
                str += item["word"]
                continue

            if before == item["entity"]:
                str += item["word"]
            else:
                ans[str] = str + "(" + before + ")"
                str = item["word"]
                before = item["entity"]
        ans[str] = str + "(" + before + ")"
        return ans


def temp_test1():
    t1 = time.time()
    model = NamedEntityRecognition("../models/bert-base-chinese", "../models/ckiplab/bert-base-chinese-ner")
    t2 = time.time()
    print("加载时长：" + str(t2 - t1))
    sentence = "国台办发言人朱凤莲答记者问。(中国台湾网 尹赛楠 摄) 国台办发言人朱凤莲答记者问。(中国台湾网 尹赛楠 摄) 中国台湾网2月8日."
    result = model.compute(sentence)
    t3 = time.time()

    print("预测时长：" + str(t3 - t2))
    print(result)


def temp_test2():
    t1 = time.time()
    model = NamedEntityRecognition("../models/bert-base-chinese", "../models/ckiplab/bert-base-chinese-pos")
    t2 = time.time()
    print("加载时长：" + str(t2 - t1))
    sentence = "我叫克拉拉，我住在加州伯克利。"
    result = model.compute_pos(sentence)
    t3 = time.time()

    print("预测时长：" + str(t3 - t2))
    print(result)


if __name__ == '__main__':
    # temp_test1()
    temp_test2()
