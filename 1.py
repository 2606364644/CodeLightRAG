import asyncio

import numpy as np

from nano_graphrag._llm import openai_embed


async def embedding_func(texts: list[str]) -> np.ndarray:
    """
    指定嵌入模型
    """

    return await openai_embed(
        texts,
        # model="solar-embedding-1-large-query",
        model="xxx",
        api_key='111',
        base_url="http://10.72.1.16:16540/v1",
    )

async def get_embedding_dim():
    test_text = ["This is a test sentence."]
    embedding = await embedding_func(test_text)
    embedding_dim = embedding.shape[1]
    return embedding_dim


async def main():
    dim = await get_embedding_dim()
    print(f"Embedding dimension: {dim}")  # 输出整数

asyncio.run(main())