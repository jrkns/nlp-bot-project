import warnings
warnings.filterwarnings("ignore")

from keras.models import Sequential
from keras.models import Model
from keras.layers import Input, Dense, GRU, Embedding, Bidirectional, TimeDistributed, Dropout
from keras.optimizers import Adam
from keras.preprocessing.sequence import pad_sequences
import numpy as np
import os
import pickle
import cunlp as cu


def _load(path):
    with open(path, 'rb') as f:
        return pickle.load(f)


def _get_intent_model():
    input1 = Input(shape=(400,))
    x = Embedding(379, 150)(input1)
    x = Dropout(0.5)(x)
    x = Bidirectional(GRU(64))(x)
    x = Dense(256, activation='relu')(x)
    x = Dropout(0.25)(x)
    out = Dense(7, activation='softmax')(x)

    model = Model(inputs=input1, outputs=out)
    model.compile(optimizer=Adam(lr=0.01, decay=0.001),
                  loss='categorical_crossentropy',
                  metrics=['acc'])
    return model

# POS Tagger Model


def _get_pos_model():
    model_pos = Sequential()
    model_pos.add(Embedding(552, 50, input_length=20, mask_zero=True))
    model_pos.add(Bidirectional(GRU(50, return_sequences=True)))
    model_pos.add(Dropout(0.2))
    model_pos.add(TimeDistributed(Dense(7, activation='softmax')))
    model_pos.compile(optimizer=Adam(),  loss='categorical_crossentropy', metrics=[
                      'categorical_accuracy'])
    return model_pos


global _word_list_intent
global _word_to_idx_intent
_word_list_intent, _word_to_idx_intent = _load(os.path.dirname(
    os.path.abspath(__file__)) + '/dump/word_to_idx_intent.pkl')

global _word_to_idx
global _idx_to_pos
_word_to_idx = _load(os.path.dirname(
    os.path.abspath(__file__)) + '/dump/word_to_idx_ner.pkl')
_idx_to_pos = {1: 'period', 2: 'cmn',
               3: 'course', 4: 'date', 5: 'month', 6: 'year'}

global _intent_map
_intent_map = {0: 'place', 1: 'description', 2: 'time',
               3: 'event', 4: 'stats', 6: 'slide', 5: 'tutor'}

global _intent_model
_intent_model = _get_intent_model()
_intent_model.load_weights(os.path.dirname(
    os.path.abspath(__file__)) + '/dump/model_intent.h5')

global _pos_model
_pos_model = _get_pos_model()
_pos_model.load_weights(os.path.dirname(
    os.path.abspath(__file__)) + '/dump/model_ner.h5')


def _pos_word_to_idx(word_list):
    feed = []
    for word in word_list:
        if word in _word_to_idx:
            feed.append(_word_to_idx[word])
        else:
            feed.append(_word_to_idx['UNK'])
    while len(feed) < 20:
        feed.append(0)
    return np.array([feed[:20]])


def _pos_idx_to_pos(classes, length):
    pos = []
    for c in classes[:length]:
        if c in _idx_to_pos:
            pos.append(_idx_to_pos[c])
        else:
            pos.append('UNK')
    return pos


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False


def _word_map(w):
    if w in _word_list_intent:
        if is_number(w):
            return 1
        return _word_to_idx_intent[w]
    else:
        if w == "<\s>":
            return _word_to_idx_intent['</s>']
        if is_number(w):
            return 1
        return 0


def tag(tokens):
    if len(tokens) == 0:
        return []
    results = []
    for i in range(0, len(tokens), 20):
        batch = tokens[i:i + 20]
        ready_to_feed = _pos_word_to_idx(batch)
        results.extend(_pos_idx_to_pos(
            _pos_model.predict_classes(ready_to_feed)[0], len(batch)))
    return results


def classify(tokens):
    if len(tokens) == 0:
        return []
    to_index = [_word_map(i) for i in tokens + ['</s>']]
    ready_to_feed = pad_sequences([np.array(to_index)], maxlen=400)
    pred_prob = _intent_model.predict(ready_to_feed)
    pred_cls = np.argmax(pred_prob, 1)
    return pred_cls[0]


def compute(raw_text):
    tokens = cu.model.tokenize(raw_text)
    intent = _intent_map[classify(tokens)]
    frame = {'period': '', 'cmn': '', 'course': '',
             'date': '', 'month': '', 'year': ''}
    tags = tag(tokens)
    for i in range(len(tokens)):
        if len(tokens[i].strip()) > 0:
            frame[tags[i]] += tokens[i]
    return {'intent': intent, 'frame': frame}
