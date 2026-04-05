# Plugin Node

## Purpose

Executes a registered plugin (tool) within the workflow. The plugin is identified by its plugin ID and tool (API) ID. Inputs and outputs are dynamically defined by the plugin's API specification.

**Node type identifier:** `StandardNodeType.Api` (frontend), `NodeTypePlugin` (backend)

## Core Fields

| Field | Path | Type | Required | Description |
|-------|------|------|----------|-------------|
| pluginID | `inputs.apiParam[name="pluginID"]` | string (parsed to int64) | Yes | ID of the plugin |
| apiID | `inputs.apiParam[name="apiID"]` | string (parsed to int64) | Yes | ID of the specific tool/API within the plugin |
| pluginVersion | `inputs.apiParam[name="pluginVersion"]` | string | Yes | Version of the plugin to use |
| pluginFrom | `inputs.pluginFrom` | enum | No | Plugin source: e.g., `FromSaas` for marketplace plugins |
| inputParameters | `inputs.inputParameters` | object/array | Yes | Dynamic input parameters defined by the plugin's API schema |
| batch | `inputs.batch` | object | No | Batch execution configuration |
| batchMode | `inputs.batchMode` | string | No | `"batch"` or `"single"` (frontend only) |
| settingOnError | `inputs.settingOnError` | object | No | Error handling configuration |

## Input Parameters

Input parameters are dynamically defined by the plugin's API specification (`apiDetail.inputs`). Each parameter has:

| Property | Type | Description |
|----------|------|-------------|
| `name` | string | Parameter name |
| `type` | string | Data type |
| `required` | boolean | Whether the parameter is required |
| `description` | string | Parameter description |

### DTO Format (Backend)

```jsonc
"inputParameters": [
  { "name": "param1", "input": { /* ValueExpression */ } },
  { "name": "param2", "input": { /* ValueExpression */ } }
]
```

### Form Format (Frontend)

Input parameters are converted to a map for the form:

```jsonc
"inputParameters": {
  "param1": { /* ValueExpression */ },
  "param2": { /* ValueExpression */ }
}
```

## Outputs

Outputs are dynamically defined by the plugin's API specification (`apiDetail.outputs`). They follow the standard `VariableMetaDTO` format with `name`, `type`, and optional `schema`.

## Batch Mode

When `batchMode` is `"batch"`:

| Field | Path | Type | Description |
|-------|------|------|-------------|
| batchEnable | `inputs.batch.batchEnable` | boolean | Must be `true` |
| inputLists | `inputs.batch.inputLists` | array | Batch input list configuration |

## Full Schema (DTO)

```jsonc
{
  "nodeMeta": { "title": "...", "description": "...", "icon": "..." },
  "inputs": {
    "apiParam": [
      {
        "name": "pluginID",
        "input": { "type": "string", "value": { "type": "literal", "content": "12345" } }
      },
      {
        "name": "apiID",
        "input": { "type": "string", "value": { "type": "literal", "content": "67890" } }
      },
      {
        "name": "pluginVersion",
        "input": { "type": "string", "value": { "type": "literal", "content": "1.0.0" } }
      }
    ],
    "pluginFrom": "FromSaas",            // optional, plugin source
    "inputDefs": [/* plugin input schema definitions */],
    "inputParameters": [
      { "name": "query", "input": { "type": "ref", "content": { "keyPath": ["node1", "output_field"] } } },
      { "name": "limit", "input": { "type": "literal", "content": "10" } }
    ],
    "batch": null,                        // or { "batchEnable": true, "inputLists": [...] }
    "batchMode": "single",               // "single" | "batch"
    "settingOnError": null                // optional error handling
  },
  "outputs": [
    { "key": "...", "name": "result", "type": "String" },
    { "key": "...", "name": "data", "type": "Object", "schema": [...] }
  ]
}
```

## Variable Reference Rules

- `apiParam` values are always literal strings containing the plugin/API IDs and version.
- `inputParameters` use standard `ValueExpression` format: `{type: "ref", content: {keyPath: [...]}}` for references or `{type: "literal", content: "..."}` for literals.
- Custom setter parameters (special UI components) store their values as literal ValueExpressions with stringified content.
- The `inputParametersPath` is `inputs.inputParameters`.
- Empty/unfilled parameters are filtered out during submit and re-added with defaults during init.

## Backend Behavior

- The backend parses `pluginID`, `apiID`, and `pluginVersion` from `apiParam` entries.
- Plugin execution is delegated to the cross-domain plugin service.
- Supports interrupt/rerun flow for plugins requiring authorization (e.g., OAuth).
- Input parameters are passed as a flat `map[string]any` to the plugin executor.

## Plugin Update Detection

The frontend checks if the plugin has been updated since the node was last configured by comparing:
- API name changes
- Input parameter changes (added/removed/type changes)
- Output parameter changes

If updates are detected, the node data is synchronized to the latest plugin version.

## Example JSON Snippet

```json
{
  "inputs": {
    "apiParam": [
      { "name": "pluginID", "input": { "type": "string", "value": { "type": "literal", "content": "7001" } } },
      { "name": "apiID", "input": { "type": "string", "value": { "type": "literal", "content": "8001" } } },
      { "name": "pluginVersion", "input": { "type": "string", "value": { "type": "literal", "content": "2.1.0" } } }
    ],
    "inputParameters": [
      { "name": "text", "input": { "type": "ref", "content": { "keyPath": ["llm_node", "output"] } } },
      { "name": "language", "input": { "type": "literal", "content": "en" } }
    ]
  }
}
```

## Source Files

- Frontend: `source/coze-studio/frontend/packages/workflow/playground/src/node-registries/plugin/`
- Backend: `source/coze-studio/backend/domain/workflow/internal/nodes/plugin/`
