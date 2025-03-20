import argparse
import json
import asyncio
import uvicorn
from fastapi import FastAPI

from loguru import logger
# from insert_rag import query_rag_db
from insert_rag_inf_retriever_v1 import query_rag_db
from lightrag import QueryParam
from lightrag.llm.openai import openai_complete
# from minirag import MiniRAG, QueryParam
# from minirag.llm.openai import openai_complete

app = FastAPI()


@app.get("/test")
def heart_beat():
    return {}


@app.get("/rag")
async def query_rag(query: str, topk=10, rag_mode='hybrid'):
    res = await app.state.rag.aquery(query, param=QueryParam(mode=rag_mode, top_k=topk))
    # res = app.state.rag.query(query, param=QueryParam(mode=rag_mode, top_k=topk))
    # res = await rag.aquery(query, param=QueryParam(mode=rag_mode, top_k=topk))

    with open("rag_debug", "w", encoding="utf-8") as f:
        f.write(res)
    return {"res": res}


@app.get("/rag/context")
def query_context_doc(query: str, topk=10, rag_mode='hybrid'):
    res = app.state.rag.query(
        query, param=QueryParam(mode=rag_mode, top_k=topk, only_need_context=True)
    )
    with open("rag_debug_ctx", "w", encoding="utf-8") as f:
        f.write(res)
    return {"res": res}


def gen_llm_func(base_url, api_key, ):
    async def reasoning_or_normal_complete(*arg, **kwargs):
        res = await openai_complete(base_url=base_url, api_key=api_key, *arg, **kwargs)
        reasoning_tag = "</think>"
        if reasoning_tag in res:  # 推理模型
            return res[res.index(reasoning_tag) + len(reasoning_tag) :]
        return res.lstrip("```json").lstrip("json").rstrip("```")
    return reasoning_or_normal_complete


def parse_args():
    parser = argparse.ArgumentParser(description="MiniRAG 服务启动参数")
    parser.add_argument("name", help="数据库名称（用于生成工作目录）")
    parser.add_argument("--config", "-c", help="配置文件路径（JSON 格式）")
    parser.add_argument("--host", default="127.0.0.1", help="服务监听地址")
    parser.add_argument("--port", type=int, default=8008, help="服务监听端口")
    return parser.parse_args()

@app.on_event("startup")
async def init_rag():
    args = parse_args()  # 直接在初始化时解析参数
    
    config = {}
    if args.config:
        with open(args.config, "r") as f:
            config = json.load(f)
    
    config["llm_model_func"] = gen_llm_func(
        config.get('llm_base_url', ''),
        config.get('llm_api_key', '')
    )
    
    app.state.rag = await query_rag_db(args.name, config)


if __name__ == "__main__":
    # 直接获取解析后的参数
    args = parse_args()
    
    uvicorn.run(
        app,  # 直接使用app实例
        host=args.host,
        port=args.port,
        # 移除了reload参数
    )
