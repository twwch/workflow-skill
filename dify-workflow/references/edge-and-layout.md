# Edge and Layout Rules

Reference for generating edges (connections between nodes) and node positions in Dify workflow DSL files.

Source: `source/dify/web/app/components/workflow/`

## Edge Object Schema

An edge in the DSL graph represents a connection between two nodes. The minimal and full schemas are:

### Minimal Edge (Backend/DSL)

The backend (`_EdgeType` in `api/services/workflow/workflow_converter.py`) requires:

```json
{
  "id": "source-node-id-sourceHandle-target-node-id-targetHandle",
  "source": "<source_node_id>",
  "target": "<target_node_id>",
  "sourceHandle": "source",
  "targetHandle": "target"
}
```

### Full Edge (Frontend/ReactFlow)

The frontend (`Edge` type in `web/app/components/workflow/types.ts`) extends ReactFlow's `Edge<CommonEdgeType>`:

```typescript
type CommonEdgeType = {
  _hovering?: boolean
  _connectedNodeIsHovering?: boolean
  _connectedNodeIsSelected?: boolean
  _isBundled?: boolean
  _sourceRunningStatus?: NodeRunningStatus
  _targetRunningStatus?: NodeRunningStatus
  _waitingRun?: boolean
  isInIteration?: boolean
  iteration_id?: string
  isInLoop?: boolean
  loop_id?: string
  sourceType: BlockEnum
  targetType: BlockEnum
  _isTemp?: boolean
}
```

Fields prefixed with `_` are runtime UI state and are NOT persisted in the DSL. The DSL-relevant fields on `data` are:

- `sourceType` - BlockEnum of the source node
- `targetType` - BlockEnum of the target node
- `isInIteration` - whether the edge is inside an iteration container
- `iteration_id` - parent iteration node ID (if inside iteration)
- `isInLoop` - whether the edge is inside a loop container
- `loop_id` - parent loop node ID (if inside loop)

### Edge ID Convention

Edge IDs follow the pattern:
```
{source}-{sourceHandle}-{target}-{targetHandle}
```

Examples:
- `start-1-source-llm-1-target` (start node to LLM)
- `if-else-1-true-code-1-target` (if-else true branch to code node)
- `if-else-1-false-llm-2-target` (if-else false branch to LLM)

### Edge Type

All edges use `type: "custom"` (constant `CUSTOM_EDGE = 'custom'`).

### zIndex for Edges

- Edges at root level: `0`
- Edges inside iteration containers: `1002` (`ITERATION_CHILDREN_Z_INDEX`)
- Edges inside loop containers: `1002` (`LOOP_CHILDREN_Z_INDEX`)

## sourceHandle Naming Conventions

The `sourceHandle` determines which output port of a node the edge originates from.

### Standard Nodes (Single Output)

For most node types, the sourceHandle is `"source"`:
- Start, LLM, Code, HTTP Request, Template Transform, Knowledge Retrieval, Tool, Parameter Extractor, Answer, End, Document Extractor, List Operator, Variable Assigner/Aggregator, Agent, Assigner, DataSource

### If-Else Node (Conditional Branches)

The if-else node uses `cases` array. Each case has a `case_id`:
- **First case (legacy)**: `sourceHandle = "true"` (case_id is `"true"`)
- **Additional cases**: `sourceHandle = case_id` (a UUID or string identifier)
- **Else branch (always last)**: `sourceHandle = "false"`

The `_targetBranches` array is built from cases + the final `false` branch:
```typescript
// From workflow-init.ts
node.data._targetBranches = [
  ...cases.map(item => ({ id: item.case_id, name: '' })),
  { id: 'false', name: '' },
]
```

### Question Classifier Node

Each class/topic has an `id`. The sourceHandle for each branch is the topic's `id`:
```typescript
// classes: Topic[] where Topic = { id: string, name: string }
sourceHandle = topic.id  // e.g., a UUID string
```

### Human Input Node

Each user action has an `id`. The sourceHandle is:
- **Action branches**: `sourceHandle = action.id` (UUID of the user action)
- **Timeout branch**: `sourceHandle = "__timeout"`

### Trigger Nodes (Schedule, Webhook, Plugin)

Trigger nodes use `sourceHandle = "success"` based on test fixtures in `api/tests/test_containers_integration_tests/trigger/test_trigger_e2e.py`.

Note: In frontend code, trigger nodes render the standard `"source"` handle via `node-handle.tsx`. The `"success"` handle appears in backend test configurations. When generating DSL, use `"source"` for consistency with the frontend convention.

### Error/Failure Branch

Nodes that support error handling (LLM, Tool, HTTP Request, Code, Agent) can have:
- `sourceHandle = "fail-branch"` (value of `ErrorHandleTypeEnum.failBranch`)

This is only active when `error_strategy` is set to `"fail-branch"`.

## targetHandle Naming Convention

The `targetHandle` is almost always `"target"`. This is the default input port for all nodes.

The only exception is Variable Assigner/Aggregator nodes with group mode enabled, which can have custom target handles per group.

When no targetHandle is specified, the system defaults to `"target"`:
```typescript
// From workflow-init.ts
if (!edge.targetHandle)
  edge.targetHandle = 'target'
```

## Connection Validation Rules

From `use-workflow.ts` `isValidConnection()` and `use-available-blocks.ts`:

### Which Nodes Cannot Have Predecessors (No Incoming Edges)

- `Start`
- `DataSource`
- `TriggerSchedule`
- `TriggerWebhook`
- `TriggerPlugin`

### Which Nodes Cannot Have Successors (No Outgoing Edges)

- `End`
- `LoopEnd`
- `KnowledgeBase` (knowledge-index)

### Container Restrictions

When inside an iteration or loop container (`inContainer = true`), these node types are excluded:
- `Iteration` (no nested iterations)
- `Loop` (no nested loops)
- `End`
- `DataSource`
- `KnowledgeBase`
- `HumanInput`

When NOT in a container, `LoopEnd` is excluded from the available blocks.

### Additional Validation Rules

1. **No cross-level connections**: Source and target must have the same `parentId` (both at root level, or both inside the same iteration/loop).
2. **No cycles**: The system performs DFS cycle detection. Adding an edge that creates a cycle is rejected.
3. **No note-node connections**: Note nodes (type `"custom-note"`) cannot be connected.
4. **No duplicate edges**: An edge with the same source, sourceHandle, target, and targetHandle cannot be added twice.

## Layout Coordinate System

### Coordinate System

- Origin: top-left corner of the canvas
- X-axis: increases to the right (flow direction)
- Y-axis: increases downward
- Unit: pixels

### Node Dimensions and Spacing Constants

From `constants.ts`:

```typescript
NODE_WIDTH = 240
X_OFFSET = 60
NODE_WIDTH_X_OFFSET = 300  // NODE_WIDTH + X_OFFSET
Y_OFFSET = 39

START_INITIAL_POSITION = { x: 80, y: 282 }
AUTO_LAYOUT_OFFSET = { x: -42, y: 243 }

ITERATION_PADDING = { top: 65, right: 16, bottom: 20, left: 16 }
LOOP_PADDING = { top: 65, right: 16, bottom: 20, left: 16 }

NODE_LAYOUT_HORIZONTAL_PADDING = 60
NODE_LAYOUT_VERTICAL_PADDING = 60
NODE_LAYOUT_MIN_DISTANCE = 100
```

### Default Node Size

```typescript
DEFAULT_NODE_WIDTH = 244   // Used in ELK layout
DEFAULT_NODE_HEIGHT = 100  // Used in ELK layout
```

### Initial Positioning (No Layout)

When nodes have no stored positions, they are placed in a horizontal line:
```typescript
nodes.forEach((node, index) => {
  node.position = {
    x: START_INITIAL_POSITION.x + index * NODE_WIDTH_X_OFFSET,  // 80 + index * 300
    y: START_INITIAL_POSITION.y,  // 282
  }
})
```

## Auto-Layout with ELK

Dify uses the ELK (Eclipse Layout Kernel) library for auto-layout with a `layered` algorithm flowing left-to-right.

### Root Layout Configuration

Key settings from `elk-layout.ts`:

- **Algorithm**: `layered` (hierarchical/Sugiyama style)
- **Direction**: `RIGHT` (left-to-right flow)
- **Node-to-node spacing between layers**: 100px
- **Node-to-node spacing within same layer**: 80px
- **Edge-to-node spacing**: 50px
- **Node placement**: `BRANDES_KOEPF` with `BALANCED` alignment
- **Edge routing**: `SPLINES`
- **Crossing minimization**: `LAYER_SWEEP`
- **Layering strategy**: `NETWORK_SIMPLEX`
- **Hierarchy handling**: `INCLUDE_CHILDREN`

### Child Layout (Inside Iteration/Loop)

- **Node-to-node spacing between layers**: 80px
- **Node-to-node spacing within same layer**: 60px
- **Edge-to-node spacing**: 40px
- Same algorithm and strategies as root, with tighter spacing.

### Layout Process

1. Root-level nodes and edges are extracted (excluding iteration/loop children).
2. ELK computes positions using the layered algorithm.
3. Results are normalized so the top-left bounding box starts at (0, 0).
4. Child nodes inside iterations/loops get separate layout passes with `getLayoutForChildNodes()`.

### Branching Node Edge Ordering

During layout, edges from branching nodes are sorted to control vertical ordering:

- **If-Else**: Case branches in array order, `"false"` (else) branch always last.
- **Question Classifier**: Classes in array order.
- **Human Input**: Actions in array order, `"__timeout"` always last.

## Practical Guidelines for DSL Generation

### Simple Linear Workflow

For a simple chain of nodes, position them with ~300px horizontal spacing:

```
Start (80, 282) -> Node1 (380, 282) -> Node2 (680, 282) -> End (980, 282)
```

### Branching Workflows

For if-else or classifier nodes, offset branches vertically:

```
                     +-> TrueBranch (680, 182) -> ...
IfElse (380, 282) --+
                     +-> FalseBranch (680, 382) -> ...
```

Use ~200px vertical offset between branches.

### Edge Generation Checklist

1. Set `id` to `{source}-{sourceHandle}-{target}-{targetHandle}`
2. Set `type` to `"custom"`
3. Set `sourceHandle` based on node type (see naming conventions above)
4. Set `targetHandle` to `"target"` (almost always)
5. Set `data.sourceType` and `data.targetType` to the BlockEnum values
6. For edges inside iteration/loop, set `isInIteration`/`isInLoop` and the container ID
7. Set `zIndex` to `0` for root-level, `1002` for container-level

### BlockEnum Values

```
start, end, answer, llm, knowledge-retrieval, question-classifier,
if-else, code, template-transform, http-request, variable-assigner,
variable-aggregator, tool, parameter-extractor, iteration,
document-extractor, list-operator, iteration-start, assigner, agent,
loop, loop-start, loop-end, human-input, datasource, datasource-empty,
knowledge-index, trigger-schedule, trigger-webhook, trigger-plugin
```
