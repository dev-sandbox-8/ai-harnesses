# harness-translate resources

Supporting data files for the `harness-translate` script.

---

## tool-mappings.json

Defines how tool names translate between the two platforms.

| Key | Purpose |
|-----|---------|
| `copilotGroupToClaud` | Maps a VS Code Copilot namespace group (`edit`, `read`, …) to one or more Claude Code tool names |
| `copilotNamespaceToClaud` | Maps the namespace prefix of a specific namespaced Copilot tool (`vscode/runCommand` → `vscode` prefix) to Claude Code tools |
| `claudToCopilotGroup` | Maps a single Claude Code tool name to the Copilot namespace group that best covers it |
| `bodyTextCopilotToClaud` | Inline tool-name substitutions applied to body text when converting Copilot → Claude |
| `bodyTextClaudToCopilot` | Inline tool-name substitutions applied to body text when converting Claude → Copilot |

### Copilot namespace groups

VS Code Copilot agents list tools using either namespace groups (`'edit'`, `'read'`, …) or
fully-qualified namespaced names (`vscode/runCommand`, `execute/runInTerminal`, …).

| Group | Covers |
|-------|--------|
| `read` | `read/readFile`, `read/problems`, … |
| `edit` | `edit/createFile`, … |
| `search` | `search/codebase`, `search/fileSearch`, `search/textSearch`, `search/usages`, … |
| `execute` | `execute/runInTerminal`, `execute/createAndRunTask`, … |
| `agent` | Sub-agent dispatch |
| `todo` | Task tracking |
| `vscode` | VS Code-specific APIs — no Claude equivalent; dropped on conversion |

### Claude Code tools

Claude Code uses capitalised single-word tool names: `Read`, `Write`, `Edit`, `Bash`, `Grep`, `Glob`, `Search`, `Agent`, `SendMessage`, `TodoWrite`, `WebFetch`, `TaskCreate`, `TaskList`, `TaskUpdate`, `TaskGet`, `TaskStop`.

---

## Extending mappings

Add entries to `tool-mappings.json` to handle additional tools introduced in newer
platform versions. The script reads the file at runtime, so no rebuild is required.
