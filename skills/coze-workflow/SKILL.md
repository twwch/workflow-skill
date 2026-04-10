---
name: coze-workflow
description: Generate Coze workflow YAML files packaged as ZIP for import into coze.cn cloud platform. Produces importable workflow definitions with correct node schemas, edges, and layout.
---

# Coze Workflow Generator

## Overview

This skill generates Coze workflow files that can be directly imported into **coze.cn** cloud platform via ZIP upload. Given a natural language description of a desired workflow, it produces a complete YAML file packaged as a ZIP with correct node schemas, edges, layout, and byte-level zip formatting.

The skill triggers when the user asks to:
- Create, generate, or build a Coze workflow
- Convert a process description into a Coze workflow
- Scaffold a workflow for a Coze bot or application

**Primary output**: `.zip` file for coze.cn cloud import (via UI "导入" dialog).

## Smart Interaction Logic

Before generating, assess whether the user's description is sufficient:

**Proceed directly** if the description includes:
- Clear input/output expectations
- Processing logic (what the workflow should do)
- Enough detail to select appropriate nodes

**Ask clarifying questions** (max 3 rounds) if unclear:
1. "What inputs will the workflow receive, and what outputs should it produce?"
2. "What processing steps are needed? (e.g., LLM call, loop iteration, data aggregation)"
3. "Any specific models or plugins to use?"

## Node Type Reference

### Core node types (all verified from real coze.cn export)

| YAML Type | Purpose |
|-----------|---------|
| `start` | Entry point; defines workflow input variables |
| `end` | Terminal node; collects outputs |
| `llm` | Invokes a large language model |
| `loop` | Iterates over array with inner sub-nodes |
| `plugin` | Executes a registered plugin/tool |
| `variable_merge` | Merges variables from multiple branches |
| `image_generate` | Generates images from prompts |
| `code` | Run Python (language: 3) / TypeScript (language: 5) |
| `http` | HTTP API calls (GET/POST/PUT/DELETE) |
| `condition` | Conditional branching (IF/ELIF/ELSE) |
| `intent` | LLM-based intent classification |
| `knowledge` | Knowledge base search |
| `text` | Text concat/split |
| `question` | Pause for user input |
| `batch` | Parallel array processing |
| `subflow` | Sub-workflow call |

### Additional node types (verified from real coze.cn export)

| YAML Type | Purpose | Builder Function |
|-----------|---------|-----------------|
| `code` | Run Python/TypeScript code | `code_node()` |
| `http` | HTTP API calls | `http_node()` |
| `condition` | Conditional branching (IF/ELSE) | `selector_node()` |
| `intent` | LLM-based intent classification | `intent_node()` |
| `knowledge` | Knowledge base search | `knowledge_node()` |
| `subflow` | Sub-workflow call | — |
| `batch` | Parallel array processing | — |
| `text` | Text concat/split | — |
| `question` | Pause for user input | — |
| `to_json` | JSON serialize | — |
| `from_json` | JSON deserialize | — |
| `assign_variable` | Variable assignment | — |
| `database` | SQL custom query | — |
| `insert_record` / `update_record` / `select_record` / `delete_record` | DB CRUD | — |
| `dataset_write` / `dataset_delete` | Knowledge write/delete | — |
| `image_generate` / `drawing_board` | Image generation | — |
| `video_generation` / `video_audio_extractor` / `video_frame_extractor` | Video | — |
| `conversation_create` / `conversation_update` / `conversation_delete` / `conversation_list` | Conversation mgmt | — |
| `conversation_history_list` / `conversation_clear` | Conversation history | — |
| `message_create` / `message_update` / `message_delete` / `message_list` | Message mgmt | — |
| `ltm_write` / `ltm_read` | Long-term memory | — |

**Condition edge ports**: `sourcePortID="true"` (IF), `sourcePortID="false"` (ELSE), `sourcePortID="true_1"` (ELIF)
**Intent edge ports**: `sourcePortID="branch_0"`, `sourcePortID="branch_1"`, ..., `sourcePortID="default"`

## YAML Format (coze.cn Cloud)

### Critical formatting rules (verified via byte-level experiments)

1. **4-space indentation** for all nesting levels
2. **Double quotes** for string IDs: `id: "100001"`, not `id: '100001'`
3. **YAML must NOT be generated via `yaml.dump()`** — use string template concatenation to preserve exact formatting
4. **Node IDs**: Start = `"100001"`, End = `"900001"`, others = 6-digit strings

### Top-level structure

```yaml
schema_version: 1.0.0
name: workflow_name
id: 7585079438426600001
description: "Description here"
mode: workflow
icon: plugin_icon/workflow.png
nodes:
    - id: "100001"
      type: start
      ...
    - id: "200001"
      type: llm
      ...
    - id: "900001"
      type: end
      ...
edges:
    - source_node: "100001"
      target_node: "200001"
    - source_node: "200001"
      target_node: "900001"
```

### Data references (between nodes)

```yaml
value:
    path: output_field_name
    ref_node: "source_node_id"
```

### Start node template

```yaml
    - id: "100001"
      type: start
      title: 开始
      icon: https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-Start-v2.jpg
      description: "工作流的起始节点，用于设定启动工作流需要的信息"
      position:
        x: -1810
        y: 0
      parameters:
        node_outputs:
            input_var_name:
                type: string
                required: true
                value: null
```

### LLM node template (complete — all 14 llmParam fields required)

```yaml
    - id: "200001"
      type: llm
      title: Node Title
      icon: https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-LLM-v2.jpg
      description: "调用大语言模型,使用变量和提示词生成回复"
      version: "3"
      position:
        x: 0
        y: 0
      parameters:
        fcParamVar:
            knowledgeFCParam: {}
        llmParam:
            - name: apiMode
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
                value: "{{input}}"
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
                value: "Your system prompt here"
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
                value: ""
        node_inputs:
            - name: input
              input:
                type: string
                value:
                    path: output
                    ref_node: "100001"
        node_outputs:
            output:
                type: string
                value: null
        settingOnError:
            processType: 1
            retryTimes: 0
            switch: false
            timeoutMs: 180000
```

### End node template

```yaml
    - id: "900001"
      type: end
      title: 结束
      icon: https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-End-v2.jpg
      description: "工作流的最终节点，用于返回工作流运行后的结果信息"
      position:
        x: 1810
        y: 0
      parameters:
        node_inputs:
            - name: output
              input:
                value:
                    path: output
                    ref_node: "200001"
        terminatePlan: returnVariables
```

### Loop node template (with inner sub-nodes)

```yaml
    - id: "200002"
      type: loop
      title: Loop Title
      icon: https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-Loop-v2.jpg
      description: "用于通过设定循环次数和逻辑，重复执行一系列任务"
      position:
        x: 0
        y: 0
      canvas_position:
        x: -200
        y: 200
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
                    path: output
                    ref_node: "200001"
        node_outputs:
            output:
                value:
                    type: list
                    items:
                        type: string
                        value: null
                    value:
                        path: output
                        ref_node: "last_inner_node_id"
        variableParameters: []
      nodes:
        - id: "301001"
          type: llm
          ...inner LLM node (8-space indent)...
      edges:
        - source_node: "200002"
          target_node: "301001"
          source_port: loop-function-inline-output
        - source_node: "301001"
          target_node: "200002"
          target_port: loop-function-inline-input
```

**Loop edge rules:**
- Entry edge: `source_node: "<loop_id>"`, `source_port: loop-function-inline-output` → first inner node
- Exit edge: last inner node → `target_node: "<loop_id>"`, `target_port: loop-function-inline-input`
- Top-level edge out of loop: `source_port: loop-output`

### Variable Merge node template

```yaml
    - id: "200010"
      type: variable_merge
      title: 变量聚合
      icon: https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/VariableMerge-icon.jpg
      description: "对多个分支的输出进行聚合处理"
      position:
        x: 500
        y: 0
      parameters:
        mergeGroups:
            - name: v
              variables:
                - type: string
                  value:
                    content:
                        blockID: "200003"
                        name: output
                        source: block-output
                    rawMeta:
                        type: 1
                    type: ref
        node_outputs:
            output:
                type: string
                value: null
```

### Edge format

```yaml
edges:
    - source_node: "100001"
      target_node: "200001"
    - source_node: "200001"
      target_node: "200002"
      source_port: loop-output
```

## ZIP Packaging

### Directory structure (naming contract — strictly enforced)

```
Workflow-<NAME>-draft-<DIGITS>/
├── MANIFEST.yml
└── workflow/
    └── <NAME>-draft.yaml
```

- `<NAME>` must match in directory name, filename, and YAML `name:` field
- `<NAME>` must be `^[a-zA-Z][a-zA-Z0-9_]*$`
- `<DIGITS>` can be any number (e.g., `0001`)

### MANIFEST.yml format

```yaml
type: Workflow
version: 1.0.0
main:
    id: 7585079438426600001
    name: workflow_name
    desc: Description
    icon: plugin_icon/workflow.png
    version: ""
    flowMode: 0
    commitId: ""
sub: []
```

### ZIP byte-level requirements (Go archive/zip compatibility)

- **No directory entries** — only 2 file entries (MANIFEST first, YAML second)
- **flags = 0x08** (bit 3 set, data descriptor mode)
- **time/date = 0x0000** in both local headers and central directory
- **vmade = 20** (DOS) in central directory
- **external_attr = 0x00000000** in central directory

Use `build_coze_zip.py` tool: `pack_workflow(name, workflow_id, workflow_yaml_body, desc, out_path)`

## Generation Flow (CRITICAL — must follow exactly)

**Do NOT hand-write YAML. Always generate Python code that calls `scripts/coze_yaml_builder.py`.**

1. **Parse requirement** — Identify needed nodes and data flow
2. **Write a Python script** that imports from `scripts/coze_yaml_builder.py` and calls the template functions
3. **Run the script** via Bash to produce the ZIP file
4. Intermediate files → `/tmp/coze-workflow/`, final ZIP → **current working directory**

### Python Generation Example

```python
import sys, os
sys.path.insert(0, '<skill_base_dir>/scripts')
from coze_yaml_builder import *

os.makedirs('/tmp/coze-workflow', exist_ok=True)

nodes = start_node("100001", {"input": "string"})
nodes += llm_node("200001", "分析", "你是分析专家", "{{input}}", "100001", "input", -1200, 0)
nodes += llm_node("200002", "总结", "你是总结专家", "{{input}}", "200001", "output", 0, 0)
nodes += end_node("900001", "200002", "output", x=1200)
edges = edge("100001", "200001") + edge("200001", "200002") + edge("200002", "900001")

# Final ZIP to current directory, temp files to /tmp/coze-workflow/
build_workflow("my_workflow", "7585079438426600001", "描述", nodes, edges, "./Workflow-my_workflow-draft-0001.zip")
```

### Available template functions

| Function | Purpose | Key params |
|----------|---------|-----------|
| `start_node(id, outputs_dict)` | Start node | `outputs_dict`: `{"var_name": "type"}` |
| `end_node(id, ref_id, ref_path, x)` | End node | `ref_id`: upstream node ID |
| `llm_node(id, title, sys_prompt, prompt, ref_id, ref_path, x, y)` | Top-level LLM | All 14 llmParam fields auto-included |
| `inner_llm_node(id, title, sys_prompt, prompt, ref_id, ref_path, x, y)` | LLM inside Loop | 8-space indent version |
| `loop_node(id, title, ref_id, ref_path, inner_str, edge_pairs, last_id, x, y)` | Loop container | `inner_str`: concatenated inner_llm_node outputs |
| `merge_node(id, refs, x, y)` | Variable merge | `refs`: `[(node_id, "output"), ...]` |
| `code_node(id, title, code, lang, inputs, outputs, ref_id, ref_path, x, y)` | Code (`code`) | `lang`: 3=Python, 5=TS |
| `http_node(id, title, method, url, ref_id, ref_path, x, y)` | HTTP (`http`) | `method`: GET/POST/PUT/DELETE |
| `selector_node(id, title, ref_id, ref_path, condition_value, x, y)` | Condition (`condition`) | Edges: `true`/`false` ports |
| `intent_node(id, title, intents_list, ref_id, ref_path, x, y)` | Intent (`intent`) | Edges: `branch_0`/`branch_1`/... |
| `knowledge_node(id, title, ref_id, ref_path, x, y)` | Knowledge (`knowledge`) | Returns `outputList` |
| `edge(src, tgt, source_port=None)` | Edge connection | `source_port="loop-output"` for loop exit |
| `build_workflow(name, wf_id, desc, nodes, edges, out_path)` | Assemble + ZIP | Produces importable zip |

### Loop construction pattern

```python
inner = inner_llm_node("301001", "处理", "prompt", "{{input}}", "200002", "input", 180, 0)
inner += inner_llm_node("301002", "评审", "prompt", "{{input}}", "301001", "output", 640, 0)
nodes += loop_node("200002", "循环", "200001", "output",
    inner, [("301001", "301002")], "301002", x=0, y=0)
edges += edge("200002", "200003", "loop-output")  # loop exit
```

### Parallel + merge pattern

```python
nodes += llm_node("200003", "A分析", "...", "{{input}}", "200002", "output", 400, -200)
nodes += llm_node("200004", "B分析", "...", "{{input}}", "200002", "output", 400, 0)
nodes += llm_node("200005", "C分析", "...", "{{input}}", "200002", "output", 400, 200)
nodes += merge_node("200006", [("200003","output"),("200004","output"),("200005","output")], 800, 0)
edges += edge("200002","200003") + edge("200002","200004") + edge("200002","200005")
edges += edge("200003","200006") + edge("200004","200006") + edge("200005","200006")
```

## Open-Source Coze Studio (Alternative)

For open-source Coze Studio (PR #2172+), use Canvas JSON format with numeric type IDs:

```
POST /api/workflow_api/import
{ "workflow_data": "<WorkflowExportData JSON>", "workflow_name": "name", "space_id": "id", "creator_id": "id", "import_format": "json" }
```

Canvas JSON uses `node.type = "1"/"3"/"21"` (numeric IDs), `data.inputs`/`data.outputs`, and `{source: "block-output", blockID, name}` references. See `references/nodes/*.md` for Canvas JSON schemas.
