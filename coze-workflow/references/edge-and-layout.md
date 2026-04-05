# Coze Workflow Edge Connections and Layout Rules

Extracted from Coze Studio source code.

Sources:
- `backend/domain/workflow/entity/vo/canvas.go` (Edge struct)
- `backend/domain/workflow/internal/schema/branch_schema.go` (port constants)
- `backend/domain/workflow/internal/canvas/adaptor/to_schema.go` (port normalization, edge conversion)
- `frontend/packages/workflow/nodes/src/constants.ts` (node sizes)
- `frontend/packages/workflow/sdk/__tests__/__mock_data__/canvas-schema.ts` (example positions)

---

## Edge Format

**Go type** (`vo.Edge`):

```json
{
  "sourceNodeID": "100001",
  "targetNodeID": "200001",
  "sourcePortID": "",
  "targetPortID": ""
}
```

| Field          | JSON key         | Type     | Description                                           |
|----------------|------------------|----------|-------------------------------------------------------|
| SourceNodeID   | `sourceNodeID`   | `string` | ID of the source node.                                |
| TargetNodeID   | `targetNodeID`   | `string` | ID of the target node.                                |
| SourcePortID   | `sourcePortID`   | `string` | Source port (empty string = default/only output port). |
| TargetPortID   | `targetPortID`   | `string` | Target port (empty string = default/only input port).  |

All edges in Coze are **control flow edges**. Data flow is implicit -- it is defined within `inputParameters` via `BlockInputReference` (referencing another node's output by `blockID` + field `name`), not via separate data-flow edges.

---

## Edge Types: Control Flow Only

Coze workflows use a single edge type for control flow. There are no separate "data flow" edges in the canvas JSON. Data dependencies between nodes are encoded inside each node's `inputParameters` using `ref` values that point to another node's output (see `dsl-format.md` for BlockInputReference).

### Standard Edge (no branching)

For most nodes, edges have an **empty** `sourcePortID`:

```json
{ "sourceNodeID": "100001", "targetNodeID": "200001", "sourcePortID": "" }
```

This means: after node `100001` finishes, control flows to node `200001`.

---

## Port Naming Conventions

Certain node types produce multiple output ports (branches). The `sourcePortID` field identifies which branch an edge belongs to.

### Selector Node (If/Condition, type=8)

The Selector node supports multiple condition branches plus an "else" branch.

| sourcePortID | Meaning                                   | Backend Mapping         |
|--------------|-------------------------------------------|-------------------------|
| `"true"`     | First condition branch (index 0)          | `branch_0`              |
| `"true_1"`   | Second condition branch (index 1)         | `branch_1`              |
| `"true_N"`   | Nth condition branch (index N)            | `branch_N`              |
| `"false"`    | Else branch (none of the conditions met)  | `default`               |

### IntentDetector Node (type=22)

| sourcePortID  | Meaning                        | Backend Mapping |
|---------------|--------------------------------|-----------------|
| `"default"`   | Default/fallback intent        | `default`       |
| `"branch_0"`  | First intent match             | `branch_0`      |
| `"branch_N"`  | Nth intent match               | `branch_N`      |

### Exception Branch (Error Handling)

When a node has `settingOnError.processType = 3` (exception branch mode):

| sourcePortID    | Meaning                           | Backend Mapping |
|-----------------|-----------------------------------|-----------------|
| `""`            | Normal (success) output           | (no port)       |
| `"default"`     | Normal (success) output with port | `default`       |
| `"branch_error"`| Exception/error branch            | `branch_error`  |

### Composite Node Ports (Loop, Batch)

Loop and Batch nodes are composite -- they contain sub-nodes in `blocks` and sub-edges in `edges`. Special port IDs connect the composite boundary to its inner/outer graph.

#### Loop Node (type=21)

| Port ID                         | Used On        | Meaning                                            |
|----------------------------------|----------------|----------------------------------------------------|
| `"loop-function-inline-output"` | sourcePortID   | Output from the last inner node to the loop boundary. |
| `"loop-function-inline-input"`  | targetPortID   | Input from the loop boundary to the first inner node. |
| `"loop-output"`                 | sourcePortID   | Output from the loop node to the next outer node.  |

#### Batch Node (type=28)

| Port ID                          | Used On        | Meaning                                            |
|-----------------------------------|----------------|----------------------------------------------------|
| `"batch-function-inline-output"` | sourcePortID   | Output from the last inner node to the batch boundary. |
| `"batch-function-inline-input"`  | targetPortID   | Input from the batch boundary to the first inner node. |
| `"batch-output"`                 | sourcePortID   | Output from the batch node to the next outer node. |

---

## Edge Placement: Top-Level vs. Inner

- **Top-level edges** go in `canvas.edges` -- these connect top-level nodes (and composite nodes to their successors).
- **Inner edges** (within Loop/Batch) go in the composite node's `node.edges` -- these connect sub-nodes inside `node.blocks`.
- Sub-nodes inside composite nodes must **not** have their own `edges` field.
- Nesting composite nodes (composite within composite) is **not supported**.

---

## Layout Coordinate System

### Coordinate System

- Origin `(0, 0)` is at the **top-left** of the canvas.
- **X axis** increases to the right.
- **Y axis** increases downward.
- Positions are in **pixel units**.
- The `position` in node `meta` represents the **top-left corner** of the node.

### Default Node Size

From `frontend/packages/workflow/nodes/src/constants.ts`:

```typescript
export const DEFAULT_NODE_SIZE = {
  width: 360,
  height: 104.7,
};
```

- **Default width**: 360px
- **Default height**: 104.7px (this is the base height; actual height varies by node content)

Some node types override the default height:

| Node Type            | Width  | Height  | Source                                    |
|----------------------|--------|---------|-------------------------------------------|
| Default              | 360    | 104.7   | `DEFAULT_NODE_SIZE`                       |
| Chat node            | 360    | 113     | `create-node-registry.ts`                 |
| Variable/Question/Intent | 360 | 156.7  | Various `node-registry.ts` files          |
| Comment              | Custom | Custom  | Set via `data.size` on the node itself    |

### Layout Conventions (from examples)

Based on the default canvas templates and test mock data:

- **Entry node** (Start) is placed at `(0, 0)` or a small offset like `(180, 39)`.
- **Exit node** (End) is placed at `x = 1000` in the default template.
- **Horizontal spacing** between nodes is typically **~460px** (360px node width + ~100px gap).
- **Nodes flow left-to-right**: increasing X values represent later nodes in the workflow.
- **Vertical offset** (Y) is used to arrange parallel branches.

Example from default template:

```
Start (0, 0) -----> End (1000, 0)
```

Example from mock data with 4 nodes:

```
Start (180, 39) -> Code (640, 26) -> LLM (1100, 0) -> End (1560, 26)
```

The approximate horizontal gap between node left edges is **460px** (matching 360px width + 100px gap).

---

## Connection Rules

### General Rules

1. Every workflow must have exactly one **Entry node** (id=`100001`, type=`1`) and exactly one **Exit node** (id=`900001`, type=`2`).
2. Edges define **control flow only**. Data flow is encoded in `inputParameters`.
3. A node can have multiple outgoing edges only if it is a **branching node** (Selector, IntentDetector) or has **exception handling** enabled.
4. Non-branching nodes should have at most one outgoing edge with empty `sourcePortID`.
5. Isolated nodes (not connected to any path from Entry to Exit) are **pruned** before execution (`PruneIsolatedNodes`).
6. Comment nodes (type=31) are **skipped** during execution and do not need edges.

### Break and Continue (within Loop)

- `Break` (type=19) and `Continue` (type=29) nodes can only appear inside a Loop node's `blocks`.
- They implicitly connect back to their parent Loop node (handled by the backend adaptor).

### Composite Node Rules

- Loop and Batch nodes contain sub-nodes in `blocks` and sub-edges in `edges`.
- The inner sub-graph must form a valid path.
- The composite node itself connects to other top-level nodes via top-level edges using the special port IDs (`loop-output`, `batch-output`, etc.).
