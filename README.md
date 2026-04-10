# Workflow Skill

[English](#english) | [中文](#中文)

---

<a id="中文"></a>

## 中文

**用自然语言生成可直接导入的工作流文件。**

一句话描述你想要的工作流，自动生成 Coze / Dify / ComfyUI 平台可直接导入的完整工作流定义文件——包括节点配置、连线、布局和所有平台特有的格式要求。

### 为什么需要这个？

在低代码/无代码平台上手动拖拽搭建复杂工作流（20+ 节点、嵌套循环、多路并行）非常耗时。这个 skill 让你用一句话描述业务逻辑，AI 自动生成完整的工作流定义文件，拖进平台即可运行。

### 核心能力

| Skill | 平台 | 输出格式 | 导入方式 |
|-------|------|---------|---------|
| `coze-workflow` | [coze.cn](https://www.coze.cn) | `.zip` (YAML + MANIFEST) | UI「导入」弹窗 |
| `dify-workflow` | [Dify](https://dify.ai) | `.dify.yml` / `.dify.json` | UI「导入 DSL」 |
| `comfyui-workflow` | [ComfyUI](https://github.com/comfyanonymous/ComfyUI) | `.json` (Litegraph) | 拖入 ComfyUI |

### 安装

```bash
# 手动安装
git clone <repo-url> /tmp/workflow-skill
cp -r /tmp/workflow-skill/skills/coze-workflow ~/.claude/skills/
cp -r /tmp/workflow-skill/skills/dify-workflow ~/.claude/skills/
cp -r /tmp/workflow-skill/skills/comfyui-workflow ~/.claude/skills/
```

### 使用示例

```bash
# Coze：跨境电商选品上架
/coze-workflow 创建一个跨境电商选品工作流：输入品类和预算 → LLM分析候选SKU → Loop遍历评估 → 3路并行生成详情页 → 汇总上架

# Dify：客服工单自动处理
/dify-workflow 创建一个客服工单自动分类和回复工作流

# ComfyUI：文生图+图生视频
/comfyui-workflow 创建一个 Flux 文生图 + WAN2.1 图生视频工作流
```

### 支持的节点类型

**Coze** (coze.cn 已验证): `start` / `end` / `llm` / `loop` / `plugin` / `variable_merge` / `image_generate`

**Dify**: `start` / `end` / `llm` / `code` / `http-request` / `if-else` / `iteration` / `knowledge-retrieval` / `variable-aggregator` / `template-transform` / `question-classifier` / `parameter-extractor` / `tool` / `answer`

**ComfyUI**: 支持所有 ComfyUI 节点（KSampler / CLIPTextEncode / VAEDecode / LoraLoader / WAN 视频等）

### Coze.cn ZIP 格式技术细节

coze.cn 要求特定的 ZIP 格式导入，通过字节级逆向工程发现：

**ZIP 结构**：
```
Workflow-<NAME>-draft-<DIGITS>/
├── MANIFEST.yml
└── workflow/
    └── <NAME>-draft.yaml
```

**命名契约**：`<NAME>` 在目录名、文件名、YAML `name:` 字段中必须完全一致。

**字节级要求**（Go `archive/zip` 兼容）：
- ZIP 内无目录条目，仅 2 个文件条目
- `flags = 0x08`（data descriptor 模式）
- `time/date = 0x0000`（零时间戳）
- Central directory: `vmade = 20` (DOS), `external_attr = 0x00000000`

**YAML 格式**（严格，不能用 `yaml.dump()`）：
- 4 空格缩进
- 双引号字符串 ID
- LLM 节点必须包含完整 14 字段 `llmParam` 数组

---

<a id="english"></a>

## English

**Generate importable workflow files from natural language descriptions.**

Describe your workflow in one sentence, and get a complete workflow definition file ready to import into Coze, Dify, or ComfyUI — including node configuration, edges, layout, and all platform-specific format requirements.

### Why?

Manually building complex workflows (20+ nodes, nested loops, parallel branches) on low-code platforms is time-consuming. This skill lets you describe business logic in plain language and automatically generates importable workflow files.

### Skills

| Skill | Platform | Output | Import Method |
|-------|----------|--------|---------------|
| `coze-workflow` | [coze.cn](https://www.coze.cn) | `.zip` (YAML + MANIFEST) | UI import dialog |
| `dify-workflow` | [Dify](https://dify.ai) | `.dify.yml` / `.dify.json` | UI "Import DSL" |
| `comfyui-workflow` | [ComfyUI](https://github.com/comfyanonymous/ComfyUI) | `.json` (Litegraph) | Drag & drop |

### Installation

```bash
# Manual install
git clone <repo-url> /tmp/workflow-skill
cp -r /tmp/workflow-skill/skills/coze-workflow ~/.claude/skills/
cp -r /tmp/workflow-skill/skills/dify-workflow ~/.claude/skills/
cp -r /tmp/workflow-skill/skills/comfyui-workflow ~/.claude/skills/
```

### Usage

```bash
# Coze: E-commerce product listing
/coze-workflow Create a cross-border e-commerce workflow: input category → LLM analyze SKUs → Loop evaluate → 3-way parallel detail pages → aggregate and publish

# Dify: Customer service
/dify-workflow Create a customer service ticket auto-classification and reply workflow

# ComfyUI: Text-to-image + image-to-video
/comfyui-workflow Create a Flux txt2img + WAN2.1 img2vid workflow
```

### Supported Node Types

**Coze** (verified on coze.cn): `start` / `end` / `llm` / `loop` / `plugin` / `variable_merge` / `image_generate`

**Dify**: `start` / `end` / `llm` / `code` / `http-request` / `if-else` / `iteration` / `knowledge-retrieval` / `variable-aggregator` / `template-transform` / `question-classifier` / `parameter-extractor` / `tool` / `answer`

**ComfyUI**: All ComfyUI nodes (KSampler / CLIPTextEncode / VAEDecode / LoraLoader / WAN video etc.)

### Project Structure

```
workflow-skill/
├── .claude-plugin/
│   ├── plugin.json              # Plugin metadata
│   └── marketplace.json         # Marketplace registration
├── skills/
│   ├── coze-workflow/
│   │   ├── SKILL.md
│   │   ├── scripts/             # build_coze_zip.py + coze_yaml_builder.py
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
├── scripts/
├── test-scenarios.md
└── README.md
```

### Coze.cn ZIP Format (Technical Details)

The coze.cn cloud platform requires a specific ZIP format, discovered through byte-level reverse engineering:

**ZIP structure**:
```
Workflow-<NAME>-draft-<DIGITS>/
├── MANIFEST.yml
└── workflow/
    └── <NAME>-draft.yaml
```

**Naming contract**: `<NAME>` must be identical in directory name, YAML filename, and YAML `name:` field.

**Byte-level requirements** (Go `archive/zip` compatibility):
- No directory entries — only 2 file entries
- `flags = 0x08` (data descriptor mode)
- `time/date = 0x0000` (zero timestamp)
- Central directory: `vmade = 20` (DOS), `external_attr = 0x00000000`

**YAML formatting** (strict — cannot use `yaml.dump()`):
- 4-space indentation
- Double-quoted string IDs
- Complete 14-field `llmParam` array for LLM nodes

---

## License

MIT
