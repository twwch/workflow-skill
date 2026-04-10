# 开源了一个 AI Skill：说句话就能生成 Coze / Dify / ComfyUI 工作流，直接导入就能跑

> 不用拖拽、不用连线、不用配参数。描述你的业务逻辑，AI 自动生成 20+ 节点的完整工作流文件，拖进平台秒导入。

## 痛点

在 Coze、Dify、ComfyUI 这些低代码平台上搭建复杂工作流，你是不是也经历过：

- 20+ 个节点手动拖拽、连线、配置参数，搞了一下午
- 节点间的数据引用一不小心接错，调试半天
- 想复用一个成熟的业务流程模板，但平台之间格式不通用

**现在，这些都不用了。**

## Workflow Skill 是什么

这是一套 Claude Code 的 Skills，支持三大平台：

| 平台 | 输出格式 | 导入方式 |
|------|---------|---------|
| **Coze** (coze.cn) | ZIP 文件 | 拖入导入弹窗 |
| **Dify** | YAML/JSON DSL | 导入 DSL |
| **ComfyUI** | Litegraph JSON | 拖入 ComfyUI |

一句话描述你的需求，自动生成**包含所有节点配置、连线、布局的完整工作流定义文件**——直接导入平台就能用。

## 效果展示

### Coze：跨境电商智能选品上架

```
/coze-workflow 创建一个跨境电商选品上架工作流：
输入品类和预算 → 拉取1688 SKU → 循环评估打分 →
类目分流生成详情页 → 多市场本地化翻译 → 多平台并行上架
```

AI 自动生成 Python 脚本，调用已验证的节点模板函数，产出可直接导入的 ZIP：

![Coze 工作流生成](https://cdn.jsdelivr.net/gh/twwch/images/workflow-skill/images/2026/04/coze-workflow.png)

导入 coze.cn 后的效果——22 个节点、27 条连线，自动布局：

![跨境电商工作流](https://cdn.jsdelivr.net/gh/twwch/images/workflow-skill/images/2026/04/cross_border_ecommerce.png)

![完整工作流视图](https://cdn.jsdelivr.net/gh/twwch/images/workflow-skill/images/2026/04/跨境电商智能选品上架工作流-whole-workflow.png)

### Dify：财务分析工作流

```
/dify-workflow 创建一个财务分析工作流：
用户上传财务文件 → 内容提取 → 大模型多维分析 → 模板汇总报告
```

![Dify 工作流生成](https://cdn.jsdelivr.net/gh/twwch/images/workflow-skill/images/2026/04/dify-workflow.png)

Dify 的工作流支持 14 种节点类型，包括 Code、HTTP、If/Else、Iteration、Knowledge Retrieval 等，生成的 YAML DSL 导入即可运行。

### ComfyUI：文生图 + 图生视频

```
/comfyui-workflow 创建一个 Flux 文生图 + WAN2.1 图生视频工作流
```

![ComfyUI 工作流](https://cdn.jsdelivr.net/gh/twwch/images/workflow-skill/images/2026/04/生图转视频workflow.png)

![运行结果](https://cdn.jsdelivr.net/gh/twwch/images/workflow-skill/images/2026/04/运行结果.png)

ComfyUI Skill 内置 34 个模板、360+ 节点定义，支持自动模型下载——导入后 ComfyUI 会自动检测缺失模型并弹窗下载。

## 安装

三步搞定：

```bash
git clone https://github.com/twwch/workflow-skill.git /tmp/workflow-skill
cp -r /tmp/workflow-skill/skills/coze-workflow ~/.claude/skills/
cp -r /tmp/workflow-skill/skills/dify-workflow ~/.claude/skills/
cp -r /tmp/workflow-skill/skills/comfyui-workflow ~/.claude/skills/
```

![安装](https://cdn.jsdelivr.net/gh/twwch/images/workflow-skill/images/2026/04/安装.png)

## Coze 的坑：字节级逆向

这个项目最硬核的部分是 Coze 的 ZIP 导入。coze.cn 的导入格式没有任何公开文档，我们通过**16 轮字节级逆向实验**才搞定：

1. **ZIP 打包格式**：必须模仿 Go 的 `archive/zip` 库——`flags=0x08`（data descriptor）、`vmade=20`（DOS）、`time/date=0x0000`。Python 的 `zipfile` 默认输出会被拒绝
2. **命名契约**：目录 `Workflow-<NAME>-draft-<NUM>`、文件 `<NAME>-draft.yaml`、YAML 内 `name: <NAME>` 三者必须完全一致
3. **YAML 格式**：4 空格缩进、双引号 ID，不能用 `yaml.dump()`（缩进和引号格式不对）
4. **节点类型字符串**：和开源版完全不同（`condition` 不是 `selector`，`http` 不是 `http_requester`，`intent` 不是 `intent_detector`）
5. **字段结构**：每种节点有严格的必填字段，`type: list` 必须有 `items` 子类型，否则前端直接崩溃

最终写出了 `build_coze_zip.py` 打包工具和 `coze_yaml_builder.py` 节点模板库，确保生成的每个字节都和 coze.cn 兼容。

## 支持的节点类型

**Coze**：`start` / `end` / `llm` / `loop` / `plugin` / `variable_merge` / `image_generate` / `code` / `http` / `condition` / `intent` / `knowledge` 等 48 种

**Dify**：`start` / `end` / `llm` / `code` / `http-request` / `if-else` / `iteration` / `knowledge-retrieval` / `variable-aggregator` / `template-transform` / `question-classifier` / `parameter-extractor` / `tool` / `answer`

**ComfyUI**：支持所有 ComfyUI 节点

## 项目地址

GitHub: https://github.com/twwch/workflow-skill

讨论: https://linux.do/

欢迎 Star、Issue、PR！
