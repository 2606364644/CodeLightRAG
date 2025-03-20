import os.path

# PRE_CHUNK_ROOT = '_pre_chunk'
# ENRICH_CHUNK_ROOT = '_rich_chunk'
PRE_CHUNK_ROOT = '_pre_chunk_test'
ENRICH_CHUNK_ROOT = '_rich_chunk_test'

# RAG_WORKING_DIR = './_index'
RAG_WORKING_DIR = './_index_go'
RAG_WORKING_BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_rag_db')
RAG_LLM_MODEL = 'qwen72b-int8'
RAG_BASE_URL = 'http://10.72.1.151:12588/v1' # qwen-72b
RAG_API_KEY = 'sk-Gsu1YdjHJkIlAm9aD3F63f22A5Bd4d04BdC797881a6428B3'

RAG_EMBEDDING_MODEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "all-MiniLM-L6-v2")

CODE_LLM_CHUNK_PROMPT = """你是一个高级开发工程师，接下来你将会收到一段代码，请你根据你的知识对代码进行分块

- 如果收到的是一个函数或者普通代码，那么只需要分析导入语句中有哪些被该函数/代码使用了，整理出 `被使用的导入语句`
- 如果收到的是一个类，那么需要提取出`类定义`、`类变量`，分割每一个方法代码作为一个块，同时对于每一个方法块，分析导入语句中有哪些被该方法使用了，整理出 `被使用的导入语句`

## 输出定义：每个块都应该使用 <block>标签包裹
对于函数输入，输出的块内容是 `被使用的导入语句` + 函数代码
<block>
`被使用的导入语句`
`函数体`
</block>
对于类输入，输出的块内容是 `被使用的导入语句` + 类定义 + 类变量 + 方法代码；且每个方法为一个块
<block>
`被使用的导入语句`
`class xxx 类定义`
`类变量`
`方法体`
</block>
<block>
`被使用的导入语句`
`class xxx 类定义`
`类变量`
`方法体`
</block>
...

## 注意
输出结果中，你需要注意代码的有效性，比如python代码的缩进，go的{}
"""

CODE_CHUNK_EXPLAIN_PROMPT = """你是一个高级开发工程师，接下来你将会收到一段函数/类方法的代码，请你根据你的专业知识对代码进行逐行、逐个标识符进行解释
要求：
1、对代码的整体功能进行解释
2、对每个使用到的函数、类方法在段代码中的作用进行讲解
3、对函数/类方法每行的功能作用进行讲解
输出：
## 整体功能
xxx
## 使用到的函数/类方法的作用
- func1: xxx
- class1: xxx
xxx
"""
