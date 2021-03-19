#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 10 12:51:45 2021

@author: liuyi
"""
# 导入Flask类
from flask import Flask
from flask import render_template
from flask import request
# 实例化，可视为固定格式
app = Flask(__name__)

# route()方法用于设定路由；类似spring路由配置
#等价于在方法后写：app.add_url_rule('/', 'helloworld', hello_world)
@app.route('/')
def root_html():
    # 使用render_template()方法重定向到templates文件夹下查找get.html文件
    return render_template('index.html')


# 配置路由，当请求get.html时交由get_html()处理
@app.route('/get.html')
def get_html():
    # 使用render_template()方法重定向到templates文件夹下查找get.html文件
    return render_template('get.html')

# 配置路由，当请求post.html时交由post_html()处理
@app.route('/post.html')
def post_html():
    # 使用render_template()方法重定向到templates文件夹下查找post.html文件
    return render_template('post.html')

# 配置路由，当请求deal_request时交由deal_request()处理
# 默认处理get请求，我们通过methods参数指明也处理post请求
# 当然还可以直接指定methods = ['POST']只处理post请求, 这样下面就不需要if了
@app.route('/deal_request', methods = ['GET', 'POST'])
def deal_request():
    if request.method == "GET":
        # get通过request.args.get("param_name","")形式获取参数值
        #get_q = request.args.get("q","")
        #print("start ai")
        
        import sys
        sys.path.append("../AI/")
        import MCTS
        mcts_manager = MCTS.mcts(timeLimit=10000)#开启mcts程序
        print("初始化中...")
        #from datetime import date
        from datetime import datetime
        #from datetime import timedelta

        start_datetime = datetime(2021, 2, 1, 9, 30, 0)
        end_datetime = datetime(2021,2,1,20,30,0)
        initialstate=MCTS.State(nowspotname="横滨港未来21",
                        travelpoint=0,
                        totaltravelpoint=0,
                        moneycost=0,
                        onfoottime=0,
                        now_datetime=start_datetime,
                        end_datetime=end_datetime,
                        hasbeenspots=[])
        print("初始化sucess")

        root = mcts_manager.search(initialState=initialstate)
        result = mcts_manager.getBestRoute(root)
        
        return str(result)
    
    elif request.method == "POST":
        # post通过request.form["param_name"]形式获取参数值
        post_q = request.form["q"]
        return render_template("result.html", result=post_q)
    
@app.route('/get_username', methods = ['GET', 'POST'])
def get_username():
    if request.method == "GET":
        # get通过request.args.get("param_name","")形式获取参数值
        get_q = request.args.get("username","")
        return render_template("result.html", result=get_q)
    elif request.method == "POST":
        # post通过request.form["param_name"]形式获取参数值
        post_q = request.form["username"]
        return render_template("result.html", result=post_q)
    

    
    
@app.route('/mcts_ai_request', methods = ['GET', 'POST'])
def start_mcts_ai():
    if request.method == 'GET':
        trip_period = request.args.get("trip_period","")
        trip_like = request.args.get("trip_like","")
        trip_customer = request.args.get("trip_customer","")
        

        return render_template("cal.html")
    elif request.method == "POST":
        pass
    else:
        print("wrong")
        
        
if __name__ == '__main__':
    # app.run(host, port, debug, options)
    # 默认值：host=127.0.0.1, port=5000, debug=false
    app.run()
    
    
    
    
    