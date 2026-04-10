## coze.cn Cloud YAML Format

YAML type: `to_json` / `from_json` | Status: 未验证

> This node type's cloud YAML format is based on source code analysis.
> For verified format, export a real workflow from coze.cn containing this node.

```yaml
    - id: "200001"
      type: to_json
      title: JSON序列化
      position:
        x: 0
        y: 0
      parameters:
        node_inputs:
            - name: input
              input:
                type: string
                value:
                    path: output
                    ref_node: "100001"
        node_outputs:
            output:
                type: string
                value: null
```

---

# JSON Stringify Node

## Purpose

Converts any input value (object, array, scalar) into its JSON string representation. The backend also supports the inverse operation (JSON deserialization) as a separate node type. Node type IDs: `58` (frontend JsonStringify) / `JsonSerialization` and `JsonDeserialization` (backend).

## Core Fields

### JSON Stringify (Serialization)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `inputs.inputParameters` | `InputParam[]` | Yes | Single input parameter, conventionally named `input` |
| `outputs` | `Variable[]` | Yes | Single output named `output` of type `String` |

### JSON Parse (Deserialization)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `inputs.inputParameters` | `InputParam[]` | Yes | Single input parameter named `input` (must be a JSON string) |
| `outputs` | `Variable[]` | Yes | Single output named `output` with user-defined type schema |

## Full Schema

### JSON Stringify
```jsonc
{
  "type": "58",
  "data": {
    "inputs": {
      "inputParameters": [
        {
          "name": "input",
          "input": {
            "type": "ref",
            "content": "",
            "value": { /* reference to any variable */ }
          }
        }
      ]
    },
    "outputs": [
      { "name": "output", "type": "String" }
    ]
  }
}
```

### JSON Parse (Deserialization)
```jsonc
{
  "data": {
    "inputs": {
      "inputParameters": [
        {
          "name": "input",
          "input": {
            "type": "ref",
            "content": "",
            "value": { /* reference to a string variable containing JSON */ }
          }
        }
      ]
    },
    "outputs": [
      {
        "name": "output",
        "type": "Object",  // or "Array", "String", "Integer", "Number", "Boolean"
        "children": [
          // Nested type schema for structured output
        ]
      }
    ]
  }
}
```

## Variable Reference Rules

- **Stringify**: The `input` parameter can reference any variable type (object, array, string, number, etc.). The output is always a JSON string.
- **Parse**: The `input` must be a string containing valid JSON. The output type is defined by the `outputs` schema and the backend performs type conversion/validation.
- Default input parameter name: `input`. Default output name: `output`.

## Runtime Behavior

### Serialization
- Takes the value from `input` key in the input map
- Marshals it to JSON using `sonic.Marshal`
- Returns `{"output": "<json_string>"}`
- Returns error if input is nil

### Deserialization
- Takes the string value from `input` key
- Unmarshals based on the declared output type (scalar, array, or object)
- Performs type conversion against the output schema
- Emits warnings (not errors) for type mismatches that can be coerced
- Returns `{"output": <parsed_value>}`

## Example JSON Snippet

```json
{
  "data": {
    "inputs": {
      "inputParameters": [
        {
          "name": "input",
          "input": {
            "type": "ref",
            "content": "",
            "value": {
              "type": "reference",
              "content": "{{nodeId.output}}"
            }
          }
        }
      ]
    },
    "outputs": [
      { "name": "output", "type": "String" }
    ]
  }
}
```
