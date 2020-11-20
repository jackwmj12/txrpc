from globalobject import remoteserviceHandle
from utils import Log


@remoteserviceHandle("server")
def test():
    Log.debug(32*"*")
    return 32*"*"