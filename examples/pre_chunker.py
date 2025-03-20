""" 实现代码分块的方法 """

import os
from typing import List, Tuple, Optional
from loguru import logger
import tree_sitter_go as tsgo
import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Query
from dataclasses import dataclass

PARSER_MAP = {
    '.go': Parser(Language(tsgo.language())),
    '.py': Parser(Language(tspython.language())),
}

pre_chunk_conf = {
    '.py': { # https://github.com/tree-sitter/tree-sitter-python/blob/78c4e9b6b2f08e1be23b541ffced47b15e2972ad/grammar.js
        "direct_chunk": [ # 单独成块
            'function_definition', 
            'class_definition', 
            'decorated_definition',
        ],
        "import_chunk": [
            'import_statement',
            'import_from_statement',
        ],
    },
    '.go': { # https://github.com/tree-sitter/tree-sitter-go/blob/master/src/grammar.json
        "direct_chunk": [ # 单独成块
            'function_declaration', 
            'method_declaration', 
            'type_declaration',
        ],
        "import_chunk": [
            'import_declaration',
        ],
    }
}

@dataclass
class CodeChunk:
    direct_chunk: List[str]
    import_chunk: List[str]
    others: List[str]
    path: str = None

# def pre_chunker(code_path: str) -> Tuple[List[str],List[str],List[str]]:
def pre_chunker(code_path: str) -> CodeChunk:
    """ Python预分块
    
    函数/类单独作为一个块，其他语句合并为一个块

    Args:
        code_path: 代码路径
    Returns:
        单独块列表, 导入块列表, 其他语句列表, 代码路径
    """
    logger.debug(f"对 {code_path} 进行预分块")
    ext = os.path.splitext(code_path)[1]
    parser = PARSER_MAP.get(ext)
    settings = pre_chunk_conf.get(ext)
    if not parser:
        logger.error(f"未注册对应的解析器: {ext}")
        # return [], [], []
        return CodeChunk([], [], "")
    with open(code_path, 'rb') as f:
        # 解析代码文件
        tree = parser.parse(f.read())
    root_node = tree.root_node

    # 存储 import 语句
    import_block = []
    # 存储最终的代码块
    blocks = []
    # 其他语句
    others = []

    for child in root_node.children:
        child_code = child.text.decode('utf-8')
        child_type =  child.type
        if child_type in settings.get('direct_chunk', []):
            blocks.append(child_code)
        elif child_type in settings.get('import_chunk', []):
            import_block.append(child_code)
        else:
            others.append(child_code)

    return CodeChunk(blocks, import_block, others)


if __name__ == "__main__":
    import sys
    import json
    from const import PRE_CHUNK_ROOT
    repo_root = sys.argv[1]
    repo_parent = os.path.dirname(repo_root)
    # repo_parent = repo_parent.split(os.sep, 2)[-1]
    src_ext = '.py' if len(sys.argv) <= 2 else sys.argv[2]

    total_chunk = 0
    for root, dirs, files in os.walk(repo_root):
        for fn in files:
            if not fn.endswith(src_ext):
                continue
            fpath = os.path.join(root, fn)
            chunk = pre_chunker(fpath)
            # total_chunk += len(chunk[0]) + 1
            total_chunk += len(chunk.direct_chunk) + 1
            rel_path = fpath[len(repo_parent):].lstrip('.\\/')
            res_path = os.path.join(PRE_CHUNK_ROOT, rel_path)
            res_dir = os.path.dirname(res_path)
            os.makedirs(res_dir, exist_ok=True)
            chunk_file = f"{res_path}.json"
            with open(chunk_file, 'w', encoding='utf-8') as f:
                # json.dump((*chunk, rel_path.split(os.sep, 1)[-1]), f, ensure_ascii=False)
                json.dump((chunk.__dict__, rel_path.split(os.sep, 1)[-1]), f, ensure_ascii=False)
            logger.debug(f'保存预分块结果到 {chunk_file}')

    logger.info(f'分块数量 {total_chunk} 保存到 {PRE_CHUNK_ROOT}')