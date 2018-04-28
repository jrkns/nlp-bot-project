import warnings
warnings.filterwarnings("ignore")

from keras.models import Sequential
from keras.layers import Dense, GRU, Embedding, Bidirectional, TimeDistributed, Dropout
from keras.optimizers import Adam
import numpy as np
import os, pickle

# Private Zone
_CHARS = [
  '\n', ' ', '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+',
  ',', '-', '.', '/', '0', '1', '2', '3', '4', '5', '6', '7', '8',
  '9', ':', ';', '<', '=', '>', '?', '@', 'A', 'B', 'C', 'D', 'E',
  'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
  'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '[', '\\', ']', '^', '_',
  'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
  'n', 'o', 'other', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y',
  'z', '}', '~', 'ก', 'ข', 'ฃ', 'ค', 'ฅ', 'ฆ', 'ง', 'จ', 'ฉ', 'ช',
  'ซ', 'ฌ', 'ญ', 'ฎ', 'ฏ', 'ฐ', 'ฑ', 'ฒ', 'ณ', 'ด', 'ต', 'ถ', 'ท',
  'ธ', 'น', 'บ', 'ป', 'ผ', 'ฝ', 'พ', 'ฟ', 'ภ', 'ม', 'ย', 'ร', 'ฤ',
  'ล', 'ว', 'ศ', 'ษ', 'ส', 'ห', 'ฬ', 'อ', 'ฮ', 'ฯ', 'ะ', 'ั', 'า',
  'ำ', 'ิ', 'ี', 'ึ', 'ื', 'ุ', 'ู', 'ฺ', 'เ', 'แ', 'โ', 'ใ', 'ไ',
  'ๅ', 'ๆ', '็', '่', '้', '๊', '๋', '์', 'ํ', '๐', '๑', '๒', '๓',
  '๔', '๕', '๖', '๗', '๘', '๙', '‘', '’', '\ufeff'
]
_CHARS_MAP = {v: k for k, v in enumerate(_CHARS)}

def _load(path):
    with open(path, 'rb') as f:
        return pickle.load(f)

# POS Tagger Model
def _get_pos_model():
    model_pos = Sequential()
    model_pos.add(Embedding(552, 50, input_length=20, mask_zero=True))
    model_pos.add(Bidirectional(GRU(50, return_sequences=True)))
    model_pos.add(Dropout(0.2))
    model_pos.add(TimeDistributed(Dense(7, activation='softmax')))
    model_pos.compile(optimizer=Adam(),  loss='categorical_crossentropy', metrics=['categorical_accuracy'])
    return model_pos

global _word_to_idx
global _idx_to_pos
_word_to_idx = _load(os.path.dirname(os.path.abspath(__file__)) + '/word_to_idx.pkl')
_idx_to_pos = _load(os.path.dirname(os.path.abspath(__file__)) + '/idx_to_label.pkl')

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

global _pos_model
_pos_model = _get_pos_model()
_pos_model.load_weights(os.path.dirname(os.path.abspath(__file__)) + '/no_crf.h5')

# Public Zone
def tag(tokens):
    if len(tokens) == 0:
        return []
    results = []
    for i in range(0, len(tokens), 20):
        batch = tokens[i:i+20]
        ready_to_feed = _pos_word_to_idx(batch)
        results.extend(_pos_idx_to_pos(_pos_model.predict_classes(ready_to_feed)[0], len(batch)))
    return results