# Dify Workflow DSL Format Reference

This document describes the YAML structure of a Dify workflow DSL file, extracted from the Dify source code. The current DSL version is `0.6.0`.

Source files:
- `api/services/app_dsl_service.py` -- export/import logic
- `api/models/workflow.py` -- `Workflow.to_dict()`, `WorkflowContentDict`
- `web/app/components/workflow/types.ts` -- frontend type definitions
- `api/core/workflow/system_variables.py` -- system variable keys
- `api/core/workflow/variable_prefixes.py` -- variable node ID prefixes
- `api/tests/fixtures/workflow/*.yml` -- real workflow examples

---

## Top-Level Structure

```yaml
version: "0.6.0"          # Required. String. DSL version.
kind: "app"                # Required. Must be "app".
app:                       # Required. App metadata object.
  ...
workflow:                  # Required for mode "workflow" or "advanced-chat".
  ...
dependencies:              # Optional. List of plugin dependencies.
  - type: marketplace
    value:
      marketplace_plugin_unique_identifier: "org/plugin:version@hash"
    current_identifier: null
```

### Version compatibility rules

| Condition | Import status |
|---|---|
| Imported version > current version | `pending` (requires confirmation) |
| Imported major < current major | `pending` |
| Imported minor < current minor | `completed-with-warnings` |
| Same or micro difference only | `completed` |

---

## `app` -- App Metadata

```yaml
app:
  name: "My Workflow"                # Required. String. Display name.
  mode: "workflow"                   # Required. One of the app modes (see below).
  description: "What this app does"  # Optional. String.
  icon: "\U0001F916"                 # Optional. Emoji string or image URL/ID.
  icon_type: "emoji"                 # Optional. "emoji" | "image" | "link". Defaults to "emoji".
  icon_background: "#FFEAD5"         # Optional. Hex color string. Defaults to "#FFFFFF".
  use_icon_as_answer_icon: false     # Optional. Boolean. Defaults to false.
```

### App modes (relevant to workflow DSL)

| Value | Description |
|---|---|
| `workflow` | Standalone workflow app (uses Start/End nodes) |
| `advanced-chat` | Chatflow app (uses Start/Answer nodes, supports memory) |

Other modes (`completion`, `chat`, `agent-chat`, `channel`, `rag-pipeline`) use `model_config` instead of `workflow` and are not covered here.

---

## `workflow` -- Workflow Content

```yaml
workflow:
  graph:                        # Required. The workflow graph.
    nodes: []                   # Required. List of node objects.
    edges: []                   # Required. List of edge objects.
    viewport:                   # Optional. Canvas viewport state.
      x: 0
      y: 0
      zoom: 0.7
  features: {}                  # Required. App feature flags (see below).
  environment_variables: []     # Optional. List of environment variable objects.
  conversation_variables: []    # Optional. List of conversation variable objects.
```

This structure is defined by `WorkflowContentDict` in `api/models/workflow.py`:
```python
class WorkflowContentDict(TypedDict):
    graph: Mapping[str, Any]
    features: dict[str, Any]
    environment_variables: list[dict[str, Any]]
    conversation_variables: list[dict[str, Any]]
    rag_pipeline_variables: list[dict[str, Any]]
```

---

## Node Object Format

Each node in `graph.nodes` has this structure:

```yaml
- id: "node_id_string"          # Required. Unique node ID (typically a timestamp string).
  data:                          # Required. Node configuration.
    type: "start"                # Required. Node type (see BlockEnum below).
    title: "Start"               # Required. Display title.
    desc: ""                     # Optional. Description string.
    # ... type-specific fields (see per-node sections below)
  position:                      # Required. Canvas position.
    x: 80
    y: 282
  # Optional layout fields (used by the UI, safe to include):
  positionAbsolute:              # Optional. Absolute position on canvas.
    x: 80
    y: 282
  width: 244                     # Optional. Node width in pixels.
  height: 90                     # Optional. Node height in pixels.
  type: custom                   # Optional. ReactFlow node type. Always "custom" for normal nodes.
  selected: false                # Optional. Whether node is selected in UI.
  sourcePosition: right          # Optional. Default "right".
  targetPosition: left           # Optional. Default "left".
  zIndex: 0                      # Optional. Stacking order.
  parentId: "iteration_node_id"  # Optional. Set when node is inside an iteration/loop.
  draggable: false               # Optional. Set to false for iteration-start nodes.
  selectable: false              # Optional. Set to false for iteration-start nodes.
```

### Node types (BlockEnum)

From `web/app/components/workflow/types.ts`:

| Type value | Description |
|---|---|
| `start` | Entry point. Defines input variables. |
| `end` | Terminal node for `workflow` mode. Defines output variables. |
| `answer` | Terminal node for `advanced-chat` mode. Streams text output. |
| `llm` | Large Language Model call. |
| `knowledge-retrieval` | Query knowledge bases. |
| `question-classifier` | Classify input into categories. |
| `if-else` | Conditional branching. |
| `code` | Execute Python/JavaScript code. |
| `template-transform` | Jinja2 template rendering. |
| `http-request` | Make HTTP requests. |
| `variable-assigner` | Legacy name. Assign values to variables. |
| `variable-aggregator` | Aggregate variables from multiple branches. |
| `tool` | Call an external tool/plugin. |
| `parameter-extractor` | Extract structured parameters from text using LLM. |
| `iteration` | Iterate over an array, running child nodes per element. |
| `iteration-start` | Auto-generated start node inside an iteration. |
| `document-extractor` | Extract text from documents. |
| `list-operator` | Filter/sort/limit list data. |
| `assigner` | Current variable assigner (renamed from variable-assigner). |
| `agent` | Agent node with tool access. |
| `loop` | Loop with break condition. |
| `loop-start` | Auto-generated start node inside a loop. |
| `loop-end` | Auto-generated end node inside a loop. |
| `human-input` | Pause and wait for human input. |

---

## Edge Object Format

Each edge in `graph.edges` connects two nodes:

```yaml
- id: "unique_edge_id"           # Required. Unique edge ID.
  source: "source_node_id"       # Required. ID of the source node.
  sourceHandle: "source"         # Required. Output handle name.
                                 #   "source" for default output.
                                 #   "true" / "false" for if-else branches.
                                 #   Case ID string for question-classifier.
  target: "target_node_id"       # Required. ID of the target node.
  targetHandle: "target"         # Required. Input handle name. Always "target".
  type: custom                   # Optional. Always "custom".
  zIndex: 0                      # Optional. Stacking order.
  data:                          # Optional. Edge metadata.
    sourceType: "start"          # Node type of the source.
    targetType: "llm"            # Node type of the target.
    isInIteration: false         # Whether this edge is inside an iteration.
    isInLoop: false              # Whether this edge is inside a loop.
    iteration_id: "iter_node_id" # Set when isInIteration is true.
```

---

## Variable Reference Syntax

Dify uses two reference syntaxes depending on context:

### Template string syntax (in prompt text, answer text, template-transform templates)

```
{{#node_id.output_key#}}
```

Examples:
- `{{#start_node.query#}}` -- reference the `query` variable from the start node
- `{{#llm_node.text#}}` -- reference the `text` output from an LLM node
- `{{#http_node.body#}}` -- reference the `body` output from an HTTP request node

### Value selector syntax (in structured fields like `value_selector`, `variable_selector`, `iterator_selector`)

An array of strings forming a path: `[node_id, key]`

```yaml
value_selector:
  - "start_node"
  - "query"
```

For system variables: `["sys", "query"]`
For environment variables: `["env", "var_name"]`
For conversation variables: `["conversation", "var_name"]`

---

## System Variables

Referenced as `{{#sys.variable_name#}}` in templates, or `["sys", "variable_name"]` in selectors.

Defined in `api/core/workflow/system_variables.py` (`SystemVariableKey`):

| Variable | Description |
|---|---|
| `sys.query` | User's input query (advanced-chat mode) |
| `sys.files` | Uploaded files |
| `sys.conversation_id` | Current conversation ID (advanced-chat mode) |
| `sys.user_id` | Current user ID |
| `sys.dialogue_count` | Number of dialogue turns |
| `sys.app_id` | Application ID |
| `sys.workflow_id` | Workflow ID |
| `sys.workflow_run_id` | Current workflow execution ID |
| `sys.timestamp` | Current timestamp |

Variable node ID prefixes (from `api/core/workflow/variable_prefixes.py`):
- `sys` -- system variables
- `env` -- environment variables
- `conversation` -- conversation variables
- `rag` -- RAG pipeline variables

---

## Features Block

The `features` block controls app-level behavior. Structure:

```yaml
features:
  file_upload:                          # File upload configuration.
    enabled: false                      # Boolean. Whether file upload is enabled.
    allowed_file_types:                 # List. Allowed file type categories.
      - image
    allowed_file_extensions:            # List. Allowed file extensions.
      - .JPG
      - .PNG
    allowed_file_upload_methods:        # List. Upload methods.
      - local_file
      - remote_url
    number_limits: 3                    # Integer. Max number of files.
    # Legacy sub-field (auto-normalized on import):
    image:
      enabled: false
      number_limits: 3
      transfer_methods:
        - local_file
        - remote_url
    fileUploadConfig:                   # Optional. Size limit configuration.
      audio_file_size_limit: 50
      batch_count_limit: 5
      file_size_limit: 15
      image_file_size_limit: 10
      video_file_size_limit: 100
      workflow_file_upload_limit: 10
  opening_statement: ""                 # String. Opening message for chat apps.
  suggested_questions: []               # List of strings. Initial suggested questions.
  suggested_questions_after_answer:
    enabled: false                      # Boolean. Show suggestions after answers.
  speech_to_text:
    enabled: false                      # Boolean.
  text_to_speech:
    enabled: false                      # Boolean.
    language: ""                        # String. TTS language.
    voice: ""                           # String. TTS voice.
  retriever_resource:
    enabled: false                      # Boolean. Show citation sources.
  sensitive_word_avoidance:
    enabled: false                      # Boolean. Content moderation.
```

A minimal features block:
```yaml
features:
  file_upload:
    enabled: false
  opening_statement: ""
  retriever_resource:
    enabled: false
  sensitive_word_avoidance:
    enabled: false
  speech_to_text:
    enabled: false
  suggested_questions: []
  suggested_questions_after_answer:
    enabled: false
  text_to_speech:
    enabled: false
```

---

## Environment Variables

```yaml
environment_variables:
  - id: "uuid-string"
    name: "API_KEY"
    value: "sk-..."           # Value (empty string for secrets on export without include_secret)
    value_type: "secret"      # "string" | "number" | "secret"
    description: "API key"
```

On export without `include_secret`, secret variable values are set to empty string.

---

## Conversation Variables

Used in `advanced-chat` mode to persist state across conversation turns.

```yaml
conversation_variables:
  - id: "uuid-string"
    name: "counter"
    value: 0
    value_type: "number"      # ChatVarType values
    description: "Turn counter"
```

---

## Node Type Details

### Start Node

```yaml
data:
  type: start
  title: Start
  desc: ""
  variables:                   # List of input variable definitions.
    - variable: "query"        # Variable name.
      label: "query"           # Display label.
      type: "text-input"       # Input type (see InputVarType below).
      required: true           # Boolean.
      max_length: null         # Optional. Max input length.
      options: []              # For "select" type: list of option strings.
```

Input variable types (`InputVarType`):
- `text-input` -- single-line text
- `paragraph` -- multi-line text
- `select` -- dropdown selection
- `number` -- numeric input
- `url` -- URL input
- `files` -- multiple file upload
- `file` -- single file upload
- `file-list` -- file list
- `json` -- JSON input
- `json_object` -- JSON object with schema support
- `checkbox` -- boolean checkbox

### End Node (workflow mode)

```yaml
data:
  type: end
  title: End
  desc: ""
  outputs:                       # List of output variable mappings.
    - variable: "result"         # Output variable name.
      value_selector:            # Source of the value.
        - "llm_node"
        - "text"
      value_type: "string"       # Output type: string, number, object, array[string], etc.
```

### Answer Node (advanced-chat mode)

```yaml
data:
  type: answer
  title: Answer
  desc: ""
  answer: "{{#llm.text#}}"      # Template string with variable references.
  variables: []
```

### LLM Node

```yaml
data:
  type: llm
  title: LLM
  desc: ""
  model:
    provider: "langgenius/openai/openai"   # Provider identifier.
    name: "gpt-4o"                          # Model name.
    mode: "chat"                            # "chat" or "completion".
    completion_params:                      # Optional. Model parameters.
      temperature: 0.7
  prompt_template:                          # List of prompt messages.
    - id: "optional-uuid"                   # Optional.
      role: "system"                        # "system" | "user" | "assistant"
      text: "You are a helpful assistant."  # Prompt text. Supports {{#ref#}} syntax.
  variables: []                             # Optional. Additional input variable mappings.
  context:
    enabled: false                          # Whether knowledge context is injected.
    variable_selector: []                   # Source of context data.
  vision:
    enabled: false                          # Whether vision/image input is enabled.
    configs:                                # Optional.
      variable_selector: []
  memory:                                   # Optional. Conversation memory (advanced-chat only).
    enabled: false
    window:
      enabled: false
      size: 10                              # Number of recent turns to include.
    query_prompt_template: "{{#sys.query#}}\n\n{{#sys.files#}}"
    role_prefix:                            # Optional.
      user: ""
      assistant: ""
  structured_output:                        # Optional.
    enabled: false
  retry_config:                             # Optional. Retry on failure.
    enabled: false
    max_retries: 1
    retry_interval: 1000
    exponential_backoff:
      enabled: false
      multiplier: 2
      max_interval: 10000
```

### Code Node

```yaml
data:
  type: code
  title: Code
  desc: ""
  code: |
    def main() -> dict:
        return {"result": "hello"}
  code_language: "python3"        # "python3" or "javascript"
  variables: []                   # Input variables mapped from other nodes.
  outputs:                        # Output variable schema (dict, not list).
    result:
      type: "string"             # Variable type.
      children: null              # For object types, nested schema.
```

Note: Code node `outputs` is a **dict** (keyed by variable name), unlike End node `outputs` which is a **list**.

### IF/ELSE Node

```yaml
data:
  type: if-else
  title: IF/ELSE
  desc: ""
  cases:
    - id: "true"                  # Case ID. Used as sourceHandle on edges.
      case_id: "true"
      logical_operator: "and"     # "and" | "or"
      conditions:
        - id: "uuid"
          variable_selector:      # Variable to test.
            - "start_node"
            - "query"
          comparison_operator: "contains"  # See comparison operators below.
          value: "hello"          # Comparison value.
          varType: "string"       # Variable type for comparison.
```

The default/else branch uses sourceHandle `"false"`.

Comparison operators: `contains`, `not contains`, `start with`, `end with`, `is`, `is not`, `empty`, `not empty`, `=`, `!=`, `>`, `<`, `>=`, `<=`, `in`, `not in`, `null`, `not null`.

### Template Transform Node

```yaml
data:
  type: template-transform
  title: Template
  desc: ""
  template: "{{ arg1 }}"         # Jinja2 template string.
  variables:                      # Input variable mappings for the template.
    - variable: "arg1"            # Template variable name.
      value_selector:             # Source value.
        - "llm_node"
        - "text"
      value_type: "string"
```

Output is available as `output` (e.g., `{{#template_node.output#}}`).

### HTTP Request Node

```yaml
data:
  type: http-request
  title: HTTP Request
  desc: ""
  method: "GET"                   # "GET" | "POST" | "PUT" | "DELETE" | "PATCH" | "HEAD"
  url: "{{#start_node.url#}}"    # URL with optional variable references.
  authorization:
    type: "no-auth"               # "no-auth" | "api-key" | "custom"
  headers: ""                     # Key-value pairs as string or structured.
  params: ""                      # Query parameters.
  body:
    type: "none"                  # "none" | "form-data" | "x-www-form-urlencoded" | "raw-text" | "json"
    data: ""
  timeout:
    connect: 10
    read: 30
    write: 30
  retry_config:                   # Optional.
    enabled: false
    max_retries: 1
    retry_interval: 1000
    exponential_backoff:
      enabled: false
      multiplier: 2
      max_interval: 10000
```

Outputs: `status_code` (number), `body` (string), `headers` (string).

### Tool Node

```yaml
data:
  type: tool
  title: Tool
  desc: ""
  provider_id: "builtin"
  provider_type: "builtin"
  provider_name: "Builtin Tools"
  tool_name: "json_parse"
  tool_label: "JSON Parse"
  tool_configurations: {}
  tool_parameters:
    json_string: "{{#http_node.body#}}"
```

### Iteration Node

```yaml
data:
  type: iteration
  title: Iteration
  desc: ""
  iterator_selector:              # Source array to iterate over.
    - "code_node"
    - "result"
  iterator_input_type: "array[number]"
  output_selector:                # Which child node output to collect.
    - "template_node"
    - "output"
  output_type: "array[string]"
  start_node_id: "iter_node_idstart"   # ID of the iteration-start child node.
  is_parallel: false
  parallel_nums: 10
  error_handle_mode: "terminated"      # "terminated" | "continue-on-error" | "remove-abnormal-output"
  width: 388                           # Iteration container width.
  height: 178                          # Iteration container height.
```

Child nodes inside an iteration have:
- `parentId` set to the iteration node ID (on the node object, not inside `data`)
- `isInIteration: true` in their `data`
- `iteration_id` set to the iteration node ID

The iteration-start node:
```yaml
- id: "iter_node_idstart"         # Convention: iteration node ID + "start"
  parentId: "iter_node_id"
  type: custom-iteration-start    # Special ReactFlow type.
  data:
    type: iteration-start
    title: ""
    desc: ""
    isInIteration: true
  draggable: false
  selectable: false
```

### Variable Aggregator Node

Used to merge outputs from parallel branches:

```yaml
data:
  type: variable-aggregator
  title: Variable Aggregator
  desc: ""
  variables:
    - value_selector:
        - "branch1_node"
        - "result"
    - value_selector:
        - "branch2_node"
        - "result"
  output_type: "string"
```

---

## Retry Config (shared across node types)

Several node types (LLM, HTTP Request, Code, Tool) support a `retry_config`:

```yaml
retry_config:
  enabled: false
  max_retries: 1                   # Integer. 1-10.
  retry_interval: 1000             # Milliseconds.
  exponential_backoff:
    enabled: false
    multiplier: 2
    max_interval: 10000
```

---

## Error Handling (shared across node types)

Nodes can define error handling behavior:

```yaml
error_strategy: "fail"             # ErrorHandleTypeEnum value.
default_value: []                  # Default values to use on error.
```

Error handle modes: `terminated`, `continue-on-error`, `remove-abnormal-output`.

---

## Complete Minimal Example (workflow mode)

```yaml
version: "0.6.0"
kind: app
app:
  name: "Simple Echo"
  mode: workflow
  icon: "\U0001F916"
  icon_background: "#FFEAD5"
  icon_type: emoji
  description: "Echoes the input query"
  use_icon_as_answer_icon: false
dependencies: []
workflow:
  environment_variables: []
  conversation_variables: []
  features:
    file_upload:
      enabled: false
    opening_statement: ""
    retriever_resource:
      enabled: false
    sensitive_word_avoidance:
      enabled: false
    speech_to_text:
      enabled: false
    suggested_questions: []
    suggested_questions_after_answer:
      enabled: false
    text_to_speech:
      enabled: false
  graph:
    edges:
      - id: start-to-end
        source: "start_node"
        sourceHandle: source
        target: "end_node"
        targetHandle: target
        type: custom
        data:
          sourceType: start
          targetType: end
          isInIteration: false
          isInLoop: false
    nodes:
      - id: "start_node"
        type: custom
        position:
          x: 80
          y: 282
        data:
          type: start
          title: Start
          desc: ""
          variables:
            - variable: query
              label: query
              type: text-input
              required: true
              max_length: null
              options: []
      - id: "end_node"
        type: custom
        position:
          x: 384
          y: 282
        data:
          type: end
          title: End
          desc: ""
          outputs:
            - variable: result
              value_selector:
                - "start_node"
                - query
              value_type: string
    viewport:
      x: 0
      y: 0
      zoom: 0.7
```

## Complete Minimal Example (advanced-chat mode)

```yaml
version: "0.6.0"
kind: app
app:
  name: "Simple Chat"
  mode: advanced-chat
  icon: "\U0001F916"
  icon_background: "#FFEAD5"
  icon_type: emoji
  description: "Simple chatflow with LLM"
  use_icon_as_answer_icon: false
dependencies: []
workflow:
  environment_variables: []
  conversation_variables: []
  features:
    file_upload:
      enabled: false
    opening_statement: ""
    retriever_resource:
      enabled: false
    sensitive_word_avoidance:
      enabled: false
    speech_to_text:
      enabled: false
    suggested_questions: []
    suggested_questions_after_answer:
      enabled: false
    text_to_speech:
      enabled: false
  graph:
    edges:
      - id: start-to-llm
        source: "start_node"
        sourceHandle: source
        target: "llm_node"
        targetHandle: target
      - id: llm-to-answer
        source: "llm_node"
        sourceHandle: source
        target: "answer_node"
        targetHandle: target
    nodes:
      - id: "start_node"
        type: custom
        position:
          x: 80
          y: 282
        data:
          type: start
          title: Start
          desc: ""
          variables: []
      - id: "llm_node"
        type: custom
        position:
          x: 380
          y: 282
        data:
          type: llm
          title: LLM
          desc: ""
          model:
            provider: ""
            name: ""
            mode: chat
            completion_params:
              temperature: 0.7
          prompt_template:
            - role: system
              text: "You are a helpful assistant."
          variables: []
          context:
            enabled: false
            variable_selector: []
          vision:
            enabled: false
          memory:
            query_prompt_template: "{{#sys.query#}}\n\n{{#sys.files#}}"
            window:
              enabled: false
              size: 10
      - id: "answer_node"
        type: custom
        position:
          x: 680
          y: 282
        data:
          type: answer
          title: Answer
          desc: ""
          answer: "{{#llm_node.text#}}"
          variables: []
    viewport:
      x: 0
      y: 0
      zoom: 0.7
```
