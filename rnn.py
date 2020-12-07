from __future__ import absolute_import, division, print_function, unicode_literals

import tensorflow as tf

# tf.enable_eager_execution()

import numpy as np
import os
import time

import functools

text = open( '/DataSet.txt', 'rb' ).read().decode( encoding='utf-8' )
print( 'Общее количество символов: {}'.format( len( text ) ) )

# Составляем словарь символов
vocab = sorted( set( text ) )
print( 'Уникальных символов: {}'.format( len( vocab ) ) )

# Функции для преобразования текста в массив чисел и обратно
char2idx = { u: i for i, u in enumerate( vocab ) }
idx2char = np.array( vocab )
text_as_int = np.array( [char2idx[c] for c in text] )
# Подгатавливаем обучающий датасет
seq_length = 100
examples_per_epoch = len( text ) // seq_length
char_dataset = tf.data.Dataset.from_tensor_slices( text_as_int )

sequences = char_dataset.batch( seq_length + 1, drop_remainder=True )


def split_input_target( chunk ):
    input_text = chunk[:-1]
    target_text = chunk[1:]
    return input_text, target_text


dataset = sequences.map( split_input_target )
for input_example, target_example in dataset.take( 1 ):
    print( 'Вход:  ', repr( ''.join( idx2char[input_example.numpy()] ) ) )
    print( 'Выход:', repr( ''.join( idx2char[target_example.numpy()] ) ) )
BATCH_SIZE = 64
steps_per_epoch = examples_per_epoch // BATCH_SIZE

# SHUFFLE_BUFFER_SIZE = 1392231
SHUFFLE_BUFFER_SIZE = 4375

dataset = dataset.shuffle( SHUFFLE_BUFFER_SIZE ).batch( BATCH_SIZE, drop_remainder=True )

# Размер используемого словаря
vocab_size = len( vocab )
# Размерности сети
embedding_dim = 256
rnn_units = 1024

# Здесь можно попробовать различные варианты архитектуры сети. На текущий момент лучший вариант у LSTM.

rnn = functools.partial( tf.keras.layers.LSTM, recurrent_activation='sigmoid' )


# rnn = tf.compat.v1.keras.layers.CuDNNLSTM


# rnn = tf.keras.layers.CuDNNGRU

# Для ускорения работы на GPU можно использовать rnn = tf.keras.layers.CuDNNGRU, но такая сеть не может быть потом
# использована для работы на CPU.

def build_model( vocab_size, embedding_dim, rnn_units, batch_size ):
    return tf.keras.Sequential( [
        tf.keras.layers.Embedding( vocab_size, embedding_dim,
                                   batch_input_shape=[batch_size, None] ),
        rnn( rnn_units,
             return_sequences=True,
             recurrent_initializer='glorot_uniform',
             stateful=True ),
        tf.keras.layers.Dense( vocab_size )
    ] )


model = build_model(
    vocab_size=len( vocab ),
    embedding_dim=embedding_dim,
    rnn_units=rnn_units,
    batch_size=BATCH_SIZE )

model.summary()


def loss( labels, logits ):
    return tf.keras.losses.sparse_categorical_crossentropy( labels, logits, from_logits=True )


checkpoint_dir = '/content/drive/My Drive/Colab Notebooks/training_checkpoints'
np.save( os.path.join( checkpoint_dir, 'idx2char.npy' ), idx2char )
checkpoint_prefix = os.path.join( checkpoint_dir, "ckpt_{epoch}" )

checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
    filepath=checkpoint_prefix,
    save_weights_only=True )
model.compile(
    optimizer=tf.optimizers.Adam(),
    loss=loss )
history = model.fit( dataset.repeat(), epochs=35, steps_per_epoch=steps_per_epoch, callbacks=[checkpoint_callback] )

tf.train.latest_checkpoint( checkpoint_dir )
model = build_model( vocab_size, embedding_dim, rnn_units, batch_size=1 )
model.load_weights( tf.train.latest_checkpoint( checkpoint_dir ) )

model.build( tf.TensorShape( [1, None] ) )
model.summary()


def generate_text( model, start_string, oneString, temperature ):
    # Максимальное количество генерируемых символов
    num_generate = 200
    input_eval = [char2idx[s] for s in start_string]
    input_eval = tf.expand_dims( input_eval, 0 )

    text_generated = []

    model.reset_states()
    for i in range( num_generate ):
        predictions = model( input_eval )
        predictions = tf.squeeze( predictions, 0 )

        if temperature > 0:
            predictions = predictions / temperature
        predicted_id = tf.compat.v1.multinomial( predictions, num_samples=1 )[-1, 0].numpy()

        input_eval = tf.expand_dims( [predicted_id], 0 )

        c = idx2char[predicted_id]
        text_generated.append( c )
        if c == '\n' and oneString:
            break

    return (start_string + ''.join( text_generated ))


print(generate_text(model, "< Как дела?\n>", True, 1))
print(generate_text(model, "< Как дела?\n>", True, 0.9))
print(generate_text(model, "< Как дела?\n>", True, 0.8))
print(generate_text(model, "< Как дела?\n>", True, 0.6))
print(generate_text(model, "< Как дела?\n>", True, 0.7))
print(generate_text(model, "< Как дела?\n>", True, 0.5))
print(generate_text(model, "< Как дела?\n>", True, 0.4))
print(generate_text(model, "< Как дела?\n>", True, 0.3))
print(generate_text(model, "< Как дела?\n>", True, 0.2))
print(generate_text(model, "< Как дела?\n>", True, 0.1))
print(generate_text(model, "< Как дела?\n>", True, 0.01))


dialog = u"===\n"
while (True):
    rq = input( "< " )
    if rq == '':
        break;
    dialog += f"< {rq}\n> "

    fullAns = generate_text( model, start_string=dialog, temperature=0.1, oneString=True )
    shortAns = fullAns[len( dialog ):]
    print( "< " + shortAns )
    dialog = fullAns
