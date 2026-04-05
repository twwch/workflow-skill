# Intent Detection Node

## Purpose

Uses an LLM to classify user input into one of several predefined intent categories. Creates dynamic output ports for branching based on the detected intent. Supports two modes: **standard** (full LLM reasoning with JSON output including reason) and **minimal/fast** (outputs only a classification number). Node type ID: `22` (frontend) / `IntentDetector` (backend).

## Core Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `inputs.inputParameters` | `InputParam[]` | Yes | Input variables; must include a `query` parameter |
| `inputs.intents` | `Intent[]` | Yes | List of intent categories to classify against |
| `inputs.mode` | `"all"` \| `"top_speed"` | No | Classification mode. `"all"` = standard, `"top_speed"` = minimal/fast. Default: `"all"` (open-source), `"top_speed"` (new nodes in non-open-source) |
| `inputs.llmParam` | `IntentDetectorLLMParam` | Yes | LLM configuration including model, prompt, and parameters |
| `inputs.chatHistorySetting` | `ChatHistorySetting` | No | Conversation history settings |
| `outputs` | `Variable[]` | Yes | Output variables |

### Intent Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | `string` | Yes | Intent description text |

### LLM Config (`llmParam`)

| Field | Type | Description |
|-------|------|-------------|
| `modelType` | `number` | Model ID |
| `modelName` | `string` | Model display name |
| `temperature` | `number` | Sampling temperature |
| `topP` | `number` | Top-p sampling |
| `maxTokens` | `number` | Maximum output tokens |
| `responseFormat` | `string` | Response format |
| `systemPrompt` | `ValueExpression` | Custom system prompt template with `{{query}}` reference (standard mode only) |
| `enableChatHistory` | `boolean` | Whether to include conversation history |
| `chatHistoryRound` | `number` | Number of history rounds to include |

### Chat History Setting

| Field | Type | Description |
|-------|------|-------------|
| `enableChatHistory` | `boolean` | Enable conversation history context |
| `chatHistoryRound` | `number` | Number of past rounds to include |

### Output Variables

| Output Name | Type | Mode | Description |
|-------------|------|------|-------------|
| `classificationId` | `Integer` | Both | Intent index (1-based) matching the intents list, or `0` for "other/unmatched" |
| `reason` | `String` | Standard only | LLM's explanation for the classification |

## Full Schema

```jsonc
{
  "type": "22",
  "data": {
    "nodeMeta": { "title": "Intent Detection", "icon": "..." },
    "inputs": {
      "inputParameters": [
        {
          "name": "query",
          "input": { "type": "ref", "content": "", "value": { /* reference */ } }
        }
      ],
      "intents": [
        { "name": "Order inquiry" },
        { "name": "Technical support" },
        { "name": "Billing question" }
      ],
      "mode": "all",   // or "top_speed"
      "llmParam": {
        "modelType": 123,
        "modelName": "model-name",
        "temperature": 0.7,
        "topP": 0.9,
        "maxTokens": 4096,
        "prompt": {
          "type": "literal",
          "content": "{{query}}"
        },
        "systemPrompt": {
          "type": "literal",
          "content": ""   // Additional classification guidance (standard mode)
        },
        "enableChatHistory": false,
        "chatHistoryRound": 3
      },
      "chatHistorySetting": {
        "enableChatHistory": false,
        "chatHistoryRound": 3
      }
    },
    "outputs": [
      { "name": "classificationId", "type": "Integer" },
      { "name": "reason", "type": "String" }
    ]
  }
}
```

## Variable Reference Rules

- The `query` input parameter is required and provides the text to classify.
- In **standard mode**, the `systemPrompt` supports `{{query}}` template syntax and is injected as an "advance" section in the classification prompt.
- In **minimal/fast mode**, the system prompt is ignored; only the query is sent to the LLM.
- The `prompt` field in `llmParam` references `{{query}}` by default.

## Runtime Behavior

1. The node constructs a system prompt containing the intent classification list. Each intent is assigned a 1-based `classificationId`. ID `0` is reserved for "Other intentions" (no match).
2. **Standard mode**: LLM returns JSON with `classificationId` and `reason` fields. The custom `systemPrompt` is rendered and appended as additional classification guidance.
3. **Minimal/fast mode**: LLM returns only a number (the classificationId). No `reason` output is produced.
4. If `enableChatHistory` is true, conversation history (up to `chatHistoryRound` rounds) is prepended to the LLM context.

## Dynamic Ports

The node creates one output branch port per intent, plus a `default` port:
- `branch_0` through `branch_N-1`: One per intent in the `intents` array (ordered).
- `default`: Routes when `classificationId` is `0` (no match / "Other intentions").

The branching logic maps `classificationId - 1` to the branch index. A `classificationId` of `0` triggers the default port.

## Example JSON Snippet

```json
{
  "data": {
    "inputs": {
      "inputParameters": [
        {
          "name": "query",
          "input": {
            "type": "ref",
            "content": "{{start.user_input}}"
          }
        }
      ],
      "intents": [
        { "name": "Want to book a flight" },
        { "name": "Check booking status" },
        { "name": "Cancel reservation" }
      ],
      "mode": "all",
      "llmParam": {
        "modelType": 123,
        "modelName": "gpt-4",
        "temperature": 0.3,
        "topP": 0.9,
        "maxTokens": 512,
        "systemPrompt": { "type": "literal", "content": "" },
        "enableChatHistory": false,
        "chatHistoryRound": 3
      }
    },
    "outputs": [
      { "name": "classificationId", "type": "Integer" },
      { "name": "reason", "type": "String" }
    ]
  }
}
```
