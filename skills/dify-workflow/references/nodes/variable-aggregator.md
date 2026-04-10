# Variable Aggregator (`variable-aggregator`)

Also known as: "Variable Assigner" in source code (`variable-assigner` directory). The frontend component lives under `nodes/variable-assigner/` but the `BlockEnum` type key is `variable-aggregator`. A separate `variable-assigner` enum value (`assigner`) exists for a different node (now renamed to "VariableAssigner"/"Assigner").

## Purpose

Merges variables from multiple upstream branches into a single output, selecting the first available result. Useful after conditional branches (IF/ELSE) to unify divergent paths.

## Core Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `output_type` | `VarType` | Yes | The type of the output variable. Default: `"any"`. |
| `variables` | `ValueSelector[]` | Yes (when groups disabled) | Array of variable selectors to aggregate. Each is `[node_id, variable_name]`. |
| `advanced_settings` | `object` | No | Configuration for grouped aggregation mode. |

## Full Schema

### Node Data (`type: "variable-aggregator"`)

Standard `CommonNodeType` fields (`title`, `desc`, `type`) plus:

```typescript
{
  output_type: VarType          // Type of the aggregated output (e.g., "string", "number", "any").
  variables: ValueSelector[]    // List of variable references to aggregate.
  advanced_settings: {
    group_enabled: boolean      // Whether grouped mode is active.
    groups: {
      groupId: string           // Unique ID for the group (UUID).
      group_name: string        // Display name for the group (e.g., "Group1").
      output_type: VarType      // Output type for this group.
      variables: ValueSelector[] // Variable selectors in this group.
    }[]
  }
}
```

### VarType (common values)

`"string"`, `"number"`, `"integer"`, `"boolean"`, `"object"`, `"file"`, `"array"`, `"array[string]"`, `"array[number]"`, `"array[object]"`, `"array[file]"`, `"any"`

### ValueSelector

An array of strings forming a path: `["node_id", "output_field"]` or `["node_id", "group_name", "output"]` for grouped outputs.

## Variable Reference Rules

- **Input**: Each entry in `variables` (or `groups[].variables`) references an upstream node's output via `[node_id, variable_name]`.
- **Output (simple mode)**: The node outputs a single variable `output` of the configured `output_type`.
- **Output (grouped mode)**: Each group produces its own output, accessible as `[aggregator_node_id, group_name, "output"]`.

All variables within a single group (or within the flat `variables` list) must be of the same type, matching `output_type`.

The node picks the **first available** result among the listed variables. This means it selects whichever upstream branch actually executed and produced a value.

## Example Snippet

### Simple mode (no groups)

```yaml
- data:
    output_type: string
    variables:
      - - "template_node_1"
        - output
      - - "template_node_2"
        - output
    desc: ""
    title: Variable Aggregator
    type: variable-aggregator
  height: 150
  id: "agg_1"
  position:
    x: 800
    y: 300
  sourcePosition: right
  targetPosition: left
  type: custom
  width: 244
```

### Grouped mode

```yaml
- data:
    advanced_settings:
      group_enabled: true
      groups:
        - groupId: a924f802-235c-47c1-85f6-922569221a39
          group_name: Group1
          output_type: string
          variables:
            - - "switch1_on_node"
              - output
            - - "switch1_off_node"
              - output
        - groupId: 940f08b5-dc9a-4907-b17a-38f24d3377e7
          group_name: Group2
          output_type: string
          variables:
            - - "switch2_on_node"
              - output
            - - "switch2_off_node"
              - output
    output_type: string
    variables:
      - - "switch1_on_node"
        - output
      - - "switch1_off_node"
        - output
    desc: ""
    title: Variable Aggregator
    type: variable-aggregator
  height: 218
  id: "agg_1"
  position:
    x: 1162
    y: 346
  sourcePosition: right
  targetPosition: left
  type: custom
  width: 244
```

Downstream End node referencing grouped output:

```yaml
outputs:
  - value_selector:
      - "agg_1"
      - Group1
      - output
    value_type: object
    variable: group1
  - value_selector:
      - "agg_1"
      - Group2
      - output
    value_type: object
    variable: group2
```
