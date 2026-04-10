# Workflow Skill 复杂场景测试集

用于批量测试 `dify-workflow` 和 `coze-workflow` 两个 skill。每个场景都设计为 **20+ 节点、多层分支嵌套、多次聚合**，覆盖 Start / LLM / Vision / Knowledge Retrieval / HTTP / Code / If-Else / Question Classifier / Parameter Extractor / Iteration / Variable Aggregator / Template Transform / Tool / End 全谱系节点。

---

## 场景 1：跨境电商全链路选品上架机器人（~35 节点）

**输入**：类目 + 目标市场（多选）+ 预算上限

**流程**：
1. Start 收集参数
2. HTTP 拉取 1688 / Alibaba 供应链 API 候选 SKU 列表
3. Code 清洗、去重、按预算过滤
4. **Iteration #1** 遍历候选 SKU：
   - HTTP 查历史销量
   - LLM 预测爆款分（structured_output 打分）
   - If/Else：分 > 7 继续，否则丢弃
   - Knowledge Retrieval 查合规黑名单
   - Parameter Extractor 抽取关键参数
5. 聚合后 Question Classifier 按类目分三路（3C / 服饰 / 家居），每路独立 LLM prompt 生成详情页
6. Variable Aggregator 合流
7. **Iteration #2** 遍历目标市场，内部：
   - LLM 翻译
   - Tool 本地合规检查
   - Code 价格换算（汇率）
   - LLM 生成本地化营销文案
8. Code 构建多语言 payload
9. 并行 3 路 HTTP 推送：Shopify / Amazon / 速卖通
10. Variable Aggregator 合流三路上架结果
11. End 输出上架报告

**考点**：双层 Iteration、Question Classifier、Parameter Extractor、Knowledge Retrieval、多 HTTP 并行、深层嵌套

---

## 场景 2：金融研报自动生成与风控审核（~40 节点）

**输入**：股票代码 + 分析维度（财务/行业/风险/估值）

**流程**：
1. Start
2. 并行 5 路数据采集：
   - HTTP 财报 API
   - HTTP 新闻 API
   - HTTP 社交舆情 API
   - Knowledge Retrieval 历史研报库
   - Tool 技术指标计算
3. 每路后接 Code 清洗 + LLM 摘要
4. Variable Aggregator 合流 5 路结果
5. LLM 生成初版研报（structured_output 分四章）
6. **Iteration** 遍历"财务/行业/风险/估值"四章：
   - LLM 撰写章节
   - LLM 自我评分
   - If/Else：分数 < 8 → 走重写分支（再调 LLM + Template Transform 兜底）；否则通过
7. Question Classifier 判断最终结论（买入/持有/卖出）→ 三路不同合规模板
8. Template Transform 渲染完整研报
9. 并行 3 路风控：
   - LLM 查敏感词
   - Code 查数字前后一致性
   - HTTP 查监管黑名单
10. Variable Aggregator 合流风控结果
11. If/Else：任一 fail → HTTP 转人工审核；全通过 → HTTP 发布
12. End

**考点**：5 路并行采集、Iteration 内嵌条件循环、多层 Classifier、风控聚合、结构化输出

---

## 场景 3：企业级客服工单全自动闭环（~45 节点，Chatflow 模式）

**输入**：用户消息（sys.query）+ 用户 ID

**流程**：
1. Start
2. HTTP 拉用户画像
3. HTTP 拉订单历史
4. Parameter Extractor 抽取意图、情绪分、订单号
5. Question Classifier L1：退款 / 投诉 / 咨询 / bug / 其他（5 路）
6. **退款路径**：HTTP 查订单 → If/Else 7 天内 → 自动退款 HTTP；否则 Question Classifier L2 判断退款原因 → 3 路不同话术 LLM
7. **bug 路径**：Knowledge Retrieval 查 FAQ → LLM 判断是否命中 → If/Else → 命中直接回复；未命中 → HTTP 创建 Jira 工单 → LLM 生成等待话术
8. **投诉路径**：LLM 情绪分析 → If/Else 情绪 < 3 → HTTP Slack 转人工；否则 LLM 安抚
9. **咨询路径**：Iteration 遍历 3 个知识库并行检索 → 聚合 → LLM 融合答案
10. **其他路径**：LLM 兜底回复
11. 五路 Variable Aggregator
12. LLM 改写成统一语气
13. Template Transform 加签名
14. Answer 节点输出
15. 旁路：Code 记录埋点 + HTTP 写数据仓库

**考点**：两层 Question Classifier、多路 If/Else 嵌套、Iteration、Chatflow memory、旁路埋点

---

## 场景 4：视频内容工厂 - 长视频到多平台矩阵分发（~50 节点）

**输入**：YouTube URL + 目标平台多选（抖音/B站/小红书/Twitter/LinkedIn）

**流程**：
1. Start
2. HTTP 下载字幕 + 视频元数据
3. Code 切分章节
4. LLM 提取 10 个高光时刻（structured_output JSON 数组）
5. **Iteration #1** 遍历高光时刻：
   - LLM 写标题
   - LLM 写描述
   - LLM 生成封面 prompt
   - Tool 调 Stable Diffusion 生图
   - Code 打包片段资产
6. 聚合高光资产
7. **Iteration #2** 遍历目标平台：
   - Question Classifier 选模板（图文/短视频/长推文）
   - LLM 改写文案匹配平台调性
   - If/Else 判断是否需要 BGM → Tool 调音乐生成 API
   - HTTP 发布
   - Code 记录发布结果
8. 并行 3 路：
   - HTTP 写飞书多维表
   - HTTP Slack 通知
   - Code 生成周报数据
9. Variable Aggregator 聚合
10. End

**考点**：双层 Iteration 嵌套、Iteration 内部再嵌 Classifier + If/Else、多 Tool 调用、跨平台适配

---

## 场景 5：代码仓库安全审计 Agent（~38 节点）

**输入**：GitHub repo URL

**流程**：
1. Start
2. HTTP 调 GitHub API 获取文件树
3. Code 解析、过滤源码文件
4. **Iteration** 遍历文件：
   - HTTP 拉取文件内容
   - If/Else 按扩展名四路分流（py / js / go / java）
   - 每路独立 LLM 安全扫描（不同 prompt 模板）
   - Parameter Extractor 抽取漏洞信息（CWE 编号、严重度、位置）
   - Code 打分
5. 聚合所有漏洞
6. Question Classifier 按严重度分 P0 / P1 / P2 三路
7. **P0 路径**：LLM 生成修复 PR 描述 → HTTP 创建 GitHub PR → HTTP 发 PagerDuty 告警
8. **P1 路径**：Template Transform 生成 issue 正文 → HTTP 创建 GitHub issue
9. **P2 路径**：Code 汇总进周报队列
10. Variable Aggregator 合流
11. LLM 生成执行摘要
12. Knowledge Retrieval 查历史同类问题
13. LLM 对比趋势（新增/修复/遗留）
14. Template Transform 出 Markdown 报告
15. HTTP 上传 Confluence
16. End

**考点**：Iteration 内多路 If/Else、三路严重度分流、历史趋势对比、多外部系统集成

---

## 测试执行建议

| 场景 | 推荐触发命令 | 验证重点 |
|------|------------|---------|
| 1 跨境电商 | `/dify-workflow` + 场景1描述 | 双层 Iteration 是否正确嵌套、变量作用域 |
| 2 金融研报 | `/coze-workflow` + 场景2描述 | 5 路并行的 edge 连线、结构化输出 |
| 3 客服工单 | `/dify-workflow` (Chatflow) + 场景3描述 | 两层 Classifier 的 sourceHandle、Answer 节点 |
| 4 视频工厂 | `/coze-workflow` + 场景4描述 | 嵌套 Iteration 内部 If/Else 是否渲染 |
| 5 安全审计 | `/dify-workflow` + 场景5描述 | Iteration 内多路分流 + 外层三路聚合 |

> 批量跑完后，重点对比两个 skill 在**复杂拓扑**下的：节点数完整性、edge 正确性、variable_selector 指向、layout 坐标不重叠、导入后能否直接运行。
