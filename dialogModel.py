import functools
import tensorflow as tf
import numpy as np

embedding_dim = 256
rnn_units = 1024
rnn = functools.partial( tf.keras.layers.LSTM, recurrent_activation = 'sigmoid' )


class Model:
    def __init__( self, vocabFileName: str, modelFileName: str ):
        self.__idx2char = np.load( vocabFileName )
        self.__char2idx = { u: i for i, u in enumerate( self.__idx2char ) }
        self.__model = self.__buildModel( self.__idx2char.shape[0], 1 )
        self.__model.load_weights( modelFileName )
        self.__model.build( tf.TensorShape( [1, None] ) )
        self.__model.summary()

    @staticmethod
    def __buildModel( vocab_size, batch_size ):
        return tf.keras.Sequential( [
            tf.keras.layers.Embedding( vocab_size, embedding_dim,
                                       batch_input_shape = [batch_size, None] ),
            rnn( rnn_units,
                 return_sequences = True,
                 recurrent_initializer = 'glorot_uniform',
                 stateful = True ),
            tf.keras.layers.Dense( vocab_size )
        ] )

    def generate_text( self, start_string, oneString, temperature ):
        # Максимальное количество генерируемых символов
        num_generate = 200
        input_eval = [self.__char2idx[s] for s in start_string]
        input_eval = tf.expand_dims( input_eval, 0 )

        text_generated = []

        self.__model.reset_states()
        for i in range( num_generate ):
            predictions = self.__model( input_eval )
            predictions = tf.squeeze( predictions, 0 )

            if temperature > 0:
                predictions = predictions / temperature
            predicted_id = tf.compat.v1.multinomial( predictions, num_samples = 1 )[-1, 0].numpy()

            input_eval = tf.expand_dims( [predicted_id], 0 )

            c = self.__idx2char[predicted_id]
            text_generated.append( c )
            if c == '\n' and oneString:
                break

        return  ''.join( text_generated )


if __name__ == '__main__':
    model = Model( 'idx2char.npy', 'ckpt_30' )
    while True:
        print( model.generate_text( f'>{input()}\n<', True, 0.8) )
