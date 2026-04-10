# HN Title

Show HN: Workflow Skill – Generate importable Coze/Dify/ComfyUI workflows from natural language

# HN URL

https://github.com/twwch/workflow-skill

# HN Comment (first comment by submitter)

Hi HN, I built a set of Claude Code skills that generate complete workflow definition files for three platforms: Coze (coze.cn), Dify, and ComfyUI — directly from natural language descriptions.

**The problem:** Building complex workflows (20+ nodes, nested loops, parallel branches) on low-code platforms means hours of dragging, connecting, and configuring nodes manually. And each platform has its own proprietary format.

**What this does:** You describe your workflow in plain English (or Chinese), and the skill generates a complete, importable file — with all node configs, edges, layout positions, and platform-specific formatting.

Example:
```
/coze-workflow Create a cross-border e-commerce workflow:
fetch SKUs → loop evaluate → category routing → multi-market localization → multi-platform publishing
```

→ Outputs a ZIP file you drag into coze.cn's import dialog. Done.

**The hard part was Coze.** coze.cn has zero public documentation for its import format. It took 16 rounds of byte-level reverse engineering to figure out:

- The ZIP must mimic Go's `archive/zip` output (flags=0x08, vmade=20, time/date=0x0000). Python's `zipfile` default output gets rejected.
- Directory naming contract: `Workflow-<NAME>-draft-<NUM>/` + `<NAME>-draft.yaml` — the name must match in three places.
- YAML must use 4-space indent with double-quoted IDs. `yaml.dump()` produces wrong formatting.
- Node type strings differ from open-source (`condition` not `selector`, `http` not `http_requester`, `intent` not `intent_detector`).
- Every `type: list` field needs an `items` sub-type, or the frontend crashes with `Unknown variable DTO list need sub type but get undefined`.

The final tool chain: `build_coze_zip.py` (byte-level Go archive/zip compatible packer) + `coze_yaml_builder.py` (verified node template library with all 48 node types).

**Dify** was straightforward — standard YAML DSL, well-documented. Supports 14 node types.

**ComfyUI** generates Litegraph JSON with 360+ node definitions extracted from source, 34 built-in templates, and auto model download support.

**Tech stack:** Pure Python scripts invoked by Claude Code. No server, no API costs beyond the LLM itself.

GitHub: https://github.com/twwch/workflow-skill

Would love feedback, especially from anyone who's worked with Coze's import format or has ideas for supporting more node types.
