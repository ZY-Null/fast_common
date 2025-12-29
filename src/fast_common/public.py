from dataclasses import dataclass, field
from typing import Literal, Callable, Optional, Type
from pydantic import BaseModel
from functools import wraps

HTTP_REQ_TYPE = Literal["GET","POST","PUT","DELETE","PATCH"]

@dataclass
class ToolsInfo:
    method: HTTP_REQ_TYPE
    url: str
    name: str
    description: str
    callback: Callable[[any], any]
    param_model: Optional[Type[BaseModel]]


@dataclass
class ApiRouterInfo:
    prefix: str = ""
    tags: list[str] = field(default_factory=list[str])
    tools: list[ToolsInfo] = field(default_factory=list[ToolsInfo])

    def register_tool(self, tool_name: str, method: HTTP_REQ_TYPE, url: str, tool_description: str):
        def decorator(func: Callable):
            if all(tool.name != tool_name for tool in self.tools):
                toolInfo: ToolsInfo = ToolsInfo(
                    method=method,
                    url=url,
                    name=tool_name,
                    description=tool_description,
                    param_model=None,
                    callback=func
                )
                self.tools.append(toolInfo)
            return func
        return decorator
