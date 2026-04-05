# Answer (`answer`)

## Purpose

Streams a text response to the user in a Chatflow application, supporting inline variable interpolation from upstream nodes.

**Important**: The Answer node is used only in **Chatflow** mode (not Workflow). In Workflow mode, use the End node instead to declare structured outputs.

## Core Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `answer` | `string` | Yes | The response template text. Supports variable interpolation using `{{#nodeId.variableName#}}` syntax. Must not be empty. |
| `variables` | `Variable[]` | No | List of variable references used within the `answer` template. Defaults to `[]`. Automatically managed by the editor UI. |

## Full Schema

### Node Metadata

Source: `source/dify/web/app/components/workflow/nodes/answer/default.ts`

```
type: BlockEnum.Answer        # "answer"
sort: 2.1
isRequired: true              # required for Chatflow applications
```

Unlike Start and End, the Answer node has `isRequired: true`, meaning a Chatflow must contain at least one Answer node. A workflow can contain multiple Answer nodes on different branches.

### AnswerNodeType

Source: `source/dify/web/app/components/workflow/nodes/answer/types.ts`

```typescript
type AnswerNodeType = CommonNodeType & {
  variables: Variable[]
  answer: string
}
```

Extends `CommonNodeType` which provides shared fields inherited by every node:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | `string` | Yes | Display name shown on the canvas. |
| `desc` | `string` | Yes | Description text (can be empty string). |
| `type` | `BlockEnum` | Yes | Must be `"answer"`. |
| `width` | `number` | No | Canvas width in pixels. |
| `height` | `number` | No | Canvas height in pixels. |
| `position` | `{ x: number, y: number }` | No | Position on the canvas. |
| `selected` | `boolean` | No | Whether the node is currently selected in the UI. |
| `error_strategy` | `ErrorHandleTypeEnum` | No | Error handling strategy. |
| `retry_config` | `WorkflowRetryConfig` | No | Retry configuration. |
| `default_value` | `DefaultValueForm[]` | No | Default value forms for error handling. |

### Variable (in `variables` array)

Source: `source/dify/web/app/components/workflow/types.ts`

Each entry in the `variables` array maps a placeholder in the `answer` template to an upstream node output:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `variable` | `string` | Yes | The variable reference key as used in the answer template. |
| `value_selector` | `ValueSelector` | Yes | Path to the source variable: `[nodeId, ...keyPath]`. |
| `label` | `string \| object` | No | Display label. Can be a string or `{ nodeType: BlockEnum, nodeName: string, variable: string }`. |
| `value_type` | `VarType` | No | Expected data type of the referenced variable. |
| `variable_type` | `VarKindType` | No | Variable kind classification. |
| `value` | `string` | No | Static value (rarely used). |
| `options` | `string[]` | No | Allowed values for constrained fields. |
| `required` | `boolean` | No | Whether this variable is required. |
| `isParagraph` | `boolean` | No | Whether the value is multi-line text. |

### ValueSelector

```typescript
type ValueSelector = string[]  // [nodeId, key | obj key path]
```

### Variable Filtering

Source: `source/dify/web/app/components/workflow/nodes/answer/use-config.ts`

The Answer node filters out variables of type `array[object]` (`VarType.arrayObject`). All other variable types are supported in the answer template, including:
- `string`, `number`, `integer`, `boolean`
- `object`, `file`
- `array`, `array[string]`, `array[number]`, `array[boolean]`, `array[file]`
- `any`, `array[any]`

## Variable Reference Rules

### Answer Template Syntax

The `answer` field uses Dify's variable interpolation syntax:

```
{{#<node_id>.<variable_name>#}}
```

Examples:
```
Here is the summary: {{#node-llm-001.text#}}

The user asked: {{#node-start-001.query#}}
```

Variables are resolved at runtime and their values are inserted into the streamed response.

### Variables Array Relationship

The `variables` array must contain an entry for every variable reference used in the `answer` template. The editor UI manages this automatically, but when constructing DSL manually, ensure consistency:

- Every `{{#nodeId.varName#}}` in `answer` must have a corresponding entry in `variables` with a matching `value_selector`.
- The `variable` field in each entry typically matches the full reference path (e.g., `node-llm-001.text`).

### Available Variable Sources

The Answer node can reference outputs from any upstream node in the same branch:

- **Start node variables**: `{{#node-start-001.user_name#}}`
- **LLM node text**: `{{#node-llm-001.text#}}`
- **Code node outputs**: `{{#node-code-001.result#}}`
- **System variables**: `{{#sys.user_id#}}`
- **Environment variables**: accessible via the `env` prefix
- **Conversation variables**: accessible via the `conversation` prefix

### Input vs Output

- **Input**: The Answer node consumes variables from upstream nodes via its `answer` template.
- **Output**: The Answer node does not produce output variables for downstream nodes. It streams its resolved text directly to the user. However, other nodes can follow an Answer node in the graph -- the answer is streamed as a side effect, not a terminal action.

## Validation Rules

Source: `source/dify/web/app/components/workflow/nodes/answer/default.ts`

The Answer node validation checks:

1. The `answer` field must not be empty. If it is empty, validation fails with a "field required" error.
2. There is no validation on the `variables` array itself -- only the `answer` text is checked.

## Example Snippet

### Minimal Answer Node

```yaml
nodes:
  - data:
      type: answer
      title: Answer
      desc: ''
      answer: '{{#node-llm-001.text#}}'
      variables:
        - variable: node-llm-001.text
          value_selector:
            - node-llm-001
            - text
    id: node-answer-001
    position:
      x: 800
      y: 282
```

### Answer Node with Mixed Text and Variables

```yaml
nodes:
  - data:
      type: answer
      title: Answer
      desc: ''
      answer: >-
        Hello {{#node-start-001.user_name#}}!

        Based on your question, here is my analysis:

        {{#node-llm-001.text#}}

        ---
        Generated for conversation {{#sys.conversation_id#}}
      variables:
        - variable: node-start-001.user_name
          value_selector:
            - node-start-001
            - user_name
        - variable: node-llm-001.text
          value_selector:
            - node-llm-001
            - text
        - variable: sys.conversation_id
          value_selector:
            - sys
            - conversation_id
    id: node-answer-001
    position:
      x: 800
      y: 282
```

### Answer Node with Plain Text (No Variables)

```yaml
nodes:
  - data:
      type: answer
      title: Answer
      desc: ''
      answer: 'Thank you for your question. I will process it now.'
      variables: []
    id: node-answer-001
    position:
      x: 800
      y: 282
```

### Connecting to Answer Node (Edge)

```yaml
edges:
  - source: node-llm-001
    sourceHandle: source
    target: node-answer-001
    targetHandle: target
    data:
      sourceType: llm
      targetType: answer
```

## Multiple Answer Nodes

Unlike the Start node (which is a singleton), a Chatflow can have multiple Answer nodes. This is useful for conditional responses:

```yaml
# Example: different answers on different branches of an if-else
nodes:
  - data:
      type: answer
      title: Positive Response
      desc: ''
      answer: 'Great news! {{#node-llm-positive.text#}}'
      variables:
        - variable: node-llm-positive.text
          value_selector:
            - node-llm-positive
            - text
    id: node-answer-positive
    position:
      x: 1200
      y: 100

  - data:
      type: answer
      title: Negative Response
      desc: ''
      answer: 'I apologize, but {{#node-llm-negative.text#}}'
      variables:
        - variable: node-llm-negative.text
          value_selector:
            - node-llm-negative
            - text
    id: node-answer-negative
    position:
      x: 1200
      y: 500
```

## Source Files

- Type definition: `source/dify/web/app/components/workflow/nodes/answer/types.ts`
- Default config: `source/dify/web/app/components/workflow/nodes/answer/default.ts`
- Panel UI: `source/dify/web/app/components/workflow/nodes/answer/panel.tsx`
- Config logic: `source/dify/web/app/components/workflow/nodes/answer/use-config.ts`
- Node rendering: `source/dify/web/app/components/workflow/nodes/answer/node.tsx`
- Shared types: `source/dify/web/app/components/workflow/types.ts`
