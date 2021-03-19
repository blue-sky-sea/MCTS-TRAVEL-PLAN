from __future__ import division
import copy 
import time
import math
import random
import xlrd
from datetime import date
from datetime import datetime
from datetime import timedelta

CHILDFLAG = False

JINJIAFLAG = False
 
SHOPPINGFLAG = False

ANIMEFLAG = False

NIGHTSCOPFLAG = True

WANTTOGO =["横滨中华街","横滨地标大厦"]
WILLNEVERGO = ["英国馆和港见丘公园","GUNDAM FACTORY YOKOHAMA"]

print("READ IN DATA...")
import pandas as pd

spot_io = "../../DATA/YOKOHAMA.xls"
traffic_io = "../../DATA/YOKOHAMA_traffic.xlsx"


spot_data = pd.read_excel(spot_io,sheet_name = 'Sheet1')
traffic_data = pd.read_excel(traffic_io,sheet_name = 'Sheet1')

spot_data_dictlist = spot_data.to_dict(orient='records')
traffic_data_dictlist = traffic_data.to_dict(orient='records')

def find_route(original,destination):
    routes = []
    #flag=False
    for  data_column in traffic_data_dictlist :
        #print(data_column['Original_name'],data_column['Destination_name'])
        if(data_column['Original_name' ] == original 
           and data_column['Destination_name'] == destination):
            routes.append(data_column)
        else:
            pass
            #print("pass")
    return routes

def find_possibleroutes(original):
    routes = []
    for data_column in traffic_data_dictlist:
        if(data_column['Original_name'] == original):
            routes.append(data_column)
        else:
            pass
    return routes

def find_spot(name):
    for data_column in spot_data_dictlist:
        if(data_column['Name'] == name):
            return data_column
        else:
            pass
    return None

class State():
    def __init__(self,
                 nowspotname,
                 travelpoint,
                 totaltravelpoint,
                 moneycost,
                 onfoottime,
                 now_datetime,
                 end_datetime,
                 hasbeenspots):
        self.nowspotname = nowspotname
        self.travelpoint = travelpoint#平均的travel分
        self.totaltravelpoint = 0 #一个是的total分
        self.moneycost = moneycost  #已经花费的钱
        self.onfoottime = onfoottime
        self.now_datetime = now_datetime #当前的日期和时间点
        self.end_datetime = end_datetime #结束旅行的时间
        self.hasbeenspots = hasbeenspots #当前状态下已经去过的兴趣点
      
    def takeSecond(self,elem):
        return elem[1]      
    def getGoodroute(self,nowspotname,n):
        
        routes = find_possibleroutes(original = nowspotname) 
        #TODO清除完全不可能走的路线
        goodroutes  = []
        for route in routes:
            #时间太长不考虑
            if(int(route['Costtime'])>75):
                print("[getGoodroute]costtime too long DELETED!")
                continue   
            else:
                goodroutes.append(route)
        return goodroutes
    
    def getPossibleActions(self):
        n=10
        spotname  = self.nowspotname
        print("【getPossibleAction】:nowspot",spotname)
        possible_good_routes = self.getGoodroute(self.nowspotname,n)
        
        possible_actions = []
        #将route和spot结合转化为action
        for item in possible_good_routes:
            #input("for while")
            if(item['Destination_name'] not in self.hasbeenspots):
                destination = find_spot(item['Destination_name'])
                
                #如果地点已经事先确定一定不会去
                if(item['Destination_name'] in WILLNEVERGO):
                    continue
                
                #如果在交通到达后spot已经不开放，排除
                arrivespot_time = self.now_datetime+timedelta(minutes=item['Costtime'])
                arrivespot_time_hour = int(arrivespot_time.hour)
                spot_opnetime=str(destination['PossibleTime'])
                opentime_list = spot_opnetime.split(',', 1 )
                
                if(arrivespot_time_hour>= int(opentime_list[0]) and  arrivespot_time_hour <= int(opentime_list[1])):
                    #print("test!",arrivespot_time.hour,opentime_list)
                    pass
                else:
                    #跳过当前景点
                    continue
               # input()
                
                action = Action(route=item,destination=destination)
                possible_actions.append(action)
                #print(destination['Name'],"  ",item['Original_name'],"-->",item['Destination_name'])
            else:
                pass
                #print(item['Destination_name'],"该地点已经去过",self.hasbeenspots)
        """for action in possible_actions:
            print("getPossileActions debbug:",action.route['Original_name'],"-->",action.route['Destination_name'])
        input()"""
        return possible_actions
    
    #判断当前是否该结束旅程了
    def isTerminal(self):
        #now_datetime=datetime(2021, 2, 1, 13, 30, 0)
        s = (self.end_datetime-self.now_datetime).total_seconds()
        #print("[isTerminal]:",s)
        #input()
        hasbeenspotnum =len(self.hasbeenspots)
        if(hasbeenspotnum>1):
            hasbeenspotnum = hasbeenspotnum-1
        if(s<0 or(abs(s)/60) <= (60*1.5) ):
            #print("isTerminal,s=",s," travelpoint=",self.travelpoint,"self.nowtime",self.now_datetime)
            return True,self.totaltravelpoint/hasbeenspotnum
        #print("[isTerminal]:","False")
        randomseed = random.uniform(98,101)*0.01
        return False,self.totaltravelpoint * randomseed/hasbeenspotnum
    
    def getReward(self):
        #TODO
        #根据当前的用户评价value、综合游览时长、已经花费的钱结合计算reward（奖励计算公式如何获得是需要考虑的）
        isTerminal,reward = self.isTerminal()
        #print("getReward-flag:",flag)
        return reward
    
    def getspotdata(self,name):
        spotdata =find_spot(name)
        return spotdata
    
    def positive_ratio_cal(self,newstate,action):
        ratio=1
        #如果出现了以下几种情况，action的value要上升
        #1.action的地点适合情侣儿童，且用户有明确要求情侣线路，儿童线路等
            #TODO
        if(CHILDFLAG==True and str(action.destination["family"])=="1"):
            ratio=ratio*1.08
            
        attribute = action.destination['Attribute']
        attribute_list = attribute.split('，')

        #2.action的地点属性符合用户需求，如用户喜欢神社，则神社类上升
        if(JINJIAFLAG==True and ("神社" in attribute_list)):
           ratio = ratio*1.06
        #3.action的地点属性符合用户需求，如用户要看夜景，则夜景上升   
        if(NIGHTSCOPFLAG==True and ("夜景" in attribute_list)):
            if(int(newstate.now_datetime.hour) >= 17):
                ratio = ratio*1.08
        #4.距离很近，几乎等同于同一个景点
        if(action.destination['Costtime']<=10):
            ratio=ratio*1.14
        #5.如果spot在倾向去景区的数组中  
        if(action.destination['Name'] in WANTTOGO):
            ratio = ratio*1.05
        
        return ratio
    
    def negative_ratio_cal(self,newstate,action):
        ratio=1
        #如果出现了以下几种情况，action的value要下降
        #1.action结束后，已经是夜晚10点以后
        if(int(newstate.now_datetime.hour)>=22):
            ratio=ratio*0.93
        #2.action结束后，超过了钱预算
        if(int(newstate.moneycost)>=8888):
            ratio=ratio*0.95
        #3.action结束后，步行路程超过了阈值
        if(int(newstate.onfoottime) >= 90):
            ratio=ratio*0.93
            
        #4.action的地点适合儿童，可用户没有要求儿童线路
        if(CHILDFLAG==False and str(action.destination["family"])=="1"):
            ratio=ratio*0.75
            #input("child")
        #5.如果不是在最佳游览时间之间到景点，则value下降
        arrivespot_time = newstate.now_datetime-timedelta(minutes=action.route['Costtime'])
        arrivespot_time_hour = int(arrivespot_time.hour)
        spot_goodperiod=str(action.destination['Goodperiod'])
        goodperiod_list = spot_goodperiod.split(',', 1 )
        if(arrivespot_time_hour >= int(goodperiod_list[0]) and arrivespot_time_hour <= int(goodperiod_list[1])):
            pass
        else:
            ratio = ratio*0.92
        
        return ratio
    #def getActionvalue(self,action,)
    def takeAction(self,action):
        """  
        print("[takeAction]:",TRAFFIC_ORIGINAL_LIST[i],"->",TRAFFIC_DESTINATION_LIST[i],
              " traffictime:",TRAFFIC_COSTTIME_LIST[i]," destinationtime:",spotcosttime)
        
        """
       
        newstate = copy.deepcopy(self)
        
        newstate.nowspotname = action.destination['Name']#spot class
        newstate.moneycost = int(newstate.moneycost)+int(action.route['Costmoney'])+int(action.destination['Costmoney'])  #已经花费的钱
        arrive_datetime = newstate.now_datetime +\
                            timedelta(minutes=action.route['Costtime'])
        newstate.now_datetime = arrive_datetime+\
                            timedelta(minutes=action.destination['Costtime']) #当前的日期和时间点
        print("[TAKEACTION]:出发地点为:",action.route['Original_name'],"->到达地点为:",action.route['Destination_name'],
              " traffictime:",action.route['Costtime']," destinationtime:", action.destination['Name'],action.destination['Costtime'],
              "直到目的地游玩结束时间为:",newstate.now_datetime)
                             
        """#lunch,考虑吃饭。如果不按照正常时间吃饭，则分数下降
        if(newstate.now_datetime.hour>=12 and newstate.now_datetime.hour<=13):
            tempdatetime1 = newstate.now_datetime+timedelta(hours=1,minutes=5)
            newstate.now_datetime = tempdatetime1
        #dinner
        if(newstate.now_datetime.hour>=17 and newstate.now_datetime.hour<=18):
            tempdatetime2 = newstate.now_datetime+timedelta(hours=1,minutes=15)
            newstate.now_datetime = tempdatetime2"""
            
        if(action.route['Traffic_genre'] == 'foot'):
            newstate.onfoottime  = newstate.onfoottime+action.route['Costmoney'] 
        else:
            newstate.onfoottime   = newstate.onfoottime+action.route['Costmoney']*0.12
            
        newstate.hasbeenspots.append(newstate.nowspotname)
        
        
        ratio1 = self.positive_ratio_cal(newstate,action)
        ratio2 = self.negative_ratio_cal(newstate,action)
        
        value=0
        value =(action.route['Point']+action.destination['Point'])*ratio1*ratio2
        #action_value=0      
        newstate.travelpoint = value/2.0
        newstate.totaltravelpoint = newstate.totaltravelpoint + newstate.travelpoint
        
        return newstate
    
class Action():
    def __init__(self,route,destination):
        self.route = route
        self.destination =destination
    def tostr(self):
        return str(self.route)
        
def randomPolicy(state):
    #input("RANDONPOLICY")
    simspotname = state.nowspotname
    print("[RANDOMPOLICY]:开始随机模拟出行,出发地为:",simspotname," nowdatetime",state.now_datetime)
    #zpa = state.getPossibleActions()
    #print("test",pa)
    isTerminal,_ = state.isTerminal()
    #print(isTerminal)
    #simstate = state
    while not isTerminal:
        if(len(state.getPossibleActions())!=0):
            action = random.choice(state.getPossibleActions())
        else:
            print("Non-terminal state has no possible actions: " + str(state))
            s = (state.end_datetime-state.now_datetime).total_seconds()
            if((abs(s)/60) >= (60*4) ):
                randomseed = random.uniform(86,90)*0.01
                state.totaltravelpoint = state.totaltravelpoint * randomseed
            elif((abs(s)/60) >= (60*3) ):   
                randomseed = random.uniform(90,94)*0.01
                state.totaltravelpoint = state.totaltravelpoint * randomseed
            elif((abs(s)/60) >= (60*2) ):   
                randomseed = random.uniform(95,98)*0.01
                state.totaltravelpoint = state.totaltravelpoint * randomseed
            break
        state = state.takeAction(action)
        isTerminal,_ = state.isTerminal()
    #print("simspot randomPolicy finish",simspotname,state.now_datetime,state.hasbeenspots)
    #input()
    print("[RANDOMPOLICY]:随机模拟出行结束, 结束时间为：",state.now_datetime)
    return state.getReward()


class treeNode():
    def __init__(self, state, parent):
        self.state = state
        #self.isTerminal = state.isTerminal()
        self.isTerminal,flag= state.isTerminal() #代表当前的状态是否是终结态
        self.isFullyExpanded = self.isTerminal #节点是否完全扩展
        #self.isFullyExpanded = self.isTerminal
        self.parent = parent
        self.numVisits = 0
        self.totalReward = 0#多次采样后获得的travelpoint总和
        #TODO实际应该用一个参数表示平均旅行体验
        self.children = {}

    def __str__(self):
        s=[]
        s.append("totalReward: %s"%(self.totalReward))
        s.append("numVisits: %d"%(self.numVisits))
        s.append("isTerminal: %s"%(self.isTerminal))
        s.append("possibleActions: %s"%(self.children.keys()))
        return "%s: {%s}"%(self.__class__.__name__, ', '.join(s))

class mcts():
    def __init__(self, timeLimit=None, iterationLimit=None, explorationConstant=1 / math.sqrt(2),
                 rolloutPolicy=randomPolicy):
        if timeLimit != None:
            if iterationLimit != None:
                raise ValueError("Cannot have both a time limit and an iteration limit")
            # time taken for each MCTS search in milliseconds
            self.timeLimit = timeLimit
            self.limitType = 'time'
        else:
            if iterationLimit == None:
                raise ValueError("Must have either a time limit or an iteration limit")
            # number of iterations of the search
            if iterationLimit < 1:
                raise ValueError("Iteration limit must be greater than one")
            self.searchLimit = iterationLimit
            self.limitType = 'iterations'
        self.explorationConstant = explorationConstant
        self.rollout = rolloutPolicy

    def search(self, initialState, needDetails=False):
        #mizukiyuta||mizukimizuki||mizukimizuki||mizukimizuki||mizukimizuki||mizukimizuki||mizukimizuki
        print("创建root结点,初始地点为：",initialState.nowspotname," 出发时间：",initialState.now_datetime," 结束时间：",initialState.end_datetime)
        initialState.hasbeenspots.append(initialState.nowspotname)
        #mizukiyuta||mizukimizuki||mizukimizuki||mizukimizuki||mizukimizuki||mizukimizuki||mizukimizuki
        
        self.root = treeNode(initialState, None)

        if self.limitType == 'time':
            timeLimit = time.time() + self.timeLimit / 1000
            while time.time() < timeLimit:
                self.executeRound()
        else:
            for i in range(self.searchLimit):
                self.executeRound()
        
        
        #self.getBestRoute(self.root)
        #self.getTreeInfo(self.root)
        return self.root
    
        """
        bestChild = self.getBestChild(self.root, 0)
        action=(action for action, node in self.root.children.items() if node is bestChild).__next__()
        if needDetails:
            return {"action": action, "expectedReward": bestChild.totalReward / bestChild.numVisits}
        else:
            return action"""

    def executeRound(self):
        """
            execute a selection-expansion-simulation-backpropagation round
        """
        node = self.selectNode(self.root)
        reward = self.rollout(node.state)
        self.backpropogate(node, reward)

    def selectNode(self, node):
        while not node.isTerminal:
            if node.isFullyExpanded:
                node = self.getBestChild(node, self.explorationConstant)
                #print("selectnode nowspot",node.state.nowspot)
            else:
                return self.expand(node)
        return node
    def actionToflag(self,action):
        flag=""
        #flag = action['Original_name']
        flag = str(action.route['Original_name'])+"|"+str(action.route['Destination_name'])+"|"+str(action.route["Traffic_genre"])
        #print("ACTIONTOFLAG:",flag)
        return flag
    
    def expand(self, node):
        actions = node.state.getPossibleActions()
        """input("[EXPAND]","#"*30)
        print(len(actions),actions)
        input("#"*30)"""
        
        """for action in actions:
            print("expand getPossileActions debbug:",action.route['Original_name'],"-->",action.route['Destination_name'])
        
        """
        #input()
        for action in actions:
            #print("[expand]",action.route['Original_name'],"-->",action.route['Destination_name'])
            #input()
            #print(node.children)
            #input()
            flag=self.actionToflag(action)
            if flag not in node.children:
                newstate = node.state.takeAction(action)
                newNode = treeNode(newstate, node)
                #TODO    
                node.children[flag] = newNode
                if len(actions) == len(node.children):
                    node.isFullyExpanded = True
                return newNode

        #raise Exception("Should never reach here")

    def backpropogate(self, node, reward):
        while node is not None:
            node.numVisits += 1
            node.totalReward += reward
            node = node.parent

    def getBestChild(self, node, explorationValue):
        bestValue = float("-inf")
        bestNodes = []
        for child in node.children.values():
            nodeValue = child.totalReward / child.numVisits + explorationValue * math.sqrt(
                2 * math.log(node.numVisits) / child.numVisits)
            if nodeValue > bestValue:
                bestValue = nodeValue
                bestNodes = [child]
            elif nodeValue == bestValue:
                bestNodes.append(child)
        return random.choice(bestNodes)
    
    def getBestRoute(self,root):
        nownode = root
        #input()
        #bestChild = self.getBestChild(nownode, 0) 
        #print(bestChild)
        result_str="";
        while(len(nownode.children)>0):
            print(len(nownode.children))
            
            bestChild = self.getBestChild(nownode, 0) 
            #action1 = None
            #node1 = None
            for action, node in nownode.children.items():
                if node is bestChild:
                    #action1 = action        
                    print("numvisits:",nownode.numVisits," totalReward:", nownode.totalReward,end="")
                    print(action)
                    value=float(nownode.totalReward)/float(nownode.numVisits)
                    result_str=result_str+str(value)+str(action)+"    "
                    nownode = node
                    #input()
                    break
        return result_str
    def getTreeInfo(self,root):
        print()
        print("$"*30)
        nownode = root
        level=1
        while(len(nownode.children)>0):
            print("【level:",level,"   has childnum:",len(nownode.children),"】")
            bestChild = self.getBestChild(nownode, 0) 
            for action, node in nownode.children.items():
                if node is bestChild:
                    #action1 = action        
                    print("【IS BESTCHILD】numvisits:",node.numVisits," totalReward:", node.totalReward)
                    print(action)
                    temp_nownode = node
                    level = level+1
                    #continue
                else:
                    print("numvisits:",node.numVisits," totalReward:", node.totalReward,action)
            nownode =   temp_nownode 
            input()