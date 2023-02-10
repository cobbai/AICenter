import time
import os
from tensorflow import keras
import jieba
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

class Classification:
    def __init__(self, modelpath):
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

    def compute(self, sentence):
        X = [self.word_index[x] if x in self.word_index else 1 for x in jieba.cut(sentence)]
        X = keras.preprocessing.sequence.pad_sequences([X], maxlen=150, padding="post", truncating="post")
        Y = self.transformer_model.predict(X)

        # 去除一级类目：遍历最大值的索引，看该索引下的类目是否在 data_d 中
        Y = self.idx_cate[list(Y[0]).index(max(Y[0]))]

        return self.cateId2name[Y]


if __name__ == '__main__':
    t1 = time.time()
    model = Classification("../models/total_category1_score_new_0.5")
    t2 = time.time()
    print("加载时长：" + str(t2 - t1))
    sentence = "需要一个拥有虚拟现实技术的装备"
    result = model.compute(sentence)
    t3 = time.time()

    print("预测时长：" + str(t3 - t2))
    print(result)