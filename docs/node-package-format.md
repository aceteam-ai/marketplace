# Node Package Format

Standard format for community node packages in the AceTeam workflow ecosystem.

## Package Structure

```
my-nodes/
  pyproject.toml
  src/my_nodes/
    __init__.py          # register_nodes() entry point
    my_node.py           # Node implementations
  tests/
    test_my_node.py
```

## pyproject.toml

```toml
[project]
name = "my-nodes"
version = "0.1.0"
description = "My custom workflow nodes"
requires-python = ">=3.12"
dependencies = [
    "aceteam-workflow-engine>=2.0.0rc5",
]

[project.entry-points."aceteam.nodes"]
my_nodes = "my_nodes:register_nodes"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/my_nodes"]
```

The entry point group **must** be `aceteam.nodes`. The entry point value **must** be a callable with signature `register_nodes(builder: EagerNodeRegistryBuilder) -> None`.

## register_nodes Function

```python
from __future__ import annotations

from typing import TYPE_CHECKING

from .my_node import MyNode

if TYPE_CHECKING:
    from workflow_engine.core.node import EagerNodeRegistryBuilder

def register_nodes(builder: EagerNodeRegistryBuilder) -> None:
    builder.register_node_class(MyNode)
```

The function receives a pre-populated builder containing all core + aceteam nodes. Register your node classes onto it. Do not call `.build()` — the caller handles that.

## Node Implementation

Every node must follow the `Node[Input, Output, Params]` generic pattern:

```python
from functools import cached_property
from typing import Literal

from overrides import override
from pydantic import Field
from workflow_engine import Context, Data, Node, NodeTypeInfo, Params, StringValue

class MyNodeParams(Params):
    setting: StringValue = Field(
        title="Setting",
        default=StringValue("default"),
        description="The configuration setting.",
    )

class MyNodeInput(Data):
    text: StringValue = Field(
        title="Text",
        description="The input text.",
    )

class MyNodeOutput(Data):
    result: StringValue = Field(
        title="Result",
        description="The output result.",
    )

class MyNode(Node[MyNodeInput, MyNodeOutput, MyNodeParams]):
    TYPE_INFO = NodeTypeInfo.from_parameter_type(
        name="MyNode",
        display_name="My Node",
        description="Does something useful.",
        version="1.0.0",
        parameter_type=MyNodeParams,
    )
    type: Literal["MyNode"] = "MyNode"

    @cached_property
    def input_type(self):
        return MyNodeInput

    @cached_property
    def output_type(self):
        return MyNodeOutput

    @override
    async def run(self, context: Context, input: MyNodeInput) -> MyNodeOutput:
        return MyNodeOutput(result=StringValue(input.text.root.upper()))
```

### Requirements

- **Do not use `from __future__ import annotations` in node files.** The engine inspects `type: Literal["..."]` annotations at runtime; future annotations turn them into strings, breaking node registration.
- `TYPE_INFO` must be a `ClassVar[NodeTypeInfo]` with a unique `name`, semantic `version`, and human-readable `display_name` and `description`.
- `type` must be a `Literal` matching the `name` in `TYPE_INFO`.
- `input_type` and `output_type` must be `@cached_property` returning the Data subclass.
- `run()` must be async and return an instance of the output type.
- All `Data` and `Params` fields must use `Field()` with `title` and `description`.

## Authentication Convention

Community nodes that require credentials should read from environment variables. Document which env vars are required in your package README.

```python
import os

class MyAPINode(Node[...]):
    async def run(self, context, input):
        api_key = os.environ.get("MY_SERVICE_API_KEY")
        if not api_key:
            raise ValueError("MY_SERVICE_API_KEY environment variable is required")
        ...
```

## Installing Community Packages

For use with the ace-local MCP plugin, install packages into the tool environment:

```bash
uv tool install --with my-nodes aceteam-nodes[mcp]
```

Then restart your MCP server. The discovery system will find all installed packages that declare `aceteam.nodes` entry points.

## Publishing to the Registry

Submit a PR to the [marketplace](https://github.com/aceteam-ai/marketplace) repo adding a JSON file to `registry/`:

```json
{
  "name": "my-nodes",
  "version": "0.1.0",
  "description": "My custom workflow nodes",
  "pypi": "my-nodes",
  "repository": "https://github.com/you/my-nodes",
  "nodes": ["MyNode"],
  "keywords": ["custom"],
  "author": {
    "name": "Your Name",
    "email": "you@example.com"
  }
}
```

And add the filename to `_index.json`. See existing entries for reference.
