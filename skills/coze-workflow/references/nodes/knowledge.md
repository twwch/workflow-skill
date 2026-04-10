## coze.cn Cloud YAML Format

YAML type: `knowledge` | Status: 未验证

> This node type's cloud YAML format is based on source code analysis.
> For verified format, export a real workflow from coze.cn containing this node.

```yaml
    - id: "200001"
      type: knowledge
      title: 知识库检索
      position:
        x: 0
        y: 0
      parameters:
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
```

---

# Knowledge Node

## Purpose

Interacts with knowledge bases (datasets). Has two sub-types: **search** (retrieve relevant documents) and **write** (index new documents into a knowledge base).

**Node type identifiers:**
- Search: `StandardNodeType.Dataset` (frontend), `NodeTypeKnowledgeRetriever` (backend)
- Write: `StandardNodeType.DatasetWrite` (frontend), `NodeTypeKnowledgeIndexer` (backend)

---

## Knowledge Search Node

### Core Fields

| Field | Path | Type | Required | Description |
|-------|------|------|----------|-------------|
| Query | `inputs.inputParameters[name="Query"]` | ValueExpression | Yes | The search query string |
| datasetList | `inputs.datasetParam[name="datasetList"]` | array of string/int64 | Yes | List of knowledge base IDs to search |
| topK | `inputs.datasetParam[name="topK"]` | integer | No | Maximum number of results to return |
| minScore | `inputs.datasetParam[name="minScore"]` | float | No | Minimum relevance score threshold |
| strategy | `inputs.datasetParam[name="strategy"]` | integer | No | Retrieval search type strategy |
| useRerank | `inputs.datasetParam[name="useRerank"]` | boolean | No | Enable reranking of results |
| useRewrite | `inputs.datasetParam[name="useRewrite"]` | boolean | No | Enable query rewriting |
| isPersonalOnly | `inputs.datasetParam[name="isPersonalOnly"]` | boolean | No | Restrict to personal knowledge only |
| useNl2sql | `inputs.datasetParam[name="useNl2sql"]` | boolean | No | Enable NL-to-SQL for table knowledge bases |
| chatHistorySetting | `inputs.chatHistorySetting` | object | No | Chat history configuration for chatflow mode |

### Default Outputs (Search)

| Name | Type | Description |
|------|------|-------------|
| `outputList` | ArrayObject | Array of retrieved document slices |
| `outputList[].documentId` | String | Document ID of the matched slice |
| `outputList[].output` | String | Content of the matched slice |

### Full Schema (Search DTO)

```jsonc
{
  "nodeMeta": { "title": "...", "description": "..." },
  "inputs": {
    "inputParameters": [
      {
        "name": "Query",
        "input": { /* ValueExpression: ref or literal */ }
      }
    ],
    "datasetParam": [
      {
        "name": "datasetList",
        "input": {
          "type": "list",
          "schema": { "type": "string" },
          "value": { "type": "literal", "content": ["12345", "67890"] }
        }
      },
      {
        "name": "topK",
        "input": { "type": "integer", "value": { "type": "literal", "content": 3 } }
      },
      {
        "name": "minScore",
        "input": { "type": "float", "value": { "type": "literal", "content": 0.5 } }
      },
      {
        "name": "strategy",
        "input": { "type": "integer", "value": { "type": "literal", "content": 0 } }
      },
      // Boolean params use BlockInput.createBoolean format:
      { "name": "useRerank", "input": { "type": "boolean", "value": { "type": "literal", "content": false } } },
      { "name": "useRewrite", "input": { "type": "boolean", "value": { "type": "literal", "content": false } } },
      { "name": "isPersonalOnly", "input": { "type": "boolean", "value": { "type": "literal", "content": false } } },
      { "name": "useNl2sql", "input": { "type": "boolean", "value": { "type": "literal", "content": false } } }
    ],
    "chatHistorySetting": {              // optional, for chatflow mode
      "enableChatHistory": true,
      "chatHistoryRound": 5
    }
  },
  "outputs": [
    {
      "key": "...",
      "name": "outputList",
      "type": "ArrayObject",
      "children": [
        { "key": "...", "name": "output", "type": "String" }
      ]
    }
  ]
}
```

### Frontend Form Data Mapping (Search)

The frontend transforms `datasetParam` into a flat form structure:

```
inputs.inputParameters.Query  ->  ValueExpression
inputs.datasetParameters.datasetParam  ->  array of dataset IDs (content values)
inputs.datasetParameters.datasetSetting.top_k  ->  number
inputs.datasetParameters.datasetSetting.min_score  ->  number
inputs.datasetParameters.datasetSetting.strategy  ->  number
inputs.datasetParameters.datasetSetting.use_rerank  ->  boolean
inputs.datasetParameters.datasetSetting.use_rewrite  ->  boolean
inputs.datasetParameters.datasetSetting.is_personal_only  ->  boolean
inputs.datasetParameters.datasetSetting.use_nl2sql  ->  boolean
```

---

## Knowledge Write Node

### Core Fields

| Field | Path | Type | Required | Description |
|-------|------|------|----------|-------------|
| knowledge | `inputs.inputParameters[name="knowledge"]` | ValueExpression | Yes | File URL to index into the knowledge base |
| datasetList | `inputs.datasetParam[name="datasetList"]` | array of string | Yes | Target knowledge base ID (single ID in array) |
| strategyParam | `inputs.strategyParam` | object | Yes | Parsing, chunking, and indexing strategies |

### Strategy Parameters

| Field | Path | Type | Description |
|-------|------|------|-------------|
| parsingStrategy.parsingType | `strategyParam.parsingStrategy.parsingType` | string | Parsing mode |
| parsingStrategy.imageOcr | `strategyParam.parsingStrategy.imageOcr` | boolean | Enable image OCR |
| parsingStrategy.imageExtraction | `strategyParam.parsingStrategy.imageExtraction` | boolean | Enable image extraction |
| parsingStrategy.tableExtraction | `strategyParam.parsingStrategy.tableExtraction` | boolean | Enable table extraction |
| chunkStrategy.chunkType | `strategyParam.chunkStrategy.chunkType` | string | Chunking type |
| chunkStrategy.separator | `strategyParam.chunkStrategy.separator` | string | Chunk separator |
| chunkStrategy.maxToken | `strategyParam.chunkStrategy.maxToken` | integer | Max tokens per chunk |
| chunkStrategy.overlap | `strategyParam.chunkStrategy.overlap` | float | Overlap ratio (0-1, multiplied by maxToken for actual overlap) |
| indexStrategy.vectorModel | `strategyParam.indexStrategy.vectorModel` | string | Embedding vector model name |

### Default Outputs (Write)

| Name | Type | Description |
|------|------|-------------|
| `documentId` | String | ID of the created document |
| `fileName` | String | Name of the indexed file |
| `fileUrl` | String | URL of the indexed file |

### Full Schema (Write DTO)

```jsonc
{
  "nodeMeta": { "title": "...", "description": "..." },
  "inputs": {
    "inputParameters": [
      {
        "name": "knowledge",
        "input": { /* ValueExpression: file URL ref or literal */ }
      }
    ],
    "datasetParam": [
      {
        "name": "datasetList",
        "input": {
          "type": "list",
          "schema": { "type": "string" },
          "value": { "type": "literal", "content": ["12345"] }
        }
      }
    ],
    "strategyParam": {
      "parsingStrategy": {
        "parsingType": "auto",
        "imageOcr": true,
        "imageExtraction": false,
        "tableExtraction": false
      },
      "chunkStrategy": {
        "chunkType": "auto",
        "separator": "",
        "maxToken": 500,
        "overlap": 0.1
      },
      "indexStrategy": {
        "vectorModel": "model_name"
      }
    }
  },
  "outputs": [
    { "key": "...", "name": "documentId", "type": "String" },
    { "key": "...", "name": "fileName", "type": "String" },
    { "key": "...", "name": "fileUrl", "type": "String" }
  ]
}
```

## Variable Reference Rules

- `Query` (search) and `knowledge` (write) use standard `ValueExpression` format.
- `datasetParam` items use a nested `input.value.content` structure where `content` holds the literal value.
- Boolean parameters use `BlockInput.createBoolean(name, value)` which produces `{type: "boolean", value: {type: "literal", content: <bool>}}`.
- Strategy parameters (write) are flat literal values, not ValueExpressions.

## Backend Behavior

- Search: invokes cross-domain knowledge retrieval service; supports chat history context in chatflow mode.
- Write: validates file extension (supported formats enforced by parser), creates a document in the target knowledge base.
- The `inputParametersPath` for search is `/inputs/inputParameters`.

## Example JSON Snippet (Search)

```json
{
  "inputs": {
    "inputParameters": [
      { "name": "Query", "input": { "type": "ref", "content": { "keyPath": ["start_node", "user_query"] } } }
    ],
    "datasetParam": [
      {
        "name": "datasetList",
        "input": { "type": "list", "schema": { "type": "string" }, "value": { "type": "literal", "content": ["100001"] } }
      },
      { "name": "topK", "input": { "type": "integer", "value": { "type": "literal", "content": 3 } } },
      { "name": "useRerank", "input": { "type": "boolean", "value": { "type": "literal", "content": true } } }
    ]
  }
}
```

## Source Files

- Frontend (search): `source/coze-studio/frontend/packages/workflow/playground/src/node-registries/dataset/dataset-search/`
- Frontend (write): `source/coze-studio/frontend/packages/workflow/playground/src/node-registries/dataset/dataset-write/`
- Backend (retrieve): `source/coze-studio/backend/domain/workflow/internal/nodes/knowledge/knowledge_retrieve.go`
- Backend (indexer): `source/coze-studio/backend/domain/workflow/internal/nodes/knowledge/knowledge_indexer.go`
