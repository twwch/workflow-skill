---
name: coze-workflow
description: Generate Coze Studio workflow JSON files from natural language descriptions. Produces importable JSON workflow definitions with correct node schemas, edges, and layout.
---

# Coze Workflow JSON Generator

## Overview

This skill generates Coze Studio workflow JSON files that can be directly imported into Coze Studio. Given a natural language description of a desired workflow, it produces a complete JSON file containing all nodes, edges, layout positions, and configuration.

The skill triggers when the user asks to:
- Create, generate, or build a Coze workflow
- Convert a process description into a Coze workflow JSON
- Scaffold a workflow for a Coze bot or application

Output format is JSON only (`.coze.json`).

## Smart Interaction Logic

Before generating, assess whether the user's description is sufficient:

**Proceed directly** if the description includes:
- Clear input/output expectations
- Processing logic (what the workflow should do)
- Enough detail to select appropriate nodes

**Ask clarifying questions** (max 3 rounds) if unclear:
1. "What inputs will the workflow receive, and what outputs should it produce?"
2. "What processing steps are needed? (e.g., LLM call, knowledge retrieval, API call, conditional logic, code execution)"
3. "Any specific models, plugins, or knowledge bases to use?"

Once requirements are clear, proceed to generation.

## Node Router Table

| Node | Type ID | Type Key (Backend) | Frontend Key | Purpose | Key Params | Schema Path |
|------|---------|-------------------|--------------|---------|------------|-------------|
| Start | `1` | `Entry` | `Start` | Entry point; defines workflow input variables | `outputs` (variable definitions) | `references/nodes/start.md` |
| End | `2` | `Exit` | `End` | Terminal node; collects outputs, optional answer content | `inputs.inputParameters`, `inputs.terminatePlan` | `references/nodes/end.md` |
| LLM | `3` | `LLM` | `LLM` | Invokes a large language model | `inputs.llmParam`, `inputs.inputParameters` | `references/nodes/llm.md` |
| Plugin | `4` | `Plugin` | `Api` | Executes a registered plugin/tool | `inputs.pluginID`, `inputs.apiID` | `references/nodes/plugin.md` |
| Code | `5` | `CodeRunner` | `Code` | Runs Python or JavaScript/TypeScript code | `inputs.code`, `inputs.language` (3=Python, 5=TS) | `references/nodes/code.md` |
| Knowledge (Search) | `6` | `KnowledgeRetriever` | `Dataset` | Searches knowledge bases for relevant docs | `inputs.datasetIDs`, `inputs.query` | `references/nodes/knowledge.md` |
| If/Selector | `8` | `Selector` | `If` | Conditional branching (IF/ELIF/ELSE) | `inputs.branches` | `references/nodes/if.md` |
| Sub-Workflow | `9` | `SubWorkflow` | `SubWorkflow` | Executes another workflow as a nested call | `inputs.workflowID` | `references/nodes/sub-workflow.md` |
| Text Process | `15` | `TextProcessor` | `Text` | String concat or split operations | `inputs.mode`, `inputs.content` | `references/nodes/text-process.md` |
| Question | `18` | `QuestionAnswer` | `Question` | Pauses to ask user a question | `inputs.questionContent`, `inputs.answerMode` | `references/nodes/question.md` |
| Loop | `21` | `Loop` | `Loop` | Iterates over array/count with inner sub-canvas | `inputs.loopType`, `blocks`, `edges` | `references/nodes/loop.md` |
| Intent | `22` | `IntentDetector` | `Intent` | LLM-based intent classification with branching | `inputs.intents`, `inputs.llmParam` | `references/nodes/intent.md` |
| Knowledge (Write) | `27` | `KnowledgeIndexer` | `DatasetWrite` | Indexes documents into a knowledge base | `inputs.datasetID`, `inputs.content` | `references/nodes/knowledge.md` |
| Batch | `28` | `Batch` | `Batch` | Parallel array processing with inner sub-canvas | `inputs.batchSize`, `blocks`, `edges` | `references/nodes/batch.md` |
| Variable Aggregator | `32` | `VariableAggregator` | `VariableAggregator` | Merges variables from multiple branches | `inputs.variables` | `references/nodes/variable.md` |
| Variable (Get/Set) | `11` | `VariableAssigner` | `Variable` | Gets or sets app/user-level variables | `inputs.variableConfig` | `references/nodes/variable.md` |
| Set Variable | `20` | `VariableAssignerWithinLoop` | `LoopSetVariable` | Assigns values within loops or to global vars | `inputs.assignments` | `references/nodes/variable.md` |
| HTTP Request | `45` | `HTTPRequester` | `Http` | Makes HTTP API calls | `inputs.method`, `inputs.url`, `inputs.headers` | `references/nodes/http-request.md` |
| JSON Stringify | `58` | `JsonSerialization` | `ToJSON` | Converts values to JSON strings | `inputs.inputParameters` | `references/nodes/json-stringify.md` |
| Database (Query) | `43` | `DatabaseQuery` | `DatabaseSelect` | Queries a Coze database | `inputs.tableID`, `inputs.conditions` | `references/nodes/database.md` |
| Database (Insert) | `46` | `DatabaseInsert` | `DatabaseInsert` | Inserts rows into a database | `inputs.tableID`, `inputs.rows` | `references/nodes/database.md` |
| Database (Update) | `42` | `DatabaseUpdate` | `DatabaseUpdate` | Updates database rows | `inputs.tableID`, `inputs.conditions` | `references/nodes/database.md` |
| Database (Delete) | `44` | `DatabaseDelete` | `DatabaseDelete` | Deletes database rows | `inputs.tableID`, `inputs.conditions` | `references/nodes/database.md` |

## Generation Flow

Follow these steps to produce a valid workflow JSON:

1. **Parse requirement** -- Identify the needed nodes, data flow, and branching logic.
   - Every workflow must have exactly one Start node (id `100001`, type `1`) and one End node (id `900001`, type `2`).

2. **Select nodes** from the router table above. Load the corresponding schema file for each selected node to get the full field specification.

3. **Check template match** -- If the requirement closely matches a known pattern, start from a template (see Template Matching below). Adapt fields as needed.

4. **Assemble from schemas** -- If no template matches, build nodes individually. For each node:
   - Assign a unique string ID (Start = `100001`, End = `900001`, others = `200001`, `200002`, etc.).
   - Set `type` to the numeric string from the router table (e.g., `"3"` for LLM).
   - Fill `data.nodeMeta` with `title`, `description`, `icon`.
   - Fill `data.inputs` and `data.outputs` per the node schema.
   - Use `ref` expressions for data flow between nodes (see DSL Structure below).

5. **Generate edges** -- Connect nodes with control flow edges:
   - Standard: `{ "sourceNodeID": "X", "targetNodeID": "Y", "sourcePortID": "", "targetPortID": "" }`
   - If/Selector branches: `sourcePortID` = `"true"` (first branch), `"true_1"` (second), `"false"` (else)
   - IntentDetector branches: `sourcePortID` = `"branch_0"`, `"branch_1"`, ..., `"default"`
   - Loop/Batch inner edges go in the composite node's `edges` array, not top-level

6. **Calculate layout positions** -- Place nodes left-to-right:
   - Start node at `(0, 0)`.
   - Horizontal spacing: ~460px between node left edges (360px width + 100px gap).
   - Parallel branches offset on Y axis by ~200px.

7. **Output file** -- Render as JSON. Validate structure completeness.

## DSL Structure Quick Reference

```json
{
  "nodes": [
    {
      "id": "100001",
      "type": "1",
      "meta": { "position": { "x": 0, "y": 0 } },
      "data": {
        "nodeMeta": { "title": "Start", "description": "", "icon": "icon-Start-v2.jpg", "subTitle": "" },
        "outputs": [ { "name": "input", "type": "string", "required": true, "description": "" } ],
        "inputs": {}
      }
    }
  ],
  "edges": [
    { "sourceNodeID": "100001", "targetNodeID": "200001", "sourcePortID": "", "targetPortID": "" }
  ],
  "versions": { "loop": "v2" }
}
```

### Data Flow: Reference Expressions

Data between nodes is passed via `ref` in `inputParameters`, not via edges. Format:

```json
{
  "name": "my_input",
  "input": {
    "type": "string",
    "value": {
      "type": "ref",
      "content": {
        "source": "block-output",
        "blockID": "100001",
        "name": "USER_INPUT"
      }
    }
  }
}
```

For literal values:

```json
{
  "name": "temperature",
  "input": {
    "type": "string",
    "value": {
      "type": "literal",
      "content": "0.7"
    }
  }
}
```

### Variable Types

`"string"`, `"integer"`, `"float"`, `"boolean"`, `"object"`, `"list"`

### LLM Param Keys

The `llmParam` array uses named entries: `modelType`, `modleName`, `temperature`, `maxTokens`, `responseFormat`, `systemPrompt`, `prompt`, `enableChatHistory`, `chatHistoryRound`.

### End Node Terminate Plans

- `"returnVariables"` -- Returns collected `inputParameters` as structured output.
- `"useAnswerContent"` -- Returns a rendered `content` template string (supports streaming).

## Output Rules

- **Filename**: `<kebab-case-name>.coze.json`
- **Node IDs**: Start = `"100001"`, End = `"900001"`. Other nodes use `"200001"`, `"200002"`, etc. All IDs are strings.
- **Coordinates**: Start at `(0, 0)`. Each subsequent column at +460px on X axis. Parallel branches offset +200px on Y axis.
- **Node type**: Always a numeric string matching the Type ID column (e.g., `"3"`, not `3`).
- **Version field**: LLM and some nodes use `"version": "3"`. Include when the schema specifies it.
- **Top-level `versions`**: Always include `{ "loop": "v2" }`.
- **Edges are control flow only**: Data dependencies go in `inputParameters` with `ref` values pointing to upstream node outputs.
- **Composite nodes** (Loop type `21`, Batch type `28`): Inner sub-nodes go in `blocks`, inner edges go in the node's `edges` array.

## Template Matching

Use a template when the user's request closely matches a known pattern. Load the template, then customize fields (prompts, variables, model config) to fit the specific requirement.

| Template | Path | Matches When |
|----------|------|-------------|
| Chatbot | `references/templates/chatbot.json` | Simple conversational bot: Start -> LLM -> End (with answer content) |

If the requirement partially matches, use the closest template as a starting point and add/remove nodes as needed.

## Few-Shot Example

A minimal workflow (Start -> LLM -> End):

```json
{
  "nodes": [
    {
      "id": "100001",
      "type": "1",
      "meta": { "position": { "x": 0, "y": 0 } },
      "data": {
        "nodeMeta": { "title": "Start", "description": "", "icon": "icon-Start-v2.jpg", "subTitle": "" },
        "outputs": [
          { "name": "USER_INPUT", "type": "string", "required": true, "description": "The user message" }
        ]
      }
    },
    {
      "id": "200001",
      "type": "3",
      "meta": { "position": { "x": 460, "y": 0 } },
      "data": {
        "nodeMeta": { "title": "LLM", "description": "Generate a response.", "icon": "icon-LLM-v2.jpg", "mainColor": "#5C62FF", "subTitle": "LLM" },
        "inputs": {
          "inputParameters": [
            {
              "name": "user_input",
              "input": {
                "type": "string",
                "value": { "type": "ref", "content": { "source": "block-output", "blockID": "100001", "name": "USER_INPUT" } }
              }
            }
          ],
          "llmParam": [
            { "name": "modelType", "input": { "type": "string", "value": { "type": "literal", "content": "YOUR_MODEL_TYPE" } } },
            { "name": "modleName", "input": { "type": "string", "value": { "type": "literal", "content": "YOUR_MODEL_NAME" } } },
            { "name": "temperature", "input": { "type": "string", "value": { "type": "literal", "content": "0.7" } } },
            { "name": "maxTokens", "input": { "type": "string", "value": { "type": "literal", "content": "4096" } } },
            { "name": "systemPrompt", "input": { "type": "string", "value": { "type": "literal", "content": "You are a helpful assistant." } } },
            { "name": "prompt", "input": { "type": "string", "value": { "type": "literal", "content": "{{user_input}}" } } }
          ]
        },
        "outputs": [ { "name": "output", "type": "string" } ],
        "version": "3"
      }
    },
    {
      "id": "900001",
      "type": "2",
      "meta": { "position": { "x": 920, "y": 0 } },
      "data": {
        "nodeMeta": { "title": "End", "description": "", "icon": "icon-End-v2.jpg", "subTitle": "" },
        "inputs": {
          "terminatePlan": "useAnswerContent",
          "streamingOutput": true,
          "content": { "type": "string", "value": { "type": "literal", "content": "{{200001.output}}" } },
          "inputParameters": [
            {
              "name": "output",
              "input": {
                "type": "string",
                "value": { "type": "ref", "content": { "source": "block-output", "blockID": "200001", "name": "output" } }
              }
            }
          ]
        }
      }
    }
  ],
  "edges": [
    { "sourceNodeID": "100001", "targetNodeID": "200001", "sourcePortID": "", "targetPortID": "" },
    { "sourceNodeID": "200001", "targetNodeID": "900001", "sourcePortID": "", "targetPortID": "" }
  ],
  "versions": { "loop": "v2" }
}
```

## Format

JSON only. All output files use the `.coze.json` extension. Use standard JSON formatting with 2-space indentation.
