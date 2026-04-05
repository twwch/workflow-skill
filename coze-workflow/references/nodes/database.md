# Database Node

## Purpose

Performs CRUD operations and custom SQL queries against Coze databases. There are five distinct sub-types: Query, Insert, Update, Delete, and Custom SQL.

**Node type identifiers (frontend / backend):**
- Query: `StandardNodeType.DatabaseQuery` / `NodeTypeDatabaseQuery`
- Insert: `StandardNodeType.DatabaseCreate` / `NodeTypeDatabaseInsert`
- Update: `StandardNodeType.DatabaseUpdate` / `NodeTypeDatabaseUpdate`
- Delete: `StandardNodeType.DatabaseDelete` / `NodeTypeDatabaseDelete`
- Custom SQL: `StandardNodeType.DatabaseBase` / `NodeTypeDatabaseCustomSQL`

---

## Common Fields (All Sub-Types)

| Field | Path | Type | Required | Description |
|-------|------|------|----------|-------------|
| databaseInfoList | `inputs.databaseInfoList` | array | Yes | Array containing the target database info. Uses `databaseInfoList[0].databaseInfoID` (string, parsed to int64) |

## Common Outputs (All Sub-Types)

| Name | Type | Description |
|------|------|-------------|
| `outputList` | ArrayObject | Array of result objects with fields matching the output schema |
| `rowNum` | Integer/null | Number of affected/returned rows (null for some operations) |

---

## Database Query Node

### Additional Fields

| Field | Path | Type | Required | Description |
|-------|------|------|----------|-------------|
| selectParam.fieldList | `inputs.selectParam.fieldList` | array | Yes | Fields to select. Each: `{fieldID: int64, isDistinct?: boolean}` |
| selectParam.limit | `inputs.selectParam.limit` | integer | Yes | Maximum rows to return (must be > 0) |
| selectParam.orderByList | `inputs.selectParam.orderByList` | array | No | Sort order. Each: `{fieldID: int64, isAsc: boolean}` |
| selectParam.condition | `inputs.selectParam.condition` | object | No | Filter conditions (see Condition format below) |

### Full Schema (Query DTO)

```jsonc
{
  "nodeMeta": { "title": "...", "description": "..." },
  "inputs": {
    "databaseInfoList": [
      { "databaseInfoID": "12345" }
    ],
    "selectParam": {
      "fieldList": [
        { "fieldID": 1001, "isDistinct": false },
        { "fieldID": 1002 }
      ],
      "limit": 10,
      "orderByList": [
        { "fieldID": 1001, "isAsc": true }
      ],
      "condition": {
        "conditionList": [
          [
            { "name": "left", "input": { "type": "string", "value": { "type": "literal", "content": "1001" } } },
            { "name": "operation", "input": { "type": "string", "value": { "type": "literal", "content": "EQUAL" } } },
            { "name": "right", "input": { /* ValueExpression */ } }
          ]
        ],
        "logic": "AND"
      }
    }
  },
  "outputs": [
    {
      "name": "outputList",
      "type": "ArrayObject",
      "schema": [
        { "name": "field_name", "type": "String" }
      ]
    },
    { "name": "rowNum", "type": "Integer" }
  ]
}
```

---

## Database Insert Node

### Additional Fields

| Field | Path | Type | Required | Description |
|-------|------|------|----------|-------------|
| insertParam.fieldInfo | `inputs.insertParam.fieldInfo` | array | Yes | Fields to insert. Each entry is a pair: `[{name: "fieldName", input: literal}, {name: "fieldValue", input: ValueExpression}]` |

### Full Schema (Insert DTO)

```jsonc
{
  "nodeMeta": { "title": "...", "description": "..." },
  "inputs": {
    "databaseInfoList": [{ "databaseInfoID": "12345" }],
    "insertParam": {
      "fieldInfo": [
        [
          { "name": "fieldName", "input": { "type": "string", "value": { "type": "literal", "content": "1001" } } },
          { "name": "fieldValue", "input": { "type": "ref", "content": { "keyPath": ["node1", "name"] } } }
        ]
      ]
    }
  },
  "outputs": [
    { "name": "outputList", "type": "ArrayObject", "schema": [...] },
    { "name": "rowNum", "type": "Integer" }
  ]
}
```

---

## Database Update Node

### Additional Fields

| Field | Path | Type | Required | Description |
|-------|------|------|----------|-------------|
| updateParam.condition | `inputs.updateParam.condition` | object | Yes | Filter conditions for rows to update (same Condition format) |
| updateParam.fieldInfo | `inputs.updateParam.fieldInfo` | array | Yes | Fields to update (same format as Insert fieldInfo) |

### Full Schema (Update DTO)

```jsonc
{
  "nodeMeta": { "title": "...", "description": "..." },
  "inputs": {
    "databaseInfoList": [{ "databaseInfoID": "12345" }],
    "updateParam": {
      "condition": {
        "conditionList": [[/* left, operation, right params */]],
        "logic": "AND"
      },
      "fieldInfo": [
        [
          { "name": "fieldName", "input": { "type": "string", "value": { "type": "literal", "content": "1001" } } },
          { "name": "fieldValue", "input": { /* ValueExpression */ } }
        ]
      ]
    }
  },
  "outputs": [
    { "name": "outputList", "type": "ArrayObject", "schema": [...] },
    { "name": "rowNum", "type": "Integer" }
  ]
}
```

---

## Database Delete Node

### Additional Fields

| Field | Path | Type | Required | Description |
|-------|------|------|----------|-------------|
| deleteParam.condition | `inputs.deleteParam.condition` | object | Yes | Filter conditions for rows to delete (same Condition format) |

### Full Schema (Delete DTO)

```jsonc
{
  "nodeMeta": { "title": "...", "description": "..." },
  "inputs": {
    "databaseInfoList": [{ "databaseInfoID": "12345" }],
    "deleteParam": {
      "condition": {
        "conditionList": [[/* left, operation, right params */]],
        "logic": "AND"
      }
    }
  },
  "outputs": [
    { "name": "outputList", "type": "ArrayObject", "schema": [...] },
    { "name": "rowNum", "type": "Integer" }
  ]
}
```

---

## Database Custom SQL Node

### Additional Fields

| Field | Path | Type | Required | Description |
|-------|------|------|----------|-------------|
| sql | `inputs.sql` | string | Yes | SQL template with `{{variable}}` interpolation. Variables in single quotes become parameterized. |

### Full Schema (Custom SQL DTO)

```jsonc
{
  "nodeMeta": { "title": "...", "description": "..." },
  "inputs": {
    "databaseInfoList": [{ "databaseInfoID": "12345" }],
    "sql": "SELECT * FROM users WHERE name = '{{user_name}}' AND age > {{min_age}}",
    "inputParameters": [
      { "name": "user_name", "input": { /* ValueExpression */ } },
      { "name": "min_age", "input": { /* ValueExpression */ } }
    ]
  },
  "outputs": [
    { "name": "outputList", "type": "ArrayObject", "schema": [...] },
    { "name": "rowNum", "type": "Integer" }
  ]
}
```

---

## Condition Format

Conditions filter rows for Query, Update, and Delete operations.

```jsonc
{
  "conditionList": [
    // Each inner array represents one condition with 3 params:
    [
      { "name": "left", "input": { "type": "string", "value": { "type": "literal", "content": "<fieldID>" } } },
      { "name": "operation", "input": { "type": "string", "value": { "type": "literal", "content": "<operator>" } } },
      { "name": "right", "input": { /* ValueExpression - the comparison value */ } }
    ]
  ],
  "logic": "AND"  // "AND" | "OR"
}
```

### Supported Operators

| Operator | Description |
|----------|-------------|
| `EQUAL` | Equal to |
| `NOT_EQUAL` | Not equal to |
| `GREATER_THAN` | Greater than |
| `LESS_THAN` | Less than |
| `GREATER_EQUAL` | Greater than or equal |
| `LESS_EQUAL` | Less than or equal |
| `IN` | In set |
| `NOT_IN` | Not in set |
| `IS_NULL` | Is null (no right value needed) |
| `IS_NOT_NULL` | Is not null (no right value needed) |
| `LIKE` | Pattern match |
| `NOT_LIKE` | Not pattern match |

## Variable Reference Rules

- `databaseInfoID` is always a literal string containing the database ID.
- Condition `right` values and field values use standard `ValueExpression` format.
- Backend maps field values with `__setting_field_` prefix and condition rights with `__condition_right_<index>` prefix.
- Custom SQL uses `{{variable}}` template syntax; variables wrapped in single quotes (`'{{var}}'`) are treated as parameterized values for SQL injection safety.

## Backend Behavior

- All database operations go through the cross-domain database service.
- Debug mode detection: different behavior for debug vs. production runs.
- User context (userID, connectorID) is extracted from execution context for access control.
- Output formatting converts raw database types (bytes, time, etc.) to the configured output type schema.
- Supported data types: string, integer, number, boolean, time, array, object.

## Frontend Data Transformer

The base database node transformer is simple: it flattens `inputs` into the form root on init and wraps it back on submit:

```
// Init: { nodeMeta, inputs: { ...fields }, outputs } -> { nodeMeta, ...fields, outputs }
// Submit: { nodeMeta, ...fields, outputs } -> { nodeMeta, inputs: { ...fields }, outputs }
```

## Example JSON Snippet (Query)

```json
{
  "inputs": {
    "databaseInfoList": [{ "databaseInfoID": "100001" }],
    "selectParam": {
      "fieldList": [{ "fieldID": 2001 }, { "fieldID": 2002 }],
      "limit": 20,
      "orderByList": [{ "fieldID": 2001, "isAsc": false }],
      "condition": {
        "conditionList": [
          [
            { "name": "left", "input": { "type": "string", "value": { "type": "literal", "content": "2003" } } },
            { "name": "operation", "input": { "type": "string", "value": { "type": "literal", "content": "GREATER_THAN" } } },
            { "name": "right", "input": { "type": "ref", "content": { "keyPath": ["start_node", "min_value"] } } }
          ]
        ],
        "logic": "AND"
      }
    }
  }
}
```

## Source Files

- Frontend (base): `source/coze-studio/frontend/packages/workflow/playground/src/node-registries/database/database-base/`
- Frontend (query): `source/coze-studio/frontend/packages/workflow/playground/src/node-registries/database/database-query/`
- Frontend (create): `source/coze-studio/frontend/packages/workflow/playground/src/node-registries/database/database-create/`
- Frontend (update): `source/coze-studio/frontend/packages/workflow/playground/src/node-registries/database/database-update/`
- Frontend (delete): `source/coze-studio/frontend/packages/workflow/playground/src/node-registries/database/database-delete/`
- Backend: `source/coze-studio/backend/domain/workflow/internal/nodes/database/`
