from txrpc.utils import logger
from txrpc.client import RPCClient

logger.init()

app = RPCClient()\
	.clientConnect(name="client",target_name="server",host="127.0.0.1",port=10000,service_path="demo.baserpc.app.clientapp",weight=10)

@app.startServiceHandle
def doWhenStart():
	logger.debug("i am starting")

app.run()