## coze.cn Cloud YAML Format

YAML type: `subflow` | Status: 未验证

> This node type's cloud YAML format is based on source code analysis.
> For verified format, export a real workflow from coze.cn containing this node.

```yaml
    - id: "200001"
      type: subflow
      title: 子工作流
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

# Sub-Workflow Node

## Purpose

Executes another published workflow as a nested sub-workflow within the current workflow. Supports both invoke (non-streaming) and stream modes. Inputs and outputs are dynamically defined by the referenced workflow's start/end node configuration.

**Node type identifier:** `StandardNodeType.SubWorkflow` (frontend), `NodeTypeSubWorkflow` (backend)

## Core Fields

| Field | Path | Type | Required | Description |
|-------|------|------|----------|-------------|
| workflowId | `inputs.workflowId` | string | Yes | ID of the sub-workflow to execute |
| workflowVersion | `inputs.workflowVersion` | string | Yes | Version of the sub-workflow |
| inputParameters | `inputs.inputParameters` | object/array | Yes | Dynamic input parameters defined by the sub-workflow's start node |
| batch | `inputs.batch` | object | No | Batch execution configuration |
| batchMode | `inputs.batchMode` | string | No | `"batch"` or `"single"` (frontend only) |
| settingOnError | `inputs.settingOnError` | object | No | Error handling configuration |
| spaceId | `inputs.spaceId` | string | No | Workspace ID |
| type | `inputs.type` | number | No | Workflow type |

## Input Parameters

Input parameters are dynamically determined by the sub-workflow's start node input definitions. Each parameter follows the `InputVariableDTO` format:

| Property | Type | Description |
|----------|------|-------------|
| `name` | string | Parameter name |
| `type` | string | Data type (string, integer, object, list, etc.) |
| `required` | boolean | Whether the parameter is required |
| `schema` | array | Nested schema for object/list types |
| `description` | string | Parameter description |

### DTO Format (Backend)

```jsonc
"inputParameters": [
  { "name": "param1", "input": { /* ValueExpression */ } },
  { "name": "param2", "input": { /* ValueExpression */ } }
]
```

### Form Format (Frontend)

During init, converted to a map; during submit, converted back to array:

```jsonc
// Form (init)
"inputParameters": {
  "param1": { /* ValueExpression */ },
  "param2": { /* ValueExpression */ }
}

// DTO (submit) - converted back to array format via nodeUtils.formValueToDto
```

## Outputs

Outputs are dynamically defined by the sub-workflow's end node output configuration. They follow the standard `VariableMetaDTO` / `ViewVariableMeta` format.

## Batch Mode

When `batchMode` is `"batch"`:

| Field | Path | Type | Description |
|-------|------|------|-------------|
| batchEnable | `inputs.batch.batchEnable` | boolean | Must be `true` |
| inputLists | `inputs.batch.inputLists` | array | Batch input list configuration |

## Full Schema (DTO)

```jsonc
{
  "nodeMeta": { "title": "...", "description": "..." },
  "inputs": {
    "workflowId": "wf_123456",
    "workflowVersion": "1.0.0",
    "inputDefs": [/* sub-workflow input definitions from start node */],
    "inputParameters": [
      {
        "name": "user_query",
        "input": { "type": "ref", "content": { "keyPath": ["start_node", "query"] } }
      },
      {
        "name": "context",
        "input": { "type": "literal", "content": "some context" }
      }
    ],
    "batch": null,                        // or { "batchEnable": true, "inputLists": [...] }
    "batchMode": "single",
    "settingOnError": null,
    "spaceId": "...",                     // optional
    "type": 1                             // optional
  },
  "outputs": [
    { "key": "...", "name": "output", "type": "String" },
    { "key": "...", "name": "result", "type": "Object", "schema": [...] }
  ]
}
```

## Streaming Behavior

The sub-workflow supports streaming when all of the following conditions are met:
1. The parent workflow requires streaming.
2. The inner (sub) workflow requires streaming.
3. The inner workflow's exit node uses stream-based output (not `ReturnVariables` terminate plan).
4. The exit node has `RequireStreamingInput` set.
5. The streaming output field must be named `output`.

When streaming is not applicable, the node falls back to invoke (non-streaming) mode.

## Variable Reference Rules

- `workflowId` and `workflowVersion` are literal string values identifying the sub-workflow.
- `inputParameters` use standard `ValueExpression` format.
- The `inputParametersPath` is `inputs.inputParameters`.
- Default values for unfilled parameters are retrieved from the sub-workflow's input definitions during init.
- For chatflow sub-workflows, the `CONVERSATION_NAME` parameter is auto-filled from the parent start node if available.

## Backend Behavior

- The backend config extracts `WorkflowID` (int64) and `WorkflowVersion` (string) from input params.
- Execution is delegated to a `compose.Runnable` that runs the nested workflow graph.
- Supports interrupt/rerun: if the sub-workflow encounters an interrupt (e.g., from a plugin auth flow), it propagates the interrupt with `SubWorkflowInterruptInfo`.
- Checkpoint IDs are constructed hierarchically for state persistence: `<parentCheckpoint>_<subExecuteID>_<nodeExecuteID>`.

## Sub-Workflow Version Tracking

The frontend tracks whether the referenced workflow has been updated:
- `latestVersion`: the latest published version (for marketplace/released workflows).
- `flow_mode`: whether the sub-workflow is a standard workflow or chatflow.
- `inputsDefinition`: preserved input definitions from the sub-workflow.

## Example JSON Snippet

```json
{
  "inputs": {
    "workflowId": "7200001234567890",
    "workflowVersion": "3",
    "inputParameters": [
      {
        "name": "user_input",
        "input": { "type": "ref", "content": { "keyPath": ["start_node", "input"] } }
      },
      {
        "name": "max_tokens",
        "input": { "type": "literal", "content": "2048" }
      }
    ],
    "batchMode": "single"
  }
}
```

## Source Files

- Frontend: `source/coze-studio/frontend/packages/workflow/playground/src/node-registries/sub-workflow/`
- Backend: `source/coze-studio/backend/domain/workflow/internal/nodes/subworkflow/`
