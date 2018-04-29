import pyrebase

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


def exist(key):
    return key in db.child("states").get().val()


def get_all_db():
    return db.child("states").get().val()


def get_all_key():
    return [key for key in db.child("states").get().val()]


def update_state(key, state):
    if not exist(key):
        return -1
    db.child("states").child(key).update({"state": state})
    return 0


def add_user(key, overide=False, init='greeting'):
    if exist(key) and not overide:
        return -1
    data = {'data': [], 'state': init, 'userId': key}
    db.child("states").child(key).set(data)
    return 0


def remove_user(key):
    if not exist(key):
        return -1
    db.child("states").child(key).remove()
    return 0


def get_state(key):
    if not exist(key):
        return -1
    return db.child("states").get().val()[key]
