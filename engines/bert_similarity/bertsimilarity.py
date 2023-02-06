import os
import time
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel
from optimum.bettertransformer import BetterTransformer

"""
    input: 可变参数
    output: {"key": 入参字段名, "score": 第一个文本与每个文本的余弦相似度}
"""
class BertSimilarity(object):
    def __init__(self, modelpath):
        self.model_file = modelpath  # max_length=512
        """
        Encoder
            WordEmbedding(21128, 768)
            PositionEmbedding(512, 768)
            QKV(768, 768)
            fc1(768, 3072)
            fc2(3072, 3072)
        Linear(768, 21128)
        """
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_file)
        self.model = AutoModel.from_pretrained(self.model_file)
        # self.model.to(0)
        # self.model = BetterTransformer.transform(self.model)

    def mean_pooling(self, model_output, attention_mask):
        token_embeddings = model_output[0] #First element of model_output contains all token embeddings
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

    def cosine(self, sentence_embeddings):
        text = sentence_embeddings[0]
        compare = sentence_embeddings
        compare_vec = np.array(compare)
        upND = np.dot(text, compare_vec.T)  # (None, 1000)
        downND = np.linalg.norm(text) * (np.sum(compare_vec ** 2, axis=1) ** 0.5)
        score_ND = upND / downND
        return score_ND

    def compute(self, data_dic):
        key = []
        sentence = []
        for k, v in data_dic.items():
            key.append(k)
            sentence.extend(v)
        encoded_input = self.tokenizer(sentence, padding=True, truncation=True, return_tensors='pt', max_length=512)
        with torch.no_grad():
            model_output = self.model(**encoded_input)  # 耗时
        sentence_embeddings = self.mean_pooling(model_output, encoded_input['attention_mask'])
        score = self.cosine(sentence_embeddings)
        data_dic["score"] = [round(float(x), 4) for x in score]
        return data_dic


if __name__ == '__main__':
    t1 = time.time()
    model = BertSimilarity("./text2vec_base_chinese")
    t2 = time.time()
    print("加载时长：" + str(t2 - t1))
    result = model.compute({"text":["logo设计"], "compare":["商标设计", "软件设计", "庭院设计"]})
    print(result)
    print("计算时长：" + str(time.time() - t1))