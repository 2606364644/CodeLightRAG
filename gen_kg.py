import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
import sys
from typing import Dict
from loguru import logger
from tqdm import tqdm
from tqdm.asyncio import tqdm_asyncio

# from minirag.llm.openai import openai_complete
from lightrag.llm.openai import openai_complete, openai_embed
from chunk_rich import enrich_main
from insert_rag import insert_doc, get_rag_db
from const import ENRICH_CHUNK_ROOT, PRE_CHUNK_ROOT
from openai_api import OpenaiApiClient

logger.add('_log/gen_kg.log')


def gen_llm_func(base_url, api_key, ):
    async def reasoning_or_normal_complete(*arg, **kwargs):
        res = await openai_complete(base_url=base_url, api_key=api_key, *arg, **kwargs)
        reasoning_tag = "</think>"
        if reasoning_tag in res:  # 推理模型
            return res[res.index(reasoning_tag) + len(reasoning_tag) :]
        return res.lstrip("```json").lstrip("json").rstrip("```")
    return reasoning_or_normal_complete

async def gen_doc(client: OpenaiApiClient, fpath: str, rag):
    logger.info(f"插入代码文件 {fpath}")
    try:
        chunk_file = enrich_main(client, fpath)
        if not chunk_file:
            raise ValueError("chunk富化出错")
        await insert_doc(chunk_file, rag)
        # insert_doc(fpath)
        return fpath
    except Exception as e:
        logger.exception(e)

async def main(repo: str, config: Dict):
    fpaths = []
    rag = await get_rag_db(repo, config)
    llm_client = OpenaiApiClient(
        base_url=config.get('llm_base_url'),
        api_key=config.get('llm_api_key'),
        model_name=config.get('llm_model_name')
    )
    for root, dirs, files in os.walk(os.path.join(PRE_CHUNK_ROOT, repo)):
        for fn in files:
            fpath = os.path.join(root, fn)
            fpaths.append(fpath)

    logger.debug(f"待插入代码文件 {len(fpaths)}")

    # 带进度条的异步执行
    # tasks = [
    #     gen_doc(llm_client, fp, rag)  # 假设 gen_doc 是异步函数
    #     for fp in fpaths
    # ]
    # batch_size = 4
    # for i in range(0, len(tasks), batch_size):
    #     batch = tasks[i:i + batch_size]
        # await tqdm_asyncio.gather(*batch, desc=f"Processing batch {i}/{len(fpaths)}")

    with tqdm_asyncio(total=len(fpaths), desc="Total Progress", colour="#00ff00") as pbar_total:
        batch_size = 4
        for i in range(0, len(fpaths), batch_size):
            batch_tasks = [gen_doc(llm_client, fp, rag) for fp in fpaths[i:i+batch_size]]

            # 批次级进度条
            batch_desc = f"Batch {i//batch_size+1}/{(len(fpaths)+batch_size-1)//batch_size}"
            await tqdm_asyncio.gather(
                *batch_tasks,
                desc=batch_desc,
                bar_format="{l_bar}{bar:20}{r_bar}",
                colour="#FFA500",
                postfix={"status": "processing"}
            )
            pbar_total.update(len(batch_tasks))



    # 带进度条的异步执行
    # with ThreadPoolExecutor(4) as executor:
    #     futures = [
    #         executor.submit(gen_doc, llm_client, fp, rag)
    #         for fp in fpaths
    #     ]
    #
    #     for future in tqdm(as_completed(futures), total=len(fpaths)):
    #         logger.debug(f'插入完成 {future.result()}')
    
    logger.info('结束')

if __name__ == "__main__":
    # main('dhealthz-go')
    # repos = os.listdir(PRE_CHUNK_ROOT)
    repos = sys.argv[2:]
    config_path = sys.argv[1]
    logger.info(f"使用配置路径: {config_path}")
    logger.info(f"扫描仓库: {repos}")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    config['llm_model_func'] = gen_llm_func(config['llm_base_url'], config['llm_api_key'])
    logger.debug(f"自定义配置: {config}")
    for repo in repos:
        try:
            # main(repo, config)
            asyncio.run(main(repo, config))
        except Exception as e:
            logger.exception(e)
