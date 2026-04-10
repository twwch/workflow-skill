## coze.cn Cloud YAML Format

YAML type: `question` | Status: 未验证

> This node type's cloud YAML format is based on source code analysis.
> For verified format, export a real workflow from coze.cn containing this node.

```yaml
    - id: "200001"
      type: question
      title: 问答暂停
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

# Question Node

## Purpose

Interactive node that pauses workflow execution to ask the user a question, then processes the response. Supports two answer modes: free-text input or multiple-choice options. When using options, creates dynamic output ports for branching. Can optionally use an LLM to extract structured data from the user's response. Node type ID: `18` (frontend) / `QuestionAnswer` (backend).

## Core Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `inputs.answer_type` | `"text"` \| `"option"` | Yes | Answer mode. Default: `"text"` |
| `inputs.question` | `string` | Yes | Question template with `{{variable}}` references |
| `inputs.inputParameters` | `InputParam[]` | No | Input variables for template rendering |
| `inputs.llmParam` | `LLMConfig` | Conditional | LLM config; required for option intent detection and text extraction |
| `inputs.option_type` | `"static"` \| `"dynamic"` | For options | How options are sourced |
| `inputs.options` | `Option[]` | For static options | List of fixed option objects with `name` field |
| `inputs.dynamic_option` | `BlockInput` | For dynamic options | Reference to an array variable providing option strings |
| `inputs.extra_output` | `boolean` | For text mode | Whether to extract structured output from the answer |
| `inputs.limit` | `integer` | For extraction | Max follow-up rounds for extracting required fields. Default: `3` |
| `outputs` | `Variable[]` | Yes | Output variables (varies by mode) |

### LLM Config (`llmParam`)

| Field | Type | Description |
|-------|------|-------------|
| `modelType` | `number` | Model ID |
| `modelName` | `string` | Model display name |
| `temperature` | `number` | Sampling temperature |
| `topP` | `number` | Top-p sampling |
| `maxTokens` | `number` | Maximum output tokens |
| `responseFormat` | `string` | Response format |
| `systemPrompt` | `string` | Custom system prompt for extraction persona |

### Output Variables by Mode

| Mode | Output Name | Type | Description |
|------|-------------|------|-------------|
| text (basic) | `USER_RESPONSE` | `String` | The user's raw text response |
| text (extract) | `USER_RESPONSE` | `String` | The user's raw text response |
| text (extract) | (custom fields) | varies | Extracted structured fields defined in outputs |
| option | `optionId` | `String` | Alphabetic ID of selected option (A, B, C...) or `"other"` |
| option | `optionContent` | `String` | Content text of selected option or the raw answer if "other" |

## Full Schema

```jsonc
{
  "type": "18",
  "data": {
    "nodeMeta": { "title": "Question", "icon": "..." },
    "inputs": {
      "answer_type": "text",       // or "option"
      "question": "What is your name?",
      "inputParameters": [],
      "llmParam": {
        "modelType": 123,
        "modelName": "model-name",
        "temperature": 0.7,
        "topP": 0.9,
        "maxTokens": 4096,
        "systemPrompt": ""
      },
      // Text mode with extraction:
      "extra_output": true,
      "limit": 3,

      // Option mode:
      "option_type": "static",     // or "dynamic"
      "options": [
        { "name": "Option A" },
        { "name": "Option B" }
      ],
      "dynamic_option": null       // or BlockInput reference for dynamic
    },
    "outputs": [
      { "name": "USER_RESPONSE", "type": "String", "required": true },
      // Additional outputs for extraction mode:
      { "name": "fieldName", "type": "String", "required": true }
    ]
  }
}
```

## Variable Reference Rules

- The `question` field supports `{{variableName}}` template syntax, resolved against `inputParameters` at runtime.
- For **static options**: each `options[].name` also supports `{{variableName}}` template rendering.
- For **dynamic options**: `dynamic_option` is a `BlockInput` reference to an array of strings from another node.
- In **extraction mode**: the `systemPrompt` in `llmParam` supports `{{variableName}}` template syntax for the extraction persona prompt.

## Runtime Behavior

1. **First execution**: Renders the question template, formats options if applicable, then **interrupts** the workflow with an `InterruptEvent` of type `question`.
2. **Resumed with user response**: Processes the answer based on mode:
   - **Text (basic)**: Returns `USER_RESPONSE` directly.
   - **Text (extract)**: Uses LLM with a structured extraction prompt to pull fields from the answer. If required fields are missing, generates follow-up questions (up to `limit` rounds).
   - **Option**: Matches user response against choices (exact match first, then LLM intent detection). Returns `optionId` (alphabetic: A=0, B=1, etc.) and `optionContent`. Unmatched responses return `optionId: "other"`.
3. **Branching (option mode)**: The node creates dynamic output ports. Each option maps to a branch port (`branch_0`, `branch_1`, etc.). Unmatched answers route to the default port.

## Dynamic Ports

When `answer_type` is `"option"`:
- **Static options**: One branch port per option, plus a `default` port for "other".
- **Dynamic options**: One branch port (`branch_0`) for matched options, plus a `default` port for "other".

## Example JSON Snippet

### Text Mode with Extraction
```json
{
  "data": {
    "inputs": {
      "answer_type": "text",
      "question": "Please provide your shipping address and phone number.",
      "inputParameters": [],
      "extra_output": true,
      "limit": 3,
      "llmParam": {
        "modelType": 123,
        "temperature": 0.7,
        "topP": 0.9,
        "maxTokens": 4096,
        "systemPrompt": "Extract the address and phone from the user's response."
      }
    },
    "outputs": [
      { "name": "USER_RESPONSE", "type": "String", "required": true },
      { "name": "address", "type": "String", "required": true },
      { "name": "phone", "type": "String", "required": true }
    ]
  }
}
```

### Option Mode (Static)
```json
{
  "data": {
    "inputs": {
      "answer_type": "option",
      "question": "Which plan do you prefer?",
      "option_type": "static",
      "options": [
        { "name": "Basic Plan" },
        { "name": "Pro Plan" },
        { "name": "Enterprise Plan" }
      ],
      "inputParameters": [],
      "llmParam": {
        "modelType": 123,
        "temperature": 0.3,
        "topP": 0.9,
        "maxTokens": 512
      }
    },
    "outputs": [
      { "name": "USER_RESPONSE", "type": "String", "required": true },
      { "name": "optionId", "type": "String", "required": false },
      { "name": "optionContent", "type": "String", "required": false }
    ]
  }
}
```
