# Roadmap

### High Priority

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

### Minor agent edits
- All agents should provide a clear and concise summary of their actions and outputs, including any errors or issues encountered during execution and next steps which need the user's attention.
- Add aility to pick up more local information about the project, such as the current state of the codebase, recent changes, and any relevant documentation or specifications. This can help agents make more informed decisions and provide more accurate outputs.
  - Examples of issues which shouldnn't happen:
    - "The src directory doesn't exist! This is likely the root cause. Let me check what's in the .next folder or if there's any build output:"
    - "Let me check if the app is expected to be run directly as a Next.js app (with pages in the .next/build/app):"

### Minimize agent cycles
- How can I change the agents to need fewer turns in order to complete a task? This is important because it can help reduce the overall time and resources required to complete a task, as well as improve the efficiency and effectiveness of the agents. 

### Specs should link to bug tracking system
- Spec files should 
  - reference the original bug file
  - Include a section for priority, complexity, etc. to help with triaging and planning
- Implementer should update specs files and their associated bug/feat files and move them to the archive when the work is complete, so that the spec files remain up-to-date and relevant.
