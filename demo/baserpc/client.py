from globalobject import remoteserviceHandle, GlobalObject
from utils import logger
from rpc import RPCClient

logger.init()

client = RPCClient(name="client",target_name="server",host="127.0.0.1",port=10000,service_path="demo.baserpc.app.clientapp",weight=10)
client.run()