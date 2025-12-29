from fastapi import FastAPI, APIRouter
from fast_common import ToolsInfo, ApiRouterInfo
import uvicorn
from pydantic import validate_call

class FastapiMgr:
    def __init__(self):
        self.api = FastAPI(title="MCP Plugin API", version="1.0.0", description="MCP Plugin API")
        self.routers: dict[str, APIRouter] = {}

    @staticmethod
    def _add_route(router: APIRouter, toolInfo: ToolsInfo):
        if toolInfo.param_model is not None:
            ModelType = toolInfo.param_model
            async def callback_func(params: ModelType):
                return await toolInfo.callback(**params.model_dump())
            router.add_api_route(name=toolInfo.name, path=toolInfo.url, endpoint=callback_func, methods=[toolInfo.method], description=toolInfo.description)
        else:
            router.add_api_route(name=toolInfo.name, path=toolInfo.url, endpoint=toolInfo.callback, methods=[toolInfo.method], description=toolInfo.description)

    @validate_call
    def load_tools_router(self, api_router: ApiRouterInfo):
        new_router = APIRouter(prefix=api_router.prefix, tags=api_router.tags)
        for toolInfo in api_router.tools:
            FastapiMgr._add_route(new_router, toolInfo)
        self.api.include_router(router=new_router)

    def startServer(self):
        # 自行确定，目前暂时写死
        uvicorn.run(app=self.api, host="0.0.0.0", port=10030)