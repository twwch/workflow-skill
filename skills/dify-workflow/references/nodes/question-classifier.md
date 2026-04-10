# Question Classifier (`question-classifier`)

## Purpose
Routes input to different downstream branches by classifying the query into one of several predefined categories using an LLM.

## Core Fields
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `query_variable_selector` | `ValueSelector` (string[]) | Yes | Reference to the variable containing the text to classify, e.g. `["sys", "query"]` |
| `model` | `ModelConfig` | Yes | LLM model configuration (see below) |
| `classes` | `Topic[]` | Yes | List of classification categories; minimum 2 required |
| `instruction` | `string` | No | Additional instruction/prompt to guide the classifier |
| `memory` | `Memory` | No | Conversation memory settings for chat context |
| `vision` | `object` | No | Vision settings for multimodal input |

## Full Schema

### ModelConfig
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `provider` | `string` | Yes | Model provider identifier, e.g. `"langgenius/openai/openai"` |
| `name` | `string` | Yes | Model name, e.g. `"gpt-4o-mini"` |
| `mode` | `string` | Yes | Model mode, typically `"chat"` |
| `completion_params` | `Record<string, any>` | No | Model parameters such as `temperature` |

### Topic (class entry)
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `string` | Yes | Unique identifier for this class, e.g. `"1"`, `"2"` |
| `name` | `string` | Yes | Human-readable name describing the category |

The `classes` array defines the classification categories. Each class `id` is also used in `_targetBranches` to define the routing branches. The `id` values in `classes` and `_targetBranches` must match.

### _targetBranches
The node's `_targetBranches` array must mirror the `classes` array:
```yaml
_targetBranches:
  - id: "1"
    name: "Technical Question"
  - id: "2"
    name: "General Question"
```

### Memory (optional)
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `role_prefix` | `RolePrefix` | No | Prefix for memory roles |
| `window.enabled` | `boolean` | Yes | Whether memory window is enabled |
| `window.size` | `number \| string \| null` | No | Memory window size |
| `query_prompt_template` | `string` | No | Template for the query prompt |

### Vision (optional)
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `enabled` | `boolean` | Yes | Whether vision input is enabled |
| `configs.variable_selector` | `ValueSelector` | Conditional | Required when `enabled` is true |
| `configs.detail` | `"low" \| "high"` | No | Vision resolution detail level |

## Variable Reference Rules

**Inputs:**
- `query_variable_selector` references a variable from an upstream node, typically `["sys", "query"]` for the user query or any `string` variable.

**Outputs:**
- This node does not produce output variables directly. Instead, it routes execution to one of its branch targets based on the classification result. Each branch corresponds to one entry in `classes`.

## Example Snippet
```yaml
nodes:
  - data:
      type: question-classifier
      title: Classify Intent
      query_variable_selector:
        - sys
        - query
      model:
        provider: langgenius/openai/openai
        name: gpt-4o-mini
        mode: chat
        completion_params:
          temperature: 0.7
      classes:
        - id: "1"
          name: Technical Question
        - id: "2"
          name: Billing Question
        - id: "3"
          name: General Inquiry
      instruction: "Classify the user's question into one of the provided categories."
      _targetBranches:
        - id: "1"
          name: Technical Question
        - id: "2"
          name: Billing Question
        - id: "3"
          name: General Inquiry
      vision:
        enabled: false
    id: question-classifier-1
```
