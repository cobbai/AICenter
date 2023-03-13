from transformers import ViTImageProcessor, ViTForImageClassification
from PIL import Image


class ImgClassification:
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