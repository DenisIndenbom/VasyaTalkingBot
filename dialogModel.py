import numpy as np
import sentencepiece as sp
print("import tensorflow")
import tensorflow as tf

print("loading rnn")


rnn = tf.compat.v1.keras.layers.LSTM

dataPath = ''

class ModelBySymbols:
    """
        The dialog model by symbols uses 1 rnn layer. RNN units 1024; Embedding dim 256
    """
    def __init__( self, vocabFileName: str, modelFileName: str ):
        self.__embedding_dim = 256
        self.__rnn_units = 1024
        print('loading vocab')
        self.__idx2char = np.load( vocabFileName )
        self.__char2idx = { u: i for i, u in enumerate( self.__idx2char ) }
        print("building model")
        self.__model = self.__buildModel( self.__idx2char.shape[0], 1 )
        self.__model.load_weights( modelFileName )
        self.__model.build( tf.TensorShape( [1, None] ) )
        self.__model.summary()

    def __buildModel(self, vocab_size, batch_size ):
        return tf.keras.Sequential( [
            tf.keras.layers.Embedding( vocab_size, self.__embedding_dim,
                                       batch_input_shape = [batch_size, None] ),
            rnn( self.__rnn_units,
                 return_sequences = True,
                 recurrent_initializer = 'glorot_uniform',
                 stateful = True ),
            tf.keras.layers.Dense( vocab_size )
        ] )

    def generate_text( self, start_string, oneString, temperature ):
        # Максимальное количество генерируемых символов
        num_generate = 150
        input_eval = [self.__char2idx[s] for s in start_string]
        input_eval = tf.expand_dims( input_eval, 0 )

        text_generated = []

        self.__model.reset_states()
        for i in range(num_generate):
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

class ModelBySymbols2:
    """
        The dialog model by symbols uses 2 rnn layers. RNN units 512; Embedding dim 256
    """
    def __init__( self, vocabFileName: str, modelFileName: str ):
        self.__embedding_dim = 256
        self.__rnn_units = 1024
        print('loading vocab')
        self.__idx2char = np.load( vocabFileName )
        self.__char2idx = { u: i for i, u in enumerate( self.__idx2char ) }
        print("building model")
        self.__model = self.__buildModel( self.__idx2char.shape[0], 1 )
        self.__model.load_weights( modelFileName )
        self.__model.build( tf.TensorShape( [1, None] ) )
        self.__model.summary()

    def __buildModel(self, vocab_size, batch_size ):
        return tf.keras.Sequential( [
            tf.keras.layers.Embedding( vocab_size, self.__embedding_dim,
                                       batch_input_shape = [batch_size, None] ),
            rnn( self.__embedding_dim,
                 return_sequences = True,
                 recurrent_initializer = 'glorot_uniform',
                 stateful = True ),

            rnn( self.__embedding_dim,
                 return_sequences=True,
                 recurrent_initializer='glorot_uniform',
                 stateful=True ),
            tf.keras.layers.Dense(vocab_size)
        ] )

    def generate_text( self, start_string, oneString, temperature ):
        # Максимальное количество генерируемых символов
        num_generate = 150
        input_eval = [self.__char2idx[s] for s in start_string]
        input_eval = tf.expand_dims( input_eval, 0 )

        text_generated = []

        self.__model.reset_states()
        for i in range(num_generate):
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

class ModelByWord:
    """
        The dialog model by words uses 1 rnn layers. RNN units 1024; Embedding dim 256
    """
    def __init__( self, vocabFileName: str, modelFileName: str ):
        print("building model")
        self.__embedding_dim = 256
        self.__rnn_units = 1024
        self.bpe = sp.SentencePieceProcessor()
        self.bpe.load(vocabFileName)
        # Размер используемого словаря
        self.vocab_size = self.bpe.get_piece_size()
        self.__model = self.__build_model( self.vocab_size, self.__embedding_dim, self.__rnn_units, batch_size=1 )
        self.__model.load_weights( modelFileName )
        self.__model.build( tf.TensorShape( [1, None] ) )
        self.__model.summary()


    @staticmethod
    def __build_model( vocab_size, embedding_dim, rnn_units, batch_size ):
        return tf.keras.Sequential( [
            tf.keras.layers.Embedding( vocab_size, embedding_dim,
                                       batch_input_shape=[batch_size, None] ),
            rnn( rnn_units,
                 return_sequences=True,
                 recurrent_initializer='glorot_uniform',
                 stateful=False ),
            tf.keras.layers.Dense( vocab_size )
        ] )

    def iterate_bpe(self, toEncode ):
        for line in toEncode.splitlines( keepends=True ):
            hasNewLine = line.endswith('\n')
            for token in self.bpe.encode_as_ids(line):
                yield token

            if hasNewLine:
                yield self.bpe.eos_id()

    def bpe_encode(self, toEncode ):
        return np.fromiter( self.iterate_bpe( toEncode ), dtype=np.float )

    def generate_text( self, start_string, oneString, temperature ):
        # Максимальное количество генерируемых символов
        num_generate = 200
        inputTensor = self.bpe_encode( start_string )
        inputTensor = tf.expand_dims( inputTensor, 0 )

        generated = []

        self.__model.reset_states()
        for i in range( num_generate ):
            predictions = self.__model( inputTensor )
            predictions = tf.squeeze( predictions, 0 )

            if temperature > 0:
                predictions = predictions / temperature
            predicted_id = tf.random.categorical( predictions[-1:], num_samples=1 ).numpy()[0, 0]

            if predicted_id == self.bpe.eos_id():
                break

            inputTensor = tf.expand_dims( [predicted_id], 0 )
            generated.append( int( predicted_id ) )

        return self.bpe.decode_ids( generated )
