# NER
### 标签说明
    B，即Begin，表示开始
    
    I，即Intermediate，表示中间
    
    E，即End，表示结尾
    
    S，即Single，表示单个字符
    
    O，即Other，表示其他，用于标记无关字符
---
### id2label
    {
    "0": "O",
    "1": "B-CARDINAL",
    "2": "B-DATE",
    "3": "B-EVENT",
    "4": "B-FAC",
    "5": "B-GPE",
    "6": "B-LANGUAGE",
    "7": "B-LAW",
    "8": "B-LOC",
    "9": "B-MONEY",
    "10": "B-NORP",
    "11": "B-ORDINAL",
    "12": "B-ORG",
    "13": "B-PERCENT",
    "14": "B-PERSON",
    "15": "B-PRODUCT",
    "16": "B-QUANTITY",
    "17": "B-TIME",
    "18": "B-WORK_OF_ART",
    "19": "I-CARDINAL",
    "20": "I-DATE",
    "21": "I-EVENT",
    "22": "I-FAC",
    "23": "I-GPE",
    "24": "I-LANGUAGE",
    "25": "I-LAW",
    "26": "I-LOC",
    "27": "I-MONEY",
    "28": "I-NORP",
    "29": "I-ORDINAL",
    "30": "I-ORG",
    "31": "I-PERCENT",
    "32": "I-PERSON",
    "33": "I-PRODUCT",
    "34": "I-QUANTITY",
    "35": "I-TIME",
    "36": "I-WORK_OF_ART",
    "37": "E-CARDINAL",
    "38": "E-DATE",
    "39": "E-EVENT",
    "40": "E-FAC",
    "41": "E-GPE",
    "42": "E-LANGUAGE",
    "43": "E-LAW",
    "44": "E-LOC",
    "45": "E-MONEY",
    "46": "E-NORP",
    "47": "E-ORDINAL",
    "48": "E-ORG",
    "49": "E-PERCENT",
    "50": "E-PERSON",
    "51": "E-PRODUCT",
    "52": "E-QUANTITY",
    "53": "E-TIME",
    "54": "E-WORK_OF_ART",
    "55": "S-CARDINAL",
    "56": "S-DATE",
    "57": "S-EVENT",
    "58": "S-FAC",
    "59": "S-GPE",
    "60": "S-LANGUAGE",
    "61": "S-LAW",
    "62": "S-LOC",
    "63": "S-MONEY",
    "64": "S-NORP",
    "65": "S-ORDINAL",
    "66": "S-ORG",
    "67": "S-PERCENT",
    "68": "S-PERSON",
    "69": "S-PRODUCT",
    "70": "S-QUANTITY",
    "71": "S-TIME",
    "72": "S-WORK_OF_ART"
  }

---
### 模型结构
    Encoder
        WordEmbedding(21128, 768)
        PositionEmbedding(512, 768)
        token_type_embeddings(2, 768)
        QKV(768, 768)
        fc1(768, 3072)
        fc2(3072, 768)
    Linear(768, 73)

# POS
### 标签说明
    

---
### id2label
    {
    "0": "A",
    "1": "Caa",
    "2": "Cab",
    "3": "Cba",
    "4": "Cbb",
    "5": "D",
    "6": "Da",
    "7": "Dfa",
    "8": "Dfb",
    "9": "Di",
    "10": "Dk",
    "11": "DM",
    "12": "I",
    "13": "Na",
    "14": "Nb",
    "15": "Nc",
    "16": "Ncd",
    "17": "Nd",
    "18": "Nep",
    "19": "Neqa",
    "20": "Neqb",
    "21": "Nes",
    "22": "Neu",
    "23": "Nf",
    "24": "Ng",
    "25": "Nh",
    "26": "Nv",
    "27": "P",
    "28": "T",
    "29": "VA",
    "30": "VAC",
    "31": "VB",
    "32": "VC",
    "33": "VCL",
    "34": "VD",
    "35": "VF",
    "36": "VE",
    "37": "VG",
    "38": "VH",
    "39": "VHC",
    "40": "VI",
    "41": "VJ",
    "42": "VK",
    "43": "VL",
    "44": "V_2",
    "45": "DE",
    "46": "SHI",
    "47": "FW",
    "48": "COLONCATEGORY",
    "49": "COMMACATEGORY",
    "50": "DASHCATEGORY",
    "51": "DOTCATEGORY",
    "52": "ETCCATEGORY",
    "53": "EXCLAMATIONCATEGORY",
    "54": "PARENTHESISCATEGORY",
    "55": "PAUSECATEGORY",
    "56": "PERIODCATEGORY",
    "57": "QUESTIONCATEGORY",
    "58": "SEMICOLONCATEGORY",
    "59": "SPCHANGECATEGORY"
  }