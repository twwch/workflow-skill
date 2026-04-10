# Template Transform (`template-transform`)

## Purpose
Transform data using Jinja2 template syntax, rendering a template string with mapped input variables to produce a single string output.

## Core Fields
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `template` | `string` | Yes | Jinja2 template string to render |
| `variables` | `Variable[]` | Yes | Input variable mappings available in the template |

## Full Schema

### TemplateTransformNodeType (extends CommonNodeType)

```typescript
{
  // --- CommonNodeType fields ---
  title: string               // Display name of the node
  desc: string                // Description of the node
  type: 'template-transform'  // BlockEnum.TemplateTransform

  // --- Template-specific fields ---
  variables: Variable[]       // Input variable mappings
  template: string            // Jinja2 template string

  // --- Optional CommonNodeType fields ---
  error_strategy?: ErrorHandleTypeEnum  // 'terminated' | 'continue-on-error' | 'remove-abnormal-output'
  retry_config?: {
    retry_enabled: boolean
    max_retries: number
    retry_interval: number
  }
}
```

### Variable
```typescript
{
  variable: string            // Name used in the Jinja2 template (e.g., {{ variable_name }})
  value_selector: string[]    // Reference path: [nodeId, ...keyPath]
  value_type?: VarType        // Optional type hint
  required?: boolean          // Whether the variable is required
}
```

## Variable Reference Rules

**Inputs:** Each entry in `variables` maps a name to an upstream node output via `value_selector`. The variable name becomes available in the Jinja2 template as `{{ variable_name }}`.

**Outputs:** The Template Transform node produces a single output:
- `output` (string) -- the rendered template result

Downstream nodes reference this as `[thisNodeId, "output"]`.

## Default Values
```json
{
  "template": "",
  "variables": []
}
```

## Validation Rules
- Every entry in `variables` must have a non-empty `variable` name
- Every entry in `variables` must have a non-empty `value_selector`
- `template` must be non-empty

## Example Snippet

```yaml
- data:
    title: Format Output
    desc: Combine variables into formatted text
    type: template-transform
    variables:
      - variable: name
        value_selector:
          - "start_node_id"
          - name
      - variable: score
        value_selector:
          - "code_node_id"
          - result
    template: |
      Hello {{ name }}, your score is {{ score }}.
  id: template-node-1
  position:
    x: 400
    y: 200
```
