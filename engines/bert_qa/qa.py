import time
import tensorflow as tf
from transformers import AutoModelForQuestionAnswering,AutoTokenizer,pipeline


class QA:
    def __init__(self, modelpath):
        # 以字符分割的 tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(modelpath)
        self.model = AutoModelForQuestionAnswering.from_pretrained(modelpath)
        # print(self.model)
        # print(self.model.config)
        if len(tf.config.list_physical_devices('GPU')) != 0:
            self.pipeline = pipeline('question-answering', model=self.model, tokenizer=self.tokenizer, device=0)
        else:
            self.pipeline = pipeline('question-answering', model=self.model, tokenizer=self.tokenizer)

    def compute(self, sentence, q):
        QA_input = {"question": q, "context": sentence}
        return self.pipeline(QA_input)


def temp_test1():
    t1 = time.time()
    model = QA("../models/uer/roberta-base-chinese-extractive-qa")
    t2 = time.time()
    print("加载时长：" + str(t2 - t1))
    sentence = "国台办发言人朱凤莲答记者问。(中国台湾网 尹赛楠 摄) 国台办发言人朱凤莲答记者问。(中国台湾网 尹赛楠 摄) 中国台湾网2月8日."
    q = "谁拍摄的"
    result = model.compute(sentence, q)
    t3 = time.time()

    print("预测时长：" + str(t3 - t2))
    print(result)


if __name__ == '__main__':
    temp_test1()