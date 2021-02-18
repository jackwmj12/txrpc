import asyncio
from twisted.internet import asyncioreactor
loop = asyncio.get_event_loop()
asyncioreactor.install(eventloop=loop)

from utils import logger
from rpc import RPCClient

logger.init()

client = RPCClient(
    name="client",
    target_name="server",
    host="127.0.0.1",
    port=10000,
    service_path="demo.zkrpc.app.clientapp"
)

client.run()