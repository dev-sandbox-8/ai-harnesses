# Findings

## Agents need onboarding
It’s important to ensure that new agents are properly onboarded to understand their roles, responsibilities, and the tools they will be using. This includes familiarizing them with the project’s codebase, design system, testing conventions, and any relevant documentation.

This is best done using prompts that guide them through the necessary steps to get up to speed. For example, a prompt could be created to help new agents navigate the codebase and identify key files and components they will be working with.

### Example prompts

#### Compress AGNETS.md for easy consumption

```
Please adjust the content of AGETNS.md to maximise how easily it can be consumed by agents using the least possible context
```

#### Onboarding prompt

```
Please summarize this project in @AGENTS.md , including:
* Technologies used
* Project structure
* Styling/theming configuration/files
* Other important files
* Important relationships/interfaces
* Any other pertinent information which will prevent the need for examining the codebase directly as much as possible
```

## Loops 

### can be repaired

When a loop is observed, it’s important to stop the process and fix it. Move into Ask mode and prompt the agent to fix the issue, e.g. 

```
Is there a loop happening here? Why are the same things being checked? Is there a way we can adjust the AGENTS.md file to prevent this happening?
```

Note: This did not result in an edit to the Agents file, but did result in the agent realizing that it was checking the same files repeatedly and adjusting its process to avoid that. This is a good example of how agents can learn and adapt their behavior based on feedback.

Getting out of the loop doesn't seem to work on any mode other than Ask. If you use Code, it will try to restart the process, and fail (perhaps because the context is lost, which may be the root cause of the loop in the first place).

It might be good to ask Ask mode for suggestions on how to adjust the AGENTS.md file to prevent loops from happening in the future, as this could help improve the overall efficiency and effectiveness of the agents.

This prompt was effective to get suggestions which could be put in the AGENTS.md file to prevent loops from happening in the future:
```
Is there a loop happening here? Why are the same things being checked? Can you suggest adjustments to the AGENTS.md file to prevent this happening?
```

### How to avoid?

- No idea. The agent seems to ignore instructions to avoid loops, and continues to make the same requests and checks repeatedly. This may be due to the way the agent processes information and makes decisions, which could be influenced by its training data and algorithms.


## Context window exhaustion

When working with local agents, it’s important to be mindful of the context window and ensure that the agent is not trying to process too much information at once. If the agent is approaching the context window limit, it may be necessary to summarize the current state and begin a new session to continue working effectively. This can help prevent issues with memory and ensure that the agent can continue to function properly without being overwhelmed by too much information.

## SubAgents

THere seems to be an issue with subagents repeating their commands/requests which can be aolved by using the main agents one at a time

It's probably best to run each agent separately. For example, run the spec-expander agent to produce the spec file, then run the test-driven-developer agent to produce the tests. This can help prevent issues with subagents repeating their commands/requests and ensure that each agent is able to focus on its specific task without being overwhelmed by too much information or conflicting instructions.

## Proposed Workflows

BEFORE STARTING: 
- Exit LM Studio and restart
- Restart your IDE/CLI tool

Work through using the following agents:

### Digester
Make sure that all instructions are up to date using the following prompt:
```
Please review the AGENTS.md file and the contents of the agent-context folder and ensure that all instructions are up to date and accurate. If you find any discrepancies or outdated information, please update the files accordingly to ensure that it reflects the current processes and procedures for the agents.
```

### Spec Expander
Use the following prompt to create spec files for requirements in the roadmap:
```
Please review the requirements in the ROADMAP.md file under the "Prepared requirements" section and create detailed spec files for each requirement using the Specification template provided in the AGENTS.md file. Ensure that each spec file is comprehensive, includes unit or playwright tests, and follows the specified format to facilitate effective implementation and testing by the development team.
```

### Implementer
Use the following prompt to implement the changes specified in the spec files:
```
Please review the <FILENAME> spec file and implement the necessary changes in the codebase to meet the specified requirements. Ensure that your implementation follows best practices, adheres to the project’s coding standards, and is thoroughly tested to ensure functionality and reliability. Add unit and playwright tests as necessary to cover the new functionality and prevent regressions.
```

```
Please implement the spec at <FILENAME> 
```

To continue partial work
```
Please continue implementation of `specs/clickable-tags-in-cards.md`, with the understanding that the implementation has been partially completed
```

### Bug Fixer
Grab the test results using the following command:
```
npx playwright test > agent-output/playwright-logs.txt 
```
Use the following prompt to fix any issues identified during testing:
```
There are some playwright issues which need fixing. Please look at the logs in `agent-output/playwright-logs.txt` and make the required fixes so that `npx playwright test` passes successfully, or provide instruction on what I would need to do to get things running correctly.
```


### Quality Gate

Simple prompt: `Please run all tests and report the results to agent-output/quality-gate.md`
Simple prompt: `Please perform a quality check on the codebase`

#### Fixes needed

- Seems not to output results to a file right now, which would be better
- Should only summarize issues, not try to fix them, as this can lead to loops and context exhaustion. The implementer agent should be responsible for fixing issues, while the quality gate agent should focus on identifying and summarizing them.

### Debug

- This is a system agent and should perhaps not be used, in favour of more specialized agents

### Digester


https://github.com/shanraisshan/claude-code-best-practice/blob/main/best-practice/claude-settings.md

please concisely summarize the current state of this chat, including the original prompt, the things you've tried, what the next steps should be, and all context that is needed moving forward and output it to agent-output/chat-state.md

There are some issues running `npx playwright test --headed --grep "should persist limit across page reload"`,
which are also happening when using the app for real. Please make a plan to fix the issue

### Resources

https://localclaw.io/hardware/macbook-pro-m4-16gb
https://www.reddit.com/r/LocalLLaMA/comments/1gc0t0c/how_does_mlx_quantization_compare_to_gguf/
https://github.com/shanraisshan/claude-code-best-practice/blob/main/best-practice/claude-settings.md
https://github.com/shanraisshan/claude-code-hooks
https://code.claude.com/docs/en/hooks
https://stackoverflow.com/questions/62227905/using-curl-in-the-cmd-to-send-a-discord-webhook

## Choice of model

Model should be chosen based on 
- Privacy: Local models are preferred for sensitive data
- Complexity: Lighter models can be used for simple tasks
- Speed: The fastest possible model should be used without compromising accuracy, especially for time-sensitive tasks
- Cost: The cheapest possible model should be used, without sacrificing privacy, accuracy, or speed



| Privacy-sensitive | Time constraint? | Complexity | Model choice
|-------|-------|-------|------|
| Not sensitive | Fastest possible | High | Laguna M.1 via Kilo |
| Not sensitive | Fastest possible | Low | Auto Free via Kilo |
| Sensitive | Fastest possible | High | Claude Sonnet 4.6 via Copilot  |
| Sensitive | None | High | Local model |
| Sensitive | Moderate | Low | GPT-5.4 mini via Copilot |
| Sensitive | None | High | Manual coding |

### Examples of sensitive requests
- Codebase-related requests
- Generating knowledge graphs

### Examples of non-sensitive requests
- Generating skills/agents
- General questions on technology and tools

### Cautions
- Don't use free public models in the same IDE as your codebase, as this can lead to data leakage. Use local models or private cloud models instead.

### How to detrermine complexity
- High complexity: Requires understanding of the codebase, architecture, and design patterns. Involves multiple files, components, or modules. Requires reasoning and problem-solving skills.
- Low complexity: Involves simple tasks that can be completed with minimal understanding of the codebase. Involves a single file or component. Requires basic coding skills and knowledge of the programming language.

### Complexity process
1. Analyze the problem - if it's an obviously simple problem, use a simple model
2. Attempt to solve the problem using AI
3. If the AI is unable to solve the problem, consider escalating to a more capable AI or human developer

Categorize the complexity using the following categories:
- AI-Simple: Can be solved with basic coding skills and knowledge of the programming language
- AI-Moderate: Requires some understanding of the codebase and architecture, but can be solved with reasoning and problem-solving skills
- AI-Complex: Requires a deep understanding of the codebase, architecture, and design patterns
- Learning: Useful to take on as a human as a learning exercise, perhaps after an initial pass using AI

## Model results

### Qwen3.5-9B

#### Success
- [portfolio-website/003](https://github.com/sleeke/portfolio-website/pull/34): 
  - [Spec file created by Sonnet 3.6](https://github.com/sleeke/portfolio-website/blob/772bccb6e41b4f8341b8c54211d0769b81d9b613/specs/clickable-tags-in-cards.md)
  - Implementation completed with minor edits
- [booze-tracker/004](https://github.com/sleeke/booze-tracker/pull/16)
  - [Spec file created by Sonnet 3.6](https://github.com/sleeke/booze-tracker/blob/6857d0e4fdee392f85e7611e3da3343fa3c15e58/specs/copy-drink-from-drinks-list.md)
  - Implementation completed with 1 extra quality-gate pass

#### Issues

#### Failure