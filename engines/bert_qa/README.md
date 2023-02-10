# QA
---
### 模型结构
    Encoder
        WordEmbedding(21128, 768)
        PositionEmbedding(512, 768)
        token_type_embeddings(2, 768)
        QKV(768, 768)
        fc1(768, 3072)
        fc2(3072, 768)
    Linear(768, 2)
