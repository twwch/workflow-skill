# Code Node (type: "5")

## Purpose
Executes user-written code (Python or JavaScript/TypeScript) with defined input parameters and structured output variables.

## Core Fields
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `inputs.code` | `string` | Yes | The source code to execute. |
| `inputs.language` | `int64` | Yes | Programming language: `3` = Python, `5` = JavaScript/TypeScript. |
| `inputs.inputParameters` | `InputValueDTO[]` | No | Input variables passed to the code as function arguments. |
| `outputs` | `VariableMetaDTO[]` | Yes | Output variable definitions. The code must return an object matching these fields. |
| `nodeMeta` | `NodeMetaFE` | No | Frontend display metadata. |

## Full Schema

### Frontend FormData (`code/types.ts`)
```typescript
interface FormData {
  inputParameters: InputValueVO[];
  nodeMeta: NodeDataDTO['nodeMeta'];
  outputs: OutputValueVO[];
  codeParams: CodeEditorValue;       // { code: string; language: LanguageEnum }
}
```

### Frontend CodeEditorValue
```typescript
interface CodeEditorValue {
  code: string;
  language: LanguageEnum;  // 3 = Python, 5 = TypeScript
}
```

### Language Enum (`code/constants.ts`)
| Value | Language | Display Name |
|-------|----------|-------------|
| `3` | Python | Python |
| `5` | TypeScript | JavaScript |

Note: The open-source version only supports Python (backend limitation).

### Backend DTO (submitted format from `transformOnSubmit`)
```typescript
{
  nodeMeta: NodeMetaFE;
  inputs: {
    inputParameters: InputValueDTO[];
    code: string;
    language: LanguageEnum;
  };
  outputs: VariableMetaDTO[];
}
```

### Backend Go Config (`code/code.go`)
```go
type Config struct {
    Code     string
    Language coderunner.Language   // "python" or "javascript"
}
```

### Backend Language Mapping
| Frontend Value | Backend Value | coderunner.Language |
|----------------|--------------|---------------------|
| `3` | Python | `"python"` |
| `5` | JavaScript | `"javascript"` |

### Backend Go Runner (`code/code.go`)
```go
type Runner struct {
    outputConfig map[string]*vo.TypeInfo
    code         string
    language     coderunner.Language
    runner       coderunner.Runner
    importError  error
}
```

### Canvas VO (`vo/canvas.go`)
```go
type CodeRunner struct {
    Code     string `json:"code"`
    Language int64  `json:"language"`
}
```

### Frontend Constants (`code/constants.ts`)
| Constant | Value | Description |
|----------|-------|-------------|
| `INPUT_PATH` | `"inputParameters"` | Form path for input parameters |
| `CODE_PATH` | `"codeParams"` | Form path for code editor value |
| `OUTPUT_PATH` | `"outputs"` | Form path for output variables |

### Default Values
**Default Inputs:**
```typescript
[{ name: 'input' }]
```

**Default Outputs:**
```typescript
[
  { name: 'key0', type: ViewVariableType.String },        // 1
  { name: 'key1', type: ViewVariableType.ArrayString },    // 99
  {
    name: 'key2', type: ViewVariableType.Object,           // 6
    children: [
      { name: 'key21', type: ViewVariableType.String },    // 1
    ],
  },
]
```

**Default Python Code Template:**
```python
async def main(args: Args) -> Output:
    params = args.params
    # your logic here
    ret: Output = {
        "key0": "value0",
        "key1": ["value1"],
        "key2": {
            "key21": "value21"
        }
    }
    return ret
```

**Default TypeScript Code Template:**
```typescript
async function main({ params }: Args): Promise<Output> {
    const ret = {
        "key0": "value0",
        "key1": ["value1"],
        "key2": {
            "key21": "value21"
        }
    };
    return ret;
}
```

### Python Import Validation
The backend validates Python imports at build time:
- **Allowed**: Python standard library modules (except blacklisted ones) and whitelisted third-party modules.
- **Blacklisted standard library modules**: `curses`, `dbm`, `ensurepip`, `fcntl`, `grp`, `idlelib`, `lib2to3`, `msvcrt`, `pwd`, `resource`, `syslog`, `termios`, `tkinter`, `turtle`, `turtledemo`, `venv`, `winreg`, `winsound`, `multiprocessing`, `threading`, `socket`, `pty`, `tty`.
- **Third-party modules**: Only modules in the configured whitelist are allowed.

## Node Registry Metadata
| Property | Value |
|----------|-------|
| `type` | `StandardNodeType.Code` = `"5"` |
| `nodeDTOType` | `"5"` |
| `size` | default node size, styled with `width: 484` |
| `inputParametersPath` | `"inputParameters"` |
| `outputsPath` | default outputs path |
| Backend NodeType | `"CodeRunner"` (ID: 5) |

## Variable Reference Rules
- Input variables are defined in `inputs.inputParameters` and passed to the code function as `params` (Python: `args.params`, TypeScript: `{ params }`).
- Each input maps to an upstream node output via a reference expression.
- Output variables are defined in `outputs` and must match the return value structure of the code.
- Downstream nodes reference outputs as `{{node_id.variable_name}}`.
- For Object types, nested fields can be referenced as `{{node_id.variable_name.child_name}}`.

## Example Snippet
```json
{
  "id": "node_xyz",
  "type": "5",
  "data": {
    "nodeMeta": {
      "title": "Code"
    },
    "inputs": {
      "inputParameters": [
        {
          "name": "input",
          "input": {
            "type": "ref",
            "content": {
              "sourceNodeId": "0",
              "outputKey": "user_input"
            }
          }
        }
      ],
      "code": "async def main(args: Args) -> Output:\n    params = args.params\n    ret: Output = {\n        \"result\": params[\"input\"].upper()\n    }\n    return ret",
      "language": 3
    },
    "outputs": [
      {
        "name": "result",
        "type": 1
      }
    ]
  }
}
```
