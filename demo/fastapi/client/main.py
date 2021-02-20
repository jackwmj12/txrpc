
from fastapi import FastAPI

client = None

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

def register_rpc(app: FastAPI) -> None:
    """
    把redis挂载到app对象上面
    :param app:
    :return:
    """

    @app.on_event('startup')
    async def startup_event():
        """
        获取链接
        :return:
        """
        # await register_zmq()
        import asyncio
        loop = asyncio.get_event_loop()
        
        from twisted.internet import asyncioreactor
        asyncioreactor.install(eventloop=loop)
        from txrpc.client import RPCClient
        
        global client
        
        client = RPCClient().clientConnect(name="client", target_name="server", host="127.0.0.1", port=10000,
                  service_path="demo.fastapi.client.app.clientapp", weight=10)
        
        from txrpc.utils import logger
        logger.init()
        
        # from twisted.internet import reactor
        
        # reactor.run()

    @app.on_event('shutdown')
    async def shutdown_event():
        """
        关闭
        :return:
        """
        # app.state.rpc_client.close()
        # await app.state.rpc_client.wait_closed()

register_rpc(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app='main:app', host="0.0.0.0", port=5000, reload=True, debug=True)