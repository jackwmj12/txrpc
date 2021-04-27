import aiozk
import os
from txrpc.globalobject import remoteserviceHandle
from loguru import logger

@remoteserviceHandle("SERVER")
async def client_test():
    zk = aiozk.ZKClient('{}:2181'.format(os.environ.get("TEST_ZK_HOST")))
    await zk.start()
    await zk.ensure_path('/greeting/to')
    await zk.delete('/greeting/to/words')
    await zk.create('/greeting/to/words',"hello")
    data, stat = await zk.get('/greeting/to/words')
    # logger.debug(type(data))
    # logger.debug(type(stat))
    logger.debug(data.decode())
    # b'hello world' is printed
    # await zk.delete('/greeting/to/words')
    # await zk.close()
    return f"this is a response from client : {data.decode()}"