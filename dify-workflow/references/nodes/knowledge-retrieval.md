# Knowledge Retrieval Node (`knowledge-retrieval`)

## Purpose
Retrieves relevant document chunks from one or more Dify knowledge bases (datasets) using semantic search, keyword search, or a hybrid approach.

## Core Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `query_variable_selector` | `ValueSelector` (string[]) | Yes* | Reference to the text query variable |
| `dataset_ids` | `string[]` | Yes | List of knowledge base (dataset) UUIDs to search |
| `retrieval_mode` | `string` | Yes | Retrieval strategy: `"single"` or `"multiple"` |
| `query_attachment_selector` | `ValueSelector` (string[]) | No | Reference to file attachments for image-based retrieval |
| `multiple_retrieval_config` | `MultipleRetrievalConfig` | No* | Config for multi-way retrieval (required when `retrieval_mode` is `"multiple"`) |
| `single_retrieval_config` | `SingleRetrievalConfig` | No* | Config for single retrieval (required when `retrieval_mode` is `"single"`) |
| `metadata_filtering_mode` | `string` | No | Metadata filter mode: `"disabled"` (default), `"automatic"`, `"manual"` |
| `metadata_filtering_conditions` | `MetadataFilteringConditions` | No | Filter conditions when `metadata_filtering_mode` is `"manual"` |
| `metadata_model_config` | `ModelConfig` | No | LLM config for automatic metadata filtering |

*At least one of `query_variable_selector` or `query_attachment_selector` must be set for the node to execute.

## Full Schema

### retrieval_mode

| Value | Description |
|-------|-------------|
| `"single"` | Uses an LLM to pick the best-matching knowledge base, then retrieves from it. Requires `single_retrieval_config`. |
| `"multiple"` | Retrieves from all selected knowledge bases simultaneously and merges results. Requires `multiple_retrieval_config`. |

### MultipleRetrievalConfig

```yaml
multiple_retrieval_config:
  top_k: 4                          # integer, required - Max number of chunks to return (default: 4)
  score_threshold: null              # float | null - Min relevance score (0-1). null = disabled. Default threshold: 0.8 when enabled
  reranking_enable: true             # boolean - Whether reranking is active (backend default: true)
  reranking_mode: "reranking_model"  # string - "reranking_model" (default) | "weighted_score"
  reranking_model:                   # optional - Required when reranking_mode is "reranking_model"
    provider: ""                     # string - Reranking model provider
    model: ""                        # string - Reranking model name
  weights:                           # optional - Required when reranking_mode is "weighted_score"
    weight_type: "customized"        # WeightedScoreEnum: "semantic_first" | "keyword_first" | "customized"
    vector_setting:
      vector_weight: 0.7             # float - Weight for semantic/vector search (0-1)
      embedding_provider_name: ""    # string - Embedding model provider
      embedding_model_name: ""       # string - Embedding model name
    keyword_setting:
      keyword_weight: 0.3            # float - Weight for keyword search (0-1, should sum to 1 with vector_weight)
```

**RerankingModeEnum values:** `"reranking_model"`, `"weighted_score"`

**WeightedScoreEnum values:** `"semantic_first"`, `"keyword_first"`, `"customized"`

### SingleRetrievalConfig

Uses an LLM to determine which knowledge base to query and how to formulate the retrieval:

```yaml
single_retrieval_config:
  model:
    provider: ""              # string - Model provider
    name: ""                  # string - Model name
    mode: "chat"              # string - "chat" or "completion"
    completion_params:        # Record<string, any>
      temperature: 0.7
```

### ModelConfig (shared type)

```yaml
model:
  provider: ""              # string, required - Model provider identifier
  name: ""                  # string, required - Model name
  mode: "chat"              # string, required - "chat" or "completion"
  completion_params:        # Record<string, any>, required
    temperature: 0.7
```

### Metadata Filtering

#### metadata_filtering_mode

| Value | Description |
|-------|-------------|
| `"disabled"` | No metadata filtering (default) |
| `"automatic"` | Uses an LLM to automatically determine filter conditions. Requires `metadata_model_config` |
| `"manual"` | Uses explicitly defined filter conditions. Requires `metadata_filtering_conditions` |

#### MetadataFilteringConditions (manual mode)

```yaml
metadata_filtering_conditions:
  logical_operator: "and"           # "and" | "or" - How to combine conditions (default: "and")
  conditions:
    - name: "category"              # string - Metadata field name
      comparison_operator: "is"     # SupportedComparisonOperator
      value: "technical"            # string | number | null
```

**Supported comparison operators:**

For string/array fields:
- `"contains"`, `"not contains"`, `"start with"`, `"end with"`
- `"is"`, `"is not"`, `"empty"`, `"not empty"`
- `"in"`, `"not in"`

For number fields:
- `"="`, `"!="` (displayed as `"≠"`), `">"`, `"<"`, `">="` (displayed as `"≥"`), `"<="` (displayed as `"≤"`)

For time fields:
- `"before"`, `"after"`

General:
- `"exists"`, `"not exists"`, `"is null"`, `"is not null"`, `"all of"`

### metadata_model_config (automatic mode)

Same structure as `ModelConfig`. Used when `metadata_filtering_mode` is `"automatic"` to let an LLM extract filter conditions from the query.

## Variable Reference Rules

### Input Variables
- `query_variable_selector`: Points to a string variable, typically `["start", "query"]` or the output of another node
- `query_attachment_selector`: Points to a file or array[file] variable for image-based queries

### Output Variables

| Variable | Type | Description |
|----------|------|-------------|
| `result` | `Array[Object]` | Array of retrieved document chunks |

Each object in `result` contains:

| Field | Type | Description |
|-------|------|-------------|
| `content` | `string` | The text content of the retrieved chunk |
| `title` | `string` | Document title |
| `url` | `string` | Source URL (if available) |
| `icon` | `string` | Source icon URL |
| `metadata` | `object` | Chunk metadata (dataset_id, dataset_name, document_id, document_name, document_data_source_type, segment_id, segment_position, segment_word_count, segment_hit_count, segment_index_node_hash, score) |
| `files` | `Array[File]` | Associated files (if any) |

## Default Values

```yaml
query_variable_selector: []
query_attachment_selector: []
dataset_ids: []
retrieval_mode: "multiple"
multiple_retrieval_config:
  top_k: 4
  score_threshold: null       # disabled by default
  reranking_enable: false
metadata_filtering_mode: "disabled"
```

## Example Snippet

Minimal knowledge retrieval with multiple datasets:

```yaml
- data:
    type: knowledge-retrieval
    title: "Search Knowledge"
    query_variable_selector:
      - "start"
      - "query"
    dataset_ids:
      - "dataset-uuid-1"
      - "dataset-uuid-2"
    retrieval_mode: "multiple"
    multiple_retrieval_config:
      top_k: 4
      score_threshold: null
      reranking_enable: false
```

Knowledge retrieval with reranking model:

```yaml
- data:
    type: knowledge-retrieval
    title: "Search with Reranking"
    query_variable_selector:
      - "start"
      - "query"
    dataset_ids:
      - "dataset-uuid-1"
    retrieval_mode: "multiple"
    multiple_retrieval_config:
      top_k: 6
      score_threshold: 0.5
      reranking_enable: true
      reranking_mode: "reranking_model"
      reranking_model:
        provider: "cohere"
        model: "rerank-english-v3.0"
```

Knowledge retrieval with weighted score (hybrid search):

```yaml
- data:
    type: knowledge-retrieval
    title: "Hybrid Search"
    query_variable_selector:
      - "start"
      - "query"
    dataset_ids:
      - "dataset-uuid-1"
    retrieval_mode: "multiple"
    multiple_retrieval_config:
      top_k: 5
      score_threshold: 0.3
      reranking_enable: true
      reranking_mode: "weighted_score"
      weights:
        weight_type: "customized"
        vector_setting:
          vector_weight: 0.7
          embedding_provider_name: "openai"
          embedding_model_name: "text-embedding-3-small"
        keyword_setting:
          keyword_weight: 0.3
```

Single retrieval mode (LLM-guided):

```yaml
- data:
    type: knowledge-retrieval
    title: "Smart Retrieval"
    query_variable_selector:
      - "start"
      - "query"
    dataset_ids:
      - "dataset-uuid-1"
      - "dataset-uuid-2"
      - "dataset-uuid-3"
    retrieval_mode: "single"
    single_retrieval_config:
      model:
        provider: "openai"
        name: "gpt-4o-mini"
        mode: "chat"
        completion_params:
          temperature: 0.3
```

Knowledge retrieval with manual metadata filtering:

```yaml
- data:
    type: knowledge-retrieval
    title: "Filtered Search"
    query_variable_selector:
      - "start"
      - "query"
    dataset_ids:
      - "dataset-uuid-1"
    retrieval_mode: "multiple"
    multiple_retrieval_config:
      top_k: 5
      score_threshold: 0.5
      reranking_enable: false
    metadata_filtering_mode: "manual"
    metadata_filtering_conditions:
      logical_operator: "and"
      conditions:
        - name: "category"
          comparison_operator: "is"
          value: "technical"
        - name: "year"
          comparison_operator: ">="
          value: 2024
```
