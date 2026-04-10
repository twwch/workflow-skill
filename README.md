# Workflow Skill

[中文](README.zh-CN.md) | [![Linux.do](https://img.shields.io/badge/Linux.do-Discussion-blue)](https://linux.do/)

**Generate importable workflow files from natural language descriptions.**

Describe your workflow in one sentence, and get a complete workflow definition file ready to import into Coze, Dify, or ComfyUI — including node configuration, edges, layout, and all platform-specific format requirements.

## Installation

```bash
git clone https://github.com/twwch/workflow-skill.git /tmp/workflow-skill
cp -r /tmp/workflow-skill/skills/coze-workflow ~/.claude/skills/
cp -r /tmp/workflow-skill/skills/dify-workflow ~/.claude/skills/
cp -r /tmp/workflow-skill/skills/comfyui-workflow ~/.claude/skills/
```

![Installation](images/安装.png)

---

## Coze Workflow

Generate `.zip` files for direct import into [coze.cn](https://www.coze.cn) via the UI import dialog.

### Usage

```
/coze-workflow 创建一个金融研报自动生成工作流：5路并行数据采集 → 分章撰写 → 风控审核 → 发布
```

### How it works

The skill generates a Python script using verified template functions, then runs it to produce a ZIP with byte-level Go `archive/zip` compatibility.

![Coze Workflow Generation](images/coze-workflow.png)

### Import Result

![Coze Import Result](images/finance_analysis-coze.png)
![Coze Import in UI](images/finance_analysis-coze-import.png)

### Complex Workflow Generation

![Complex Workflow](images/复杂流程生成-coze.png)

### Cross-Border E-Commerce Workflow (Full)

![Cross Border Ecommerce](images/cross_border_ecommerce.png)
![Full Workflow View](images/跨境电商智能选品上架工作流-whole-workflow.png)

### Supported Node Types

`start` / `end` / `llm` / `loop` / `plugin` / `variable_merge` / `image_generate` / `code` / `http` / `condition` / `intent` / `knowledge`

---

## Dify Workflow

Generate `.dify.yml` / `.dify.json` files for import into [Dify](https://dify.ai) via UI "Import DSL".

### Usage

```
/dify-workflow 创建一个客服工单自动分类和回复工作流
```

### AI Generate Workflow

![Dify Workflow Generation](images/dify-workflow.png)

### Complex Workflow Generation

![Complex Dify Workflow](images/复杂流程生成-dify.png)

### Supported Node Types

`start` / `end` / `llm` / `code` / `http-request` / `if-else` / `iteration` / `knowledge-retrieval` / `variable-aggregator` / `template-transform` / `question-classifier` / `parameter-extractor` / `tool` / `answer`

---

## ComfyUI Workflow

Generate `.json` files (Litegraph format) for drag & drop into [ComfyUI](https://github.com/comfyanonymous/ComfyUI).

### Usage

```
/comfyui-workflow 创建一个 Flux 文生图 + WAN2.1 图生视频工作流
```

### AI Generate Workflow → Import ComfyUI → Run

![Generate Workflow](skills/comfyui-workflow/images/生图转视频workflow.png)
![Workflow in ComfyUI](skills/comfyui-workflow/images/图生视频流程.png)

### Generated Output

![Generated Image](skills/comfyui-workflow/images/生成的图片.jpg)
![Run Result](skills/comfyui-workflow/images/运行结果.png)

### Multi-Workflow Merge

![Merge Workflows](skills/comfyui-workflow/images/多个workflow合并更新.png)

### Motion Transfer

![Motion Transfer Workflow](skills/comfyui-workflow/images/动作迁移workflow.png)
![Motion Transfer Process](skills/comfyui-workflow/images/动作迁移流程.png)

### Features

- **34 built-in templates** — covers all mainstream models and tasks
- **360+ node definitions** — extracted from ComfyUI source code
- **Auto model download** — workflows include native `models` field for automatic missing model detection

---

## Project Structure

```
workflow-skill/
├── .claude-plugin/
│   ├── plugin.json
│   └── marketplace.json
├── skills/
│   ├── coze-workflow/
│   │   ├── SKILL.md
│   │   ├── scripts/          # build_coze_zip.py + coze_yaml_builder.py
│   │   ├── examples/
│   │   └── references/
│   ├── dify-workflow/
│   │   ├── SKILL.md
│   │   ├── examples/
│   │   └── references/
│   └── comfyui-workflow/
│       ├── SKILL.md
│       ├── references/
│       └── templates/
├── images/
├── scripts/
└── README.md
```

## Technical Details

### Coze.cn ZIP Format

Discovered through byte-level reverse engineering (16 rounds of experiments):

```
Workflow-<NAME>-draft-<DIGITS>/
├── MANIFEST.yml
└── workflow/<NAME>-draft.yaml
```

**Requirements**: Go `archive/zip` compatible (flags=0x08, vmade=20, time/date=0x0000), 4-space YAML indentation, double-quoted IDs, complete 14-field llmParam.

### Dify DSL Format

Standard Dify YAML DSL with `version: "0.6.0"`, node IDs as 13-digit timestamps, `{{#nodeId.variableName#}}` variable references.

### ComfyUI Litegraph Format

Standard Litegraph UI JSON with node definitions extracted from ComfyUI source, auto model download support via `models` array.

## License

MIT
