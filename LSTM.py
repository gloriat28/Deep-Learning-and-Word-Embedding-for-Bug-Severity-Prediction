import gensim
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, f1_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from keras.models import Sequential
from keras.layers import Dense, LSTM, Flatten
from keras.optimizers import Adam
import matplotlib.pyplot as plt


def prepareData():
    # read datasets
    Mozilla = pd.read_csv("DataSets/Mozilla_total.csv")
    Eclipse = pd.read_csv("DataSets/Eclipse_total.csv")
    BothDataSets = pd.read_csv("DataSets/Both_DataSets.csv")

    # creating numpy arrays for labels
    MozillaLabel = Mozilla['severity'].values
    EclipseLabel = Eclipse['severity'].values
    BothLabel = BothDataSets['severity'].values

    # read the doc2vec models
    MozillaDoc2VecModel = gensim.models.doc2vec.Doc2Vec.load('Doc2VecModels/MozillaDoc2Vec.model')
    EclipseDoc2VecModel = gensim.models.doc2vec.Doc2Vec.load('Doc2VecModels/EclipseDoc2Vec.model')
    BothDoc2VecModel = gensim.models.doc2vec.Doc2Vec.load('Doc2VecModels/BothDoc2Vec.model')

    MozillaVectors = np.zeros((len(MozillaLabel), 500))
    EclipseVectors = np.zeros((len(EclipseLabel), 500))
    BothVectors = np.zeros((len(BothLabel), 500))

    # get documents vectors from the doc2vec model
    for i in range(len(MozillaLabel)):
        MozillaVectors[i] = MozillaDoc2VecModel.docvecs[MozillaLabel[i]+str(i)]

    for i in range(len(EclipseLabel)):
        EclipseVectors[i] = EclipseDoc2VecModel.docvecs[EclipseLabel[i]+str(i)]

    for i in range(len(BothLabel)):
        BothVectors[i] = BothDoc2VecModel.docvecs[BothLabel[i]+str(i)]

    MozillaLabelEncoded = encodingClass(MozillaLabel)
    EclipseLabelEncoded = encodingClass(EclipseLabel)
    BothLabelEncoded = encodingClass(BothLabel)

    # split datasets
    MozillaVectorsTrain, MozillaVectorsTest, MozillaLabelTrain, MozillaLabelTest = train_test_split(MozillaVectors, MozillaLabelEncoded, test_size=0.3, stratify=MozillaLabelEncoded)
    EclipseVectorsTrain, EclipseVectorsTest, EclipseLabelTrain, EclipseLabelTest = train_test_split(EclipseVectors, EclipseLabelEncoded, test_size=0.3, stratify=EclipseLabelEncoded)

    MozillaVectorsTrain = MozillaVectorsTrain.reshape(MozillaVectorsTrain.shape + (1,))
    MozillaVectorsTest = MozillaVectorsTest.reshape(MozillaVectorsTest.shape + (1,))
    EclipseVectorsTrain = EclipseVectorsTrain.reshape(EclipseVectorsTrain.shape + (1,))
    EclipseVectorsTest = EclipseVectorsTest.reshape(EclipseVectorsTest.shape + (1,))
    BothVectors = BothVectors.reshape(BothVectors.shape + (1,))

    print(BothVectors[0])

    return MozillaVectorsTrain, MozillaVectorsTest, MozillaLabelTrain, MozillaLabelTest, EclipseVectorsTrain, EclipseVectorsTest, EclipseLabelTrain, \
           EclipseLabelTest, BothVectors, BothLabelEncoded, MozillaDoc2VecModel, EclipseDoc2VecModel, BothDoc2VecModel


# apply label encoder on labels
def encodingClass(targetModel):
    labelEncoder = LabelEncoder()
    # LabelEncoder to encode class into categorical integer values
    labelEncoder.fit(targetModel)
    encodedTarget = labelEncoder.transform(targetModel)
    print("Label classes: " + labelEncoder.classes_)
    return encodedTarget


# create LSTM model
def LSTMmodel(doc2vecmodel):
    model = Sequential()
    model.add(LSTM(64, input_shape=(500, 1), dropout=0.4, recurrent_dropout=0.4, return_sequences=True))
    model.add(LSTM(32, dropout=0.5, recurrent_dropout=0.5, return_sequences=True))
    model.add(Flatten())
    model.add(Dense(5, activation='softmax'))

    # Define the optimizer and compile the model
    # optimizer = optimizers.SGD(lr=0.03, clipnorm=5.)
    model.compile(optimizer=Adam(lr=0.001), loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    print("model defined")
    print(model.summary())
    return model


# apply LSTM model on mozilla dataset
def applyLSTMonMozilla(MozillaVectorsTrain, MozillaVectorsTest, MozillaLabelTrain, MozillaLabelTest, MozillaDoc2VecModel):
    print('Applying LSTM classifier on Mozilla Dataset')
    MozillaLSTMModel = LSTMmodel(MozillaDoc2VecModel)
    MozillaLSTMModel.fit(MozillaVectorsTrain, MozillaLabelTrain, batch_size=100, epochs=20)

    predictions = MozillaLSTMModel.predict_classes(MozillaVectorsTest)
    print('Accuracy: {}'.format(accuracy_score(MozillaLabelTest, predictions)))
    print('F1 score: {}'.format(f1_score(MozillaLabelTest, predictions, average='weighted')))
    print('Confusion Matrix: {}'.format(confusion_matrix(MozillaLabelTest, predictions)))
    print(classification_report(MozillaLabelTest, predictions))
    plot_confusion_matrix(confusion_matrix(MozillaLabelTest, predictions), 'Mozilla')
    plot_classification_report(classification_report(MozillaLabelTest, predictions), 'Mozilla')
    MozillaLSTMModel.save('ClassifiersModels/LSTM_mozilla_model_keras.h5')


# apply LSTM model on eclipse dataset
def applyLSTMonEclipse(EclipseVectorsTrain, EclipseVectorsTest, EclipseLabelTrain, EclipseLabelTest, EclipseDoc2VecModel):
    print('Applying LSTM classifier on Eclipse Dataset')
    EclipseLSTMModel = LSTMmodel(EclipseDoc2VecModel)
    EclipseLSTMModel.fit(EclipseVectorsTrain, EclipseLabelTrain, batch_size=100, epochs=20)

    predictions = EclipseLSTMModel.predict_classes(EclipseVectorsTest)
    print('Accuracy: {}'.format(accuracy_score(EclipseLabelTest, predictions)))
    print('F1 score: {}'.format(f1_score(EclipseLabelTest, predictions, average='weighted')))
    print('Confusion Matrix: {}'.format(confusion_matrix(EclipseLabelTest, predictions)))
    print(classification_report(EclipseLabelTest, predictions))
    plot_confusion_matrix(confusion_matrix(EclipseLabelTest, predictions), 'Eclipse')
    plot_classification_report(classification_report(EclipseLabelTest, predictions), 'Eclipse')
    EclipseLSTMModel.save('ClassifiersModels/LSTM_eclipse_model_keras.h5')


# apply LSTM model on both datasets
def applyLSTMonBoth(BothVectors, BothLabelEncoded, BothDoc2VecModel):
    BothLSTMModel = LSTMmodel(BothDoc2VecModel)
    BothLSTMModel.fit(BothVectors, BothLabelEncoded, batch_size=100, epochs=20)

    BothLSTMModel.save('ClassifiersModels/LSTM_both_model_keras.h5')


def plot_classification_report(classificationReport, dataset, cmap='RdBu'):
    lines = classificationReport.split('\n')
    classes = ['Blocker', 'Critical', 'Major', 'Minor', 'Trivial']
    plotMat = []
    for line in lines[2:7]:
        t = line.strip().split()
        # classes.append(t[0])
        v = [float(x) for x in t[1: len(t) - 1]]
        plotMat.append(v)

    plt.imshow(plotMat, interpolation='nearest', cmap=cmap)
    plt.title('Classification Report of '+dataset+' Dataset With LSTM')
    plt.colorbar()
    x_tick_marks = np.arange(3)
    y_tick_marks = np.arange(len(classes))
    plt.xticks(x_tick_marks, ['precision', 'recall', 'f1-score'], rotation=45)
    plt.yticks(y_tick_marks, classes)
    plt.tight_layout()
    plt.ylabel('Classes')
    plt.xlabel('Measures')
    plt.show()


def plot_confusion_matrix(cm, dataset):
    labels = ['Blocker', 'Critical', 'Major', 'Minor', 'Trivial']
    fig, ax = plt.subplots()
    h = ax.matshow(cm)
    fig.colorbar(h)
    ax.set_xticklabels([''] + labels)
    ax.set_yticklabels([''] + labels)
    ax.set_xlabel('Confusion Matrix of '+dataset+' Dataset With LSTM')
    ax.set_ylabel('Severity classes')
    plt.show()


if __name__ == '__main__':
    MozillaVectorsTrain, MozillaVectorsTest, MozillaLabelTrain, MozillaLabelTest, EclipseVectorsTrain, EclipseVectorsTest, \
    EclipseLabelTrain, EclipseLabelTest, BothVectors, BothLabelEncoded, MozillaDoc2VecModel, EclipseDoc2VecModel, BothDoc2VecModel = prepareData()
    applyLSTMonMozilla(MozillaVectorsTrain, MozillaVectorsTest, MozillaLabelTrain, MozillaLabelTest, MozillaDoc2VecModel)
    applyLSTMonEclipse(EclipseVectorsTrain, EclipseVectorsTest, EclipseLabelTrain, EclipseLabelTest, EclipseDoc2VecModel)
    applyLSTMonBoth(BothVectors, BothLabelEncoded, BothDoc2VecModel)

