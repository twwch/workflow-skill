# If/Else (`if-else`)

## Purpose

Conditionally routes workflow execution to different branches based on variable comparisons (IF / ELIF / ELSE).

## Core Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `cases` | `CaseItem[]` | Yes | Array of condition cases. The first case has `case_id: "true"` (the IF branch). Additional cases are ELIF branches. |
| `logical_operator` | `"and" \| "or"` | No | Legacy field (deprecated in favor of per-case `logical_operator`). |
| `conditions` | `Condition[]` | No | Legacy field (deprecated in favor of per-case `conditions`). |

## Full Schema

### Node Data (`type: "if-else"`)

Standard `CommonNodeType` fields (`title`, `desc`, `type`) plus:

```typescript
{
  cases: CaseItem[]          // Required. Array of conditional branches.
  logical_operator?: string  // Legacy. Use cases[].logical_operator instead.
  conditions?: Condition[]   // Legacy. Use cases[].conditions instead.
}
```

### CaseItem

```typescript
{
  case_id: string                    // Unique ID for the case. First case uses "true".
  logical_operator: "and" | "or"     // How conditions within this case are combined.
  conditions: Condition[]            // Array of conditions to evaluate.
}
```

### Condition

```typescript
{
  id: string                                  // Unique condition ID (UUID).
  varType: VarType                            // Type of the variable being compared.
  variable_selector?: ValueSelector           // Path to the variable, e.g. ["node_id", "field"].
  key?: string                                // Sub-variable key (for file attribute comparisons).
  comparison_operator?: ComparisonOperator    // The comparison to perform.
  value: string | string[] | boolean          // The value to compare against.
  numberVarType?: NumberVarType               // Number sub-type hint (from tool nodes).
  sub_variable_condition?: CaseItem           // Nested sub-variable conditions (for object/file fields).
}
```

### ComparisonOperator (all valid string values)

| Operator | String Value | Applicable Types | Requires Value |
|----------|-------------|------------------|----------------|
| contains | `"contains"` | string, array[string], array[number], array[boolean], array[file] | Yes |
| notContains | `"not contains"` | string, array[string], array[number], array[boolean], array[file] | Yes |
| startWith | `"start with"` | string | Yes |
| endWith | `"end with"` | string | Yes |
| is | `"is"` | string, boolean | Yes |
| isNot | `"is not"` | string, boolean | Yes |
| empty | `"empty"` | string, number, integer, array types | No |
| notEmpty | `"not empty"` | string, number, integer, array types | No |
| equal | `"="` | number, integer | Yes |
| notEqual | `"\u2260"` | number, integer | Yes |
| largerThan | `">"` | number, integer | Yes |
| lessThan | `"<"` | number, integer | Yes |
| largerThanOrEqual | `"\u2265"` | number, integer | Yes |
| lessThanOrEqual | `"\u2264"` | number, integer | Yes |
| isNull | `"is null"` | any | No |
| isNotNull | `"is not null"` | any | No |
| in | `"in"` | file attributes (type, transfer_method) | Yes |
| notIn | `"not in"` | file attributes (type, transfer_method) | Yes |
| allOf | `"all of"` | array[file] | Yes |
| exists | `"exists"` | file | No |
| notExists | `"not exists"` | file | No |

Operators that do **not** require a `value`: `empty`, `not empty`, `is null`, `is not null`, `exists`, `not exists`.

### Operators by Variable Type

- **string**: contains, not contains, start with, end with, is, is not, empty, not empty
- **number / integer**: =, !=, >, <, >=, <=, empty, not empty
- **boolean**: is, is not
- **file**: exists, not exists
- **array[string] / array[number] / array[boolean]**: contains, not contains, empty, not empty
- **array / array[object]**: empty, not empty
- **array[file]**: contains, not contains, all of, empty, not empty

## Branching Handles

The If/Else node uses `_targetBranches` to define output handles for edges:

- **Simple IF/ELSE** (1 case): Two branches with IDs `"true"` (IF) and `"false"` (ELSE).
- **Multiple cases (ELIF)**: Each additional case gets a unique `case_id`. The ELSE branch always has ID `"false"`.

Branch naming convention:
- 2 branches: `"IF"` and `"ELSE"`
- 3+ branches: `"CASE 1"`, `"CASE 2"`, ..., `"ELSE"`

Edges connect from the if-else node using `sourceHandle` matching the `case_id` (e.g., `"true"`, `"false"`, or the ELIF case ID).

## Variable Reference Rules

- **Input**: References upstream variables via `variable_selector` in each condition (e.g., `["node_id", "variable_name"]`).
- **Output**: The If/Else node produces no output variables itself. It only controls which downstream branch executes.

## Example Snippet

Minimal IF/ELSE checking if a string variable contains "hello":

```yaml
- data:
    cases:
      - case_id: "true"
        conditions:
          - comparison_operator: contains
            id: cond-1
            value: hello
            varType: string
            variable_selector:
              - "start_node_id"
              - query
        id: "true"
        logical_operator: and
    desc: ""
    title: IF/ELSE
    type: if-else
  height: 126
  id: "ifelse_1"
  position:
    x: 364
    y: 263
  sourcePosition: right
  targetPosition: left
  type: custom
  width: 244
```

Edges for this node connect `sourceHandle: "true"` to the IF-branch target and `sourceHandle: "false"` to the ELSE-branch target.

### Numeric comparison example

```yaml
cases:
  - case_id: "true"
    conditions:
      - comparison_operator: "="
        id: cond-1
        value: "1"
        varType: number
        variable_selector:
          - "start_node_id"
          - switch1
    id: "true"
    logical_operator: and
```

Note: Numeric values in `value` are stored as strings (e.g., `"1"` not `1`).
