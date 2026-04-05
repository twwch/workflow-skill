# Text Process Node

## Purpose

String manipulation node that supports two operations: **concatenating** multiple inputs into a single string, or **splitting** a string into an array using delimiters. Node type ID: `15` (frontend) / `TextProcessor` (backend).

## Core Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `inputs.method` | `"concat"` \| `"split"` | Yes | Operation mode. Default: `"concat"` |
| `inputs.inputParameters` | `InputParam[]` | Yes | Input variables referenced in the template or as split source |
| `inputs.concatParams` | `Param[]` | For concat | Concat-specific parameters (template, join character) |
| `inputs.splitParams` | `Param[]` | For split | Split-specific parameters (delimiters) |
| `outputs` | `Variable[]` | Yes | Single output named `output` |

### Concat Mode Fields (within `concatParams`)

| Param Name | Type | Description |
|------------|------|-------------|
| `concatResult` | string | Template string with `{{variable}}` references for rendering |
| `arrayItemConcatChar` | string | Character used to join array elements when an input is an array |
| `allArrayItemConcatChars` | array | All available concat character options (including custom) |

### Split Mode Fields (within `splitParams`)

| Param Name | Type | Description |
|------------|------|-------------|
| `delimiters` | string[] | Active delimiter strings. Multiple delimiters are applied sequentially |
| `allDelimiters` | array | All available delimiter options (including custom) |

### Output Variable

| Mode | Output Name | Output Type | Description |
|------|-------------|-------------|-------------|
| concat | `output` | `String` | Rendered template result |
| split | `output` | `Array<String>` | Array of split segments |

## Full Schema

```jsonc
{
  "type": "15",
  "data": {
    "nodeMeta": {
      "title": "Text Processor",
      "icon": "...",
      "subTitle": "",
      "description": "",
      "mainColor": ""
    },
    "inputs": {
      "method": "concat",  // or "split"
      "inputParameters": [
        {
          "name": "String1",
          "input": {
            "type": "ref",
            "content": "",
            "value": { /* reference expression */ }
          }
        }
      ],
      // Concat mode params:
      "concatParams": [
        {
          "name": "concatResult",
          "input": { "type": "literal", "value": { "type": "string", "content": "{{String1}} joined text" } }
        },
        {
          "name": "arrayItemConcatChar",
          "input": { "type": "literal", "value": { "type": "string", "content": "," } }
        },
        {
          "name": "allArrayItemConcatChars",
          "input": { "type": "literal", "value": { "type": "array", "content": [] } }
        }
      ],
      // Split mode params:
      "splitParams": [
        {
          "name": "delimiters",
          "input": { "type": "literal", "value": { "type": "array", "content": [",", ";"] } }
        },
        {
          "name": "allDelimiters",
          "input": { "type": "literal", "value": { "type": "array", "content": [] } }
        }
      ]
    },
    "outputs": [
      { "name": "output", "type": "String", "required": true }
    ]
  }
}
```

## Variable Reference Rules

- **Concat mode**: The `concatResult` template uses `{{variableName}}` syntax to reference input parameters. Array inputs are automatically joined using `arrayItemConcatChar`. Object inputs are JSON-serialized.
- **Split mode**: The first input parameter (conventionally named `String`) provides the string to split. Delimiters are applied sequentially -- each delimiter further splits all segments from the previous delimiter.
- Input parameters support `ref` type (referencing other node outputs) or `literal` type.

## Runtime Behavior

- **Concat**: Renders the template by substituting variable references, joining arrays with the concat character, and serializing objects to JSON.
- **Split**: Takes the `String` input, applies each delimiter in order. Returns `[]any` (array of strings).

## Example JSON Snippet

### Concat Mode
```json
{
  "data": {
    "inputs": {
      "method": "concat",
      "inputParameters": [
        { "name": "greeting", "input": { "type": "ref" } },
        { "name": "name", "input": { "type": "ref" } }
      ],
      "concatParams": [
        {
          "name": "concatResult",
          "input": { "type": "literal", "value": { "type": "string", "content": "{{greeting}}, {{name}}!" } }
        },
        {
          "name": "arrayItemConcatChar",
          "input": { "type": "literal", "value": { "type": "string", "content": "" } }
        },
        {
          "name": "allArrayItemConcatChars",
          "input": { "type": "literal", "value": { "type": "array", "content": [] } }
        }
      ]
    },
    "outputs": [
      { "name": "output", "type": "String", "required": true }
    ]
  }
}
```

### Split Mode
```json
{
  "data": {
    "inputs": {
      "method": "split",
      "inputParameters": [
        { "name": "String", "input": { "type": "ref" } }
      ],
      "splitParams": [
        {
          "name": "delimiters",
          "input": { "type": "literal", "value": { "type": "array", "content": [","] } }
        },
        {
          "name": "allDelimiters",
          "input": { "type": "literal", "value": { "type": "array", "content": [] } }
        }
      ]
    },
    "outputs": [
      { "name": "output", "type": "Array<String>", "required": true }
    ]
  }
}
```
