from flask import Flask, request, json
import requests
from state_machine import StateMachine
from state_machine import filebase
from ai import compute

def push(text, userID):
    textList = [text]
    LINE_API = 'https://api.line.me/v2/bot/message/push'
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
        "to": userID,
        "messages":msgs
    })
    requests.post(LINE_API, headers=headers, data=data)
    return

global LINE_API_KEY
LINE_API_KEY = 'Bearer SECRET'

app = Flask(__name__)
 
@app.route('/')
def index():
    return 'Hello!'
@app.route('/bot', methods=['POST'])

def bot():
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

    if sent == 'reset':
        filebase.remove_user(userID)
        reply(replyToken, ['ลบข้อมูล State Machine บน firebase แล้ว'])
        return 'OK', 200

    if sent in ['สวัสดี','สวัสดีจ้า','สวัสดีครับ','สวัสดีค่ะ','สวัสดีค้าบ','hello','hi','ทัก']:
        reply(replyToken, ['สวัสดีจ้า :)'])
        return 'OK', 200

    state = StateMachine(push, token=userID)

    all_data = compute(sent)
    this_intention = all_data['intent']
    this_information = all_data['frame']

    state.get_input(this_intention, this_information)

    print("Intent:", this_intention)
    print("IR:", this_information)
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