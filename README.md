# AceTeam Claude Code Plugins

Claude Code plugins for [AceTeam.ai](https://aceteam.ai) — AI agent management and workflow automation MCP servers.

## Plugins

| Plugin | Description |
|--------|-------------|
| **aceteam** | Manage AI agents, knowledge bases, documents, and workbenches |
| **aceflows** | Build and run agentic AI workflows with visual graph editor |

## Installation

### Add the marketplace

```
/plugin marketplace add aceteam-ai/claude-plugins
```

### Install plugins

```
/plugin install aceteam@aceteam
/plugin install aceflows@aceteam
```

### Or install both at once

```
/plugin install aceteam@aceteam && /plugin install aceflows@aceteam
```

## What you can do

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

## Authentication

Both plugins connect to `https://aceteam.ai/api/mcp/` and require authentication. You'll be prompted to authenticate when you first use a tool.

## Requirements

- [Claude Code](https://claude.ai/code) CLI
- An [AceTeam.ai](https://aceteam.ai) account
