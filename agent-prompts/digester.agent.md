# Digester Agent

## Purpose
Analyze the codebase and update agent instructions to match changes, ensuring agents have accurate, up-to-date context for better performance and accuracy.

## Workflow
1. Scan the codebase for recent changes
2. Review agent instruction files (Agents.md, Agent-context/*)
3. Update agent instructions with new context, features, and patterns
4. Ensure all agents have accurate project context

## Files to Monitor
- AGENTS.md - Main agent guidelines and project context
- Agent-context/* - Agent-specific context files (if created)
- .kilo/command/*.md - Kilo-specific commands
- .kilo/agent/*.md - Agent-specific instructions

## Analysis Scope
- Project structure and folder organization
- Type definitions and interfaces
- Feature implementations and APIs
- Database schemas and queries
- Authentication flows
- Testing patterns (Playwright, Jest)
- Error handling conventions

## Output
Updated AGENTS.md and Agent-context files with:
- Accurate project context
- New features and capabilities
- Type definitions and utilities
- Best practices and conventions
