# Tool (`tool`)

## Purpose
Invokes an external tool (built-in, custom API, workflow, or MCP) within a workflow, passing parameters and capturing the tool's output.

## Core Fields
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `provider_id` | `string` | Yes | Unique identifier for the tool provider |
| `provider_type` | `CollectionType` | Yes | Type of tool provider (see enum below) |
| `provider_name` | `string` | Yes | Display name of the tool provider |
| `tool_name` | `string` | Yes | Name of the specific tool to invoke |
| `tool_label` | `string` | Yes | Human-readable label for the tool |
| `tool_parameters` | `ToolVarInputs` | Yes | Input parameter values for the tool |
| `tool_configurations` | `Record<string, any>` | Yes | Tool-specific configuration/settings |

## Full Schema

### All Fields
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `provider_id` | `string` | Yes | Tool provider identifier |
| `provider_type` | `CollectionType` | Yes | Provider type enum value |
| `provider_name` | `string` | Yes | Provider display name |
| `tool_name` | `string` | Yes | Tool name within the provider |
| `tool_label` | `string` | Yes | Human-readable tool label |
| `tool_parameters` | `ToolVarInputs` | Yes | Map of parameter name to input value |
| `tool_configurations` | `Record<string, any>` | Yes | Static tool configuration values |
| `tool_node_version` | `string` | No | Node version; defaults to `"2"` |
| `tool_description` | `string` | No | Description of the tool |
| `version` | `string` | No | Tool version |
| `paramSchemas` | `Record<string, any>[]` | No | Schema definitions for parameters |
| `is_team_authorization` | `boolean` | No | Whether team-level auth is used |
| `params` | `Record<string, any>` | No | Additional parameters |
| `plugin_id` | `string` | No | Plugin identifier |
| `plugin_unique_identifier` | `string` | No | Unique plugin identifier |

### CollectionType (provider_type)
| Value | DSL Value | Description |
|-------|-----------|-------------|
| `builtIn` | `"builtin"` | Built-in tool bundled with Dify |
| `custom` | `"api"` | Custom API tool |
| `workflow` | `"workflow"` | Another workflow exposed as a tool |
| `mcp` | `"mcp"` | MCP (Model Context Protocol) tool |

### ToolVarInputs (tool_parameters)
A record mapping parameter names to input descriptors:
```typescript
Record<string, {
  type: VarKindType   // "variable" | "constant" | "mixed"
  value?: string | ValueSelector | any
}>
```

Each parameter entry specifies:
| Field | Type | Description |
|-------|------|-------------|
| `type` | `"variable" \| "constant" \| "mixed"` | Whether the value is a reference to another node's output, a literal constant, or a mixed template |
| `value` | `string \| ValueSelector \| any` | The actual value: a literal string for `"constant"`, a `ValueSelector` array for `"variable"` (e.g. `["node-id", "field"]`), or a template string for `"mixed"` |

### tool_configurations
A plain key-value map for tool-specific settings that do not change per-run (e.g., API keys, base URLs, static config). Required fields depend on the specific tool's schema.

## Variable Reference Rules

**Inputs:**
- Each entry in `tool_parameters` can reference upstream variables using `type: "variable"` with a `ValueSelector` as the value.
- Constants are passed directly with `type: "constant"` and a literal string value.
- Mixed mode (`type: "mixed"`) allows template strings with variable interpolation.

**Outputs:**
The default output structure (when the tool does not define a custom output schema):
| Variable | Type | Description |
|----------|------|-------------|
| `text` | `string` | Text output from the tool |
| `files` | `array[file]` | File outputs from the tool |
| `json` | `array[object]` | Structured JSON output from the tool |

When a tool defines a custom `output_schema`, additional output variables are available based on that schema's properties.

Output variables are referenced by downstream nodes as `[node_id, "text"]`, `[node_id, "json"]`, etc.

## Example Snippet
```yaml
nodes:
  - data:
      type: tool
      title: Search the Web
      provider_id: langgenius/duckduckgo/duckduckgo
      provider_type: builtin
      provider_name: duckduckgo
      tool_name: ddg_search
      tool_label: DuckDuckGo Search
      tool_node_version: "2"
      tool_parameters:
        query:
          type: variable
          value:
            - sys
            - query
        max_results:
          type: constant
          value: "5"
      tool_configurations: {}
    id: tool-1
```
