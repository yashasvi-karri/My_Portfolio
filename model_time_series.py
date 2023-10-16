import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, LabelEncoder

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense


def train_model(features, labels):
    print("Training Model")

    # Extract features and labels
    features = merged_data[feature_columns].values
    labels = merged_data['class'].values

    # Normalize features
    scaler = MinMaxScaler()
    features = scaler.fit_transform(features)

    # One-hot encode labels
    label_encoder = LabelEncoder()
    labels = label_encoder.fit_transform(labels)
    num_classes = len(label_encoder.classes_)

    # Define the sequence length (number of frames per sequence)
    sequence_length = 50

    # Prepare sequences
    sequences = []
    sequence_labels = []
    for i in range(len(features) - sequence_length + 1):
        sequences.append(features[i:i + sequence_length])
        sequence_labels.append(labels[i + sequence_length - 1])

    # Convert sequences and labels to arrays
    sequences = np.array(sequences)
    sequence_labels = np.array(sequence_labels)

    print("Test Train Split")

    # Train-test split
    X_train, X_val, y_train, y_val = train_test_split(sequences, sequence_labels, test_size=0.2, random_state=42)

    # Define LSTM model
    model = Sequential()
    model.add(LSTM(64, input_shape=(sequence_length, len(feature_columns))))
    model.add(Dense(num_classes, activation='softmax'))

    # Compile model
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])


    print("Fitting Model")

    # Train model
    model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=10, batch_size=32)

    # Evaluate model
    _, accuracy = model.evaluate(X_val, y_val)
    print('Validation Accuracy: %.2f%%' % (accuracy * 100))
    
    model.save('my_ts_model_v2.keras')

if __name__ == "__main__":
    # add_column('archive_time_series/landmarks.csv', 'archive_time_series/angles_220.csv')
    # Load the exercise angles
    angles_data = pd.read_csv('archive_time_series/angles_trial.csv')
    # Load the exercise labels
    labels_data = pd.read_csv('archive_time_series/labels.csv')
    # Merge the angle data with exercise labels
    merged_data = pd.merge(angles_data, labels_data, on='vid_id')

    # print(angles_data.columns[2:])

    feature_columns = list(angles_data.columns[2:])

    features = merged_data[feature_columns].values
    labels = merged_data['class'].values
    # Determine the maximum number of frames
    max_frames = angles_data['frame_order'].max()

    # Set the number of timesteps
    num_timesteps = max_frames

    train_model(features, labels)
