import json
import os

import txrpc2
from txrpc2.globalobject import GlobalObject
from txrpc2.client import RPCClient
from txrpc2.server import RPCServer
from loguru import logger

with open(os.sep.join([os.path.dirname(os.path.abspath(__file__)),"config.json"])) as f:
    GlobalObject().config = json.load(f)

server = RPCServer("CLIENT_SERVER")

@server.leafConnectHandle
def doLeafConnect(name, transport):
    '''
    :return
    '''
    logger.debug("{} connected".format(name))

@server.leafLostConnectHandle
def doChildLostConnect(childId):
    '''
    :return
    '''
    logger.debug("{} lost connect".format(childId))

client = RPCClient("CLIENT").clientConnect()

txrpc2.run()