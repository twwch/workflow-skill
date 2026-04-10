## coze.cn Cloud YAML Format (variable_merge)

YAML type: `variable_merge`

```yaml
    - id: "200010"
      type: variable_merge
      title: 变量聚合
      icon: .../VariableMerge-icon.jpg
      parameters:
        mergeGroups:
            - name: v
              variables:
                - type: string
                  value:
                    content:
                        blockID: "<source_node_id>"
                        name: output
                        source: block-output
                    rawMeta:
                        type: 1
                    type: ref
        node_outputs:
            output:
                type: string
                value: null
```

Note: `mergeGroups[].variables[].value` uses `{type: ref, content: {blockID, name, source}}` format (same as open-source), NOT `{path, ref_node}`.

See `examples/parallel-merge.yaml` for complete template.

---

# Variable Nodes

This document covers three related variable nodes in Coze Studio:

1. **Variable** (get/set app/user variables) -- StandardNodeType `'11'`, backend `NodeType` handled by `variableassigner` package
2. **Set Variable** (assign values to variables within loops or to global vars) -- StandardNodeType `'20'`, backend `NodeType "VariableAssigner"` or `"VariableAssignerWithinLoop"`
3. **Variable Aggregator** (merge multiple variable sources, pick first non-null) -- StandardNodeType `'32'`, backend `NodeType "VariableAggregator"`

---

## 1. Variable Node

### Purpose

Reads or writes app-level and user-level persistent variables. Operates in one of two modes: `get` (read a variable's value as output) or `set` (write a value to a variable).

### Core Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `inputs.mode` | `"get" \| "set"` | Yes | Operation mode. |
| `inputs.inputParameters` | `InputValue[]` | Yes | The variable references -- what to get or set. |
| `outputs` | `OutputValue[]` | Yes | Output variables. In `set` mode: `[{ name: "isSuccess", type: "boolean" }]`. In `get` mode: the retrieved variable. |

### Full Schema

```typescript
// Frontend FormData
interface FormData {
  nodeMeta: NodeMeta
  mode: "set" | "get"
  inputParameters: InputValueVO[]
  outputs: OutputValueVO[]
}
```

### Mode Defaults

- **set mode**: Default output is `{ name: "isSuccess", type: Boolean, required: true }` with description "whether variable setting succeeded".
- **get mode**: Default output is `{ name: "", type: String, required: true }` (user configures the name and type).

### Frontend Constants

```typescript
enum ModeValue {
  Get = 'get',
  Set = 'set',
}
```

### Node Registry

- `headerReadonly: true` (node title is read-only)
- `headerReadonlyAllowDeleteOperation: true`
- `inputParametersPath: '/inputParameters'`
- `outputsPathList: ['outputs']`

### Variable Reference Rules

- Input parameters reference app-level or user-level variables via the variable service.
- In `set` mode, writes the referenced value and outputs `{ isSuccess: true }`.
- In `get` mode, reads the variable and produces its value as output.

---

## 2. Set Variable Node (Variable Assigner)

### Purpose

Assigns values to variables. Has two backend variants:
- **VariableAssigner** (top-level): Writes to `GlobalAPP` or `GlobalUser` persistent variables.
- **VariableAssignerWithinLoop**: Writes to parent loop's intermediate (accumulator) variables.

Frontend StandardNodeType: `'20'` (SetVariable) and `'40'` (VariableAssign).

### Core Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `inputs.inputParameters` | `SetVariableItem[]` | Yes | Array of left-right assignment pairs. |
| `inputs.inputParameters[].left` | `ValueExpression` | Yes | Target variable reference (what to assign to). |
| `inputs.inputParameters[].right` | `ValueExpression` | Yes | Source value reference (what value to assign). |

### Full Schema

```typescript
// Frontend FormData
interface SetVariableItem {
  left: RefExpression    // Target variable (must be a reference)
  right: RefExpression   // Source value (reference or expression)
}

interface FormData {
  inputs: { inputParameters: SetVariableItem[] }
}
```

### Backend Schema

```go
// Top-level variable assigner
type Config struct {
    Pairs []*Pair
}

type Pair struct {
    Left  vo.Reference         // Target: must be GlobalAPP or GlobalUser type
    Right compose.FieldPath    // Source path
}

// Within-loop variable assigner
type InLoopConfig struct {
    Pairs []*Pair              // Left must be ParentIntermediate type
}
```

### Constraints

**Top-level VariableAssigner**:
- `left.VariableType` must be `GlobalAPP` or `GlobalUser` (cannot assign to `GlobalSystem` which is read-only).
- Cannot assign to node outputs.
- Output: `{ "isSuccess": true }`.

**Within-loop VariableAssignerWithinLoop**:
- `left.VariableType` must be `ParentIntermediate` (references a loop's intermediate variable).
- The node must have a parent loop node.
- Output: empty map `{}`.

### Node Registry

- `hideTest: true` (no test run support)
- Size: `360 x 87.86`
- `inputParametersPath: 'inputs.inputParameters'`
- No output variables exposed (empty `outputsPathList` and `inputsPathList`)

### Default State

When no input parameters exist, defaults to:
```typescript
[{
  left: { type: ValueExpressionType.REF },
  right: { type: ValueExpressionType.REF }
}]
```

---

## 3. Variable Aggregator Node

### Purpose

Merges multiple variable sources using a "first non-null value" strategy. Organizes inputs into named groups, each containing multiple candidate variables. For each group, selects the first non-null candidate as the output. Supports both streaming and non-streaming values. Known as `VariableMerge` in frontend (StandardNodeType `'32'`) and `VariableAggregator` in backend (NodeType `"VariableAggregator"`).

### Core Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `inputs.variableAggregator.mergeGroups` | `Param[]` | Yes | Array of merge groups. Each group has a `name` and `variables` array. |
| `inputs.variableAggregator.mergeGroups[].name` | `string` | Yes | Name of the output group (becomes an output key). |
| `inputs.variableAggregator.mergeGroups[].variables` | `BlockInput[]` | Yes | Ordered list of candidate variable references. First non-null wins. |

### Full Schema

#### Backend VO (canvas.go)

```go
type VariableAggregator struct {
    MergeGroups []*Param `json:"mergeGroups,omitempty"`
}

// Each Param in MergeGroups has:
// - Name: string (group name)
// - Variables: []*BlockInput (candidate references)
```

#### Backend Config

```go
type Config struct {
    MergeStrategy MergeStrategy        // Always FirstNotNullValue (1)
    GroupLen      map[string]int        // group name -> number of candidates
    GroupOrder    []string              // order of groups as declared in canvas
}

type MergeStrategy uint
const FirstNotNullValue MergeStrategy = 1
```

### Runtime Behavior

1. For each group, iterate over candidates in order.
2. Select the first candidate that is non-null.
3. If all candidates are null/skipped, the group output is nil.
4. Streaming support: if a candidate is a stream source, it is considered non-null even before any content arrives. The aggregator can operate in streaming mode, passing through stream data for the chosen candidate.

### Output

The node outputs a map where each key is a group name and the value is the selected candidate's value:
```
{ "groupA": <first non-null from groupA candidates>, "groupB": <first non-null from groupB candidates> }
```

An intermediate result stores the choice index per group for callback display: `{ "groupA": 0, "groupB": 2 }` (or -1 if all candidates were null).

### Variable Reference Rules

- **Input**: Each candidate in a merge group is a `BlockInput` reference to an upstream node's output variable.
- **Output**: Output types are determined by `SetOutputTypesForNodeSchema` based on the node's output configuration.

---

## Example JSON Snippets

### Variable Node (set mode)

```json
{
  "inputs": {
    "mode": "set",
    "inputParameters": [
      {
        "name": "user_preference",
        "input": {
          "type": "string",
          "value": { "type": "reference", "content": { "nodeID": "llm_1", "keyPath": ["llm_1", "output"] } }
        }
      }
    ]
  },
  "outputs": [
    { "name": "isSuccess", "type": "boolean", "required": true }
  ]
}
```

### Set Variable (within loop)

```json
{
  "inputs": {
    "inputParameters": [
      {
        "left": {
          "type": "reference",
          "content": { "keyPath": ["loop_1", "counter"] }
        },
        "right": {
          "type": "reference",
          "content": { "nodeID": "code_1", "keyPath": ["code_1", "new_count"] }
        }
      }
    ]
  }
}
```

### Variable Aggregator

```json
{
  "inputs": {
    "variableAggregator": {
      "mergeGroups": [
        {
          "name": "result",
          "variables": [
            { "type": "string", "value": { "type": "reference", "content": { "nodeID": "branch_a", "keyPath": ["branch_a", "output"] } } },
            { "type": "string", "value": { "type": "reference", "content": { "nodeID": "branch_b", "keyPath": ["branch_b", "output"] } } }
          ]
        }
      ]
    }
  }
}
```

## Source Locations

- Frontend (variable): `frontend/packages/workflow/playground/src/node-registries/variable/`
- Frontend (set-variable): `frontend/packages/workflow/playground/src/node-registries/set-variable/`
- Backend (variable assigner): `backend/domain/workflow/internal/nodes/variableassigner/`
- Backend (variable aggregator): `backend/domain/workflow/internal/nodes/variableaggregator/`
- VO types: `backend/domain/workflow/entity/vo/canvas.go` (VariableAggregator, VariableAssigner)
