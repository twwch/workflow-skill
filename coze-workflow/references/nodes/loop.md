# Loop Node

## Purpose

Iterates over an array, a fixed count, or infinitely, executing an inner sub-canvas workflow for each iteration. Collects outputs from each iteration into arrays. Supports intermediate (accumulator) variables that persist across iterations. Known as `Loop` in both frontend (StandardNodeType `'21'`) and backend (NodeType `"Loop"`). Also encompasses `Break` (StandardNodeType `'19'`) and `Continue` (StandardNodeType `'29'`) control flow nodes that can only be placed inside a loop's sub-canvas.

## Core Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `inputs.loopType` | `LoopType` (string) | Yes | `"array"`, `"count"`, or `"infinite"`. |
| `inputs.inputParameters` | `InputValue[]` | Conditional | Array input parameters. Required when `loopType` is `"array"`. Each entry is an array variable to iterate over. |
| `inputs.loopCount` | `BlockInput` | Conditional | Number of iterations. Required when `loopType` is `"count"`. A reference or literal integer value. |
| `inputs.variableParameters` | `Param[]` | No | Intermediate (accumulator) variables that persist across loop iterations. Each has a name and initial value reference. |
| `outputs` | `OutputValue[]` | No | Output variable definitions. Each output collects values from inner workflow iterations into a list. |

## Full Schema

### Node Data (frontend DTO)

```typescript
{
  inputs: {
    loopType: "array" | "count" | "infinite"
    inputParameters: InputValue[]       // Array inputs to iterate over (for "array" mode)
    loopCount?: BlockInput              // Iteration count (for "count" mode)
    variableParameters?: Param[]        // Intermediate/accumulator variables
  }
  outputs: OutputValue[]                // Output variables collected per iteration
}
```

### LoopType

| Value | Description |
|-------|-------------|
| `"array"` | Iterates over one or more input arrays. Length = minimum array length. |
| `"count"` | Iterates a fixed number of times specified by `loopCount`. |
| `"infinite"` | Iterates until a `Break` node is hit (max = `math.MaxInt`). |

### Backend Config

```go
type Config struct {
    LoopType         Type                       // "by_array", "by_iteration", "infinite"
    InputArrays      []string                   // Keys of input fields that are arrays
    IntermediateVars map[string]*vo.TypeInfo     // Accumulator variable names and types
}
```

Backend loop type mapping:
- `"array"` -> `ByArray` (`"by_array"`)
- `"count"` -> `ByIteration` (`"by_iteration"`)
- `"infinite"` -> `Infinite` (`"infinite"`)

## Port Configuration

| Port | ID | Description |
|------|----|-------------|
| Input | (default) | Receives data from upstream nodes. |
| Output | `loop-output` | Fires after the loop completes with collected output arrays. |
| Output (internal) | `loop-output-to-function` | Disabled port connecting to the inner sub-canvas (handled internally). |

The loop node contains a **sub-canvas** (child workflow) that executes once per iteration. The sub-canvas is created automatically via `createLoopFunction`.

## Iteration Runtime Behavior

Each iteration receives:
- All non-array, non-intermediate input values (passed through).
- `{nodeKey}#index`: the current iteration index (int64, 0-based).
- `{nodeKey}#{arrayKey}`: the current element from each input array (for array mode).
- Intermediate variables are accessible via the parent intermediate store.

Output collection: after each iteration, the loop extracts specified fields from the inner workflow's output and appends them to the corresponding output arrays.

## Break and Continue Nodes

### Break (`NodeType: "Break"`, StandardNodeType `'19'`)

- Placed inside a loop's sub-canvas.
- Sets `$break = true` on the parent intermediate store.
- After the current iteration completes, the loop stops iterating.
- No inputs, no outputs. Config is empty.

### Continue (`NodeType: "Continue"`, StandardNodeType `'29'`)

- Placed inside a loop's sub-canvas.
- Passes input through as output (effectively a no-op that terminates the current iteration's branch).
- No special runtime logic -- acts as an early-exit point within the sub-canvas graph.
- No inputs, no outputs. Config is empty.

## Frontend Constants

```typescript
enum LoopPath {
  LoopType = 'inputs.loopType',
  LoopCount = 'inputs.loopCount',
  LoopArray = 'inputs.inputParameters',
  LoopVariables = 'inputs.variableParameters',
  LoopOutputs = 'outputs',
}

const LoopVariablePrefix = 'var_';
const LoopOutputsSuffix = '_list';
```

## Variable Reference Rules

- **Input**: `inputParameters` contains variable references to upstream arrays. `loopCount` references an integer. `variableParameters` reference initial values for accumulators.
- **Output**: Each output variable collects a list of values. If the output references a variable inside the loop, it becomes a list of that variable's type. If it references an intermediate variable, it takes the final value of that accumulator.
- **Intermediate variables**: Set via `SetVariable` (VariableAssignerWithinLoop) nodes inside the loop. Persist across iterations.

## Example JSON Snippet

Loop over an array, collecting transformed results:

```json
{
  "inputs": {
    "loopType": "array",
    "inputParameters": [
      {
        "name": "items",
        "input": {
          "type": "list",
          "value": { "type": "reference", "content": { "nodeID": "start_1", "keyPath": ["start_1", "items"] } }
        }
      }
    ],
    "variableParameters": [
      {
        "name": "counter",
        "input": {
          "type": "integer",
          "value": { "type": "literal", "content": 0 }
        }
      }
    ]
  },
  "outputs": [
    {
      "name": "results",
      "input": {
        "type": "string",
        "value": { "type": "reference", "content": { "nodeID": "code_1", "keyPath": ["code_1", "output"] } }
      }
    }
  ]
}
```

## Source Locations

- Frontend: `frontend/packages/workflow/playground/src/node-registries/loop/`
- Frontend (break): `frontend/packages/workflow/playground/src/node-registries/break/`
- Frontend (continue): `frontend/packages/workflow/playground/src/node-registries/continue/`
- Backend: `backend/domain/workflow/internal/nodes/loop/`
- Backend (break): `backend/domain/workflow/internal/nodes/loop/break/`
- Backend (continue): `backend/domain/workflow/internal/nodes/loop/continue/`
- VO types: `backend/domain/workflow/entity/vo/canvas.go` (Loop, LoopType)
