# End Node (type: "2")

## Purpose
Terminal node of a workflow; collects output variables and optionally provides an answer content response.

## Core Fields
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `inputs.inputParameters` | `InputValueDTO[]` | Yes | The variables to collect as workflow output. Each item has a `name` and a reference `input` expression pointing to an upstream node's output. |
| `inputs.terminatePlan` | `TerminatePlan` | Yes | How the workflow terminates: `"returnVariables"` or `"useAnswerContent"`. |
| `inputs.streamingOutput` | `boolean` | No | Whether to stream the answer content. Only relevant when `terminatePlan` is `"useAnswerContent"`. Defaults to `true` in chatflow. |
| `inputs.content` | `ValueExpressionDTO` | No | Template string for the answer content. Only used when `terminatePlan` is `"useAnswerContent"`. Stored as a literal string expression with type `"string"`. |
| `nodeMeta` | `NodeMetaFE` | No | Frontend display metadata. |

## Full Schema

### Frontend FormData (`end/types.ts`)
```typescript
enum TerminatePlan {
  ReturnVariables = 'returnVariables',
  UseAnswerContent = 'useAnswerContent',
}

type FormData = {
  inputs: {
    inputParameters: InputValueVO[];
    terminatePlan?: TerminatePlan;
    streamingOutput?: boolean;
    content?: string;              // plain string in form; wrapped to ValueExpressionDTO on submit
  };
} & Pick<BaseNodeDataDTO, 'nodeMeta'>;
```

### Backend DTO (`end/types.ts`)
```typescript
interface NodeDataDTO {
  inputs: {
    inputParameters?: InputValueDTO[];
    terminatePlan?: TerminatePlan;
    streamingOutput?: boolean;
    content?: ValueExpressionDTO;   // { type: "string", value: { type: "literal", content: "..." } }
  };
}
```

### Backend Go (`exit/exit.go`)
- **Config**: `{ Template string; TerminatePlan vo.TerminatePlan }`
- **NodeSchema**: type = `"Exit"`, key must be the fixed `entity.ExitNodeKey`.
- When `TerminatePlan` is `ReturnVariables`, the node simply passes through input variables as output.
- When `TerminatePlan` is `UseAnswerContent`, an `OutputEmitter` is built with the template string, which renders variable references and streams content.

### InputParameter Definition (each item in `inputs.inputParameters`)
| Field | Type | Description |
|-------|------|-------------|
| `name` | `string` | Output variable name |
| `input` | `ValueExpressionDTO` | Reference expression pointing to an upstream variable. Typically `{ type: "ref", content: { sourceNodeId, outputKey } }`. |

### Frontend Constants (`end/constants.ts`)
| Constant | Value | Description |
|----------|-------|-------------|
| `INPUT_PATH` | `"inputs.inputParameters"` | Path to input parameters in form data |
| `TERMINATE_PLAN_PATH` | `"inputs.terminatePlan"` | Path to terminate plan |
| `ANSWER_CONTENT_PATH` | `"inputs.content"` | Path to answer content |
| `STREAMING_OUTPUT_PATH` | `"inputs.streamingOutput"` | Path to streaming output flag |

### Default Values (from `data-transformer.ts`)
| Field | Workflow Default | Chatflow Default |
|-------|-----------------|------------------|
| `inputParameters` | `[{ name: 'output' }]` | `[{ name: 'output' }]` |
| `streamingOutput` | `false` | `true` |
| `terminatePlan` | `"returnVariables"` | `"useAnswerContent"` |

## Node Registry Metadata
| Property | Value |
|----------|-------|
| `type` | `StandardNodeType.End` = `"2"` |
| `nodeDTOType` | `"2"` |
| `isNodeEnd` | `true` |
| `deleteDisable` | `true` |
| `copyDisable` | `true` |
| `headerReadonly` | `true` |
| `size` | `{ width: 360, height: 78.2 }` |
| `defaultPorts` | `[{ type: 'input' }]` (input only, no output port) |
| Backend NodeType | `"Exit"` (ID: 2) |

## Variable Reference Rules
- End node consumes variables from upstream nodes via `inputParameters[].input` reference expressions.
- When using `"useAnswerContent"`, the `content` field is a template string that can embed variable references like `{{nodeId.variableName}}`.
- The end node does not produce output variables for other nodes.

## Example Snippet

### ReturnVariables mode
```json
{
  "id": "1",
  "type": "2",
  "data": {
    "nodeMeta": {
      "title": "End"
    },
    "inputs": {
      "terminatePlan": "returnVariables",
      "inputParameters": [
        {
          "name": "output",
          "input": {
            "type": "ref",
            "content": {
              "sourceNodeId": "some_node_id",
              "outputKey": "result"
            }
          }
        }
      ]
    }
  }
}
```

### UseAnswerContent mode
```json
{
  "id": "1",
  "type": "2",
  "data": {
    "nodeMeta": {
      "title": "End"
    },
    "inputs": {
      "terminatePlan": "useAnswerContent",
      "streamingOutput": true,
      "content": {
        "type": "string",
        "value": {
          "type": "literal",
          "content": "The answer is: {{some_node_id.result}}"
        }
      },
      "inputParameters": [
        {
          "name": "output",
          "input": {
            "type": "ref",
            "content": {
              "sourceNodeId": "some_node_id",
              "outputKey": "result"
            }
          }
        }
      ]
    }
  }
}
```
