# Vibe Coding Tutorial and Best Practices

Elaborate with LLM on the specs of the project (or just take one-shot)

```text
write a spec for an application, that will be a <something> clone. be as specific as possible. we're going to be using <python> for the backend.
```

IDE: Cursor or Windsurf

Tell what technologies you would use, how you want to code, what workflow you would follow in the rules section (kind of system message).

Model: claude-3.7-sonnet-thinking / Agent mode


```text
Descrption: How we should prefer to code

# Coding pattern preferences

- Always prefer simple solutions
- Avoid duplication of code whenever possible, which means checking for other areas of the codebase that might already have similar code and functionality (DRY principle)
- Write code that takes into account the different environments: dev, test, and prod
- You are careful to only make changes that are requested or you are confident are well understood and related to the change being requested
- When fixing an issue or bug, do not introduce a new pattern or technology without first exhausting all options for the existing implementation. and if you finally do this, make sure to remove the old implementation afterwards so we don't have duplicate logic.
- Keep the codebase very clean and organized.
- Avoid writing scripts in files if possible, especially if the script is likely only to be run once.
- Avoid having files over 200-300 lines of code. Refactor at that point.
- Mock data is only needed for tests, never mock data for dev or prod
- Never add stubbing or fake data patterns to code that affects the dev or prod environments
- Never override my .env file without first asking and confirming
```

```text
Descrption: This is the project's tech stack

# Technical stack

- Python for the backend
- html/js for the frontend
- SQL databases, never JSON file storage
- Separate databases for dev, test, and prod
- Elasticsearch for search, using elastic.co hosting
- Elastic.co will have dev and prod indexes
- Python tests
```

```text
Descrption: How I like to code (workflow)

# Coding workflow preferences

- Focus on the areas of code relevant to the task
- Do not touch code that is unrelated to the task
- Write thorough tests for all major functionality
- Avoid making major changes to the patterns and architecture of how a feature works, after it has shown to work well, unless explicitly instructed
- Always think about what other methods and areas of code might be affected by code changes
```

Copy the spec into prompt of IDE.

Be aware of how much context you give to the model. (e.g. "Start new for better results")

Always write tests and make sure they pass, do integration tests. Use popular stack.

example prompt for editing:

```text
enforce a maximum tag length limit of 20 chars, make sure we dont already have code for this, write tests for this after implementation
```

YOLO mode directly pushes everything (risky), manual mode asks for confirmation, auto mode is in between.

Commands can take up to 15 min to finish, but you can work on different tasks in different branches in differnet windows. Refactor code if needed. Commit often.

Replit on mobile is the future?

## AI DEV Project Setup Prompts

[cursor-ai-rules](http://notes.switchdimension.com/cursor-ai-rules)

Setup in VSCode, create `.github` folder and add `copilot-instructions.md` file for general instructions.

For specific instructions, create a `prompts` folder inside `.github` and add `.prompt.md` files for each prompt.

[AI-Dev-Project-Setup-Prompts](https://notes.switchdimension.com/AI-Dev-Project-Setup-Prompts-18fb5b07a94380758bd6e92baa5e8c98)

- These prompts help set up comprehensive project documentation for your LLM development
- Documentation is essential for:
  - Helping your LLM understand the project scope
  - Supporting you as a product creator/developer
  - Understanding software development flow
- Working through this process will:
  - Raise important project questions
  - Reveal alternative approaches
  - Generate new ideas
- Getting started:
  - Paste the first prompt into an LLM
  - Iterate with the model
  - Save each output as a file for use with subsequent prompts

>>[!IMPORTANT]
> ⚡️Quick Instructions: First, paste the Product Expert Prompt into o3 Mini and answer its questions. Next, paste the PRD output and UX prompt into a new chat and answer those questions. Finally, add both the PRD and UX documents to the context of another new chat, paste in the Software Architect prompt, and answer its questions.

1. Use [Product requirements prompt](../.github/prompts/01_product_requirements.prompt.md) to work with an expert product manager to create your requirements. Save result as `PRD.md` in `doc/`-folder.
2. Work with a expert UX designer to figure out how you should approach the design of this App. Use the [UI Design prompt](../.github/prompts/02_UI_design_doc.prompt.md) in your LLM and attach the `PRD.md` with it.
3. Work with a Development Architect to figure out how to build your app. It’s a good idea not to be too prescriptive with your preferred stack. Before you start the doc. Have the model come up with unbiased ideas of how to build to identify new options. Add the previous docs with these prompts as attachments. Paste in the two previous docs to the chat window before proceeding with this prompt or create a project and attach them as files.
