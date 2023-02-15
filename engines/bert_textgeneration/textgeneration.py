import time
import tensorflow as tf
from transformers import BertTokenizer, GPT2LMHeadModel, TextGenerationPipeline


class TextGenerate:
    def __init__(self, modelpath):
        self.tokenizer = BertTokenizer.from_pretrained(modelpath)
        self.model = GPT2LMHeadModel.from_pretrained(modelpath)
        # print(self.model)
        # print(self.model.config)
        if len(tf.config.list_physical_devices('GPU')) != 0:
            self.text_generator = TextGenerationPipeline(self.model, self.tokenizer, device=0)
        else:
            self.text_generator = TextGenerationPipeline(self.model, self.tokenizer)

    def compute(self, sentence, max_length=100, do_sample=True):
        return self.text_generator(sentence, max_length=max_length, do_sample=do_sample)


if __name__ == '__main__':
    t1 = time.time()
    model = TextGenerate("../models/uer/gpt2-chinese-cluecorpussmall")
    t2 = time.time()
    print("加载时长：" + str(t2 - t1))
    result = model.compute("这是很久之前的事情了")
    t3 = time.time()

    print("预测时长：" + str(t3 - t2))
    print(result)