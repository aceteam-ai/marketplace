# AceTeam Marketplace

Plugins, community node packages, and registry for the [AceTeam.ai](https://aceteam.ai) workflow ecosystem.

## Plugins

| Plugin | Description | Requires Account |
|--------|-------------|:---:|
| **aceteam** | Manage AI agents, knowledge bases, documents, and workbenches | Yes |
| **aceflows** | Build and run agentic AI workflows with visual graph editor | Yes |
| **ace-local** | Run workflows locally — list nodes, execute DAGs, install community packages | No |

### Installation

```bash
# Add the marketplace
/plugin marketplace add aceteam-ai/marketplace

# Install plugins
/plugin install aceteam@aceteam
/plugin install aceflows@aceteam
/plugin install ace-local@aceteam
```

### AceTeam Plugin

- List, create, update, and delete AI agents
- Chat with agents from your terminal
- Search knowledge bases and manage collections
- Manage documents and workbenches
- Link MCP servers and tools to agents

### AceFlows Plugin

- List, create, and update workflow graphs
- Browse available node types and their schemas
- Run workflow pipelines and get results
- Access graph templates for common patterns

### Ace Local Plugin

- `list_nodes` — browse all available node types with full schemas
- `run_workflow` — execute a workflow from a JSON file or inline definition
- `validate_workflow` — check a workflow definition without running it
- `install_nodes` — install community node packages
- `search_registry` — find community node packages by keyword

## Community Node Registry

The `registry/` directory is a Homebrew-style index of community node packages. Each package is a JSON entry listing the PyPI package name, node types, and metadata.

Browse available packages:

| Package | Nodes | Description |
|---------|-------|-------------|
| [aceteam-nodes](registry/aceteam-nodes.json) | LLM, APICall, comparison operators | Core workflow nodes |
| [aceteam-email-nodes](registry/email-nodes.json) | SmtpSend, GmailSearch, GmailDraft | Email automation |
| [aceteam-fireflies-nodes](registry/fireflies-nodes.json) | FirefliesListTranscripts, FirefliesGetTranscript, FirefliesSearchTranscripts | Meeting transcripts |

### Installing Community Packages

```bash
# Via the ace-local MCP plugin
search_registry("email")
install_nodes("aceteam-email-nodes")

# Or manually
uv tool install --with aceteam-email-nodes aceteam-nodes[mcp]
```

### Publishing Your Own Package

See [Node Package Format](docs/node-package-format.md) for the full spec. In short:

1. Create a Python package with `aceteam.nodes` entry point
2. Implement nodes following the `Node[Input, Output, Params]` pattern
3. Submit a PR adding a JSON entry to `registry/` and updating `_index.json`

## Building Node Packages

Community node packages use Python entry points for automatic discovery. When installed alongside `aceteam-nodes`, they register their node types into the workflow engine.

```
my-nodes/
  pyproject.toml              # declares aceteam.nodes entry point
  src/my_nodes/
    __init__.py               # register_nodes(builder) function
    my_node.py                # Node implementations
```

See [docs/node-package-format.md](docs/node-package-format.md) for the complete specification and examples.

## Authentication

The **aceteam** and **aceflows** plugins connect to `https://aceteam.ai/api/mcp/` and require authentication. You'll be prompted to authenticate when you first use a tool.

The **ace-local** plugin runs entirely on your machine and does not require an AceTeam account. Community nodes that access external APIs (Gmail, Fireflies, etc.) use environment variables for credentials.

## Requirements

- [Claude Code](https://claude.ai/code) CLI
- Python 3.12+ (for ace-local)
- An [AceTeam.ai](https://aceteam.ai) account (for aceteam and aceflows plugins)
