from fastmcp import FastMCP
from fastmcp.tools import FunctionTool
from fast_common import ToolsInfo
import inspect
from typing import get_type_hints
from functools import wraps, update_wrapper

def unpack_model(model_class):
    """
    装饰器：保持离散参数签名，同时确保类型注解正确
    """
    def decorator(func):
        # 获取模型字段
        fields = model_class.model_fields
        # 构建新的参数列表和类型注解
        parameters = []
        new_annotations = {}
        for field_name, field_info in fields.items():
            # 获取字段类型注解
            annotation = field_info.annotation
            if annotation is None:
                # 如果字段没有显式注解，尝试从默认值推断或使用 Any
                from typing import Any
                annotation = Any
            # 创建参数
            default = field_info.default if not field_info.is_required() else inspect.Parameter.empty
            param = inspect.Parameter(
                name=field_name,
                kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                default=default,
                annotation=annotation
            )
            parameters.append(param)
            new_annotations[field_name] = annotation
        # 保留原始函数的返回类型注解
        original_hints = get_type_hints(func)
        if 'return' in original_hints:
            new_annotations['return'] = original_hints['return']
        # 创建新签名
        new_sig = inspect.Signature(parameters)
        # 创建包装函数
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 这里直接调用原函数，参数验证由 MCP 服务器处理
            return await func(*args, **kwargs)
        # 使用 update_wrapper 来保留更多属性
        wrapper = update_wrapper(wrapper, func)
        # 更新签名和注解
        wrapper.__signature__ = new_sig
        wrapper.__annotations__ = new_annotations
        return wrapper
    return decorator

class McpMgr:
    def __init__(self):
        self.mcp = FastMCP(name="vscode mcp_server", version="0.0.0")
        pass

    def add_tools(self, fn: callable, tool_name: str, tool_desc: str):
        new_tool = FunctionTool.from_function(fn, name=tool_name, description=tool_desc)
        self.mcp.add_tool(new_tool)

    def add_tool_dynamic(self, tool_info: ToolsInfo):
        if tool_info.param_model is not None:
            ModelType = tool_info.param_model
            @unpack_model(ModelType)
            async def callback_func(**params):
                return await tool_info.callback(**params)
            self.mcp.tool(name_or_fn=callback_func, name=tool_info.name, description=tool_info.description)
        else:
            self.mcp.tool(name_or_fn=tool_info.callback, name=tool_info.name, description=tool_info.description)

    def load_tools_info(self, tools_info: list[ToolsInfo]):
        for tool_info in tools_info:
            self.add_tool_dynamic(tool_info)

    def run(self):
        # 自行确定，目前暂时写死
        self.mcp.run(transport="streamable-http", host="0.0.0.0", port=40001)
    
    def delete_tool(self, name: str):
        self.mcp.remove_tool(name)
        return