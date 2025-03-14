import os
import asyncio
from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import openai_complete_if_cache, openai_embed
from lightrag.utils import EmbeddingFunc
import numpy as np
from lightrag.kg.shared_storage import initialize_pipeline_status
import chardet
import aiofiles

WORKING_DIR = "./book"

if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)


async def llm_model_func(
    prompt, system_prompt=None, history_messages=[], keyword_extraction=False, **kwargs
) -> str:
    return await openai_complete_if_cache(
        "qwen-turbo-2024-09-19",
        prompt,
        system_prompt=system_prompt,
        history_messages=history_messages,
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        **kwargs,
    )


async def embedding_func(texts: list[str]) -> np.ndarray:
    """
    指定嵌入模型
    """
    
    return await openai_embed(
        texts,
        # model="solar-embedding-1-large-query",
        model="text-embedding-v1",
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )


async def get_embedding_dim():
    test_text = ["This is a test sentence."]
    embedding = await embedding_func(test_text)
    embedding_dim = embedding.shape[1]
    return embedding_dim


# function test
async def test_funcs():
    result = await llm_model_func("How are you?")
    print("llm_model_func: ", result)

    result = await embedding_func(["How are you?"])
    print("embedding_func: ", result)


# asyncio.run(test_funcs())


async def initialize_rag():
    embedding_dimension = await get_embedding_dim()
    print(f"Detected embedding dimension: {embedding_dimension}")

    rag = LightRAG(
        llm_model_func=llm_model_func,
        embedding_func=EmbeddingFunc(
            embedding_dim=embedding_dimension,
            max_token_size=8192,
            func=embedding_func,
        ),
    )

    await rag.initialize_storages()
    await initialize_pipeline_status()

    return rag


async def collect_file_paths(directory: str, file_extension: str = '.txt', max_file_size_mb: int = 10) -> list[str]:
    """异步函数，用于收集指定目录下符合条件的文件路径列表
    
    Args:
        directory (str): 要读取的目录路径
        file_extension (str, optional): 文件扩展名. 默认为 '.txt'
        max_file_size_mb (int, optional): 单个文件的最大大小(MB). 默认为 10MB
    
    Returns:
        list[str]: 符合条件的文件路径列表
    """
    file_paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(file_extension):
                file_path = os.path.join(root, file)
                # 检查文件大小
                file_size = os.path.getsize(file_path) / (1024 * 1024)  # 转换为MB
                if file_size <= max_file_size_mb:
                    file_paths.append(file_path)
                else:
                    print(f"警告: 文件 {file_path} 大小为 {file_size:.2f}MB，超过限制 {max_file_size_mb}MB，已跳过")
    return file_paths

async def read_file(file_path: str) -> str:
    """异步函数，用于读取单个文件内容，包含编码检测
    
    Args:
        file_path (str): 要读取的文件路径
    
    Returns:
        str | None: 文件内容，如果读取失败则返回None
    """

    
    # 检测文件编码
    async with aiofiles.open(file_path, 'rb') as f:
        raw_data = await f.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding'] or 'utf-8'
        
    try:
        async with aiofiles.open(file_path, 'r', encoding=encoding) as f:
            return await f.read()
    except Exception as e:
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # 转换为MB
        print(f"读取文件 {file_path} 时出错: {str(e)}\n编码: {encoding}\n文件大小: {file_size:.2f}MB")
        return None

async def read_files_content(file_paths: list[str]) -> str:
    """
    异步生成器函数，用于读取指定文件列表中的文件内容
    
    Args:
        file_paths (list[str]): 要读取的文件路径列表
    
    Yields:
        str: 文件内容
    """
    # 并发读取文件
    tasks = [read_file(file_path) for file_path in file_paths]
    results = await asyncio.gather(*tasks)
    
    # 过滤掉None结果并返回
    for content in filter(None, results):
        yield content

async def read_files_from_directory(directory: str, file_extension: str = '.txt', max_file_size_mb: int = 10) -> str:
    """
    异步生成器函数，用于读取指定目录下的所有指定后缀的文件内容
    
    Args:
        directory (str): 要读取的目录路径
        file_extension (str, optional): 文件扩展名. 默认为 '.txt'
        max_file_size_mb (int, optional): 单个文件的最大大小(MB). 默认为 10MB
    
    Yields:
        str: 文件内容
    """
    # 收集符合条件的文件路径
    file_paths = await collect_file_paths(directory, file_extension, max_file_size_mb)
    
    # 读取文件内容
    async for content in read_files_content(file_paths):
        yield content


async def main():
    
    
    try:
        # Initialize RAG instance
        rag = await initialize_rag()
        
        # 使用生成器读取文件并插入
        # async for content in read_files_from_directory(WORKING_DIR, '.txt'):
        #     content = content.replace("\n", "")
        #     # insert_custom_chunks 自行分块，但也会自动创建实体
        #     # 想要手动创建实体，使用 create_entity
            # await rag.insert_custom_chunks(full_text=content, text_chunks=[content], doc_id=1)
        
        # create_entity 手动创建实体
        # 不需要前面的insert_custom_chunks了，不需要插入chunk信息
        entity = await rag.acreate_entity(entity_name="糖果森林", entity_data={
            "entity_type": "world",
            "description": "糖果森林是一个虚构的世界，由一群热爱糖果的人组成。",
        })
        # acreate_relation 手动创建关系
        relation = await rag.acreate_relation(source_entity=None, target_entity=None, relation_data={})
        
        # Perform naive search
        print("naive:")
        print(
            await rag.aquery(
                "糖果森林是什么？", param=QueryParam(mode="naive")
            )
        )

        # Perform local search
        print("local:")
        print(
            await rag.aquery(
                "糖果森林是什么？", param=QueryParam(mode="local")
            )
        )

        # Perform global search
        print("global:")
        print(
            await rag.aquery(
                "糖果森林是什么？",
                param=QueryParam(mode="global"),
            )
        )

        # Perform hybrid search
        print("hybrid:")
        print(
            await rag.aquery(
                "糖果森林是什么？",
                param=QueryParam(mode="hybrid"),
            )
        )
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())
