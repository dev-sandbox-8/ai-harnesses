---
name: concept
description: Provides a quick overview of a concept.
---

# Concept Skill
This skill provides a quick overview of a concept. It can be used to quickly understand the basics of a topic, or to get a high-level overview of a complex subject.

## Output Format

The input to the skill is a string containing the name of the concept to be explained. The output should be divided into clear headers and sections as listed below, as well as following these formatting rules: 

1 Section headings should be in a bolder style than the rest of the document
2. Code snippets should be formatted as code blocks with appropriate syntax highlighting.
3. Lists should be formatted as bullet points or numbered lists, depending on the context.
4. The overall formatting should be clean and easy to read, with consistent spacing and alignment.

### Summary
A super-concise definition of the concept in one or two sentences. The explanation should be clear and straightforward, avoiding jargon or technical language where possible. The goal is to provide a quick and accessible overview of the concept that can be easily understood by someone with little to no prior knowledge of the topic.

### Technical detail
3. A simple example to illustrate the concept, if applicable.

### Further reading
Links to relevant documentation, articles, or other resources for users who want to learn more about the concept.

### Other common meanings
If the concept has different meanings in different contexts, provide a brief explanation of the other common meanings, and clarify which meaning is being explained in the summary and technical detail sections.

This section should only be included if there has not been sufficient context to determine which meaning of the concept is being explained. If there is sufficient context, this section should be omitted to avoid confusion.  

## Additional context

Context for the request should be provided in the following prioritized order:

1. Any additional context provided by the user in the request itself. This can include specific questions or areas of interest that the user wants to focus on in the explanation.
2. The content of the currently open files in the user's editor, if applicable. This can provide valuable context for understanding the user's request and tailoring the explanation to their specific needs.
3. The content of the current project/repository, if applicable. This can provide additional context about the user's work and the technologies they are using, which can help to further tailor the explanation to their specific needs.

If there is too little context to make a reasonable assumption, the skill should ask the user for clarification on which field they are referring to before providing an explanation.