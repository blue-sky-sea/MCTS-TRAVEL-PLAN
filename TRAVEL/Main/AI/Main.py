#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 13:59:39 2021

@author: liuyi
"""

from datetime import date
from datetime import datetime
from datetime import timedelta

start_datetime = datetime(2021, 2, 1, 9, 30, 0)
end_datetime = datetime(2021,2,1,20,30,0)
"""temptime=start_datetime+timedelta(hours=3,minutes=20)
if(temptime.hour>=11 and temptime.hour<=13):
    print(temptime.hour,"该吃午饭了")"""
    
import MCTS
print("生成MCTS-AI管理器")
mcts_manager = MCTS.mcts(timeLimit=10000)#开启mcts程序
print("初始化中...")
initialstate=MCTS.State(nowspotname="横滨港未来21",
                        travelpoint=0,
                        totaltravelpoint=0,
                        moneycost=0,
                        onfoottime=0,
                        now_datetime=start_datetime,
                        end_datetime=end_datetime,
                        hasbeenspots=[])

print("初始化sucess")
#print("是否开启AI计算？"）

#input("yes/no/enter")
root = mcts_manager.search(initialState=initialstate)