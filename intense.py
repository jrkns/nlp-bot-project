import warnings
warnings.filterwarnings("ignore")

from keras.layers import Input, Dense, Embedding, GRU, TimeDistributed, Bidirectional, Dropout
from keras.models import Model
from keras.optimizers import Adam
from keras.preprocessing.sequence import pad_sequences
import pickle, os
import numpy as np

def _load(path):
    with open(path, 'rb') as f:
        return pickle.load(f)

# POS Tagger Model
def _get_intense_model():
    input1 = Input(shape=(400,))
    x = Embedding(378, 150)(input1)
    x = Dropout(0.5)(x)
    x = Bidirectional(GRU(64))(x)
    x = Dense(256, activation='relu')(x)
    x = Dropout(0.25)(x)
    out = Dense(7, activation='softmax')(x)

    model = Model(inputs=input1, outputs=out)
    model.compile(optimizer=Adam(lr=0.01,decay=0.001),
                loss='categorical_crossentropy',
                metrics=['acc'])
    return model

global _word_to_idx
_word_to_idx = _load(os.path.dirname(os.path.abspath(__file__)) + '/word_to_idx_intense.pkl')

global _intense_model
_intense_model = _get_intense_model()
_intense_model.load_weights(os.path.dirname(os.path.abspath(__file__)) + '/intense_w.h5')

def _word_map(word):
    if word in _word_to_idx:
        return _word_to_idx[word]
    return _word_to_idx['UNK']

# Public Zone
def classify(tokens):
    if len(tokens) == 0:
        return []
    to_index = [_word_map(i) for i in tokens]
    ready_to_feed = pad_sequences([np.array(to_index)], maxlen=400)
    pred_prob = _intense_model.predict(ready_to_feed)
    pred_cls = np.argmax(pred_prob, 1)
    return pred_cls[0]