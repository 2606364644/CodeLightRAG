## Install

* Install from source (Recommend)

```bash
cd LightRAG
pip install -e .
```

* Install from PyPI

```bash
pip install lightrag-hku
```

## Quick Start

配置环境变量，使用本地分词器
```
TIKTOKEN_CACHE_DIR=D:\lightrag\INSTALL
```

索引
```
python gen_kg.py ./config/qwq32b.conf.json DATAIDENTIFY_TASK
```

检索
```
python run_rag_server.py DATAIDENTIFY_TASK -c config/qwq32b.conf.json --port 8009
```

## Config

INSTALL下的分词器
```
# o200k_base
fb374d419588a4632f3f557e76b4b70aebbca790

# cl100k_base
9b5ad71b2ce5302211f9c61530b329a4922fc6a4
```

一些模型对应的分词器，详见`.venv/Lib/site-packages/tiktoken/model.py:24`
```
# reasoning
"o1": "o200k_base",
"o3": "o200k_base",

# chat
"gpt-4o": "o200k_base",
"gpt-4": "cl100k_base",
```

实例配置
```
rag = LightRAG(
    working_dir=working_dir,
    llm_model_func=llm_model_func,
    llm_model_max_token_size=llm_max_token_size,
    llm_model_name=llm_model_name,
    # 设置分词器，默认gpt-4o
    tiktoken_model_name='gpt-4',
    embedding_func=embedding_func,
    # 指定嵌入模型并发数
    embedding_func_max_async=1,
)
```