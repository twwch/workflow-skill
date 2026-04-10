# Workflow Skill

[English](README.md) | [![Linux.do](https://img.shields.io/badge/Linux.do-Discussion-blue)](https://linux.do/)

**用自然语言生成可直接导入的工作流文件。**

一句话描述你想要的工作流，自动生成 Coze / Dify / ComfyUI 平台可直接导入的完整工作流定义文件——包括节点配置、连线、布局和所有平台特有的格式要求。

## 安装

```bash
git clone https://github.com/twwch/workflow-skill.git /tmp/workflow-skill
cp -r /tmp/workflow-skill/skills/coze-workflow ~/.claude/skills/
cp -r /tmp/workflow-skill/skills/dify-workflow ~/.claude/skills/
cp -r /tmp/workflow-skill/skills/comfyui-workflow ~/.claude/skills/
```

![安装](images/安装.png)

---

## Coze Workflow

生成 `.zip` 文件，直接拖入 [coze.cn](https://www.coze.cn) 导入弹窗即可使用。

### 使用

```
/coze-workflow 创建一个金融研报自动生成工作流：5路并行数据采集 → 分章撰写 → 风控审核 → 发布
```

### 工作原理

Skill 生成 Python 脚本调用已验证的模板函数，产出字节级兼容 Go `archive/zip` 的 ZIP 文件。

![Coze 工作流生成](images/coze-workflow.png)

### 导入效果

![Coze 导入结果](images/finance_analysis-coze.png)
![Coze 导入 UI](images/finance_analysis-coze-import.png)

### 复杂流程生成

![复杂流程生成](images/复杂流程生成-coze.png)

### 跨境电商智能选品上架工作流（完整效果）

![跨境电商](images/cross_border_ecommerce.png)
![完整工作流视图](images/跨境电商智能选品上架工作流-whole-workflow.png)

### 支持的节点类型

`start` / `end` / `llm` / `loop` / `plugin` / `variable_merge` / `image_generate` / `code` / `http` / `condition` / `intent` / `knowledge`

---

## Dify Workflow

生成 `.dify.yml` / `.dify.json` 文件，通过 [Dify](https://dify.ai) 的「导入 DSL」功能导入。

### 使用

```
/dify-workflow 创建一个客服工单自动分类和回复工作流
```

### AI 生成工作流

![Dify 工作流生成](images/dify-workflow.png)

### 复杂流程生成

![复杂 Dify 流程](images/复杂流程生成-dify.png)

### 支持的节点类型

`start` / `end` / `llm` / `code` / `http-request` / `if-else` / `iteration` / `knowledge-retrieval` / `variable-aggregator` / `template-transform` / `question-classifier` / `parameter-extractor` / `tool` / `answer`

---

## ComfyUI Workflow

生成 `.json` 文件（Litegraph 格式），拖入 [ComfyUI](https://github.com/comfyanonymous/ComfyUI) 即可使用。

### 使用

```
/comfyui-workflow 创建一个 Flux 文生图 + WAN2.1 图生视频工作流
```

### AI 生成工作流 → 导入 ComfyUI → 运行出图

![生成工作流](skills/comfyui-workflow/images/生图转视频workflow.png)
![ComfyUI 中的工作流](skills/comfyui-workflow/images/图生视频流程.png)

### 生成的图片 & 视频

![生成的图片](skills/comfyui-workflow/images/生成的图片.jpg)
![运行结果](skills/comfyui-workflow/images/运行结果.png)

### 多个 Workflow 合并更新

![多个 Workflow 合并](skills/comfyui-workflow/images/多个workflow合并更新.png)

### 动作迁移

![动作迁移 Workflow](skills/comfyui-workflow/images/动作迁移workflow.png)
![动作迁移流程](skills/comfyui-workflow/images/动作迁移流程.png)

### 功能特性

- **34 个内置模板** — 覆盖所有主流模型和任务类型
- **360+ 节点定义** — 从 ComfyUI 源码提取，确保字段类型和范围准确
- **自动模型下载** — 工作流包含原生 `models` 字段，导入时 ComfyUI 自动检测缺失模型并弹窗下载

---

## 项目结构

```
workflow-skill/
├── .claude-plugin/
│   ├── plugin.json              # 插件元数据
│   └── marketplace.json         # Marketplace 注册
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
├── images/
├── scripts/
└── README.md
```

## 技术细节

### Coze.cn ZIP 格式

通过 16 轮字节级逆向实验发现：

```
Workflow-<NAME>-draft-<DIGITS>/
├── MANIFEST.yml
└── workflow/<NAME>-draft.yaml
```

**要求**：Go `archive/zip` 兼容（flags=0x08, vmade=20, time/date=0x0000），4 空格 YAML 缩进，双引号 ID，完整 14 字段 llmParam。

### Dify DSL 格式

标准 Dify YAML DSL，`version: "0.6.0"`，13 位时间戳节点 ID，`{{#nodeId.variableName#}}` 变量引用。

### ComfyUI Litegraph 格式

标准 Litegraph UI JSON，节点定义从 ComfyUI 源码提取，通过 `models` 数组支持自动模型下载。

## License

MIT
