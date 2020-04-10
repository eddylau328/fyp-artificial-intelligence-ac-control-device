from enum import Enum
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam


class Feedback(Enum):
    very_hot = 0
    hot = 1
    a_bit_hot = 2
    comfy = 3
    aceptable = 4
    a_bit_cold = 5
    cold = 6
    very_cold = 7


##############################################################
#
#       Input layers              Range              Shape
#   -indoor temperature           17-30              (1,)
#   -indoor humidity              40-100             (1,)
#   -outdoor temperature          10-40              (1,)
#   -outdoor humidity             40-100             (1,)
#   -body temperature             28-35              (1,)
#   -AC temperature setting       17-25              (1,9)  <- need one hot encoding
#   -Fanspeed setting              1-3               (1,3)  <- need one hot encoding
#
##############################################################

parameters = {
    'input_shape':17,
    'output_shape': len(Feedback),
    'model_name': "Supervised Learning"
}


class SupervisedLearning:

    def __init__(self, **kwargs):
        self.input_shape = kwargs['input_shape']
        self.output_shape = kwargs['output_shape']
        self.model_name = kwargs['model_name']
        self.initiate_model()

    def initiate_model(self):
        self.model = Sequential(name=self.model_name)
        self.model.add(Dense(32, input_shape=(self.input_shape,), activation='relu'))
        self.model.add(Dense(64, activation='relu'))
        self.model.add(Dense(128, activation='relu'))
        self.model.add(Dense(self.output_shape, activation='softmax'))
        self.model.compile(loss="categorical_crossentropy", optimizer='adam', metrics=['accuracy'])
        self.model.summary()


if (__name__ == '__main__'):
    model = SupervisedLearning(**parameters)
