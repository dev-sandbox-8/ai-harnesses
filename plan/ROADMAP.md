# Roadmap

### High Priority

#### agents don't seem to run the playwright tests
- When I run a task using implementer, it seems to create playwright tests, but leaves so many issues, it can't actually be running them
- When I run the quality gate, it will pass if the playwright tests don't build

#### Ensure that the current set of agents is compatible with Claude CLI
- Run full orchestrator workflows based on discrete issues, repeating as needed until the result is clean and complete.
- Identify and fix any issues with agent interactions, tool usage, or output formatting.
- Verify that all agents can access and utilize the necessary artefacts (specs, skills, prompts, instructions) from the repository.
  - How can this be done?
    - Manual testing of each individual agent with a variety of inputs and scenarios, checking for correct behaviour and output.
      - **bug-tracker** agent: Identify bugs in the codebase and log them in the bug tracker, making sure that it accesses the other agents correctly, e.g. to verify fixes
      - **other agents**: Test as needed
    - Automated tests that simulate agent interactions and verify expected outcomes.
- Edits to agents can be completed by bringing the mentor recommendations into this repository and making the recommended changes

##### Notes
 It's possible that project agents can't use user agents... but it's more likely that the tools or invocation language is wrong

##### Example test cases:
- **Test case 1**: Run the orchestrator with a simple feature request and verify that the spec is generated correctly, tests are written, and code is produced without errors.
  - Watch out for tool use issues, such as agents not being able to access the roadmap or instructions, and ensure that any such issues are resolved promptly.
- **Test case 2**: Introduce a known bug and check that the bug-fix agent can identify and resolve it, updating the bug tracker accordingly.
- **Test case 3**: Use the code-reviewer agent to review a pull request and ensure that it provides actionable feedback based on the defined architecture rules and instructions.

#### Implement a basic bug tracker
- Create a `plan/BUG_TRACKER.md` file to log identified bugs, their status, and any relevant details.
- Integrate bug tracking into the orchestrator workflow, so that any issues identified during execution are automatically logged.