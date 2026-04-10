# Workflow Skill

[中文](README.zh-CN.md)

**Generate importable workflow files from natural language descriptions.**

Describe your workflow in one sentence, and get a complete workflow definition file ready to import into Coze, Dify, or ComfyUI — including node configuration, edges, layout, and all platform-specific format requirements.

## Why?

Manually building complex workflows (20+ nodes, nested loops, parallel branches) on low-code platforms is time-consuming. This skill lets you describe business logic in plain language and automatically generates importable workflow files.

## Skills

| Skill | Platform | Output | Import Method |
|-------|----------|--------|---------------|
| `coze-workflow` | [coze.cn](https://www.coze.cn) | `.zip` (YAML + MANIFEST) | UI import dialog |
| `dify-workflow` | [Dify](https://dify.ai) | `.dify.yml` / `.dify.json` | UI "Import DSL" |
| `comfyui-workflow` | [ComfyUI](https://github.com/comfyanonymous/ComfyUI) | `.json` (Litegraph) | Drag & drop |

## Installation

```bash
# Manual install
git clone https://github.com/twwch/workflow-skill.git /tmp/workflow-skill
cp -r /tmp/workflow-skill/skills/coze-workflow ~/.claude/skills/
cp -r /tmp/workflow-skill/skills/dify-workflow ~/.claude/skills/
cp -r /tmp/workflow-skill/skills/comfyui-workflow ~/.claude/skills/
```

## Usage

```bash
# Coze: E-commerce product listing
/coze-workflow Create a cross-border e-commerce workflow: input category → LLM analyze SKUs → Loop evaluate → 3-way parallel detail pages → aggregate and publish

# Dify: Customer service
/dify-workflow Create a customer service ticket auto-classification and reply workflow

# ComfyUI: Text-to-image + image-to-video
/comfyui-workflow Create a Flux txt2img + WAN2.1 img2vid workflow
```

## Supported Node Types

**Coze** (verified on coze.cn): `start` / `end` / `llm` / `loop` / `plugin` / `variable_merge` / `image_generate`

**Dify**: `start` / `end` / `llm` / `code` / `http-request` / `if-else` / `iteration` / `knowledge-retrieval` / `variable-aggregator` / `template-transform` / `question-classifier` / `parameter-extractor` / `tool` / `answer`

**ComfyUI**: All ComfyUI nodes (KSampler / CLIPTextEncode / VAEDecode / LoraLoader / WAN video etc.)

## Project Structure

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

## Coze.cn ZIP Format (Technical Details)

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

## License

MIT
