## Instructions specifically for Kilo

### File operations

- If a file is not found at the expected path, e.g. ROADMAP.md, search elsewhere in the workspace for a file with the same name. If found, use that file instead.
- DO NOT ASSUME that source files will be present in a folder called `src/` — they may be in the root or a different folder.

### Error handling

- If an error is encountered, make sure to output the full error context, including the error message and any related requests or file paths, to `agent-output/<feature-slug>-temp-tests.md`. This will help the user and/or orchestrator diagnose and address the issue effectively.
- If you see the error "Could not find oldString in the file. It must match exactly, including whitespace, indentation, and line endings", try an alternative edit mode, e.g. 'write' or 'apply_patch'