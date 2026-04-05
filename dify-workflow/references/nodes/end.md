# End (`end`)

## Purpose

Terminal node of a Workflow-type application that declares which variables constitute the final output of the workflow run.

**Important**: The End node is used only in **Workflow** mode (not Chatflow). In Chatflow mode, use the Answer node instead to stream responses to the user.

## Core Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `outputs` | `Variable[]` | Yes | List of output variable mappings. Each entry maps a named output to a value selected from an upstream node. Must have at least one entry. |

## Full Schema

### Node Metadata

Source: `source/dify/web/app/components/workflow/nodes/end/default.ts`

```
type: BlockEnum.End           # "end"
sort: 2.1
isRequired: false             # not automatically required, but a workflow needs at least one
```

Unlike Start, the End node does not set `isSingleton`, meaning a workflow can have multiple End nodes (for different branches).

### EndNodeType

Source: `source/dify/web/app/components/workflow/nodes/end/types.ts`

```typescript
type EndNodeType = CommonNodeType & {
  outputs: Variable[]
}
```

Extends `CommonNodeType` which provides shared fields inherited by every node:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | `string` | Yes | Display name shown on the canvas. |
| `desc` | `string` | Yes | Description text (can be empty string). |
| `type` | `BlockEnum` | Yes | Must be `"end"`. |
| `width` | `number` | No | Canvas width in pixels. |
| `height` | `number` | No | Canvas height in pixels. |
| `position` | `{ x: number, y: number }` | No | Position on the canvas. |
| `selected` | `boolean` | No | Whether the node is currently selected in the UI. |
| `error_strategy` | `ErrorHandleTypeEnum` | No | Error handling strategy. |
| `retry_config` | `WorkflowRetryConfig` | No | Retry configuration. |
| `default_value` | `DefaultValueForm[]` | No | Default value forms for error handling. |

### Variable

Source: `source/dify/web/app/components/workflow/types.ts`

Each entry in the `outputs` array is a `Variable`:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `variable` | `string` | Yes | Output variable name. This is the key that appears in the workflow run result. Must not be empty. |
| `value_selector` | `ValueSelector` | Yes | Reference to an upstream node's output. Array of strings: `[nodeId, ...keyPath]`. Must have at least one element. |
| `label` | `string \| object` | No | Display label. Can be a string or `{ nodeType: BlockEnum, nodeName: string, variable: string }`. |
| `value_type` | `VarType` | No | Expected data type of the referenced variable. |
| `variable_type` | `VarKindType` | No | Variable kind classification. |
| `value` | `string` | No | Static value (rarely used in End node context). |
| `options` | `string[]` | No | Allowed values for constrained fields. |
| `required` | `boolean` | No | Whether this output is required. |
| `isParagraph` | `boolean` | No | Whether the value is multi-line text. |

### ValueSelector

Source: `source/dify/web/app/components/workflow/types.ts`

```typescript
type ValueSelector = string[]  // [nodeId, key | obj key path]
```

A `ValueSelector` is an array of strings that forms a path to a variable:
- First element: the source node's ID
- Subsequent elements: the key path within that node's output

Examples:
- `["node-llm-001", "text"]` -- references the `text` output of an LLM node
- `["node-start-001", "user_name"]` -- references a Start node input variable
- `["sys", "user_id"]` -- references a system variable

### VarType Enum

Source: `source/dify/web/app/components/workflow/types.ts`

Possible values for `value_type`:

| Value | Description |
|-------|-------------|
| `string` | String value. |
| `number` | Floating-point number. |
| `integer` | Integer number. |
| `secret` | Secret/sensitive string. |
| `boolean` | Boolean value. |
| `object` | JSON object. |
| `file` | Single file. |
| `array` | Generic array. |
| `array[string]` | Array of strings. |
| `array[number]` | Array of numbers. |
| `array[object]` | Array of objects. |
| `array[boolean]` | Array of booleans. |
| `array[file]` | Array of files. |
| `any` | Any type. |
| `array[any]` | Array of any type. |

## Variable Reference Rules

### Input Variables

The End node **consumes** variables from upstream nodes. It does not produce output variables for other nodes (since it is terminal).

Each output entry uses `value_selector` to reference a variable from a preceding node:

```
value_selector: ["<source_node_id>", "<variable_name>"]
```

### Output Mapping

The `variable` field in each output entry determines the key name in the workflow's final result object. When the workflow completes, the API response contains:

```json
{
  "outputs": {
    "<variable_name_1>": "<resolved_value_1>",
    "<variable_name_2>": "<resolved_value_2>"
  }
}
```

### Referencing Different Node Types

The `value_selector` can point to outputs from any upstream node:

- **Start node variables**: `["node-start-001", "user_name"]`
- **LLM node text output**: `["node-llm-001", "text"]`
- **Code node outputs**: `["node-code-001", "result"]`
- **HTTP Request output**: `["node-http-001", "body"]`
- **System variables**: `["sys", "user_id"]`

## Validation Rules

Source: `source/dify/web/app/components/workflow/nodes/end/default.ts`

The End node validation checks:

1. The `outputs` array must not be empty. At least one output variable is required.
2. Each output must have:
   - A non-empty `variable` name (after trimming whitespace).
   - A non-empty `value_selector` array (at least one element).
3. If any output fails these checks, validation returns an error message.

## Example Snippet

### Minimal End Node

```yaml
nodes:
  - data:
      type: end
      title: End
      desc: ''
      outputs:
        - variable: result
          value_selector:
            - node-llm-001
            - text
    id: node-end-001
    position:
      x: 800
      y: 282
```

### End Node with Multiple Outputs

```yaml
nodes:
  - data:
      type: end
      title: End
      desc: ''
      outputs:
        - variable: summary
          value_selector:
            - node-llm-001
            - text
        - variable: classification
          value_selector:
            - node-classifier-001
            - class_name
        - variable: original_input
          value_selector:
            - node-start-001
            - user_query
    id: node-end-001
    position:
      x: 1200
      y: 282
```

### End Node Referencing System Variables

```yaml
nodes:
  - data:
      type: end
      title: End
      desc: ''
      outputs:
        - variable: response
          value_selector:
            - node-llm-001
            - text
        - variable: run_user
          value_selector:
            - sys
            - user_id
    id: node-end-001
    position:
      x: 800
      y: 282
```

### Connecting to End Node (Edge)

The End node must be connected from at least one upstream node:

```yaml
edges:
  - source: node-llm-001
    sourceHandle: source
    target: node-end-001
    targetHandle: target
    data:
      sourceType: llm
      targetType: end
```

## Source Files

- Type definition: `source/dify/web/app/components/workflow/nodes/end/types.ts`
- Default config: `source/dify/web/app/components/workflow/nodes/end/default.ts`
- Panel UI: `source/dify/web/app/components/workflow/nodes/end/panel.tsx`
- Config logic: `source/dify/web/app/components/workflow/nodes/end/use-config.ts`
- Node rendering: `source/dify/web/app/components/workflow/nodes/end/node.tsx`
- Shared types: `source/dify/web/app/components/workflow/types.ts`
