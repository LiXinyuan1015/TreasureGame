import pymongo
from pymongo import MongoClient
from flask import Flask, render_template, request
from flask_apscheduler import APScheduler
from bson.objectid import ObjectId
import random
import sys

client = MongoClient('localhost', 27017)
players = client.game.players
markets = client.game.markets
treasures = client.game.treasures
username = 'test' #设置username全局变量
table = {"T":"工具", "A":"配饰"} #添加装备种类代号到中文名称的映射表

app = Flask(__name__)

@app.route("/", methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    global username #通过获取前端数据更改全局变量username
    username = request.args.get("name")
    password = request.args.get("password")
    players.create_index([("name", pymongo.ASCENDING)], unique=True)
    if players.find_one({"name": username}) is None:
        players.insert_one({"name": username, "money": 10, "password": password,
                              "treasure": {"T": "扫帚", "A": "攻击护符"},
                              "box": [], "score": 0})
        return render_template('signup.html', name=username, tag=0)
    else:
        if players.find_one({"name": username})['password'] != password:
            return "<h1>玩家 %s 密码错误请重新输入</h1>" % username
    return render_template('homepage.html', re=username)

@app.route('/homepage')
def homepage():
    return render_template('homepage.html',re=username)

@app.route('/myinfo')
def myinfo():
    money = players.find_one({"name": username})['money']
    row = players.find_one({"name": username})['treasure']
    row1 = row['T']
    row2 = row['A']
    row3 = players.find_one({"name": username})['box']
    return render_template('myinfo.html',name=username,money=money,row1=row1,row2=row2,row3=row3)


@app.route('/equip_info')
def equip_info():
    name = request.args.get('name')
    id_ = treasures.find_one({"name": name})['_id']
    type_ = treasures.find_one({"name": name})['property']
    type_ = table[type_]
    level = treasures.find_one({"name": name})['level']
    value = treasures.find_one({"name": name})['value']
    return render_template('equipinfo.html', name=name,id=id_,type=type_,level=level,value=value)

@app.route('/take_off')
def take_off():
    treasure = request.args.get('equipments')
    type_ = treasures.find_one({"name": treasure})['property']
    original = players.find_one({"name": username})["treasure"][type_]
    box = players.find_one({'name': username})['box']
    if(len(box) < 10):
        tag = 0
    else:
        tag = 1
        recovery(username)
    box = players.find_one({'name': username})['box']
    box.append(original)
    row = players.find_one({"name": username})['treasure']
    row[type_] = '无'
    players.update_one({'name': username}, {"$set": {"treasure": row}})
    players.update_one({'name': username}, {"$set": {"box": box}})
    return render_template('take_off.html' ,tag=tag)

@app.route('/sto_info')
def sto_info():
    name = request.args.get('name')
    id_ = treasures.find_one({"name": name})['_id']
    type_ = treasures.find_one({"name": name})['property']
    type_ = table[type_]
    level = treasures.find_one({"name": name})['level']
    value = treasures.find_one({"name": name})['value']
    return render_template('stoinfo.html', name=name,id=id_,type=type_,level=level,value=value)

@app.route('/take_on')
def take_on():
    treasure = request.args.get('equipments')
    type_ = treasures.find_one({"name": treasure})['property']
    box = players.find_one({'name': username})['box']
    row = players.find_one({"name": username})['treasure']
    if(row[type_] == '无'):
        tag = 0
        for t in box:
            if t == treasure:
                box.remove(t)
                row[type_] = treasure
                players.update_one({"name": username}, {"$set": {"box": box}})
                players.update_one({"name": username}, {"$set": {"treasure": row}})
                break
    else:
        tag = 1
    return render_template('take_on.html', tag=tag)

@app.route('/look_for_treasure')
def look_for_treasure():
    box = players.find_one({'name': username})['box']
    if(len(box) < 10):
        tag = 0
    else:
        tag = 1
        recovery(username)
    # 得到的宝物和饰品的级别与价值有关,宝物的级别与饰品的级别一致，可通过融合装备升级
    box = players.find_one({'name': username})['box']
    row = players.find_one({"name": username})['treasure']
    if row['A'] != '无':
        wear_treasure_name = row['A']
        wear_treasure_level = treasures.find_one({"name": wear_treasure_name})['level']
        wear_treasure_value = treasures.find_one({"name": wear_treasure_name})['value']
        ls = []
        for col in treasures.find({"value": {"$lte": wear_treasure_value + 5, "$gte": wear_treasure_value - 5}, "level": {"$lte": wear_treasure_level + 1, "$gte": wear_treasure_level - 1}}):
            ls.append(col)
        x = random.randint(0, len(ls) - 1) #随机寻宝
        equip_name = ls[x]['name']
        box.append(equip_name)
        players.update_one({"name": username}, {"$set": {"box": box}})
        return render_template('look_for_treasure.html',equip_name=equip_name,tag=tag)
    else:
        return "<h1>没有装备配饰无法进行寻宝</h1>"

@app.route('/look_for_money')
def look_for_money():
    row = players.find_one({"name": username})['treasure']
    current_money = players.find_one({"name": username})['money']
    if row['T'] != '无':
        wear_treasure_name = row['T']
        wear_treasure_level = treasures.find_one({"name": wear_treasure_name})['level']
        wear_treasure_value = treasures.find_one({"name": wear_treasure_name})['value']
        money = random.randint(wear_treasure_value, wear_treasure_level * 5 + wear_treasure_value)
        current_money += money
        players.update_one({"name": username}, {"$set": {"money": current_money}})
        return render_template('look_for_money.html',money=money)
    else:
        return "<h1>没有装备工具无法进行赚钱</h1>"

@app.route('/merge')
def merge():
    return render_template('merge.html')

@app.route('/merge_result')
def merge_result():
    treasure = request.args.get("treasure1")
    treasure2 = request.args.get("treasure2")
    player = players.find_one({"name": username})
    box = player['box']
    tag = 0
    if player['money'] < 100:
        tag = 2
        return render_template('merge_result.html', tag=tag,ts=0)
    if treasure not in box:
        return render_template('merge_result.html', tag=tag,ts=0)
    if treasure2 not in box:
        return render_template('merge_result.html', tag=tag,ts=0)
    if treasure == treasure2:
        num = 0
        for t in box:
            if t == treasure:
                num += 1
        if num < 2:
            return render_template('merge_result.html', tag=tag,ts=0)
    tag = 1
    for t in box:
        if t == treasure:
            box.remove(t)
            break
    for t in box:
        if t == treasure2:
            box.remove(t)
            break
    ls = []
    level1 = treasures.find_one({"name": treasure})['level']
    level2 = treasures.find_one({"name": treasure2})['level']
    for col in treasures.find({"level": min(max(level1, level2) + 1, 6)}):
            ls.append(col)
    x = random.randint(0, len(ls) - 1)
    new_treasure_name = ls[x]['name']
    box.append(ls[x]['name'])
    players.update_one({"name": username}, {"$set": {"box": box}})
    money1 = player['money'] - 100
    players.update_one({"name": username}, {"$set": {"money": money1}})
    return render_template('merge_result.html', tag=tag,ts=new_treasure_name)

@app.route('/marinfo')
def marinfo():
    re=[]
    for treasure in markets.find():
        name = treasure['treasure']['name']
        type_ = treasure['treasure']['property']
        type_ = table[type_]
        level = treasure['treasure']['level']
        value = treasure['treasure']['value']
        price = treasure['price']
        owner = treasure['owner']
        id_ = treasure['_id']
        re.append([name, type_, level, value, price, owner, id_])
    return render_template('marinfo.html', re=re)

@app.route('/buy')
def buy():
    tag = 0
    id_ = request.args.get("id")
    id_ = ObjectId(id_)
    box = players.find_one({"name": username})['box']
    if(len(box) > 10):
        tag = 1
        recovery(username)
    box = players.find_one({"name": username})['box']
    treasure = markets.find_one({'_id': id_})['treasure']['name']
    price = markets.find_one({'_id': id_})['price']
    price = int(price)
    money1 = players.find_one({"name": username})['money'] - price
    if money1 < 0:
        return "<h1>玩家金币不足，购买失败</h1>"
    box.append(treasure)
    players.update_one({"name": username}, {"$set": {"box": box}})
    players.update_one({"name": username}, {"$set": {"money": money1}})
    owner = markets.find_one({'_id': id_})['owner']
    money2 = players.find_one({"name": owner})['money'] + price
    players.update_one({"name": owner}, {"$set": {"money": money2}})
    markets.delete_one({"_id": id_})
    return render_template('buy.html', tag=tag)

@app.route('/sell')
def sell():
    return render_template('sell.html')

@app.route('/sell_it')
def sell_it():
    treasure = request.args.get("treasure")
    price = request.args.get("price")
    box = players.find_one({'name': username})['box']
    if treasure not in box:
        return render_template('sellinfo.html',tag=0)
    player = players.find_one({"name": username})
    box = player['box']
    for t in box:
        if t == treasure:
            box.remove(t)
            break
    players.update_one({"name": username}, {"$set": {"box": box}})
    type_ = treasures.find_one({"name": treasure})['property']
    level = treasures.find_one({"name": treasure})['level']
    value = treasures.find_one({"name": treasure})['value']
    markets.insert_one({"treasure": {"name": treasure, "property": type_, "level": level, "value": value}, "price": price, "owner": username})
    return render_template('sellinfo.html',tag=1)

@app.route('/rank')
def rank():
    money = players.find_one({"name": username})['money']
    row = players.find_one({"name": username})['treasure']
    value1 = treasures.find_one({"name": row['T']})['value']
    value2 = treasures.find_one({"name": row['A']})['value']
    score = 0.3 * money + (value1 + value2) * 0.3
    players.update_one({"name": username}, {"$set": {"score": score}})
    rank = 1
    rank_list=[]
    for player in players.find():
        name = player['name']
        player_score = player['score']
        temp=[name, player_score]
        rank_list.append(temp)

    for i in range(0, len(rank_list)):
        if score < rank_list[i][1]:
            rank += 1
    return render_template('rank.html',score=score, rank=rank)


#回收等级最低宝物
def recovery(name):
    box = players.find_one({"name": name})['box']
    i = '无'
    while i in box:
        box.remove(i)
    players.update_one({'name': name}, {"$set": {"box": box}})
    treasure_name = box[0]
    value = treasures.find_one({"name": box[0]})['value']
    for treasure in box[1:]:
        temp = treasures.find_one({"name": treasure})['value']
        if temp < value:
            value = temp
            treasure_name = treasure
    #删除该宝物
    for treasure in box:
        if treasure == treasure_name:
            box.remove(treasure)
            break
    players.update_many({'name': name}, {"$set": {"box": box}})
    print("玩家 %s 被系统回收宝物 %-6s" % (name, treasure_name))

# 配置自动任务的类
class config(object):
    JOBS = [
        {
            'id': 'job1',
            'func': '__main__:look_for_treasure',
            'trigger': 'interval',
            'seconds': 600,

        },
        {
            'id': 'job2',
            'func': '__main__:look_for_money',
            'trigger': 'interval',
            'seconds': 600,

        }
    ]

if __name__ == "__main__":
    app.config.from_object(config())
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()
    app.run()
