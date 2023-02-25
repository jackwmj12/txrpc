
'''
Created on 2019-11-22
@author: LCC
            ┏┓　　　┏┓
          ┏┛┻━━━┛┻┓
          ┃　　　━　　　┃
          ┃　┳┛　┗┳　┃
          ┃　　　　　　　┃
          ┃　　　┻　　　┃
          ┗━┓　　　┏━┛
              ┃　　　┃
              ┃　　　┗━━━┓
              ┃　　　　　　　┣┓
              ┃　　　　　　　┏┛
              ┗┓┓┏━┳┓┏┛
                ┃┫┫　┃┫┫
                ┗┻┛　┗┻┛
                 神兽保佑，代码无BUG!
 @desc：
    分布式布局模块包
                   ---------- leaf1
                  |
        root -- node(leaf) -- leaf2
        
        root call node -> callNodeChildByName("leaf",...)
        root call leaf1 -> callNodeChildByID("leaf1",...)
'''

# 导入master服务，该服务主要提供
#     master 控制 node 的 remote连接
#     master 控制 node 的 reload
#     master 控制 node 的 stop