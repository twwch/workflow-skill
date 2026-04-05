# Dify Workflow Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Claude Code skill (`/dify-workflow`) that generates Dify-compatible workflow DSL files from natural language descriptions.

**Architecture:** Layered skill with SKILL.md as entry point containing node router table and generation logic, references/ for full node schemas and templates loaded on demand, and examples/ for few-shot learning. Source code is cloned for analysis only and git-ignored.

**Tech Stack:** Claude Code skill (Markdown), Dify DSL (YAML/JSON), Git

---

### Task 1: Project Setup & Clone Dify Source

**Files:**
- Create: `.gitignore`
- Create: `source/` (via git clone)

- [ ] **Step 1: Initialize git repo**

```bash
cd /Users/chenhao/codes/workflow-skill
git init
```

- [ ] **Step 2: Create .gitignore**

Create `.gitignore` with:

```
source/
```

- [ ] **Step 3: Clone Dify repo**

```bash
cd /Users/chenhao/codes/workflow-skill
git clone --depth 1 https://github.com/langgenius/dify.git source/dify
```

We use `--depth 1` to save disk space — we only need the latest source for schema extraction.

- [ ] **Step 4: Verify clone and locate key directories**

```bash
ls source/dify/api/core/workflow/nodes/
ls source/dify/api/core/workflow/graph/
```

Expected: directories for each node type (llm, code, http_request, etc.) and graph management files.

- [ ] **Step 5: Commit project setup**

```bash
git add .gitignore
git commit -m "chore: init project with .gitignore for source/"
```

---

### Task 2: Create Directory Structure

**Files:**
- Create: `dify-workflow/references/nodes/` (directory)
- Create: `dify-workflow/references/templates/` (directory)
- Create: `dify-workflow/examples/` (directory)

- [ ] **Step 1: Create all skill directories**

```bash
mkdir -p /Users/chenhao/codes/workflow-skill/dify-workflow/references/nodes
mkdir -p /Users/chenhao/codes/workflow-skill/dify-workflow/references/templates
mkdir -p /Users/chenhao/codes/workflow-skill/dify-workflow/examples
```

- [ ] **Step 2: Verify structure**

```bash
find /Users/chenhao/codes/workflow-skill/dify-workflow -type d
```

Expected:
```
dify-workflow/
dify-workflow/references
dify-workflow/references/nodes
dify-workflow/references/templates
dify-workflow/examples
```

No commit yet — directories alone aren't tracked by git. Files will be committed as they're created.

---

### Task 3: Analyze Dify Source — DSL Format

**Files:**
- Read: `source/dify/api/core/app/apps/workflow/` (DSL export/import logic)
- Read: `source/dify/api/core/workflow/` (workflow entity definitions)
- Create: `dify-workflow/references/dsl-format.md`

- [ ] **Step 1: Find DSL serialization code**

Search the Dify source for DSL export/import logic:

```bash
grep -r "class.*DSL\|def.*export\|def.*import.*workflow\|yaml.*dump\|yaml.*load" source/dify/api/core/app/ --include="*.py" -l
```

- [ ] **Step 2: Read DSL serialization files**

Read the files found in Step 1. Key information to extract:
- Top-level YAML structure (app metadata, workflow graph, features)
- Required fields and their types
- How nodes and edges are serialized
- Version field and format

- [ ] **Step 3: Find a real exported workflow example**

```bash
grep -r "\.yml\|\.yaml\|workflow.*fixture\|dsl.*fixture" source/dify/api/tests/ --include="*.py" -l
find source/dify/ -name "*.yml" -path "*/test*" | head -20
find source/dify/ -name "*.yaml" -path "*/workflow*" | head -20
```

- [ ] **Step 4: Write dsl-format.md**

Create `dify-workflow/references/dsl-format.md` documenting:
- Complete top-level YAML structure with all fields
- App metadata format (name, mode, description, icon, environment_variables)
- Workflow graph structure: `nodes[]` and `edges[]`
- Node object format: `{data: {type, title, desc, variables...}, id, position: {x, y}}`
- Edge object format: `{id, source, sourceHandle, target, targetHandle, type, data: {}}`
- Variable reference syntax: `{{#node_id.output_key#}}`
- System variables: `{{#sys.query#}}`, `{{#sys.user_id#}}`, `{{#sys.files#}}`
- Features block structure
- Version and format fields

The exact content depends on what we find in the source code. Document everything faithfully.

- [ ] **Step 5: Commit**

```bash
git add dify-workflow/references/dsl-format.md
git commit -m "docs: add Dify DSL format reference extracted from source"
```

---

### Task 4: Analyze Dify Source — Edge and Layout Rules

**Files:**
- Read: `source/dify/api/core/workflow/graph/`
- Create: `dify-workflow/references/edge-and-layout.md`

- [ ] **Step 1: Read graph management code**

```bash
ls source/dify/api/core/workflow/graph/
```

Read the graph validation and edge handling files. Key information:
- Edge data structure
- sourceHandle / targetHandle naming conventions
- Connection validation rules (which nodes can connect to which)
- Any layout or positioning logic

- [ ] **Step 2: Search for handle naming patterns**

```bash
grep -r "sourceHandle\|targetHandle\|source_handle\|target_handle" source/dify/api/core/workflow/ --include="*.py" -l
```

Read the matched files to understand handle naming conventions.

- [ ] **Step 3: Write edge-and-layout.md**

Create `dify-workflow/references/edge-and-layout.md` documenting:
- Edge object schema with all fields
- sourceHandle/targetHandle naming conventions (e.g., `source` for default output, `if-true`/`if-false` for conditional)
- Connection validation rules
- Layout coordinate system (auto-calculated):
  - Start node at position (80, 282)
  - Horizontal gap: 250px between sequential nodes
  - Vertical gap: 150px for parallel branches
  - Left-to-right flow

- [ ] **Step 4: Commit**

```bash
git add dify-workflow/references/edge-and-layout.md
git commit -m "docs: add edge and layout reference for Dify workflows"
```

---

### Task 5: Extract Node Schemas — Start, End, Answer

**Files:**
- Read: `source/dify/api/core/workflow/nodes/start/` (entity + node files)
- Read: `source/dify/api/core/workflow/nodes/end/`
- Read: `source/dify/api/core/workflow/nodes/answer/`
- Create: `dify-workflow/references/nodes/start.md`
- Create: `dify-workflow/references/nodes/end.md`
- Create: `dify-workflow/references/nodes/answer.md`

- [ ] **Step 1: Read Start node source**

```bash
ls source/dify/api/core/workflow/nodes/start/
```

Read the entity/data class file(s). Extract:
- All fields with types, required/optional, defaults
- Input variable definition structure
- Output variable names

- [ ] **Step 2: Write start.md**

Create `dify-workflow/references/nodes/start.md` following the reference file format:
- Purpose
- Core Fields table
- Full Schema (all fields from source)
- Variable Reference Rules (output variables available to downstream nodes)
- Example YAML snippet (minimal working start node)

- [ ] **Step 3: Read End node source**

```bash
ls source/dify/api/core/workflow/nodes/end/
```

Read and extract schema same as Step 1.

- [ ] **Step 4: Write end.md**

Create `dify-workflow/references/nodes/end.md` with same format as start.md.

- [ ] **Step 5: Read Answer node source**

```bash
ls source/dify/api/core/workflow/nodes/answer/
```

Read and extract schema.

- [ ] **Step 6: Write answer.md**

Create `dify-workflow/references/nodes/answer.md` with same format.

- [ ] **Step 7: Commit**

```bash
git add dify-workflow/references/nodes/start.md dify-workflow/references/nodes/end.md dify-workflow/references/nodes/answer.md
git commit -m "docs: add Start, End, Answer node references"
```

---

### Task 6: Extract Node Schemas — LLM, Knowledge Retrieval

**Files:**
- Read: `source/dify/api/core/workflow/nodes/llm/`
- Read: `source/dify/api/core/workflow/nodes/knowledge_retrieval/`
- Create: `dify-workflow/references/nodes/llm.md`
- Create: `dify-workflow/references/nodes/knowledge-retrieval.md`

- [ ] **Step 1: Read LLM node source**

```bash
ls source/dify/api/core/workflow/nodes/llm/
```

Read entity/data classes. LLM is the most complex node — extract:
- Model configuration (provider, name, mode, completion_params)
- Prompt template structure (role + text/jinja2)
- Context configuration (for knowledge retrieval integration)
- Memory configuration
- Vision configuration
- All output variables

- [ ] **Step 2: Write llm.md**

Create `dify-workflow/references/nodes/llm.md`. This will likely be the longest reference file (300-400 lines) given the LLM node's complexity.

- [ ] **Step 3: Read Knowledge Retrieval node source**

```bash
ls source/dify/api/core/workflow/nodes/knowledge_retrieval/
```

Extract: dataset_ids, retrieval_mode, query variable, reranking config, top_k, score_threshold.

- [ ] **Step 4: Write knowledge-retrieval.md**

Create `dify-workflow/references/nodes/knowledge-retrieval.md`.

- [ ] **Step 5: Commit**

```bash
git add dify-workflow/references/nodes/llm.md dify-workflow/references/nodes/knowledge-retrieval.md
git commit -m "docs: add LLM and Knowledge Retrieval node references"
```

---

### Task 7: Extract Node Schemas — Code, HTTP Request, Template Transform

**Files:**
- Read: `source/dify/api/core/workflow/nodes/code/`
- Read: `source/dify/api/core/workflow/nodes/http_request/`
- Read: `source/dify/api/core/workflow/nodes/template_transform/`
- Create: `dify-workflow/references/nodes/code.md`
- Create: `dify-workflow/references/nodes/http-request.md`
- Create: `dify-workflow/references/nodes/template-transform.md`

- [ ] **Step 1: Read Code node source**

```bash
ls source/dify/api/core/workflow/nodes/code/
```

Extract: code content, language (python3/javascript), input variables, output variables with types.

- [ ] **Step 2: Write code.md**

Create `dify-workflow/references/nodes/code.md`.

- [ ] **Step 3: Read HTTP Request node source**

```bash
ls source/dify/api/core/workflow/nodes/http_request/
```

Extract: method, url, headers, params, body (with body type: json/form-data/raw/none), authorization config, timeout.

- [ ] **Step 4: Write http-request.md**

Create `dify-workflow/references/nodes/http-request.md`.

- [ ] **Step 5: Read Template Transform node source**

```bash
ls source/dify/api/core/workflow/nodes/template_transform/
```

Extract: template (Jinja2), input variables.

- [ ] **Step 6: Write template-transform.md**

Create `dify-workflow/references/nodes/template-transform.md`.

- [ ] **Step 7: Commit**

```bash
git add dify-workflow/references/nodes/code.md dify-workflow/references/nodes/http-request.md dify-workflow/references/nodes/template-transform.md
git commit -m "docs: add Code, HTTP Request, Template Transform node references"
```

---

### Task 8: Extract Node Schemas — Control Flow Nodes

**Files:**
- Read: `source/dify/api/core/workflow/nodes/if_else/`
- Read: `source/dify/api/core/workflow/nodes/variable_aggregator/`
- Read: `source/dify/api/core/workflow/nodes/iteration/`
- Create: `dify-workflow/references/nodes/if-else.md`
- Create: `dify-workflow/references/nodes/variable-aggregator.md`
- Create: `dify-workflow/references/nodes/iteration.md`

- [ ] **Step 1: Read If/Else node source**

```bash
ls source/dify/api/core/workflow/nodes/if_else/
```

Extract: conditions structure (variable, comparison operator, value), logical operators (and/or), multiple condition groups, output handles (true/false).

- [ ] **Step 2: Write if-else.md**

Create `dify-workflow/references/nodes/if-else.md`. Pay special attention to the condition expression format and the branching handle names.

- [ ] **Step 3: Read Variable Aggregator node source**

```bash
ls source/dify/api/core/workflow/nodes/variable_aggregator/
```

Extract: variable list (node_id + variable_name pairs), output mode.

- [ ] **Step 4: Write variable-aggregator.md**

Create `dify-workflow/references/nodes/variable-aggregator.md`.

- [ ] **Step 5: Read Iteration node source**

```bash
ls source/dify/api/core/workflow/nodes/iteration/
```

Extract: iterator variable, sub-graph nodes, output variable, parallel mode config.

- [ ] **Step 6: Write iteration.md**

Create `dify-workflow/references/nodes/iteration.md`.

- [ ] **Step 7: Commit**

```bash
git add dify-workflow/references/nodes/if-else.md dify-workflow/references/nodes/variable-aggregator.md dify-workflow/references/nodes/iteration.md
git commit -m "docs: add If/Else, Variable Aggregator, Iteration node references"
```

---

### Task 9: Extract Node Schemas — AI Utility Nodes

**Files:**
- Read: `source/dify/api/core/workflow/nodes/question_classifier/`
- Read: `source/dify/api/core/workflow/nodes/parameter_extractor/`
- Read: `source/dify/api/core/workflow/nodes/tool/`
- Create: `dify-workflow/references/nodes/question-classifier.md`
- Create: `dify-workflow/references/nodes/parameter-extractor.md`
- Create: `dify-workflow/references/nodes/tool.md`

- [ ] **Step 1: Read Question Classifier node source**

```bash
ls source/dify/api/core/workflow/nodes/question_classifier/
```

Extract: model config, classes (id + name + description), instruction.

- [ ] **Step 2: Write question-classifier.md**

Create `dify-workflow/references/nodes/question-classifier.md`.

- [ ] **Step 3: Read Parameter Extractor node source**

```bash
ls source/dify/api/core/workflow/nodes/parameter_extractor/
```

Extract: model config, parameters (name + type + description + required), instruction, reasoning_mode.

- [ ] **Step 4: Write parameter-extractor.md**

Create `dify-workflow/references/nodes/parameter-extractor.md`.

- [ ] **Step 5: Read Tool node source**

```bash
ls source/dify/api/core/workflow/nodes/tool/
```

Extract: provider_id, provider_type, tool_name, tool_parameters, tool_configurations.

- [ ] **Step 6: Write tool.md**

Create `dify-workflow/references/nodes/tool.md`.

- [ ] **Step 7: Commit**

```bash
git add dify-workflow/references/nodes/question-classifier.md dify-workflow/references/nodes/parameter-extractor.md dify-workflow/references/nodes/tool.md
git commit -m "docs: add Question Classifier, Parameter Extractor, Tool node references"
```

---

### Task 10: Create Workflow Templates

**Files:**
- Read: `source/dify/api/tests/` (search for workflow test fixtures)
- Create: `dify-workflow/references/templates/chatbot.yml`
- Create: `dify-workflow/references/templates/rag.yml`
- Create: `dify-workflow/references/templates/agent.yml`
- Create: `dify-workflow/references/templates/translation.yml`

- [ ] **Step 1: Search for existing workflow fixtures in Dify source**

```bash
find source/dify/ -name "*.yml" -o -name "*.yaml" | xargs grep -l "workflow\|nodes\|edges" 2>/dev/null | head -20
grep -r "workflow.*graph\|graph.*nodes" source/dify/api/tests/ --include="*.py" -l | head -10
```

Use any real fixtures as base for templates.

- [ ] **Step 2: Create chatbot.yml template**

Structure: Start → LLM → Answer

A complete, importable Dify DSL YAML with:
- App metadata (name: "Chatbot", mode: "workflow")
- Start node with `sys.query` input
- LLM node with basic prompt template
- Answer node streaming LLM output
- Edges connecting all three
- YAML comments marking customization points (model, prompt)

Build this using the DSL format documented in Task 3 and node schemas from Tasks 5-6.

- [ ] **Step 3: Create rag.yml template**

Structure: Start → Knowledge Retrieval → LLM (with context) → Answer

Extends chatbot with:
- Knowledge Retrieval node (placeholder dataset_id, top_k=3)
- LLM node referencing retrieval results via `{{#knowledge_retrieval_node_id.result#}}`
- Comments marking: dataset_ids, retrieval mode, top_k, reranking

- [ ] **Step 4: Create agent.yml template**

Structure: Start → LLM (with tool selection) → Tool → LLM (synthesize) → Answer

Includes:
- First LLM for intent/tool selection
- Tool node with placeholder provider/tool
- Second LLM to synthesize tool results
- Comments marking: tool provider, tool name, tool parameters

- [ ] **Step 5: Create translation.yml template**

Structure: Start → LLM (detect language) → LLM (translate) → Answer

Includes:
- First LLM with language detection prompt
- Second LLM with translation prompt using detected language
- Comments marking: target language, translation style

- [ ] **Step 6: Validate templates are valid YAML**

```bash
python3 -c "
import yaml, sys, glob
for f in glob.glob('dify-workflow/references/templates/*.yml'):
    try:
        yaml.safe_load(open(f))
        print(f'OK: {f}')
    except Exception as e:
        print(f'FAIL: {f}: {e}')
        sys.exit(1)
"
```

Expected: All 4 files print OK.

- [ ] **Step 7: Commit**

```bash
git add dify-workflow/references/templates/
git commit -m "docs: add 4 workflow templates (chatbot, rag, agent, translation)"
```

---

### Task 11: Create Example Workflows

**Files:**
- Create: `dify-workflow/examples/simple-chatbot.yml`
- Create: `dify-workflow/examples/rag-with-rerank.yml`

- [ ] **Step 1: Create simple-chatbot.yml**

A minimal but complete chatbot workflow — similar to chatbot template but with concrete values filled in:
- Specific model (e.g., gpt-4o-mini or claude-3-haiku)
- A real system prompt (e.g., "You are a helpful assistant")
- All UUIDs filled in
- Exact positions calculated

This serves as a few-shot example in SKILL.md for format reference.

- [ ] **Step 2: Create rag-with-rerank.yml**

A more complex example showing:
- Knowledge Retrieval with reranking enabled
- LLM with context from retrieval
- Multiple edges
- Branching if-else for "no results found" case

- [ ] **Step 3: Validate examples are valid YAML**

```bash
python3 -c "
import yaml, sys, glob
for f in glob.glob('dify-workflow/examples/*.yml'):
    try:
        yaml.safe_load(open(f))
        print(f'OK: {f}')
    except Exception as e:
        print(f'FAIL: {f}: {e}')
        sys.exit(1)
"
```

Expected: Both files print OK.

- [ ] **Step 4: Commit**

```bash
git add dify-workflow/examples/
git commit -m "docs: add example workflows for few-shot reference"
```

---

### Task 12: Write SKILL.md

**Files:**
- Create: `dify-workflow/SKILL.md`

This is the core skill file. It must be self-contained enough for the LLM to understand the generation process, with references for detailed schemas.

- [ ] **Step 1: Write SKILL.md**

Create `dify-workflow/SKILL.md` with these sections:

**Frontmatter:**
```yaml
---
name: dify-workflow
description: Generate Dify workflow DSL files from natural language descriptions. Produces importable YAML/JSON workflow definitions with correct node schemas, edges, and layout.
---
```

**Body sections (in order):**

1. **Overview** — What this skill does, when it triggers
2. **Smart Interaction Logic** — Decision tree: clear description → generate; unclear → ask (max 3 rounds)
3. **Node Router Table** — 14-row table: Node | Type Key | Purpose | Key Params | Schema Path
4. **Generation Flow** — Step-by-step: parse → select nodes → match template? → assemble → output
5. **DSL Structure Quick Reference** — Inline summary of top-level YAML structure (reference `references/dsl-format.md` for full spec)
6. **Output Rules** — Filename convention, required sections, UUID format, coordinate rules
7. **Template Matching** — When to use templates, how to customize them, reference paths
8. **Few-Shot Example** — Inline a short example (reference `examples/simple-chatbot.yml` for full version)
9. **Format Selection** — Default YAML, JSON when user asks. Both formats explained.

Each section should be concise — the full SKILL.md target is 200-350 lines. Detailed schemas are in references, not here.

- [ ] **Step 2: Verify all reference paths exist**

```bash
# Check every path referenced in SKILL.md actually exists
for f in \
  dify-workflow/references/dsl-format.md \
  dify-workflow/references/edge-and-layout.md \
  dify-workflow/references/nodes/start.md \
  dify-workflow/references/nodes/end.md \
  dify-workflow/references/nodes/answer.md \
  dify-workflow/references/nodes/llm.md \
  dify-workflow/references/nodes/knowledge-retrieval.md \
  dify-workflow/references/nodes/code.md \
  dify-workflow/references/nodes/http-request.md \
  dify-workflow/references/nodes/if-else.md \
  dify-workflow/references/nodes/variable-aggregator.md \
  dify-workflow/references/nodes/iteration.md \
  dify-workflow/references/nodes/template-transform.md \
  dify-workflow/references/nodes/question-classifier.md \
  dify-workflow/references/nodes/parameter-extractor.md \
  dify-workflow/references/nodes/tool.md \
  dify-workflow/references/templates/chatbot.yml \
  dify-workflow/references/templates/rag.yml \
  dify-workflow/references/templates/agent.yml \
  dify-workflow/references/templates/translation.yml \
  dify-workflow/examples/simple-chatbot.yml \
  dify-workflow/examples/rag-with-rerank.yml; do
  [ -f "$f" ] && echo "OK: $f" || echo "MISSING: $f"
done
```

Expected: All files show OK.

- [ ] **Step 3: Commit**

```bash
git add dify-workflow/SKILL.md
git commit -m "feat: add dify-workflow skill main file"
```

---

### Task 13: Final Validation

**Files:**
- Read: All created files for consistency check

- [ ] **Step 1: Check all files are committed**

```bash
cd /Users/chenhao/codes/workflow-skill
git status
```

Expected: clean working tree.

- [ ] **Step 2: Verify skill structure**

```bash
find dify-workflow/ -type f | sort
```

Expected: SKILL.md + 14 node refs + 2 format refs + 4 templates + 2 examples = 23 files.

- [ ] **Step 3: Verify all YAML files are valid**

```bash
python3 -c "
import yaml, sys, glob
files = glob.glob('dify-workflow/**/*.yml', recursive=True)
for f in files:
    try:
        yaml.safe_load(open(f))
        print(f'OK: {f}')
    except Exception as e:
        print(f'FAIL: {f}: {e}')
        sys.exit(1)
print(f'\nAll {len(files)} YAML files valid.')
"
```

Expected: All YAML files pass validation.

- [ ] **Step 4: Quick smoke test — read SKILL.md and verify node table matches reference files**

Read SKILL.md, count nodes in router table. Verify count matches number of files in `references/nodes/`. Verify each Schema Path in the table points to an existing file.

- [ ] **Step 5: Final commit if any fixes were needed**

```bash
git add -A
git status
# Only commit if there are changes
git diff --cached --quiet || git commit -m "fix: address validation issues from final review"
```
