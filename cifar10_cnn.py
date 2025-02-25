# Original from https://github.com/fchollet/keras/tree/2.0.0/examples

from __future__ import print_function
import os
import shutil
import argparse

import keras
from keras.datasets import cifar10
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Conv2D, MaxPooling2D


def use_valohai_input():
    """
    Place input file defined through Valohai to cache where cifar10.load_data() expects it to be.
    This allows skipping download phase if the input file is already on the instance.
    """

    CIFAR10BATCHFOLDERNAME = 'cifar-10-batches-py'

    datadir_base = os.path.expanduser(os.path.join('~', '.keras'))
    datadir = os.path.join(datadir_base, 'datasets')
    print('datadir:',datadir)
    if not os.path.exists(datadir):
        print('datadir doesnt exist')
        os.makedirs(datadir)
        print('datadir created')
    else:
        print('datadir exist')

    inputs_dir = os.getenv('VH_INPUTS_DIR', '/')
    input_dir = os.path.join(inputs_dir, CIFAR10BATCHFOLDERNAME)
    input_files = os.listdir(input_dir)

    untar_fpath = datadir
    fpath = os.path.join(untar_fpath, input_files[1])
    #fpath = untar_fpath + '.tar.gz'
    print('Original input_file:',input_files)
    input_file = os.path.join(input_dir, input_files[1])  # We expect to have only one file as input
    print('New input_file:',input_file)
    print('untar_fpath:',untar_fpath)
    print('fpath:',fpath)

    if (os.path.isfile(input_file)):
        print('input_path file exists')
    if os.path.exists(untar_fpath):
        print('untar_fpath directory exists')

    shutil.move(input_file, fpath)
    print('shutil.move done')


def use_valohai_input_batch():
    """
    Place input file defined through Valohai to cache where cifar10.load_data() expects it to be.
    This allows skipping download phase if the input file is already on the instance.
    """

    CIFAR10BATCHFOLDERNAME = 'cifar-10-batches-py'

    datadir_base = os.path.expanduser(os.path.join('~', '.keras'))
    datadir = os.path.join(datadir_base, 'datasets')
    print('datadir:',datadir)
    if not os.path.exists(datadir):
        os.makedirs(datadir)

    inputs_dir = os.getenv('VH_INPUTS_DIR', '/')
    input_dir = os.path.join(inputs_dir, CIFAR10BATCHFOLDERNAME)
    input_files = os.listdir(input_dir)
    untar_fpath = datadir

    print('input_dir',input_dir)
    print('untar_fpath',untar_fpath)

    for files in input_files:
        fullpath = os.path.join(input_dir, files)
        print('this_fullpath',fullpath)
        shutil.copy2(fullpath,untar_fpath) #shutil.move(fullpath,untar_fpath)
        print('file copied')
    print('batch copy done')
    print(os.listdir(untar_fpath))



def train(params):
    batch_size = params.batch_size
    num_classes = params.num_classes
    epochs = params.epochs
    data_augmentation = params.data_augmentation

    img_rows, img_cols = 32, 32  # input image dimensions
    img_channels = 3  # The CIFAR10 images are RGB.

    # The data, shuffled and split between train and test sets:
    (x_train, y_train), (x_test, y_test) = cifar10.load_data()
    print('x_train shape:', x_train.shape)
    print(x_train.shape[0], 'train samples')
    print(x_test.shape[0], 'test samples')

    # Convert class vectors to binary class matrices.
    y_train = keras.utils.to_categorical(y_train, num_classes)
    y_test = keras.utils.to_categorical(y_test, num_classes)

    model = Sequential()

    model.add(Conv2D(32, (3, 3), padding='same', input_shape=x_train.shape[1:]))
    model.add(Activation('relu'))
    model.add(Conv2D(32, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Conv2D(64, (3, 3), padding='same'))
    model.add(Activation('relu'))
    model.add(Conv2D(64, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Flatten())
    model.add(Dense(512))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Dense(num_classes))
    model.add(Activation('softmax'))

    # Let's train the model using RMSprop
    model.compile(loss='categorical_crossentropy',
                  optimizer='rmsprop',
                  metrics=['accuracy'])

    x_train = x_train.astype('float32')
    x_test = x_test.astype('float32')
    x_train /= 255
    x_test /= 255

    if not data_augmentation:
        print('Not using data augmentation.')
        model.fit(x_train, y_train,
                  batch_size=batch_size,
                  epochs=epochs,
                  validation_data=(x_test, y_test),
                  shuffle=True,
                  verbose=2)
    else:
        print('Using real-time data augmentation.')

        # This will do preprocessing and real-time data augmentation:
        datagen = ImageDataGenerator(
            featurewise_center=False,  # set input mean to 0 over the dataset
            samplewise_center=False,  # set each sample mean to 0
            featurewise_std_normalization=False,  # divide inputs by std of the dataset
            samplewise_std_normalization=False,  # divide each input by its std
            zca_whitening=False,  # apply ZCA whitening
            rotation_range=0,  # randomly rotate images in the range (degrees, 0 to 180)
            width_shift_range=0.1,  # randomly shift images horizontally (fraction of total width)
            height_shift_range=0.1,  # randomly shift images vertically (fraction of total height)
            horizontal_flip=True,  # randomly flip images
            vertical_flip=False)  # randomly flip images

        # Compute quantities required for featurewise normalization
        # (std, mean, and principal components if ZCA whitening is applied).
        datagen.fit(x_train)

        # Fit the model on the batches generated by datagen.flow().
        model.fit_generator(datagen.flow(x_train, y_train, batch_size=batch_size),
                            steps_per_epoch=x_train.shape[0],
                            epochs=epochs,
                            validation_data=(x_test, y_test),
                            verbose=2)

    outputs_dir = os.getenv('VH_OUTPUTS_DIR', './')
    output_file = os.path.join(outputs_dir, 'my_model.h5')
    print('Saving model to %s' % output_file)
    model.save(output_file)


if __name__ == '__main__':
    use_valohai_input_batch()

    parser = argparse.ArgumentParser()
    parser.add_argument('--batch_size', type=int)
    parser.add_argument('--num_classes', type=int)
    parser.add_argument('--epochs', type=int)
    parser.add_argument('--data_augmentation', type=bool, nargs='?', const=True)
    cli_parameters, unparsed = parser.parse_known_args()
    train(cli_parameters)
