import tensorflow as tf
import numpy as np
import cv2
import sys

# Load the trained model
model = tf.keras.models.load_model("digit_model.h5")

# Load and preprocess the image
def preprocess_image(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Couldn't load image: {image_path}")

    # Invert and threshold
    _, img = cv2.threshold(255 - img, 128, 255, cv2.THRESH_BINARY)

    # Find bounding box of digit
    coords = cv2.findNonZero(img)
    x, y, w, h = cv2.boundingRect(coords)
    img = img[y:y+h, x:x+w]

    # Resize to 20x20 and place in center of 28x28 image
    img = cv2.resize(img, (20, 20))
    padded = np.zeros((28, 28), dtype=np.uint8)
    padded[4:24, 4:24] = img

    padded = padded / 255.0
    padded = padded.reshape(1, 28, 28, 1)

    return padded



# Main function
def predict(image_path):
    img = preprocess_image(image_path)
    prediction = model.predict(img)
    predicted_digit = np.argmax(prediction)
    confidence = np.max(prediction)
    
    print(f"Predicted Digit: {predicted_digit} (Confidence: {confidence:.2f})")

# Run it from command line
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python predict_digit.py path/to/image.png")
        sys.exit(1)
    
    image_path = sys.argv[1]
    predict(image_path)
