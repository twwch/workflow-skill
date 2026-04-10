# Parameter Extractor (`parameter-extractor`)

## Purpose
Uses an LLM to extract structured parameters from natural language input, outputting each extracted value as a named variable.

## Core Fields
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | `ValueSelector` (string[]) | Yes | Reference to the variable containing text to extract from, e.g. `["sys", "query"]` |
| `model` | `ModelConfig` | Yes | LLM model configuration |
| `parameters` | `Param[]` | Yes | List of parameters to extract; at least one required |
| `reasoning_mode` | `"prompt" \| "function_call"` | Yes | Extraction strategy; `"prompt"` uses prompt engineering, `"function_call"` uses tool/function calling |
| `instruction` | `string` | No | Additional instruction to guide the extraction |
| `memory` | `Memory` | No | Conversation memory settings |
| `vision` | `object` | No | Vision settings for multimodal input |

## Full Schema

### ModelConfig
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `provider` | `string` | Yes | Model provider identifier, e.g. `"langgenius/openai/openai"` |
| `name` | `string` | Yes | Model name, e.g. `"gpt-4o-mini"` |
| `mode` | `string` | Yes | Model mode, typically `"chat"` |
| `completion_params` | `Record<string, any>` | No | Model parameters such as `temperature` |

### Param (parameter definition)
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | `string` | Yes | Variable name for the extracted parameter |
| `type` | `ParamType` | Yes | Data type of the parameter (see enum below) |
| `description` | `string` | Yes | Description guiding the LLM on what to extract |
| `required` | `boolean` | No | Whether this parameter must be extracted |
| `options` | `string[]` | No | Valid options list; used when `type` is `"select"` |

### ParamType enum
| Value | Description |
|-------|-------------|
| `"string"` | Text string |
| `"number"` | Numeric value |
| `"boolean"` | Boolean true/false |
| `"select"` | One of a set of predefined options (use `options` field) |
| `"array[string]"` | Array of strings |
| `"array[number]"` | Array of numbers |
| `"array[object]"` | Array of objects |
| `"array[boolean]"` | Array of booleans |

### ReasoningModeType enum
| Value | Description |
|-------|-------------|
| `"prompt"` | Uses prompt-based extraction (works with all models) |
| `"function_call"` | Uses function/tool calling API (requires model support) |

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
- `query` references a variable from an upstream node, typically `["sys", "query"]` for the user input or any string variable.

**Outputs:**
- Each entry in `parameters` becomes an output variable accessible by downstream nodes via `[node_id, parameter_name]`.
- For example, a parameter with `name: "location"` is referenced as `["parameter-extractor-1", "location"]`.

## Example Snippet
```yaml
nodes:
  - data:
      type: parameter-extractor
      title: Extract Booking Details
      query:
        - sys
        - query
      model:
        provider: langgenius/openai/openai
        name: gpt-4o-mini
        mode: chat
        completion_params:
          temperature: 0.7
      reasoning_mode: function_call
      parameters:
        - name: location
          type: string
          description: "The city or location for the booking"
          required: true
        - name: check_in_date
          type: string
          description: "Check-in date in YYYY-MM-DD format"
          required: true
        - name: guests
          type: number
          description: "Number of guests"
          required: false
        - name: room_type
          type: select
          description: "Type of room requested"
          required: false
          options:
            - single
            - double
            - suite
      instruction: "Extract hotel booking details from the user's message."
      vision:
        enabled: false
    id: parameter-extractor-1
```
