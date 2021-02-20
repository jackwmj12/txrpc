from fastapi import FastAPI

server = None

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
		
		from twisted.internet import reactor
		
		global server
		
		from txrpc.utils import logger
		
		from txrpc.server import RPCServer
		
		logger.init()
		
		def fun():
			d = RPCServer.callRemote("client", "client_test")
			if not d:
				return None
			d.addCallback(logger.debug)
			d.addErrback(logger.err)
			return d
		
		def doChildConnect(name, transport):
			'''
			:return
			'''
			logger.debug("{} connected".format(name))
			
			for i in range(1000):
				reactor.callLater(i * 2 + 1, fun)
		
		def doChildLostConnect(childId):
			'''
			:return
			'''
			logger.debug("{} lost connect".format(childId))
		
		server = RPCServer("server", 10000, service_path="demo.fastapi.server.app.serverapp")
		server.setDoWhenChildConnect(doChildConnect)
		server.setDoWhenChildLostConnect(doChildLostConnect)
	
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
	
	uvicorn.run(app='main:app', host="0.0.0.0", port=5001, reload=True, debug=True)