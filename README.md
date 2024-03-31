# 🔍fish✨

## A magical way to **fi**nd **ish**(ues)

`fish` is a CLI tool (I'm working on an API targeting Slack bots as an interface ultimately) built to help you find existing issues in open source GitHub repositories. It uses the GitHub API to scrape all the individual Issue Comments that comprise an Issue, then loads them into the Chroma vector store using OpenAI's embeddings API. Once the Issue Comments are vectorized, you can query the store for similar issues based on a query string. The results are summarized by either Anthropic Claude Opus (for maximum quality) or Groq running Gemma 7B (for maximum speed).

The results and the issues referenced (it will grab the 6 most relevant comments as its references) are then pretty printed to the console with [Rich](https://rich.readthedocs.io/en/stable/introduction.html).

## Installation

Installation can be scoped to a virtual environment (if, for instance, you want to install `fish` alongside the project it's pointed at), or perhaps better globally as a general CLI tool. `pip` or `pipx` are the recommended installation methods.

```bash
`pipx` install fish # for global installation
```

## Usage

`fish` has two commands: `bait` and `go`. `bait` is used to scrape and vectorize the issues in a repository, while `go` is used to search the vector store for similar issues and return an LLM summary of the results with reference links.

### Head to the bait shop

As far as I'm aware (and I could be wrong), when you run `bait` it will wipe out the previous vector store. So for now, it can only be pointed at one repo at a time. This _will_ change. The `bait` command takes two arguments: the organization/user and the repository name. Optionally, you can provide a list of user ids to limit the scrape to just those users. This is useful if you only want to scrape the comments of the core maintainers, for example.

````bash
```bash
fish bait dbt-labs dbt-core # scrape and vectorize all issue comments in dbt-labs/dbt-core
fish bait dbt-labs dbt-core "<user id>,<user_id>,..." # this will limit the comments scraped to the list of user ids provided
````

This command can take several minutes depending on the activity history of the repo.

### Go fishin'

This is the fun part. Get a summary and references based on a query. The `go` command takes a single argument: the query string. It will return a summary of the most relevant issues based on the query string along with links and dates of the referenced comments. It has two options at present, `--fast` and `--temp`. `--fast` will use Groq running Gemma 7B for a faster response time and `--temp` will control the temperature of which every model you use, defaulting to good ole `0.5`.

```bash
fish go "What existing discussion is there around improving 'dbt init' with richer templates?"
```

The results for the above look like this:

```terminal
╭───────────────────────────── 📝Model summary✨ ──────────────────────────────╮
│ Here are the relevant issues I found that discuss improving dbt init with    │
│ richer templates:                                                            │
│                                                                              │
│ 1. Issue #3005 (https://github.com/dbt-labs/dbt-core/issues/3005)            │
│ - Discusses potentially using the `cookiecutter` tool to add more complexity │
│ to `dbt init` beyond just copying files                                      │
│ - @jtcohen6 says "if/as we add more complexity, we may decide it's worth the │
│ switch" to using `cookiecutter`                                              │
│                                                                              │
│ 2. Issue #3474 (https://github.com/dbt-labs/dbt-core/issues/3474)            │
│ - Further discussion of potentially using `cookiecutter` for a more          │
│ comprehensive project initialization                                         │
│ - @jtcohen6 notes they've had the idea before (links to                      │
│ https://github.com/fishtown-analytics/dbt-init/issues/31)                    │
│ - Suggests `cookiecutter` could be good if `init` needs to do something more │
│ complex than just copy files                                                 │
│ - Likes how interactive `cookiecutter` is with setup Q&A                     │
│                                                                              │
│ In summary, there has been some discussion around leveraging the             │
│ `cookiecutter` tool to enhance `dbt init` and provide richer, more           │
│ interactive project templates and setup. The main pros mentioned are         │
│ enabling `init` to do more complex setup beyond just copying files, and      │
│ providing an interactive Q&A experience. However, it's also noted that       │
│ `cookiecutter` may be overkill for the current starter project. The team     │
│ seems open to the idea, but would adopt it if/when `init` needs to become    │
│ more complex in the future.                                                  │
╰──────────────────────────────────────────────────────────────────────────────╯
╭───────────────────────── 📚Based on these issues🔍 ──────────────────────────╮
│ - https://github.com/dbt-labs/dbt-core/issues/4938 from jtcohen6 on          │
│ 2022-10-28                                                                   │
│ - https://github.com/dbt-labs/dbt-core/issues/3005 from jtcohen6 on          │
│ 2021-06-23                                                                   │
│ - https://github.com/dbt-labs/dbt-core/issues/8000 from jtcohen6 on          │
│ 2023-06-30                                                                   │
│ - https://github.com/dbt-labs/dbt-core/issues/6776 from jtcohen6 on          │
│ 2023-02-23                                                                   │
│ - https://github.com/dbt-labs/dbt-core/issues/3474 from jtcohen6 on          │
│ 2021-06-22                                                                   │
│ - https://github.com/dbt-labs/dbt-core/issues/9113 from dbeatty10 on         │
│ 2023-11-28                                                                   │
│                                                                              │
╰──────────────────────────────────────────────────────────────────────────────╯
```

## To Do

- [x] Additional flags for `bait` and `go` to allow for more fine-tuned control (such as temperature or model choice for `go`, and limiting date range for `bait` to drop comments older than `n` years)
- [ ] More robust error handling
- [ ] A _lot_ more testing
- [ ] Slackbot interface and build out API
- [ ] Example of hosting the API for the Slackbot
- [ ] GitHub Action to automatically update the vector store on a schedule or event
- [ ] Support building the vector store incrementally against multiple repositories
