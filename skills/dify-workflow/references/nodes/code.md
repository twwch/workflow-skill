# Code (`code`)

## Purpose
Execute custom Python 3, JavaScript, or JSON transformation code with mapped input variables and structured output.

## Core Fields
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `code_language` | `CodeLanguage` | Yes | Language to execute: `python3`, `javascript`, or `json` |
| `code` | `string` | Yes | The source code to run. Must define a `main` function (Python/JS) that returns an object |
| `variables` | `Variable[]` | Yes | Input variable mappings passed as arguments to the `main` function |
| `outputs` | `OutputVar` | Yes | Declared output variable schema (keys with their types) |

## Full Schema

### CodeNodeType (extends CommonNodeType)

```typescript
{
  // --- CommonNodeType fields ---
  title: string               // Display name of the node
  desc: string                // Description of the node
  type: 'code'                // BlockEnum.Code

  // --- Code-specific fields ---
  variables: Variable[]       // Input variable mappings
  code_language: CodeLanguage // 'python3' | 'javascript' | 'json'
  code: string                // Source code to execute
  outputs: OutputVar          // Output variable declarations

  // --- Optional CommonNodeType fields ---
  error_strategy?: ErrorHandleTypeEnum  // 'terminated' | 'continue-on-error' | 'remove-abnormal-output'
  retry_config?: {
    retry_enabled: boolean
    max_retries: number
    retry_interval: number
  }
}
```

### CodeLanguage (enum)
| Value | Description |
|-------|-------------|
| `python3` | Python 3 code |
| `javascript` | JavaScript code |
| `json` | JSON transformation |

### Variable
```typescript
{
  variable: string            // Name used in code (e.g., parameter name in main())
  value_selector: string[]    // Reference path: [nodeId, ...keyPath]
  value_type?: VarType        // Optional type hint
  required?: boolean          // Whether the variable is required
}
```

### OutputVar
A `Record<string, { type: VarType, children: null }>` where each key is an output variable name.

#### VarType values
`string`, `number`, `integer`, `secret`, `boolean`, `object`, `file`, `array`, `array[string]`, `array[number]`, `array[object]`, `array[boolean]`, `array[file]`, `any`, `array[any]`

## Variable Reference Rules

**Inputs:** Each entry in `variables` maps a variable name to a value from an upstream node via `value_selector`. The variable name corresponds to a parameter of the `main()` function in the code.

**Outputs:** Declared in the `outputs` field as key-type pairs. Downstream nodes reference these as `[thisNodeId, outputKey]`. The `main()` function must return an object whose keys match the declared output keys.

## Default Values
```json
{
  "code": "",
  "code_language": "python3",
  "variables": [],
  "outputs": {}
}
```

## Validation Rules
- Every entry in `variables` must have a non-empty `variable` name
- Every entry in `variables` must have a non-empty `value_selector`
- `code` must be non-empty

## Example Snippet

```yaml
- data:
    title: Transform Text
    desc: Convert text to uppercase
    type: code
    code_language: python3
    variables:
      - variable: input_text
        value_selector:
          - "start_node_id"
          - text
    code: |
      def main(input_text: str) -> dict:
          return {
              "result": input_text.upper()
          }
    outputs:
      result:
        type: string
        children: null
  id: code-node-1
  position:
    x: 400
    y: 200
```
