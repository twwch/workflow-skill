## coze.cn Cloud YAML Format

YAML type: `start` | Fixed ID: `"100001"`

```yaml
    - id: "100001"
      type: start
      title: 开始
      icon: https://lf3-static.bytednsdoc.com/obj/eden-cn/.../icon-Start-v2.jpg
      description: "工作流的起始节点，用于设定启动工作流需要的信息"
      position: { x: -1810, y: 0 }
      parameters:
        node_outputs:
            var_name:
                type: string    # or list, float, etc.
                required: true
                value: null
```

---

# Start Node (type: "1")

## Purpose
Entry point of a workflow; defines the input parameters (variables) that the workflow accepts.

## Core Fields
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `outputs` | `VariableMetaDTO[]` | Yes | Defines the workflow's input variables (confusingly named "outputs" because they are the outputs of the start node). Each item declares a variable name, type, and optional default value. |
| `inputs.auto_save_history` | `boolean` | No | Chatflow-only. Whether to automatically save conversation history. Defaults to `true` in chatflow mode. |
| `nodeMeta` | `NodeMetaFE` | No | Frontend display metadata (title, description, position). |
| `trigger_parameters` | `VariableMetaDTO[]` | No | Trigger parameter schemas saved for human review. Populated on submit from the outputs + trigger form values. |

## Full Schema

### Frontend FormData (`start/types.ts`)
```typescript
type FormData = {
  outputs: Array<ViewVariableMeta & { isPreset?: boolean; enabled?: boolean }>;
  inputs?: {
    auto_save_history: boolean;
  };
  triggerTabName?: string;   // trigger tab selection
} & Pick<BaseNodeDataDTO, 'nodeMeta'>;
```

### Backend DTO (`NodeDataDTO` in `start/types.ts`)
```typescript
type NodeDataDTO = {
  trigger_parameters?: VariableMetaDTO[];
  inputs?: {
    auto_save_history: boolean;
  };
} & Pick<BaseNodeDataDTO, 'outputs' | 'nodeMeta'>;
```

### Backend Go (`entry/entry.go`)
- **Config**: `{ DefaultValues map[string]any }` -- populated from output variables that have a `defaultValue`.
- **NodeSchema**: type = `"Entry"`, key must be the fixed `entity.EntryNodeKey`.
- On `Invoke`, merges caller-provided inputs with default values. For empty strings, empty arrays, and empty objects, falls back to the default.

### Output Variable Definition (each item in `outputs`)
| Field | Type | Description |
|-------|------|-------------|
| `name` | `string` | Variable name |
| `type` | `ViewVariableType` (enum int) | Variable type: String(1), Integer(2), Boolean(3), Number(4), Object(6), ArrayString(99), ArrayObject(103), etc. |
| `required` | `boolean` | Whether the variable is required |
| `defaultValue` | `any` | Default value when input is empty |
| `description` | `string` | Variable description |
| `children` | `VariableMetaDTO[]` | Sub-fields for Object/ArrayObject types |

### Default Outputs (from `start/constants.ts`)
When used in chatflow scenario, the default outputs include:
```typescript
[
  {
    name: 'outputList',
    type: ViewVariableType.ArrayObject,  // 103
    children: [
      { name: 'id', type: ViewVariableType.String },       // 1
      { name: 'content', type: ViewVariableType.String },   // 1
    ],
  },
]
```

## Node Registry Metadata
| Property | Value |
|----------|-------|
| `type` | `StandardNodeType.Start` = `"1"` |
| `nodeDTOType` | `"1"` |
| `isStart` | `true` |
| `deleteDisable` | `true` |
| `copyDisable` | `true` |
| `headerReadonly` | `true` |
| `size` | `{ width: 360, height: 78.7 }` |
| `defaultPorts` | `[{ type: 'output' }]` (output only, no input port) |
| Backend NodeType | `"Entry"` (ID: 1) |

## Variable Reference Rules
- Start node outputs are referenced by downstream nodes as: `{{start_node_id.variable_name}}`
- The start node ID is fixed as `entity.EntryNodeKey` in the backend.
- In chatflow mode, preset parameters (like `BOT_USER_INPUT`) get `isPreset: true` and `required: false`.

## Example Snippet
```json
{
  "id": "0",
  "type": "1",
  "data": {
    "nodeMeta": {
      "title": "Start"
    },
    "outputs": [
      {
        "name": "user_input",
        "type": 1,
        "required": true,
        "description": "The user's input text"
      },
      {
        "name": "language",
        "type": 1,
        "required": false,
        "defaultValue": "en"
      }
    ],
    "inputs": {
      "auto_save_history": true
    }
  }
}
```
