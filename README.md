# 🎣✨fiish🐟🔍

> [!NOTE]
> This is a brand new project. It's like pre-pre-alpha. I'm still working on testing and error handling. It's not on PyPI, and it's very much a work in progress, at present only use it to hack around with if you're interested in RAG flows.

## A magical way to (fi)nd (ish)ues in open source GitHub repos

`fiish` is a CLI tool (I'm working on an API targeting Slackbots as an interface ultimately) built to help you find existing issues in open source GitHub repositories. It uses the GitHub API to scrape all the individual Issue Comments that comprise an Issue, then loads them into the Chroma vector store using OpenAI's embeddings API. Once the Issue Comments are vectorized, you can query the store for similar issues based on a query string. The results are summarized by either Anthropic Claude Opus (for maximum quality) or Groq running Gemma 7B (for maximum speed).

The results and the issues referenced (it will grab the 6 most relevant comments as its references) are then pretty printed to the console with [Rich](https://rich.readthedocs.io/en/stable/introduction.html).

## Installation

Installation can be scoped to a virtual environment (if, for instance, you want to install `fiish` alongside the project it's pointed at), or perhaps better globally as a general CLI tool. `pip` or `pipx` will be the recommended installation methods once I get adequate testing in place. For now you'll need to clone the repo and install it locally. It's set up like a standard python package: activate a virtual environment, install dependencies, then `pip install .` from the root of the repo. Then, off you go!

Soon:

```bash
pipx install fiish # for global installation
```

You'll need 4 environment variables (1 optional) set to use `fiish`, which is a lot for a CLI I know, but once this is working on a server via API + Slackbot I think this will feel less onerous. I made the choice to use the best options for each stage, which means several different external APIs:

```bash
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_PAT # for accessing the GitHub API
OPENAI_API_KEY=your_openai_api_key # for the embeddings API
ANTHROPIC_API_KEY=your_anthropic_api_key # for the summaries, Claude is really good at this
GROQ_API_KEY=your_groq_api_key # optional, if you want to use the --fast flag
```

## Usage

`fiish` has two commands: `bait` and `go`. `bait` is used to scrape and vectorize the issues in a repository (your proverbial bucket of bait), while `go` is used to search the vector store for similar issues and return an LLM summary of the results with reference links (the fish you catch).

### Head to the bait shop

When you run `bait` it will wipe out the previous vector store. So for now, it can only be pointed at one repo at a time. This _will_ change. The `bait` command takes two arguments: the organization/user and the repository name. Optionally, you can provide a list of user ids to limit the scrape to just those users. This is useful if you only want to scrape the comments of the core maintainers, for example.

```bash
fiish bait DetachHead basedpyright # scrape and vectorize all issue comments in dbt-labs/dbt-core
fiish bait DetachHead basedpyright "DetachHead,<another_user_login>,..." # this will limit the comments scraped to the list of user ids provided
```

This command can take several minutes depending on the activity history of the repo.

### Go fishin'

This is the fun part. Get a summary and references based on a query. The `go` command takes a single argument: the query string. It will return a summary of the most relevant issues based on the query string along with links and dates of the referenced comments. It has two options at present, `--fast` and `--temp`. `--fast` will use Groq running Gemma 7B for a faster response time and `--temp` will control the temperature of which every model you use, defaulting to good ole `0.5`.

```bash
fiish go "How should users deal with implicit imports errors?"
```

The results for the above look like this:

```terminal
╭───────────────────────────── 📝Model summary✨ ──────────────────────────────╮
│ Here are the relevant issues I found related to implicit imports in          │
│ basedpyright:                                                                │
│                                                                              │
│ 1. Issue #158: This issue discusses a new configuration option added in      │
│ basedpyright 1.8.0 to disable reporting of implicit relative imports. The    │
│ `reportImplicitRelativeImport` setting in `pyproject.toml` can be set to     │
│ `false` to disable this behavior. Users can also set the `typeCheckingMode`  │
│ to `"strict"`, `"standard"`, or `"basic"` to control the additional rules    │
│ beyond upstream pyright.                                                     │
│                                                                              │
│ 2. Issue #178: In this issue, a user reports potential problems importing    │
│ PySide6 with basedpyright. The maintainer suggests it could be related to    │
│ the implicit import issue described in #158. They request a minimal          │
│ reproducible example to investigate further.                                 │
│                                                                              │
│ In summary, basedpyright added a configuration option in version 1.8.0 to    │
│ allow disabling the reporting of implicit relative imports via the           │
│ `reportImplicitRelativeImport` setting. This provides a way for users to     │
│ deal with implicit imports if they find the reporting problematic.           │
│                                                                              │
│ The pros are that it gives users flexibility to control this behavior to     │
│ suit their needs. The potential con is that disabling the check could allow  │
│ implicit imports to go unnoticed, which some may consider bad practice.      │
│                                                                              │
│ The maintainer is open to investigating specific cases where implicit        │
│ imports may not be handled correctly, but would need a reproducible example  │
│ to dig into it, as mentioned in issue #178 in relation to importing PySide6. │
╰──────────────────────────────────────────────────────────────────────────────╯
╭───────────────────────── 📚Based on these issues🔍 ──────────────────────────╮
│ - https://github.com/DetachHead/basedpyright/issues/35 from DetachHead on    │
│ 2024-01-19                                                                   │
│ - https://github.com/DetachHead/basedpyright/issues/78 from DetachHead on    │
│ 2024-02-11                                                                   │
│ - https://github.com/DetachHead/basedpyright/issues/158 from DetachHead on   │
│ 2024-03-29                                                                   │
│ - https://github.com/DetachHead/basedpyright/issues/225 from DetachHead on   │
│ 2024-03-29                                                                   │
│ - https://github.com/DetachHead/basedpyright/issues/78 from DetachHead on    │
│ 2024-02-11                                                                   │
│ - https://github.com/DetachHead/basedpyright/issues/178 from DetachHead on   │
│ 2024-03-29                                                                   │
│                                                                              │
╰──────────────────────────────────────────────────────────────────────────────╯``
```

## To Do

Testing, error handling, and completing type annotations so that my linter will shut up are the top priorities for now, with work on the API and Slackbot interface next priority when I'm bored with that.

- [x] Additional flags for `bait` and `go` to allow for more fine-tuned control (such as temperature or model choice for `go`, and limiting date range for `bait` to drop comments older than `n` years)
- [ ] More robust error handling (like actually adding some)
- [ ] A _lot_ more testing (again, like, actually adding some)
- [ ] Slackbot interface and build out API
- [ ] Example of hosting the API for the Slackbot
- [ ] GitHub Action to automatically update the vector store on a schedule or event
- [ ] Support building the vector store incrementally against multiple repositories
- [ ] Tiered RAG flow that pulls the entire issue for all of the individual comments it selects, I think this will give better results for the response summary, and both Gemma and Claude have really big context windows

![A robot fishing at sunset](https://github.com/gwenwindflower/fiish/assets/91998347/3d2c39a0-3159-4d21-a75f-a7a1972bed3b)
