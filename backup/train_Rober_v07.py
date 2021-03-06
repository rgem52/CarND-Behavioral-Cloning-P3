#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  4 20:58:48 2017

@author: Rober
"""

"""
Created on Tue Apr  4 11:08:35 2017

@author: goodfellow
"""
import numpy as np
import csv
import cv2
import sklearn
from sklearn.model_selection import train_test_split

samples = []
with open('./data/driving_log.csv') as csvfile:
    reader = csv.reader(csvfile)
    next(reader, None)  # skip the headers
    for line in reader:
        samples.append(line)

print('Readed CSV file')
 
print('Splitting DS..')
train_samples, validation_samples = train_test_split(samples, test_size=0.2)

def test_generator(samples, batch_size=32):
    num_samples = len(samples)
    while 1: # Loop forever so the generator never terminates
        sklearn.utils.shuffle(samples)
        for offset in range(0, num_samples, batch_size):
            batch_samples = samples[offset:offset+batch_size]

            images = []
            angles = []
            for batch_sample in batch_samples:
                center_angle = float(batch_sample[3])
                # Only high steering values
                if abs(center_angle)>0.85:
                    source_path = batch_sample[0]
                    filename = source_path.split('/')[-1]
                    current_path = './data/IMG/' + filename
                    center_image = cv2.imread(current_path)
                    images.append(center_image)
                    angles.append(center_angle)
                    images.append(cv2.flip(current_path, 1))
                    angles.append(center_angle * -1.0)

            # trim image to only see section with road
            X_train = np.array(images)
            y_train = np.array(angles)
            print(train_generator[0].shape)
            print(validation_generator[1].shape)
            return (X_train, y_train)

test_generator(samples)        

            
def generator(samples, batch_size=32):
    num_samples = len(samples)
    while 1: # Loop forever so the generator never terminates
        sklearn.utils.shuffle(samples)
        for offset in range(0, num_samples, batch_size):
            batch_samples = samples[offset:offset+batch_size]

            images = []
            angles = []
            for batch_sample in batch_samples:
                center_angle = float(batch_sample[3])
                # Only high steering values
                if abs(center_angle)>0.85:
                    source_path = batch_sample[0]
                    filename = source_path.split('/')[-1]
                    current_path = './data/IMG/' + filename
                    center_image = cv2.imread(current_path)
                    images.append(center_image)
                    angles.append(center_angle)
                    images.append(cv2.flip(current_path, 1))
                    angles.append(center_angle * -1.0)

            # trim image to only see section with road
            X_train = np.array(images)
            y_train = np.array(angles)
            #print(train_generator[0].shape)
            #print(validation_generator[1].shape)
            yield sklearn.utils.shuffle(X_train, y_train)



#Model
import keras
from keras.models import Sequential
from keras.layers import Dense, Flatten, Lambda, Cropping2D
from keras.layers import Conv2D
#from keras import losses

#Init Variables
batch_size = 32
epochs = 10
# input image dimensions
img_rows, img_cols = 160, 320
input_shape = (img_rows, img_cols, 3)
###############################################
# compile and train the model using the generator function
print('Creating Genartors...')
train_generator = generator(train_samples, batch_size=batch_size)
validation_generator = generator(validation_samples, batch_size=batch_size)
#Check shapes

###############################################

model = Sequential()
# Preprocess incoming data, centered around zero with small standard deviation 
model.add(Lambda(lambda x: x/127.5 - 1., input_shape=input_shape))
model.add(Cropping2D(cropping=((50,20), (0,0))))
model.add(Conv2D(24, kernel_size=(5, 5),strides=(2, 2), padding='valid', activation='relu'))
model.add(Conv2D(36, kernel_size=(5, 5),strides=(2, 2), padding='valid', activation='relu'))
model.add(Conv2D(48, kernel_size=(5, 5),strides=(2, 2), padding='valid', activation='relu'))
model.add(Conv2D(64, kernel_size=(3, 3), padding='valid', activation='relu'))
model.add(Conv2D(64, kernel_size=(3, 3), padding='valid', activation='relu'))
#Flatten
model.add(Flatten())
model.add(Dense(100))
model.add(Dense(50))
model.add(Dense(10))
#Output
model.add(Dense(1))

model.summary()


#LOAD PRETRAINED MODEL
pretrained_model = False
if pretrained_model:
    print('Loading Pretrained model')
    model.load_weights('./cp/model-p3-v06.h5')



from keras.callbacks import ModelCheckpoint, EarlyStopping
checkpointer = ModelCheckpoint(filepath="./cp/model-p3-v06.h5", verbose=1, save_best_only=True,
                              monitor='val_loss', save_weights_only=False, mode='auto')

earlystopping = EarlyStopping(monitor='val_loss', min_delta=0, patience=2, verbose=1, mode='auto')


model.compile(loss='mse', 
              optimizer=keras.optimizers.Adam(), 
              metrics=None, 
              sample_weight_mode=None)

history_object = model.fit_generator(
    train_generator,
    samples_per_epoch=len(train_samples),
    nb_epoch=epochs,
    validation_data=validation_generator,
    nb_val_samples=len(validation_samples),
    callbacks=[checkpointer,earlystopping],
    verbose=1)

##############################################################
import matplotlib.pyplot as plt
### print the keys contained in the history object
print(history_object.history.keys())

### plot the training and validation loss for each epoch
plt.plot(history_object.history['loss'])
plt.plot(history_object.history['val_loss'])
plt.title('model mean squared error loss')
plt.ylabel('mean squared error loss')
plt.xlabel('epoch')
plt.legend(['training set', 'validation set'], loc='upper right')
plt.show()








