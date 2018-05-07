# command line
# line
import json
import random
import pyrebase
import random

required_form = json.load(open('config/require_form.json'))

answer_require_information = json.load(
    open('config/answer_require_information.json'))
answer_question = json.load(
    open('config/answer_question.json'))

config = {
    "apiKey": "AIzaSyDTSs-TCJ7obcJUtiQfeaMqOnBqLJJU3RU",
    "authDomain": "nlp-line-chatbot.firebaseapp.com",
    "databaseURL": "https://nlp-line-chatbot.firebaseio.com",
    "projectId": "nlp-line-chatbot",
    "storageBucket": "nlp-line-chatbot.appspot.com",
    "messagingSenderId": "601884581282"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()


def query_event(frame):
    # frame = {'date':'1', 'month':'1', 'year':'2018'}
    queried = db.child('query').child('event').get().val()
    if 'date' in frame and 'month' in frame and 'year' in frame:
        q = frame['date'] + '-' + frame['month'] + '-' + frame['year']
        if q in queried:
            return queried[q]
        else:
            return 'ไม่มีกิจกรรมพิเศษในวันดังกล่าว'
    elif 'date' in frame and 'month' in frame:
        q = frame['date'] + '-' + frame['month'] + '-2018'
        if q in queried:
            return queried[q]
        else:
            return 'ไม่มีกิจกรรมพิเศษในวันดังกล่าว'
    return 'ข้อมูลไม่เพียงพอ'


def query_slide(frame):
    # frame = {'course':'nlp', 'date':'1', 'month':'1', 'year':'2018'}
    if 'course' not in frame:
        return 'ข้อมูลไม่เพียงพอ'

    queried = db.child('query').child(
        'sheet').child(frame['course']).get().val()
    if queried is None:
        return 'ข้ออภัยไม่พบข้อมูลการเรียนการสอนของวิชา ' + frame['course'] + ' ในฐานข้อมูล'

    if 'date' in frame and 'month' in frame and 'year' in frame:
        q = frame['date'] + '-' + frame['month'] + '-' + frame['year']
        if q in queried:
            return queried[q]
        else:
            return 'ไม่พบสไลด์การเรียนการสอนของวิชา ' + frame['course'] + ' ในวันดังกล่าว'
    elif 'date' in frame and 'month' in frame:
        q = frame['date'] + '-' + frame['month'] + '-2018'
        if q in queried:
            return queried[q]
        else:
            return 'ไม่พบสไลด์การเรียนการสอนของวิชา ' + frame['course'] + ' ในวันดังกล่าว'
    return queried['9-4-2018'] + ' ในคาบล่าสุด'


def query_description(frame):
    # frame = {'course':'nlp', 'date':'1', 'month':'1', 'year':'2018'}
    if 'course' not in frame:
        return 'ข้อมูลไม่เพียงพอ'

    queried = db.child('query').child(
        'topic').child(frame['course']).get().val()
    if queried is None:
        return 'ข้ออภัยไม่พบข้อมูลการเรียนการสอนของวิชา ' + frame['course'] + ' ในฐานข้อมูล'

    if 'date' in frame and 'month' in frame and 'year' in frame:
        q = frame['date'] + '-' + frame['month'] + '-' + frame['year']
        if q in queried:
            return queried[q]
        else:
            return 'ไม่พบข้อมูลเนื้อหาของวิชา ' + frame['course'] + ' ที่สอนในวันดังกล่าว'
    elif 'date' in frame and 'month' in frame:
        q = frame['date'] + '-' + frame['month'] + '-2018'
        if q in queried:
            return queried[q]
        else:
            return 'ไม่พบข้อมูลเนื้อหาของวิชา ' + frame['course'] + ' ที่สอนในวันดังกล่าว'
    return queried['9-4-2018'] + ' ในคาบล่าสุด'


def query_time(frame):
    # frame = {'course':'nlp'}
    if 'course' not in frame:
        return 'ข้อมูลไม่เพียงพอ'
    queried = db.child('query').child('when').get().val()
    q = frame['course']
    if q in queried:
        return queried[q]
    return 'ไม่พบข้อมูลช่วงเวลาการเรียนการสอนวิชา ' + q + ' ในฐานข้อมูล'


def query_place(frame):
    # frame = {'course':'nlp'}
    if 'course' not in frame:
        return 'ข้อมูลไม่เพียงพอ'
    queried = db.child('query').child('where').get().val()
    q = frame['course']
    if q in queried:
        return queried[q]
    return 'ไม่พบข้อมูลสถานที่ของการเรียนการสอนวิชา ' + q + ' ในฐานข้อมูล'


def query_tutor(frame):
    # frame = {'course':'nlp'}
    if 'course' not in frame:
        return 'ข้อมูลไม่เพียงพอ'
    queried = db.child('query').child('tutor').get().val()
    q = frame['course']
    if q in queried:
        question = queried[q]
        lucky = random.choice([key for key in question])
        return 'คำถาม: ' + lucky + '\nคำตอบ: ' + question[lucky]
    return 'ขออภัยไม่รองรับการติวในวิชา ' + q + ' ในขณะนี้'


def query_stats(frame):
    # frame = {'course':'nlp'}
    if 'course' not in frame:
        return 'ข้อมูลไม่เพียงพอ'
    queried = db.child('query').child('attend').get().val()
    q = frame['course']
    if q in queried:
        return 'วิชา ' + q + ' มีการเรียนการสอนไปแล้วทั้งหมด ' + str(queried[q]) + ' ครั้ง'
    return 'ขออภัยไม่พบสถิติการเรียนการสอนของวิชา ' + q + ' ในฐานข้อมูล'


def require_information(machine, output_method, intention, information):
    for i in required_form[intention]:
        if information[i] == '':
            output_method(random.choice(
                answer_require_information[i]), machine.token)
            return


def answer_and_reset(machine, output_method,  intention, information):
    machine.restart()
    output_method(eval("query_" + intention + "(information)"), machine.token)
