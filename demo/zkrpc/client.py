import asyncio
from twisted.internet import asyncioreactor
loop = asyncio.get_event_loop()
asyncioreactor.install(eventloop=loop)

from txrpc.utils import logger
from txrpc.client import RPCClient

logger.init()

client = RPCClient().clientConnect(
    name="client",
    target_name="server",
    host="127.0.0.1",
    port=10000,
    service_path="demo.zkrpc.app.clientapp"
)

client.run()