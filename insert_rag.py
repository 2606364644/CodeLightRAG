import asyncio
import json
import sys
import os
from functools import partial
from typing import Dict

import numpy as np
import torch
from loguru import logger
from sentence_transformers import SentenceTransformer

from lightrag import LightRAG
from lightrag.kg.shared_storage import initialize_pipeline_status
from lightrag.llm.hf import hf_model_complete, hf_embed
from lightrag.llm.openai import openai_complete, openai_embed
from lightrag.utils import EmbeddingFunc
# from minirag import MiniRAG
# from minirag.llm.hf import hf_embed
# from minirag.llm.openai import openai_complete
# from minirag.utils import EmbeddingFunc
from transformers import AutoModel, AutoTokenizer
from const import (
    RAG_WORKING_BASE,
    RAG_API_KEY,
    RAG_BASE_URL,
    RAG_EMBEDDING_MODEL,
    RAG_LLM_MODEL,
    ENRICH_CHUNK_ROOT
)


async def query_rag_db(name: str, config: Dict = None):
    if config is None:
        config = {}

    # 默认参数（假设 RAG_WORKING_BASE 等全局变量已定义）
    working_dir = os.path.join(config.get('working_dir', RAG_WORKING_BASE,), name)
    if not os.path.exists(working_dir):
        os.makedirs(working_dir, exist_ok=True)

    # LLM 相关配置
    llm_base_url = config.get('llm_base_url', RAG_BASE_URL)
    llm_api_key = config.get('llm_api_key', RAG_API_KEY)
    llm_model_name = config.get('llm_model_name', RAG_LLM_MODEL)
    llm_max_token_size = config.get('llm_model_max_token_size', 200)

    logger.info(f"使用模型: {llm_base_url} -> {llm_model_name} , api_key: {llm_api_key}")

    # 构建 LLM 模型函数
    if 'llm_model_func' in config:
        llm_model_func = config['llm_model_func']
    else:
        llm_model_func = partial(openai_complete, base_url=llm_base_url, api_key=llm_api_key)

    # Embedding 相关配置
    embedding_config = config.get('embedding', {})
    embedding_model_name = embedding_config.get('model_name', RAG_EMBEDDING_MODEL)
    embedding_dim = embedding_config.get('embedding_dim', 384)
    embedding_max_token = embedding_config.get('max_token_size', 1000)

    # 构建 Embedding 函数
    if 'func' in embedding_config:
        embedding_func = embedding_config['func']
    else:
        model = SentenceTransformer(
            "D:\\MyProject\\all-MiniLM-L6-v2",
            local_files_only=True,
            device="cuda" if torch.cuda.is_available() else "cpu"
        )
        async def embedding_func(texts: list[str]) -> np.ndarray:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None, partial(model.encode, texts, convert_to_numpy=True)
            )

        embedding_func = EmbeddingFunc(
            embedding_dim=embedding_dim,
            max_token_size=embedding_max_token,
            # func=_hf_embed,
            func=embedding_func,
        )

    # 创建 MiniRAG 实例
    os.environ["HF_HUB_OFFLINE"] = "1"
    rag = LightRAG(
        working_dir=working_dir,
        llm_model_func=llm_model_func,
        llm_model_max_token_size=llm_max_token_size,
        llm_model_name=llm_model_name,
        tiktoken_model_name='gpt-4',
        embedding_func=embedding_func,
    )

    await initialize_pipeline_status()

    return rag



async def get_rag_db(name: str, config: Dict = None):
    if config is None:
        config = {}

    # 默认参数（假设 RAG_WORKING_BASE 等全局变量已定义）
    working_dir = os.path.join(config.get('working_dir', RAG_WORKING_BASE,), name)
    if not os.path.exists(working_dir):
        os.makedirs(working_dir, exist_ok=True)

    # LLM 相关配置
    llm_base_url = config.get('llm_base_url', RAG_BASE_URL)
    llm_api_key = config.get('llm_api_key', RAG_API_KEY)
    llm_model_name = config.get('llm_model_name', RAG_LLM_MODEL)
    llm_max_token_size = config.get('llm_model_max_token_size', 200)

    logger.info(f"使用模型: {llm_base_url} -> {llm_model_name} , api_key: {llm_api_key}")

    # 构建 LLM 模型函数
    if 'llm_model_func' in config:
        llm_model_func = config['llm_model_func']
    else:
        llm_model_func = partial(openai_complete, base_url=llm_base_url, api_key=llm_api_key)

    # Embedding 相关配置
    embedding_config = config.get('embedding', {})
    embedding_model_name = embedding_config.get('model_name', RAG_EMBEDDING_MODEL)
    embedding_dim = embedding_config.get('embedding_dim', 384)
    embedding_max_token = embedding_config.get('max_token_size', 1000)

    # 构建 Embedding 函数
    if 'func' in embedding_config:
        embedding_func = embedding_config['func']
    else:
        # embedding_func=EmbeddingFunc(
        #     embedding_dim=384,
        #     max_token_size=5000,
        #     func=lambda texts: hf_embed(
        #         texts,
        #         tokenizer=AutoTokenizer.from_pretrained("embedding_model_name"),
        #         embed_model=AutoModel.from_pretrained("embedding_model_name")
        #     )
        # )

        model = SentenceTransformer(
            "./all-MiniLM-L6-v2",
            local_files_only=True,
            device="cuda" if torch.cuda.is_available() else "cpu"
        )
        async def embedding_func(texts: list[str]) -> np.ndarray:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None, partial(model.encode, texts, convert_to_numpy=True)
            )

        # async def embedding_func(texts: list[str]) -> np.ndarray:
        #     # model = SentenceTransformer("all-MiniLM-L6-v2")
        #     model = SentenceTransformer(
        #         "./INSTALL/fb374d419588a4632f3f557e76b4b70aebbca790",
        #         local_files_only=True
        #     )
        #     embeddings = model.encode(texts, convert_to_numpy=True)
        #     return embeddings

        def _hf_embed(texts):
            return hf_embed(
                texts,
                tokenizer=AutoTokenizer.from_pretrained(embedding_model_name),
                embed_model=AutoModel.from_pretrained(embedding_model_name),
            )

        embedding_func = EmbeddingFunc(
            embedding_dim=embedding_dim,
            max_token_size=embedding_max_token,
            # func=_hf_embed,
            func=embedding_func,
        )

    # 创建 MiniRAG 实例
    os.environ["HF_HUB_OFFLINE"] = "1"
    rag = LightRAG(
        working_dir=working_dir,
        llm_model_func=llm_model_func,
        llm_model_max_token_size=llm_max_token_size,
        llm_model_name=llm_model_name,
        tiktoken_model_name='gpt-4',
        embedding_func=embedding_func,
    )

    await rag.initialize_storages()
    await initialize_pipeline_status()

    return rag

# def insert_doc(chunk_path: str, rag: LightRAG):
#     logger.info(chunk_path)
#
#     with open(chunk_path, 'r', encoding='utf-8') as f:
#         docs = json.load(f)
#
#     for doc in docs:
#         rag.insert_custom_chunks(full_text=doc, text_chunks=[doc])
#         # rag.insert(doc, chunker=rag.single_doc_chunker)
#     logger.info(f"插入文档 {len(docs)}")

async def insert_doc(chunk_path: str, rag: LightRAG):
    logger.info(chunk_path)

    with open(chunk_path, 'r', encoding='utf-8') as f:
        docs = json.load(f)

    for doc in docs:
        # rag.insert_custom_chunks(full_text=doc, text_chunks=[doc])
        await rag.ainsert_custom_chunks(full_text=doc, text_chunks=[doc])
        # await rag.ainsert_custom_chunks(full_text=doc, text_chunks=[doc])
        # await rag.ainsert_custom_chunks(full_text=doc, text_chunks=[doc])
        # rag.insert(doc, chunker=rag.single_doc_chunker)
    logger.info(f"插入文档 {len(docs)}")

if __name__ == "__main__":
    import sys
        
    for root, dirs, files in os.walk(os.path.join(ENRICH_CHUNK_ROOT, sys.argv[1])):
        for fn in files:
            fpath = os.path.join(root, fn)
            insert_doc(fpath)
    logger.info(f'RAG 保存到 {RAG_WORKING_BASE}')