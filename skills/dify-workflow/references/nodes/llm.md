# LLM Node (`llm`)

## Purpose
Invokes a large language model with a configurable prompt template, optional context from knowledge retrieval, conversation memory, and vision capabilities.

## Core Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `model` | `ModelConfig` | Yes | Model provider, name, mode, and completion parameters |
| `prompt_template` | `PromptItem[]` or `PromptItem` | Yes | Prompt messages (array for chat models, single item for completion models) |
| `context` | `object` | Yes | Whether to inject retrieved knowledge context |
| `vision` | `object` | Yes | Whether to enable vision/image input |
| `prompt_config` | `object` | No | Configuration for Jinja2 template variables |
| `memory` | `Memory` | No | Conversation memory settings (chatflow only) |
| `structured_output_enabled` | `boolean` | No | Enable structured JSON output (model must support it) |
| `structured_output` | `StructuredOutput` | No | JSON schema defining the structured output format |
| `reasoning_format` | `string` | No | Reasoning output format. Enum: `"tagged"`, `"separated"` |

## Full Schema

### ModelConfig

```yaml
model:
  provider: ""          # string, required - Model provider identifier (e.g. "openai", "anthropic")
  name: ""              # string, required - Model name (e.g. "gpt-4o", "claude-sonnet-4-20250514")
  mode: "chat"          # string, required - "chat" or "completion"
  completion_params:    # Record<string, any>, required - Model-specific parameters
    temperature: 0.7    # number, common param (0-2)
    # Other params vary by model: top_p, max_tokens, presence_penalty, frequency_penalty, etc.
```

### PromptItem

For **chat models** (`mode: "chat"`), `prompt_template` is an array of `PromptItem`:

```yaml
prompt_template:
  - role: "system"           # PromptRole: "system" | "user" | "assistant"
    text: "You are a helpful assistant. {{#context#}}"
    edition_type: "basic"    # optional: "basic" (default) | "jinja2"
    jinja2_text: ""          # optional: Jinja2 template text (used when edition_type is "jinja2")
  - role: "user"
    text: "{{#sys.query#}}"
```

For **completion models** (`mode: "completion"`), `prompt_template` is a single `PromptItem`:

```yaml
prompt_template:
  text: "Answer the question: {{#sys.query#}}"
  edition_type: "basic"
  jinja2_text: ""
```

**PromptRole enum values:** `"system"`, `"user"`, `"assistant"`

**EditionType enum values:** `"basic"`, `"jinja2"`

### prompt_config (Jinja2 Variables)

When using `edition_type: "jinja2"` in prompts, map Jinja2 variable names to workflow variable selectors:

```yaml
prompt_config:
  jinja2_variables:
    - variable: "my_var"                    # string - Jinja2 variable name
      value_selector: ["node_id", "output"] # ValueSelector - reference to upstream node output
```

### Context

Injects knowledge retrieval results into the prompt. Typically connected to a Knowledge Retrieval node.

```yaml
context:
  enabled: false              # boolean, required - Whether context injection is active
  variable_selector: []       # ValueSelector (string[]) - Points to a knowledge retrieval node's output
                              # e.g. ["knowledge_retrieval_node_id", "result"]
```

When enabled, use `{{#context#}}` in your prompt template to insert the retrieved content.

### Vision

Enables image input processing for multimodal models.

```yaml
vision:
  enabled: false              # boolean, required - Whether vision is active
  configs:                    # VisionSetting, optional (required when enabled)
    variable_selector: []     # ValueSelector - Points to a file/image variable
    detail: "high"            # Resolution: "high" | "low"
```

### Memory (Chatflow Only)

Configures conversation history injection. Only applicable in chatflow (advanced-chat) apps.

```yaml
memory:
  role_prefix:                # optional - Custom prefixes for completion models
    user: "Human"
    assistant: "Assistant"
  window:
    enabled: false            # boolean - Whether to limit conversation history window
    size: 50                  # number | string | null - Number of recent messages to include
  query_prompt_template: ""   # string - Template for the user query message
                              # Must include {{#sys.query#}} when set
                              # Default (when empty): "{{#sys.query#}}"
```

### StructuredOutput

Defines a JSON schema that constrains the model output to a specific structure.

```yaml
structured_output_enabled: true
structured_output:
  schema:
    type: "object"
    properties:
      field_name:
        type: "string"            # Type enum: "string" | "number" | "boolean" | "object" | "array" |
                                  #   "array[string]" | "array[number]" | "array[object]" | "file" | "enum"
        description: "Field desc"
        enum: ["val1", "val2"]    # optional, for enum type
        properties: {}            # optional, for object type - nested field definitions
        required: ["child_key"]   # optional, for object type - required child keys
        items:                    # optional, for array type - defines item schema
          type: "string"
          description: ""
        additionalProperties: false  # required for object types
    required: ["field_name"]
    additionalProperties: false      # always false at root
```

**Structured output Type enum values:**
- `"string"`, `"number"`, `"boolean"`, `"object"`, `"array"`
- `"array[string]"`, `"array[number]"`, `"array[object]"`
- `"file"`, `"enum"`

## Variable Reference Rules

### Input Variables
- Reference upstream node outputs in prompt text: `{{#node_id.variable_name#}}`
- Reference start node inputs: `{{#sys.query#}}`, `{{#sys.files#}}`
- Context placeholder: `{{#context#}}` (requires `context.enabled: true`)
- Conversation history: automatically injected when `memory` is set

### System Variables Available
- `{{#sys.query#}}` - User query input
- `{{#sys.files#}}` - User uploaded files
- `{{#sys.conversation_id#}}` - Conversation ID (chatflow only)
- `{{#sys.user_id#}}` - User ID

### Output Variables

| Variable | Type | Description |
|----------|------|-------------|
| `text` | `string` | The generated text response from the LLM |
| `reasoning_content` | `string` | The model's reasoning/thinking content (if supported) |
| `usage` | `object` | Token usage information (prompt_tokens, completion_tokens, total_tokens, etc.) |

When `structured_output_enabled` is true, the output also includes fields defined in the structured output schema, accessible as additional output variables.

## Default Values

```yaml
model:
  provider: ""
  name: ""
  mode: "chat"
  completion_params:
    temperature: 0.7
prompt_template:
  - role: "system"
    text: ""
context:
  enabled: false
  variable_selector: []
vision:
  enabled: false
```

## Example Snippet

Minimal LLM node in a workflow (chat model):

```yaml
- data:
    type: llm
    title: "Generate Response"
    model:
      provider: "openai"
      name: "gpt-4o-mini"
      mode: "chat"
      completion_params:
        temperature: 0.7
        max_tokens: 1024
    prompt_template:
      - role: "system"
        text: "You are a helpful assistant."
      - role: "user"
        text: "{{#sys.query#}}"
    context:
      enabled: false
      variable_selector: []
    vision:
      enabled: false
```

LLM node with context from knowledge retrieval:

```yaml
- data:
    type: llm
    title: "Answer with Knowledge"
    model:
      provider: "openai"
      name: "gpt-4o"
      mode: "chat"
      completion_params:
        temperature: 0.3
    prompt_template:
      - role: "system"
        text: |
          Answer the user's question based on the following context.
          {{#context#}}
      - role: "user"
        text: "{{#sys.query#}}"
    context:
      enabled: true
      variable_selector: ["knowledge_retrieval_1", "result"]
    vision:
      enabled: false
```

LLM node with structured output:

```yaml
- data:
    type: llm
    title: "Extract Entities"
    model:
      provider: "openai"
      name: "gpt-4o"
      mode: "chat"
      completion_params:
        temperature: 0
    prompt_template:
      - role: "system"
        text: "Extract entities from the text."
      - role: "user"
        text: "{{#start.input_text#}}"
    context:
      enabled: false
      variable_selector: []
    vision:
      enabled: false
    structured_output_enabled: true
    structured_output:
      schema:
        type: "object"
        properties:
          entities:
            type: "array[object]"
            items:
              type: "object"
              properties:
                name:
                  type: "string"
                  description: "Entity name"
                category:
                  type: "string"
                  description: "Entity category"
              required: ["name", "category"]
              additionalProperties: false
        required: ["entities"]
        additionalProperties: false
```

LLM node with memory (chatflow):

```yaml
- data:
    type: llm
    title: "Chat with Memory"
    model:
      provider: "anthropic"
      name: "claude-sonnet-4-20250514"
      mode: "chat"
      completion_params:
        temperature: 0.7
        max_tokens: 2048
    prompt_template:
      - role: "system"
        text: "You are a helpful assistant."
    memory:
      window:
        enabled: true
        size: 20
      query_prompt_template: "{{#sys.query#}}"
    context:
      enabled: false
      variable_selector: []
    vision:
      enabled: false
```
