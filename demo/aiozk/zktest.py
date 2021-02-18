import os

import aiozk
import asyncio

async def main():
    zk = aiozk.ZKClient('{}:2181'.format(os.environ.get("HOST_OF_TEST")))
    await zk.start()
    await zk.ensure_path('/test')
    await zk.create('/test/to', 'hello world')
    data, stat = await zk.get('/test/to')
    print(type(data))
    print(type(stat))
    print(data)
    # b'hello world' is printed
    await zk.delete('/test/to')
    await zk.close()


asyncio.run(main())


# import aiozk
# import asyncio
#
#
# async def main():
#     zk = aiozk.ZKClient('server1:2181,server2:2181,server3:2181')
#     await zk.start()
#     await zk.ensure_path('/greeting/to')
#     await zk.create('/greeting/to/world', 'hello world')
#     data, stat = await zk.get('/greeting/to/world')
#     print(type(data))
#     print(type(stat))
#     print(data)
#     # b'hello world' is printed
#     await zk.delete('/greeting/to/world')
#     await zk.close()
#
#
# asyncio.run(main())