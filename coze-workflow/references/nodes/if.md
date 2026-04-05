# If (Selector) Node

## Purpose

Conditional branching node that evaluates one or more condition branches and routes execution to the first branch whose conditions are satisfied, or to a default ELSE branch if none match. Known as `If` in the frontend (StandardNodeType `'8'`) and `Selector` in the backend (NodeType `"Selector"`).

## Core Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `inputs.branches` | `Branch[]` | Yes | Array of condition branches. Each branch contains a compound condition. |
| `inputs.branches[].condition.logic` | `LogicType` (int) | Yes | How conditions within the branch combine: `1` = OR, `2` = AND. |
| `inputs.branches[].condition.conditions` | `Condition[]` | Yes | Array of individual comparison conditions within the branch. |

## Full Schema

### Node Data (frontend DTO)

Standard node fields (`nodeMeta`, etc.) plus:

```typescript
{
  inputs: {
    branches: Branch[]
  }
}
```

### Branch

```typescript
{
  condition: {
    logic: LogicType       // 1 = OR, 2 = AND
    conditions: Condition[]
  }
}
```

### Condition

```typescript
{
  operator: OperatorType      // Integer enum (see table below)
  left: BlockInput            // Left operand - a variable reference
  right?: BlockInput          // Right operand - a variable reference or literal (omitted for unary operators)
}
```

### OperatorType Enum (backend `vo.OperatorType`, iota starting at 1)

| Value | Name | Backend Operator String | Applicable Left Types | Requires Right |
|-------|------|------------------------|-----------------------|----------------|
| 1 | Equal | `=` | int64, float64, bool, string | Yes |
| 2 | NotEqual | `!=` | int64, float64, bool, string | Yes |
| 3 | LengthGreaterThan | `len >` | string, slice | Yes (int64) |
| 4 | LengthGreaterThanEqual | `len >=` | string, slice | Yes (int64) |
| 5 | LengthLessThan | `len <` | string, slice | Yes (int64) |
| 6 | LengthLessThanEqual | `len <=` | string, slice | Yes (int64) |
| 7 | Contain | `contain` / `contain_key` | string, slice, or object (contain_key for objects) | Yes |
| 8 | NotContain | `not_contain` / `not_contain_key` | string, slice, or object | Yes |
| 9 | Empty | `empty` | any | No |
| 10 | NotEmpty | `not_empty` | any | No |
| 11 | True | `true` | bool | No |
| 12 | False | `false` | bool | No |
| 13 | GreaterThan | `>` | int64, float64 | Yes |
| 14 | GreaterThanEqual | `>=` | int64, float64 | Yes |
| 15 | LessThan | `<` | int64, float64 | Yes |
| 16 | LessThanEqual | `<=` | int64, float64 | Yes |

### Operators by Variable Type (frontend groupings)

- **string**: Equal, NotEqual, LengthGt, LengthGtEqual, LengthLt, LengthLtEqual, Contains, NotContains, Null (empty), NotNull (not empty)
- **number / integer**: Equal, NotEqual, Gt, GtEqual, Lt, LtEqual, Null, NotNull
- **boolean**: Equal, NotEqual, Null, NotNull, True, False
- **object**: Contains (contain_key), NotContains (not_contain_key), Null, NotNull
- **array**: LengthGt, LengthGtEqual, LengthLt, LengthLtEqual, Contains, NotContains, Null, NotNull
- **file**: NotNull, Null

### LogicType

| Value | Meaning |
|-------|---------|
| 1 | OR - any condition in the branch must be true |
| 2 | AND - all conditions in the branch must be true |

## Branching / Port Rules

The If node uses dynamic output ports:

- **First branch**: port ID `"true"`
- **Additional branches**: port IDs `"true_1"`, `"true_2"`, etc.
- **ELSE (default)**: port ID `"false"`

The backend determines which port fires by evaluating branches in order. The first branch whose conditions resolve to true is selected. If none match, the default (ELSE) branch is selected. Backend output: `{ "selected": <branch_index> }` where the index equals `len(branches)` for the ELSE case.

## Backend Schema Adaptation

The backend `selector` package converts each branch into either:
- A **single clause** (`OneClauseSchema.Single`) when the branch has exactly one condition.
- A **multi clause** (`OneClauseSchema.Multi`) with a `relation` of `"and"` or `"or"` and an array of operators, when the branch has multiple conditions.

```go
type Config struct {
    Clauses []*OneClauseSchema `json:"clauses"`
}

type OneClauseSchema struct {
    Single *Operator          `json:"single,omitempty"`
    Multi  *MultiClauseSchema `json:"multi,omitempty"`
}

type MultiClauseSchema struct {
    Clauses  []*Operator    `json:"clauses"`
    Relation ClauseRelation `json:"relation"` // "and" | "or"
}
```

## Variable Reference Rules

- **Input**: Each condition's `left` and optional `right` are `BlockInput` / `Param` references to upstream node outputs or variables. The backend resolves them via `CanvasBlockInputToFieldInfo`.
- **Output**: The If node itself produces no user-visible output variables. It only controls which downstream branch executes.

## Example JSON Snippet

Minimal If node with one branch (AND logic, two conditions) plus an implicit ELSE:

```json
{
  "inputs": {
    "branches": [
      {
        "condition": {
          "logic": 2,
          "conditions": [
            {
              "operator": 1,
              "left": {
                "type": "string",
                "value": { "type": "reference", "content": { "nodeID": "node_1", "keyPath": ["node_1", "name"] } }
              },
              "right": {
                "type": "string",
                "value": { "type": "literal", "content": "hello" }
              }
            },
            {
              "operator": 10,
              "left": {
                "type": "string",
                "value": { "type": "reference", "content": { "nodeID": "node_1", "keyPath": ["node_1", "email"] } }
              }
            }
          ]
        }
      }
    ]
  }
}
```

This evaluates: IF (`name == "hello"` AND `email is not empty`) THEN branch 0, ELSE default branch.

## Source Locations

- Frontend: `frontend/packages/workflow/playground/src/node-registries/if/`
- Backend: `backend/domain/workflow/internal/nodes/selector/`
- VO types: `backend/domain/workflow/entity/vo/canvas.go` (Selector, Condition, OperatorType, LogicType)
