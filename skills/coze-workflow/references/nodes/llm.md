## coze.cn Cloud YAML Format

YAML type: `llm` | version: `"3"` | **All 14 llmParam fields required**

Key fields in `parameters`:
- `fcParamVar.knowledgeFCParam: {}`
- `llmParam[]`: apiMode, maxTokens, spCurrentTime, spAntiLeak, responseFormat, modelName, modelType, generationDiversity, parameters, prompt, enableChatHistory, chatHistoryRound, systemPrompt, stableSystemPrompt, canContinue, loopPromptVersion, loopPromptName, loopPromptId
- `node_inputs[]`: `{name, input: {type, value: {path, ref_node}}}`
- `node_outputs`: `{output: {type: string, value: null}}`
- `settingOnError`: `{processType: 1, retryTimes: 0, switch: false, timeoutMs: 180000}`

See `examples/simple-chatbot.yaml` for complete template.

---

# LLM Node (type: "3")

## Purpose
Invokes a large language model with system/user prompts, optional chat history, tool calling (skills), and structured output support.

## Core Fields
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `inputs.llmParam` | `InputValueDTO[]` | Yes | Array of named LLM parameter entries (model config, prompts, etc.). Each item has `name` and `input.value.content`. |
| `inputs.inputParameters` | `InputValueDTO[]` | No | User-defined input variables that can be referenced in prompts via `{{variable_name}}`. |
| `inputs.fcParam` | `FCParam` | No | Function calling / skills configuration (bound workflows and plugins). |
| `inputs.batch` | `NodeBatch` | No | Batch mode configuration. Present when batch mode is enabled. |
| `outputs` | `VariableMetaDTO[]` | Yes | Output variable definitions. Default: `[{ name: "output", type: String }]`. |
| `nodeMeta` | `NodeMetaFE` | No | Frontend display metadata. |
| `version` | `string` | No | Node schema version. Current default: `"3"`. |

## Full Schema

### Frontend FormData (`nodes-v2/llm/types.ts`)
```typescript
enum BatchMode {
  Single = 'single',
  Batch = 'batch',
}

interface FormData {
  batchMode: BatchMode;
  visionParam?: InputValueVO[];
  model?: IModelValue;               // { modelType: number, modelName: string, ... }
  $$input_decorator$$: {
    inputParameters?: InputValueVO[];
    chatHistorySetting?: {
      enableChatHistory?: boolean;
      chatHistoryRound?: number;      // default: 3
    };
  };
  $$prompt_decorator$$: {
    prompt: string;                   // user prompt template
    systemPrompt: string;             // system prompt template
  };
  batch: BatchVO;
  fcParam?: BoundSkills;              // function calling / skills
  outputs: OutputValueVO[];
  settingOnError?: { ... };           // error handling configuration
}
```

### Backend DTO (submitted format from `formatOnSubmit`)
```typescript
{
  nodeMeta: NodeMetaFE;
  inputs: {
    inputParameters: InputValueDTO[];
    llmParam: InputValueDTO[];        // see llmParam entries below
    fcParam?: FCParam;
    batch?: { batchEnable: boolean; ... };
  };
  outputs: VariableMetaDTO[];
  version: "3";
}
```

### llmParam Entries
Each entry in `inputs.llmParam` is an `InputValueDTO` with structure:
```typescript
{ name: string, input: { type: "literal", value: { type: "literal", content: <value> } } }
```

| Param Name | Content Type | Description |
|------------|-------------|-------------|
| `modelType` | `string` (int64) | Model ID / type identifier |
| `modleName` | `string` | Model display name (note: typo "modleName" is in source) |
| `temperature` | `string` (float) | Sampling temperature |
| `maxTokens` | `string` (int) | Maximum output tokens |
| `topP` | `string` (float) | Top-p sampling parameter |
| `responseFormat` | `string` (int) | Output format: `0` = Text, `1` = Markdown, `2` = JSON |
| `prompt` | `string` | User prompt template |
| `systemPrompt` | `string` | System prompt template |
| `enableChatHistory` | `boolean` | Whether to include chat history (chatflow only) |
| `chatHistoryRound` | `string` (int) | Number of chat history rounds to include. Default: `3` |

### Backend Go Config (`llm/llm.go`)
```go
type Config struct {
    SystemPrompt                      string
    UserPrompt                        string
    OutputFormat                      Format    // 0=Text, 1=Markdown, 2=JSON
    LLMParams                         *vo.LLMParams
    FCParam                           *vo.FCParam
    BackupLLMParams                   *vo.LLMParams  // fallback model for error handling
    ChatHistorySetting                *vo.ChatHistorySetting
    AssociateStartNodeUserInputFields map[string]struct{}
}
```

### Backend LLMParams (`vo/modelmgr.go`)
```go
type LLMParams struct {
    ModelName         string         `json:"modelName"`
    ModelType         int64          `json:"modelType"`
    Prompt            string         `json:"prompt"`           // user prompt
    Temperature       *float64       `json:"temperature"`
    MaxTokens         int            `json:"maxTokens"`
    TopP              *float64       `json:"topP"`
    TopK              *int           `json:"topK"`
    EnableChatHistory bool           `json:"enableChatHistory"`
    SystemPrompt      string         `json:"systemPrompt"`
    ResponseFormat    ResponseFormat `json:"responseFormat"`   // 0=Text, 1=Markdown, 2=JSON
    ChatHistoryRound  int64          `json:"chatHistoryRound"`
}
```

### ResponseFormat Enum
| Value | Constant | Description |
|-------|----------|-------------|
| `0` | `ResponseFormatText` | Plain text output |
| `1` | `ResponseFormatMarkdown` | Markdown-formatted output |
| `2` | `ResponseFormatJSON` | JSON-structured output (adds JSON schema constraint to prompt) |

### Output Format Behavior
- **Text**: LLM responds freely; stream-capable.
- **Markdown**: Appends markdown formatting instructions to the prompt; stream-capable.
- **JSON**: Appends JSON schema derived from output variable definitions; disables streaming. If there is only one String output (optionally with `reasoning_content`), falls back to Text mode.

### Special Output Keys
| Key | Description |
|-----|-------------|
| `output` | Default output variable name |
| `reasoning_content` | Reserved key for chain-of-thought reasoning content from supported models |

### Chat History (`vo/canvas.go`)
```go
type ChatHistorySetting struct {
    EnableChatHistory bool  `json:"enableChatHistory,omitempty"`
    ChatHistoryRound  int64 `json:"chatHistoryRound,omitempty"`
}
```
- Only active in chatflow mode.
- History messages are inserted between system prompt and user prompt.

### Prompt Template Rendering
- Prompts can reference input variables using `{{variable_name}}` syntax.
- Supports multi-modal content: file-type variables (image, audio, video) are rendered as corresponding message parts when the model supports them.
- Variables referencing the start node's `user_input` field in chatflow mode are replaced with the actual user message (including multi-modal content).

## Node Registry Metadata
| Property | Value |
|----------|-------|
| `type` | `StandardNodeType.LLM` = `"3"` |
| `nodeDTOType` | `"3"` |
| `size` | `{ width: 360, height: 130.7 }` |
| `inputParametersPath` | `"/$$input_decorator$$/inputParameters"` |
| `batchPath` | `"/batch"` |
| Backend NodeType | `"LLM"` (ID: 3) |

## Variable Reference Rules
- Input variables are defined in `inputs.inputParameters` and referenced in prompts as `{{variable_name}}`.
- Each input variable maps to an upstream node output via a reference expression.
- Output variables are defined in `outputs` and referenced by downstream nodes as `{{node_id.output_name}}`.
- The default output is a single String variable named `output`.

## Example Snippet
```json
{
  "id": "node_abc",
  "type": "3",
  "data": {
    "nodeMeta": {
      "title": "LLM"
    },
    "inputs": {
      "inputParameters": [
        {
          "name": "input",
          "input": {
            "type": "ref",
            "content": {
              "sourceNodeId": "0",
              "outputKey": "user_input"
            }
          }
        }
      ],
      "llmParam": [
        { "name": "modelType", "input": { "type": "literal", "value": { "type": "literal", "content": "4" } } },
        { "name": "modleName", "input": { "type": "literal", "value": { "type": "literal", "content": "GPT-4o" } } },
        { "name": "temperature", "input": { "type": "literal", "value": { "type": "literal", "content": "0.7" } } },
        { "name": "maxTokens", "input": { "type": "literal", "value": { "type": "literal", "content": "4096" } } },
        { "name": "responseFormat", "input": { "type": "literal", "value": { "type": "literal", "content": "0" } } },
        { "name": "prompt", "input": { "type": "literal", "value": { "type": "literal", "content": "Answer the question: {{input}}" } } },
        { "name": "systemPrompt", "input": { "type": "literal", "value": { "type": "literal", "content": "You are a helpful assistant." } } },
        { "name": "enableChatHistory", "input": { "type": "literal", "value": { "type": "literal", "content": false } } },
        { "name": "chatHistoryRound", "input": { "type": "literal", "value": { "type": "literal", "content": "3" } } }
      ]
    },
    "outputs": [
      {
        "name": "output",
        "type": 1
      }
    ],
    "version": "3"
  }
}
```
