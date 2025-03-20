""" 实现代码块富化分块 """
import re
import os
from typing import List
import json

from loguru import logger
from openai_api import OpenaiApiClient
from const import CODE_CHUNK_EXPLAIN_PROMPT, CODE_LLM_CHUNK_PROMPT
from tqdm import tqdm
from const import PRE_CHUNK_ROOT, ENRICH_CHUNK_ROOT
from pre_chunker import CodeChunk


def enrich_block(client: OpenaiApiClient, blocks: List[str], imports: List[str], others: List[str], rel_repo_path: str) -> List[str]:
    """ 对分块使用qwen72B进行富化,  """

    import_code = '\n'.join(imports)
    other_code = '\n'.join(others)

    rich_blocks = []
    blocks.append(other_code)
    for block in blocks:
        block_code = import_code + '\n\n' + block

        # 类分块
        method_split_res = client.req_common(block_code, system_prompt=CODE_LLM_CHUNK_PROMPT)
        if not method_split_res:
            logger.error("方法分块失败")
            continue
        methods_or_func = re.findall(r'<block>([\s\S]*?)</block>', method_split_res)

        for fcode in methods_or_func:
            explain = client.req_common(fcode, system_prompt=CODE_CHUNK_EXPLAIN_PROMPT)
            if not explain:
                logger.error("代码解释失败")
                continue

#             rich_block = f'''<code-block 代码路径="{rel_repo_path}">
# <代码定义>{fcode}</代码定义>
# </code-block>'''

            rich_block = f'''<code-block 代码路径="{rel_repo_path}">
<代码定义>{fcode}</代码定义>
<代码解析>{explain}</代码解析>
</code-block>'''
            rich_blocks.append(rich_block)

    return rich_blocks


def enrich_main(client: OpenaiApiClient, fpath: str):
    with open(fpath, 'r', encoding='utf-8') as f:
        chunk_pre = json.load(f)

    rel_path = chunk_pre[-1]
    res_path = os.path.join(ENRICH_CHUNK_ROOT, rel_path)
    res_dir = os.path.dirname(res_path)
    os.makedirs(res_dir, exist_ok=True)
    chunk_file = f"{res_path}.json"

    # rich_blocks = enrich_block(client, *chunk_pre)
    chunk = CodeChunk(**chunk_pre[0])
    rich_blocks = enrich_block(client, chunk.direct_chunk, chunk.import_chunk, chunk.others, rel_path)

    with open(chunk_file, 'w', encoding='utf-8') as f:
        json.dump(rich_blocks, f, ensure_ascii=False)
    logger.debug(f'保存分块富化结果到 {chunk_file}')
    return chunk_file

    

if __name__ == "__main__":
    import sys
    
    for root, dirs, files in os.walk(os.path.join(PRE_CHUNK_ROOT, sys.argv[1])):
        for fn in files:
            fpath = os.path.join(root, fn)
            enrich_main(fpath)
    logger.info(f'富化分块数量 保存到 {ENRICH_CHUNK_ROOT}')
    
