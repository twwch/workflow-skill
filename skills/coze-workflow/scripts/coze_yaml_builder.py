#!/usr/bin/env python3
"""
coze.cn workflow YAML + ZIP 生成器。
提供已验证可导入的节点模板函数，字符串拼接保证格式正确。

用法:
    from coze_yaml_builder import *

    nodes = start_node("100001", {"input": "string"})
    nodes += llm_node("200001", "大模型", "你是助手", "{{input}}", "100001", "input", 0, 0)
    nodes += end_node("900001", "200001", "output")
    edges = edge("100001", "200001") + edge("200001", "900001")

    build_workflow("my_wf", "7585079438426600001", "描述", nodes, edges, "/tmp/out.zip")
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_coze_zip import pack_workflow

ICON_START = 'https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-Start-v2.jpg'
ICON_END = 'https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-End-v2.jpg'
ICON_LLM = 'https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-LLM-v2.jpg'
ICON_LOOP = 'https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-Loop-v2.jpg'
ICON_MERGE = 'https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/VariableMerge-icon.jpg'

# ======== 完整 llmParam 模板（14字段，已验证） ========
_LLM_PARAMS_4 = '''            - name: apiMode
              input:
                type: integer
                value: "0"
            - name: maxTokens
              input:
                type: integer
                value: "4096"
            - name: spCurrentTime
              input:
                type: boolean
                value: false
            - name: spAntiLeak
              input:
                type: boolean
                value: false
            - name: responseFormat
              input:
                type: integer
                value: "2"
            - name: modelName
              input:
                type: string
                value: Kimi-K2-250905
            - name: modelType
              input:
                type: integer
                value: "1763350148"
            - name: generationDiversity
              input:
                type: string
                value: balance
            - name: parameters
              input:
                type: object
                value: null
            - name: prompt
              input:
                type: string
                value: "PROMPT_PH"
            - name: enableChatHistory
              input:
                type: boolean
                value: false
            - name: chatHistoryRound
              input:
                type: integer
                value: "3"
            - name: systemPrompt
              input:
                type: string
                value: "SYSPROMPT_PH"
            - name: stableSystemPrompt
              input:
                type: string
                value: ""
            - name: canContinue
              input:
                type: boolean
                value: false
            - name: loopPromptVersion
              input:
                type: string
                value: ""
            - name: loopPromptName
              input:
                type: string
                value: ""
            - name: loopPromptId
              input:
                type: string
                value: ""'''

# 8-space indent 版本（Loop 内部用）
_LLM_PARAMS_8 = _LLM_PARAMS_4.replace('            -', '                -').replace('              input:', '                  input:').replace('                type:', '                    type:').replace('                value:', '                    value:')

def _esc(s):
    return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')


def start_node(nid, outputs):
    """
    outputs: dict of {var_name: type_string}
    例: {"input": "string", "budget": "float"}
    """
    out_yaml = ''
    for name, typ in outputs.items():
        out_yaml += f'''            {name}:
                type: {typ}
                required: true
                value: null
'''
    return f'''    - id: "{nid}"
      type: start
      title: 开始
      icon: {ICON_START}
      description: "工作流的起始节点，用于设定启动工作流需要的信息"
      position:
        x: -2400
        y: 0
      parameters:
        node_outputs:
{out_yaml}'''


def end_node(nid, ref_id, ref_path="output", x=2400):
    return f'''    - id: "{nid}"
      type: end
      title: 结束
      icon: {ICON_END}
      description: "工作流的最终节点，用于返回工作流运行后的结果信息"
      position:
        x: {x}
        y: 0
      parameters:
        node_inputs:
            - name: output
              input:
                value:
                    path: {ref_path}
                    ref_node: "{ref_id}"
        terminatePlan: returnVariables
'''


def llm_node(nid, title, sys_prompt, prompt, ref_id, ref_path, x=0, y=0):
    """顶层 LLM 节点（4-space indent）"""
    params = _LLM_PARAMS_4.replace('SYSPROMPT_PH', _esc(sys_prompt)).replace('PROMPT_PH', _esc(prompt))
    return f'''    - id: "{nid}"
      type: llm
      title: {title}
      icon: {ICON_LLM}
      description: "调用大语言模型,使用变量和提示词生成回复"
      version: "3"
      position:
        x: {x}
        y: {y}
      parameters:
        fcParamVar:
            knowledgeFCParam: {{}}
        llmParam:
{params}
        node_inputs:
            - name: input
              input:
                type: string
                value:
                    path: {ref_path}
                    ref_node: "{ref_id}"
        node_outputs:
            output:
                type: string
                value: null
        settingOnError:
            processType: 1
            retryTimes: 0
            switch: false
            timeoutMs: 180000
'''


def inner_llm_node(nid, title, sys_prompt, prompt, ref_id, ref_path, x=180, y=0):
    """Loop 内部 LLM 节点（8-space indent）"""
    params = _LLM_PARAMS_8.replace('SYSPROMPT_PH', _esc(sys_prompt)).replace('PROMPT_PH', _esc(prompt))
    return f'''        - id: "{nid}"
          type: llm
          title: {title}
          icon: {ICON_LLM}
          description: "调用大语言模型"
          version: "3"
          position:
            x: {x}
            y: {y}
          parameters:
            fcParamVar:
                knowledgeFCParam: {{}}
            llmParam:
{params}
            node_inputs:
                - name: input
                  input:
                    type: string
                    value:
                        path: {ref_path}
                        ref_node: "{ref_id}"
            node_outputs:
                output:
                    type: string
                    value: null
            settingOnError:
                processType: 1
                retryTimes: 0
                timeoutMs: 180000
'''


def merge_node(nid, refs, x=0, y=0):
    """
    refs: list of (ref_id, ref_path) tuples
    """
    groups = ''
    for ref_id, ref_path in refs:
        groups += f'''                - name: v
                  variables:
                    - type: string
                      value:
                        content:
                            blockID: "{ref_id}"
                            name: {ref_path}
                            source: block-output
                        rawMeta:
                            type: 1
                        type: ref
'''
    return f'''    - id: "{nid}"
      type: variable_merge
      title: 变量聚合
      icon: {ICON_MERGE}
      description: "对多个分支的输出进行聚合处理"
      position:
        x: {x}
        y: {y}
      parameters:
        mergeGroups:
{groups}        node_outputs:
            output:
                type: string
                value: null
'''


def loop_node(nid, title, ref_id, ref_path, inner_nodes_str, inner_edge_pairs, last_inner_id, x=0, y=0):
    """
    inner_edge_pairs: list of (src_id, tgt_id) tuples for inner connections
    """
    inner_edges = f'        - source_node: "{nid}"\n          target_node: "{inner_edge_pairs[0][0]}"\n          source_port: loop-function-inline-output\n'
    for src, tgt in inner_edge_pairs:
        inner_edges += f'        - source_node: "{src}"\n          target_node: "{tgt}"\n'
    inner_edges += f'        - source_node: "{last_inner_id}"\n          target_node: "{nid}"\n          target_port: loop-function-inline-input\n'
    return f'''    - id: "{nid}"
      type: loop
      title: {title}
      icon: {ICON_LOOP}
      description: "用于通过设定循环次数和逻辑，重复执行一系列任务"
      position:
        x: {x}
        y: {y}
      canvas_position:
        x: {x - 200}
        y: {y + 200}
      parameters:
        loopCount:
            type: integer
            value:
                content: 10
                rawMeta:
                    type: 2
                type: literal
        loopType: array
        node_inputs:
            - name: input
              input:
                type: list
                items:
                    type: string
                    value: null
                value:
                    path: {ref_path}
                    ref_node: "{ref_id}"
        node_outputs:
            output:
                value:
                    type: list
                    items:
                        type: string
                        value: null
                    value:
                        path: output
                        ref_node: "{last_inner_id}"
        variableParameters: []
      nodes:
{inner_nodes_str}      edges:
{inner_edges}'''


def edge(src, tgt, source_port=None):
    r = f'    - source_node: "{src}"\n      target_node: "{tgt}"\n'
    if source_port:
        r += f'      source_port: {source_port}\n'
    return r


def build_workflow(name, wf_id, desc, nodes_str, edges_str, out_path):
    """组装完整 YAML 并打包为 ZIP"""
    header = f'''schema_version: 1.0.0
name: {name}
id: {wf_id}
description: "{desc}"
mode: workflow
icon: plugin_icon/workflow.png
'''
    full_yaml = header + "nodes:\n" + nodes_str + "edges:\n" + edges_str
    pack_workflow(
        name=name,
        workflow_id=str(wf_id),
        workflow_yaml_body=full_yaml,
        desc=desc,
        out_path=out_path,
    )
    import re
    nc = len(re.findall(r'    - id: "|        - id: "', full_yaml))
    ec = len(re.findall(r'source_node:', full_yaml))
    print(f"  {name}: {nc} nodes, {ec} edges -> {out_path}")
