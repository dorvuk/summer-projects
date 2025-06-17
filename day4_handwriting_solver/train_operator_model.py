import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dense, Flatten, Dropout
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from sklearn.model_selection import train_test_split

# Mapping labels
label_map = {
    'plus': 0,
    'minus': 1,
    'times': 2,
    'divide': 3
}

data = []
labels = []

# Load dataset
for label_name, label_index in label_map.items():
    folder = f"operator_dataset/{label_name}"
    for filename in os.listdir(folder):
        if filename.endswith('.png'):
            img_path = os.path.join(folder, filename)
            img = load_img(img_path, color_mode='grayscale', target_size=(28, 28))
            img = img_to_array(img) / 255.0
            data.append(img)
            labels.append(label_index)

data = np.array(data)
labels = to_categorical(labels, num_classes=4)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    data, labels, test_size=0.2, random_state=42, stratify=labels
)

# Define CNN model
model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(28, 28, 1)),
    MaxPooling2D(2, 2),
    Dropout(0.2),
    
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D(2, 2),
    Dropout(0.2),

    Flatten(),
    Dense(64, activation='relu'),
    Dropout(0.3),
    Dense(4, activation='softmax')
])

model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

# Train model
model.fit(X_train, y_train, epochs=10, batch_size=32, validation_split=0.1)

# Evaluate
loss, acc = model.evaluate(X_test, y_test)
print(f"\nFinal test accuracy: {acc:.4f}")

# Save
model.save("operator_model.h5")
print("Saved model to operator_model.h5")
