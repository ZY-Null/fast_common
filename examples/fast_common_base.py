from fast_common import ApiRouterInfo, McpMgr, FastapiMgr
from pydantic import BaseModel, Field
from fastapi import Body  # 参数表示推荐使用fastapi的body，目前测试fastapi和fastmcp都可用
from pathlib import Path

router = ApiRouterInfo(prefix="", tags=["DEMO"])



class TestParamInput(BaseModel):
    file_path: str = Field(..., description="Test for param input filePath")
    encoding:  str = Field(default="utf-8")

@router.register_tool(tool_name="readFile_httpversion", method="POST", url="/read-file-http", tool_description="使用pydantic的方式定义请求体,MCP不推荐使用")
async def get_file_content_http_style(req_body: TestParamInput):
    with Path(req_body.file_path).open("r", encoding=req_body.encoding) as f:
        content = f.read()
        return content

@router.register_tool(tool_name="readFile_mcpversion", method="POST", url="/read-file-mcp", tool_description="单独定义参数")
async def get_file_content_mcp_style(file_path: str = Body(..., description="文件路径"), encoding: str = Body(default="utf-8", description="解码方式")):
    print(f"you are open [{file_path}] with encoding [{encoding}]")
    with Path(file_path).open("r", encoding=encoding) as f:
        content = f.read()
        return content

def run_mcp():
    instance = McpMgr()
    instance.load_tools_info(router.tools)
    instance.run()

def run_http():
    instance = FastapiMgr()
    instance.load_tools_router(router)
    instance.startServer()
    
if __name__ == "__main__":
    isMcp = True
    isMcp = False
    if isMcp:
        run_mcp()
    else:
        run_http()
