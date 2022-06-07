# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : defer.py
# @Time     : 2022-06-07 17:31
# @Software : txrpc
# @Email    : jackwmj12@163.com
# @Github   : 
# @Desc     : 
#            ┏┓      ┏┓
#          ┏┛┻━━━┛┻┓
#          ┃      ━      ┃
#          ┃  ┳┛  ┗┳  ┃
#          ┃              ┃
#          ┃      ┻      ┃
#          ┗━┓      ┏━┛
#              ┃      ┃
#              ┃      ┗━━━┓
#              ┃              ┣┓
#              ┃              ┏┛
#              ┗┓┓┏━┳┓┏┛
#                ┃┫┫  ┃┫┫
#                ┗┻┛  ┗┻┛
#                 神兽保佑，代码无BUG!
#
#
#
import types
from functools import wraps

def returnValue(val):
    """
    Return val from a L{inlineCallbacks} generator.

    Note: this is currently implemented by raising an exception
    derived from L{BaseException}.  You might want to change any
    'except:' clauses to an 'except Exception:' clause so as not to
    catch this exception.

    Also: while this function currently will work when called from
    within arbitrary functions called from within the generator, do
    not rely upon this behavior.
    """
    raise _DefGen_Return(val)

def inlineCallbacks(f):
    @wraps(f)
    def unwindGenerator(*args, **kwargs):
        ret = None
        gen = f(*args, **kwargs)
        # print("type = ",type(gen))
        # print("enter function:", f.__name__)
        if isinstance(gen,types.GeneratorType):
            while True:
                try:
                    ret = gen.send(ret)
                except _DefGen_Return as e:
                    # print("leave function:{} result:{}".format(f.__name__, e.getValue()))
                    return e.getValue()
                except StopIteration:
                    # print("stop iteration raise")
                    return ret
        else:
            return gen

    return unwindGenerator

class _DefGen_Return(BaseException):
    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value