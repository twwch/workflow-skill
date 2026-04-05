# Batch Node

## Purpose

Processes array inputs in parallel by executing an inner sub-canvas workflow for each element concurrently. Similar to the Loop node but with parallel execution, configurable concurrency, and a maximum batch size limit. Known as `Batch` in both frontend (StandardNodeType `'28'`) and backend (NodeType `"Batch"`).

## Core Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `inputs.inputParameters` | `InputValue[]` | Yes | Array input parameters to iterate over in parallel. At least one array input is required. |
| `inputs.batchSize` | `BlockInput` | Yes | Maximum number of items to process (caps the iteration count). Default 100 if 0. |
| `inputs.concurrentSize` | `BlockInput` | Yes | Maximum number of concurrent parallel executions. Default 10 if 0. |
| `outputs` | `OutputValue[]` | Yes | Output variable definitions. At least one output is required. Each collects per-element results into a list. |

## Full Schema

### Node Data (frontend DTO)

```typescript
{
  inputs: {
    inputParameters: InputValue[]     // Array inputs to iterate over
    batchSize: BlockInput             // Max items to process (integer reference or literal)
    concurrentSize: BlockInput        // Max concurrent executions (integer reference or literal)
  }
  outputs: OutputValue[]              // Output variables, each becomes a list
}
```

### Frontend Paths

```typescript
enum BatchPath {
  ConcurrentSize = 'inputs.concurrentSize',
  BatchSize = 'inputs.batchSize',
  Inputs = 'inputs.inputParameters',
  Outputs = 'outputs',
}

const BatchOutputsSuffix = '_list';
```

### Backend Config

```go
type Config struct{}

// Constants
const (
    MaxBatchSizeKey   = "batchSize"
    ConcurrentSizeKey = "concurrentSize"
)
```

The backend `Config` struct is empty because the batch node dynamically determines its input arrays from the node schema's input types (any input of type `DataTypeArray` is treated as an iterable array).

### Backend VO (canvas.go)

```go
type Batch struct {
    BatchSize      *BlockInput `json:"batchSize,omitempty"`
    ConcurrentSize *BlockInput `json:"concurrentSize,omitempty"`
}
```

## Port Configuration

| Port | ID | Description |
|------|----|-------------|
| Input | (default) | Receives data from upstream nodes. |
| Output | `batch-output` | Fires after all batch items complete with collected output arrays. |
| Output (internal) | `batch-output-to-function` | Disabled port for internal sub-canvas connection. |

The batch node contains a **sub-canvas** (child workflow) created via `createBatchFunction`, similar to the loop node.

## Runtime Behavior

1. The batch node extracts all array inputs and determines `minLen` = minimum array length, capped by `batchSize`.
2. Pre-allocates output arrays of length `minLen`.
3. Executes up to `concurrentSize` inner workflows in parallel using goroutines.
4. Each iteration `i` receives:
   - All non-array input values (passed through, excluding `batchSize` and `concurrentSize`).
   - `{nodeKey}#index`: the current index (int64, 0-based).
   - `{nodeKey}#{arrayKey}`: the current element from each input array.
   - Nested map elements are recursively expanded with `#` separator keys.
5. Results are placed in the output arrays at the corresponding index (preserving order).
6. If any inner workflow fails, execution is cancelled for all remaining items.

### Interrupt/Resume Support

The batch node supports interruption (e.g., for human-in-the-loop). It tracks per-index completion state (`Index2Done`) and interrupt info (`Index2InterruptInfo`). On resume, only previously interrupted indices are re-executed.

## Variable Reference Rules

- **Input**: `inputParameters` reference upstream array variables. `batchSize` and `concurrentSize` reference integer values (variable references or literals).
- **Output**: Each output variable references a field from the inner workflow's output. The batch node wraps each per-element result into a list. If the inner variable is referenced from inside the batch sub-canvas and is not the batch node itself, it gets wrapped as `{ type: "list", schema: { type: originalType, schema: originalSchema } }`.

## Example JSON Snippet

Batch process an array of URLs with concurrency of 5, max 50 items:

```json
{
  "inputs": {
    "inputParameters": [
      {
        "name": "urls",
        "input": {
          "type": "list",
          "value": { "type": "reference", "content": { "nodeID": "start_1", "keyPath": ["start_1", "urls"] } }
        }
      }
    ],
    "batchSize": {
      "type": "integer",
      "value": { "type": "literal", "content": 50 }
    },
    "concurrentSize": {
      "type": "integer",
      "value": { "type": "literal", "content": 5 }
    }
  },
  "outputs": [
    {
      "name": "responses",
      "input": {
        "type": "string",
        "value": { "type": "reference", "content": { "nodeID": "http_1", "keyPath": ["http_1", "body"] } }
      }
    }
  ]
}
```

## Source Locations

- Frontend: `frontend/packages/workflow/playground/src/node-registries/batch/`
- Backend: `backend/domain/workflow/internal/nodes/batch/`
- VO types: `backend/domain/workflow/entity/vo/canvas.go` (Batch struct)
