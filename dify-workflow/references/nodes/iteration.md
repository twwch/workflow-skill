# Iteration (`iteration`)

## Purpose

Loops over an array input, executing an embedded sub-graph for each element, and collects results into an output array.

## Core Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `iterator_selector` | `ValueSelector` | Yes | Path to the input array variable, e.g. `["node_id", "result"]`. |
| `output_selector` | `ValueSelector` | Yes | Path to the variable produced by the sub-graph that becomes each element of the output array. |
| `start_node_id` | `string` | Yes | ID of the `iteration-start` node inside the iteration. Convention: `"<iteration_node_id>start"`. |
| `is_parallel` | `boolean` | No | Whether to run iterations in parallel. Default: `false`. |
| `parallel_nums` | `number` | No | Max parallel executions when `is_parallel` is true. Default: `10`. |
| `error_handle_mode` | `ErrorHandleMode` | No | How to handle errors in iterations. Default: `"terminated"`. |
| `flatten_output` | `boolean` | No | Whether to flatten the output array when elements are themselves arrays. Default: `true`. |

## Full Schema

### Node Data (`type: "iteration"`)

Standard `CommonNodeType` fields (`title`, `desc`, `type`) plus:

```typescript
{
  start_node_id: string              // ID of the iteration-start child node.
  startNodeType?: BlockEnum          // Type of the start node (always "iteration-start").
  iteration_id?: string              // Self-reference (set on child nodes, not on the iteration node itself).
  iterator_selector: ValueSelector   // Path to the input array.
  iterator_input_type: VarType       // Type of the input array (e.g., "array[number]").
  output_selector: ValueSelector     // Path to the per-iteration output variable.
  output_type: VarType               // Type of the collected output array (e.g., "array[array[number]]").
  is_parallel: boolean               // Enable parallel iteration.
  parallel_nums: number              // Max parallel count.
  error_handle_mode: ErrorHandleMode // "terminated" | "continue-on-error" | "remove-abnormal-output"
  flatten_output: boolean            // Flatten nested array output.
  _isShowTips: boolean               // UI-only: show tips when answer node is in parallel iteration.
}
```

### ErrorHandleMode

| Value | Description |
|-------|-------------|
| `"terminated"` | Stop the entire iteration on first error. |
| `"continue-on-error"` | Skip the failed element and continue with remaining. |
| `"remove-abnormal-output"` | Continue but exclude failed elements from output. |

## Sub-Graph Structure

An iteration node contains child nodes as a sub-graph. The structure:

1. **Iteration node** (`type: "iteration"`): The container. Has `width`/`height` that encompass child nodes. Gets `zIndex: 1` in the graph.
2. **Iteration-start node** (`type: "iteration-start"`): Entry point of the sub-graph. This is a special child node:
   - `id`: Convention is `"<iteration_node_id>start"` (no separator).
   - `parentId`: Set to the iteration node's ID.
   - `type`: `"custom-iteration-start"` (ReactFlow node type).
   - `draggable: false`, `selectable: false`.
   - `zIndex: 1002`.
   - `data.isInIteration: true`.
3. **Inner nodes**: Regular workflow nodes placed inside the iteration:
   - `parentId`: Set to the iteration node's ID.
   - `data.isInIteration: true`.
   - `data.iteration_id`: Set to the iteration node's ID.
   - `zIndex: 1002`.
   - Positions are relative to the iteration node container.

### Edges inside iteration

Edges between inner nodes have:
- `data.isInIteration: true`
- `data.iteration_id`: The iteration node's ID.
- `zIndex: 1002`

## Variable Reference Rules

- **Input**: The `iterator_selector` references an upstream array variable.
- **Iteration variable**: Inner nodes can access the current element via `[iteration_node_id, "item"]`. The type of `item` is the element type of the input array.
- **Index variable**: Inner nodes can access the current iteration index via `[iteration_node_id, "index"]`.
- **Output**: The `output_selector` points to an inner node's output variable. The iteration collects these into an array. The final output is available as `[iteration_node_id, "output"]`.
- **Output type**: Wraps the per-element type in an array. If inner code returns `array[number]` and `flatten_output` is true, the iteration output type is `array[number]` (flattened). If false, it would be `array[array[number]]`.

## Example Snippet

Iteration over an array of numbers, with an inner code node that doubles each element:

```yaml
# Iteration container node
- data:
    desc: ""
    error_handle_mode: terminated
    flatten_output: true
    height: 178
    is_parallel: false
    iterator_input_type: "array[number]"
    iterator_selector:
      - code_node
      - result
    output_selector:
      - code_inner_node
      - result
    output_type: "array[array[number]]"
    parallel_nums: 10
    start_node_id: iteration_nodestart
    title: Iteration
    type: iteration
    width: 388
  height: 178
  id: iteration_node
  position:
    x: 684
    y: 282
  sourcePosition: right
  targetPosition: left
  type: custom
  width: 388
  zIndex: 1

# Iteration-start child node
- data:
    desc: ""
    isInIteration: true
    title: ""
    type: iteration-start
  draggable: false
  height: 48
  id: iteration_nodestart
  parentId: iteration_node
  position:
    x: 24
    y: 68
  selectable: false
  sourcePosition: right
  targetPosition: left
  type: custom-iteration-start
  width: 44
  zIndex: 1002

# Inner processing node
- data:
    code: "\ndef main(arg1: int) -> dict:\n    return {\"result\": [arg1, arg1 * 2]}\n"
    code_language: python3
    desc: ""
    isInIteration: true
    isInLoop: false
    iteration_id: iteration_node
    outputs:
      result:
        children: null
        type: "array[number]"
    title: Generate Pair
    type: code
    variables:
      - value_selector:
          - iteration_node
          - item
        value_type: number
        variable: arg1
  height: 54
  id: code_inner_node
  parentId: iteration_node
  position:
    x: 128
    y: 68
  sourcePosition: right
  targetPosition: left
  type: custom
  width: 244
  zIndex: 1002
```

Edges for the sub-graph:

```yaml
# iteration-start -> inner code node
- data:
    isInIteration: true
    isInLoop: false
    iteration_id: iteration_node
    sourceType: iteration-start
    targetType: code
  id: iteration-start-source-code-inner-target
  source: iteration_nodestart
  sourceHandle: source
  target: code_inner_node
  targetHandle: target
  type: custom
  zIndex: 1002
```

Downstream reference to iteration output:

```yaml
outputs:
  - value_selector:
      - iteration_node
      - output
    value_type: "array[number]"
    variable: output
```
