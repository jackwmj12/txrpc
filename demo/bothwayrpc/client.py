import json
import os

import txrpc
from txrpc.globalobject import GlobalObject
from txrpc.client import RPCClient
from txrpc.server import RPCServer
from loguru import logger

with open(os.sep.join([os.path.dirname(os.path.abspath(__file__)),"config.json"])) as f:
    GlobalObject().config = json.load(f)

server = RPCServer("CLIENT_SERVER")

@server.childConnectHandle
def doChildConnect(name, transport):
    '''
    :return
    '''
    logger.debug("{} connected".format(name))

@server.childLostConnectHandle
def doChildLostConnect(childId):
    '''
    :return
    '''
    logger.debug("{} lost connect".format(childId))

client = RPCClient("CLIENT").clientConnect()

txrpc.run()