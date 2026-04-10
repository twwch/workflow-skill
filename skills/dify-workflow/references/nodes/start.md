# Start (`start`)

## Purpose

Entry point of a workflow that defines user-facing input variables and provides built-in system variables to downstream nodes.

## Core Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `variables` | `InputVar[]` | No | List of user-input variables presented as a form when the workflow runs. Defaults to `[]`. |

## Full Schema

### Node Metadata

Source: `source/dify/web/app/components/workflow/nodes/start/default.ts`

```
type: BlockEnum.Start        # "start"
sort: 0.1
isStart: true
isRequired: false
isSingleton: true             # only one Start node per workflow
isTypeFixed: false            # supports node type change for start node (user input)
helpLinkUri: "user-input"
```

### StartNodeType

Source: `source/dify/web/app/components/workflow/nodes/start/types.ts`

```typescript
type StartNodeType = CommonNodeType & {
  variables: InputVar[]
}
```

Extends `CommonNodeType` which provides shared fields inherited by every node:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | `string` | Yes | Display name shown on the canvas. |
| `desc` | `string` | Yes | Description text (can be empty string). |
| `type` | `BlockEnum` | Yes | Must be `"start"`. |
| `width` | `number` | No | Canvas width in pixels. |
| `height` | `number` | No | Canvas height in pixels. |
| `position` | `{ x: number, y: number }` | No | Position on the canvas. Default initial position is `{ x: 80, y: 282 }`. |
| `selected` | `boolean` | No | Whether the node is currently selected in the UI. |
| `error_strategy` | `ErrorHandleTypeEnum` | No | Error handling strategy. |
| `retry_config` | `WorkflowRetryConfig` | No | Retry configuration. |
| `default_value` | `DefaultValueForm[]` | No | Default value forms for error handling. |

### InputVar

Source: `source/dify/web/app/components/workflow/types.ts`

Each entry in the `variables` array is an `InputVar`:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `variable` | `string` | Yes | Variable key name (must be unique within the node). Used to reference this variable downstream as `{{#start_node_id.variable#}}`. |
| `label` | `string \| object` | Yes | Human-readable display label. Can be a string or `{ nodeType, nodeName, variable, isChatVar? }`. |
| `type` | `InputVarType` | Yes | The input widget type. See enum values below. |
| `required` | `boolean` | Yes | Whether the user must provide a value. |
| `max_length` | `number` | No | Maximum character length (for text inputs). |
| `default` | `string \| number` | No | Default value pre-filled in the form. |
| `hint` | `string` | No | Help text displayed to the user. |
| `options` | `string[]` | No | Allowed values when `type` is `"select"`. |
| `placeholder` | `string` | No | Placeholder text for the input field. |
| `unit` | `string` | No | Unit label displayed next to number inputs. |
| `value_selector` | `ValueSelector` | No | Reference to another variable (array of strings: `[nodeId, ...keyPath]`). |
| `json_schema` | `string \| Record<string, any>` | No | JSON Schema definition when `type` is `"json_object"`. |
| `hide` | `boolean` | No | Whether to hide this variable from the form UI. |
| `isFileItem` | `boolean` | No | Internal flag for file-type variables. |
| `getVarValueFromDependent` | `boolean` | No | Internal flag for dependent variable resolution. |

**File upload fields** (merged from `UploadFileSetting`, applicable when type is `files` / `file` / `file-list`):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `allowed_file_upload_methods` | `TransferMethod[]` | No | How files can be provided (e.g., `"remote_url"`, `"local_file"`). |
| `allowed_upload_methods` | `TransferMethod[]` | No | Alternative field name for allowed methods. |
| `allowed_file_types` | `SupportUploadFileTypes[]` | No | File categories: `"image"`, `"document"`, `"audio"`, `"video"`, `"custom"`. |
| `allowed_file_extensions` | `string[]` | No | Specific file extensions (e.g., `[".pdf", ".txt"]`). |
| `max_length` | `number` | No | Maximum file size. |
| `number_limits` | `number` | No | Maximum number of files. |

### InputVarType Enum

Source: `source/dify/web/app/components/workflow/types.ts`

| Value | DSL Key | Description |
|-------|---------|-------------|
| `text-input` | `"text-input"` | Single-line text input. |
| `paragraph` | `"paragraph"` | Multi-line text input. |
| `select` | `"select"` | Dropdown select. Requires `options` array. |
| `number` | `"number"` | Numeric input. |
| `url` | `"url"` | URL input with validation. |
| `files` | `"files"` | Multiple file upload (legacy). |
| `json` | `"json"` | JSON input (object or array). |
| `json_object` | `"json_object"` | JSON object input with optional schema validation. |
| `file` | `"file"` | Single file upload. |
| `file-list` | `"file-list"` | Multiple file upload. |
| `checkbox` | `"checkbox"` | Boolean checkbox input. |
| `contexts` | `"contexts"` | Knowledge retrieval context (internal use). |
| `iterator` | `"iterator"` | Iteration input (internal use). |
| `loop` | `"loop"` | Loop input (internal use). |

## Variable Reference Rules

### Output Variables

The Start node produces output variables that downstream nodes can reference:

1. **User-defined variables**: Each entry in `variables` becomes an output accessible via `{{#<start_node_id>.<variable_name>#}}`.

2. **Built-in variables** (always available on the Start node):
   - `sys.query` (type: `string`) -- The user's input query text. **Only available in chat mode (Chatflow).**
   - `sys.files` (type: `array[file]`) -- Files uploaded by the user. Available in both Chatflow and Workflow modes.

### System Variables (Global)

These are available to all nodes, not just Start. Referenced as `{{#sys.<name>#}}`:

| Variable | Type | Availability | Description |
|----------|------|-------------|-------------|
| `sys.user_id` | `string` | Always | ID of the current user. |
| `sys.app_id` | `string` | Always | ID of the current application. |
| `sys.workflow_id` | `string` | Always | ID of the current workflow. |
| `sys.workflow_run_id` | `string` | Always | ID of the current workflow run. |
| `sys.dialogue_count` | `number` | Chat mode only | Number of dialogue turns in the conversation. |
| `sys.conversation_id` | `string` | Chat mode only | ID of the current conversation. |
| `sys.timestamp` | `number` | Workflow mode only | Current Unix timestamp. |

### Input Variable Format

Variables from the Start node are referenced by other nodes using the value selector format:

```
["<start_node_id>", "<variable_name>"]
```

In template strings, the syntax is:

```
{{#<start_node_id>.<variable_name>#}}
```

## Validation Rules

Source: `source/dify/web/app/components/workflow/nodes/start/default.ts`

- The Start node always passes validation (`isValid: true`). Variables are optional.
- Variable names must be unique within the node (enforced by `hasDuplicateStr` check).
- Variable labels must also be unique (enforced by the same check).

Source: `source/dify/web/app/components/workflow/nodes/start/use-config.ts`

## Example Snippet

### Minimal Start Node (No User Inputs)

```yaml
nodes:
  - data:
      type: start
      title: Start
      desc: ''
      variables: []
    id: node-start-001
    position:
      x: 80
      y: 282
```

### Start Node with Text and Select Inputs

```yaml
nodes:
  - data:
      type: start
      title: Start
      desc: ''
      variables:
        - variable: user_name
          label: User Name
          type: text-input
          required: true
          max_length: 100
          default: ''
          placeholder: Enter your name
        - variable: language
          label: Language
          type: select
          required: true
          options:
            - English
            - Chinese
            - Spanish
          default: English
        - variable: age
          label: Age
          type: number
          required: false
        - variable: query_text
          label: Query
          type: paragraph
          required: true
          max_length: 2000
    id: node-start-001
    position:
      x: 80
      y: 282
```

### Start Node with File Upload

```yaml
nodes:
  - data:
      type: start
      title: Start
      desc: ''
      variables:
        - variable: uploaded_doc
          label: Document
          type: file-list
          required: true
          allowed_file_types:
            - document
          allowed_file_extensions:
            - .pdf
            - .txt
            - .docx
          allowed_file_upload_methods:
            - local_file
          number_limits: 5
    id: node-start-001
    position:
      x: 80
      y: 282
```

## Source Files

- Type definition: `source/dify/web/app/components/workflow/nodes/start/types.ts`
- Default config: `source/dify/web/app/components/workflow/nodes/start/default.ts`
- Panel UI: `source/dify/web/app/components/workflow/nodes/start/panel.tsx`
- Config logic: `source/dify/web/app/components/workflow/nodes/start/use-config.ts`
- Shared types: `source/dify/web/app/components/workflow/types.ts`
- System variables: `source/dify/web/app/components/workflow/constants.ts`
