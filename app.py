from flask import Flask, request, json, Response
import requests

from time import sleep

import cunlp as cu
import tagger
import intense
import pickle

def load(name):
    try:
        with open(name, "rb") as f:
            data = pickle.load(f)
    except Exception as e:
        print(e)
        data = []
    return data

def save(obj,name):
    with open(name, "wb") as f:
        pickle.dump(obj, f, protocol=3)
    return

global MODE
MODE = load('db/mode.data')

global WHERE
WHERE = load('db/where.data')

def where(subject):
    global WHERE
    if subject in WHERE:
        return WHERE[subject]
    return 'ไม่พบข้อมูลสถานที่เรียน'

global LINE_API_KEY
LINE_API_KEY = 'Bearer Uk3PkBEDGXtgM6XffZjQmG78H70voKJMQ2lPCHYprwb7Qr+tPz1jTv29oBSyj1/mYvbuXUN8AoebsWp6Gz8Md3raNA1uxxSPNdnMMk4SkheOL+XE2irb1HwbLdmQm9MyOTJGTNHBaEB/IM1VluJFxAdB04t89/1O/w1cDnyilFU='

app = Flask(__name__)
 
@app.route('/')
def index():
    return 'Hello!'
@app.route('/bot', methods=['POST'])

def bot():
    global MODE
    vacation = 4
    STATE = load('db/state.data')
    print(STATE)

    replyStack = list()
    msg_in_json = request.get_json()
    msg_in_string = json.dumps(msg_in_json)
    replyToken = msg_in_json["events"][0]['replyToken']
    userID =  msg_in_json["events"][0]['source']['userId']
    msgType =  msg_in_json["events"][0]['message']['type']
    
    if msgType != 'text':
       reply(replyToken, ['Only text is allowed.'])
       return 'OK', 200
    
    sent = msg_in_json["events"][0]['message']['text'].lower().strip()

    # STATE HANDLER
    if userID in STATE:
        if STATE[userID][0] == 'where_choose':
            if sent == '3':
                # Change state to 'where_manual'
                STATE = load('db/state.data')
                STATE[userID] = ['where_manual',[]]
                save(STATE, 'db/state.data')
                sleep(vacation)
                reply(replyToken, ['กรุณาบอกชื่อวิชาที่ต้องการทราบสถานที่เรียน'])
            elif sent == '1':
                where_query = where(STATE[userID][1][0])
                STATE = load('db/state.data')
                STATE[userID] = ['greeting',[]]
                save(STATE, 'db/state.data')
                sleep(vacation)
                reply(replyToken, [where_query])
            elif sent == '2':
                where_query = where(STATE[userID][1][1])
                STATE = load('db/state.data')
                STATE[userID] = ['greeting',[]]
                save(STATE, 'db/state.data')
                sleep(vacation)
                reply(replyToken, [where_query])
            else:
                sleep(vacation)
                reply(replyToken, ['กรุณาเลือกตัวเลือก 1-3'])
            return 'OK', 200
        elif STATE[userID][0] == 'where_manual':
            STATE = load('db/state.data')
            STATE[userID] = ['greeting',[]]
            save(STATE, 'db/state.data')
            sleep(vacation)
            reply(replyToken, [where(sent)])
            return 'OK', 200
    
    if userID not in STATE:
        STATE = load('db/state.data')
        STATE[userID] = ['greeting',[]]
        save(STATE, 'db/state.data')

    if sent == '!switch':
        if MODE == 'rule':
            MODE = 'deep'
        elif MODE == 'deep':
            MODE = 'rule'
        save(MODE, 'db/mode.data')
        sleep(vacation)
        reply(replyToken, ['Change to \''+ MODE + '\' mode!'])
        return 'OK', 200

    predict_intense = -1
    tokens = cu.model.tokenize(sent)
    if MODE == 'rule':
        intense_map = {0:'แจ้งสถานที่เรียน', 1:'แจ้งเนื้อหาที่เรียน', 2:'ถามเกี่ยวกับตารางเรียน', 3:'ถามเกี่ยวกับอีเวนต์สำคัญ', 4:'ถามสถิติเช็คชื่อ', 5:'ขอสไลด์เอกสาร', 6:'ติวก่อนสอบ'}
        intense_keyword = [['เรียนที่ไหน','เรียนไหน','ห้องไหน','ห้องอะไร','ห้องที่เท่าไหร่','เรียนหนาย','ห้องหนาย'], ['เรียนอะไร','เรียนไร','เนื้อหาไร','เนื้อหาอะไร','สอนอะไร','สอนไร'],['เรียนป่ะ','เรียนปะ','เรียนไหม','เรียนมั๊ย','เรียนป่าว'],['วันไหน','เมื่อไหร่','เมื่อไร'],['เช็คชื่อ','เข้าเรียน','สถิติ'],['เอกสาร','สไลด์','ชีท','หนังสือ','บทเรียน'],['ทบทวน','ติว','ทวน','คำถาม'] ]

        found = False
        for i in range(7):
            for each_keyword in intense_keyword[i]:
                if each_keyword in sent:
                    replyStack.append('Intense: ' + intense_map[i])
                    predict_intense = i
                    found = True
                    break
            if found:
                break
        if not found:
            replyStack.append('Intense: ไม่พบตามกฎที่ตั้งไว้')
    else:
        predict_intense = intense.classify(tokens)
        replyStack.append('Intense: ' + intense_map[predict_intense])
        
    tags = tagger.tag(tokens)
    frame = {'PERIOD':[], 'CMN':[], 'COURSE':[], 'DATE':[], 'MONTH':[], 'YEAR':[]}
    
    output = ''
    for i in range(len(tokens)):
        if len(tokens[i].strip()) > 0:
            frame[tags[i]].append(tokens[i])
            output += tokens[i] + ': ' + tags[i] + '\n'
    replyStack.append(output[:-1])

    # Flow from greeting
    if predict_intense == 0:
        # แจ้งสถานที่เรียน
        if len(frame['COURSE']) == 1:
            replyStack.append(where(frame['COURSE'][0]))
        elif len(frame['COURSE']) == 2:
            if where(frame['COURSE'][0]) != 'ไม่พบข้อมูลสถานที่เรียน' and where(frame['COURSE'][1]) == 'ไม่พบข้อมูลสถานที่เรียน':
                replyStack.append(where(frame['COURSE'][0]))
            elif where(frame['COURSE'][1]) != 'ไม่พบข้อมูลสถานที่เรียน' and where(frame['COURSE'][0]) == 'ไม่พบข้อมูลสถานที่เรียน':
                replyStack.append(where(frame['COURSE'][1]))
            else:
                # Change state to 'where_choose'
                STATE = load('db/state.data')
                STATE[userID] = ['where_choose', [frame['COURSE'][0],frame['COURSE'][1]]]
                save(STATE, 'db/state.data')
                replyStack.append('วิชาไหนครับ\n1: ' + frame['COURSE'][0] + '\n2: ' + frame['COURSE'][1] +'\n3: ไม่ใช่ทั้งคู่')
        else:
            replyStack.append('ไม่สามารถระบุชื่อวิชาได้ กรุณาทดลองใหม่อีกครั้ง')

    sleep(vacation)
    reply(replyToken, replyStack[:5])
    return 'OK', 200
 
def reply(replyToken, textList):
    LINE_API = 'https://api.line.me/v2/bot/message/reply'
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': LINE_API_KEY
    }
    msgs = []
    for text in textList:
        msgs.append({
            "type":"text",
            "text":text
        })
    data = json.dumps({
        "replyToken":replyToken,
        "messages":msgs
    })
    requests.post(LINE_API, headers=headers, data=data)
    return

if __name__ == '__main__':
    app.run()