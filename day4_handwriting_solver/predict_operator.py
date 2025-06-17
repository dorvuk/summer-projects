import sys
import cv2
import numpy as np
from tensorflow.keras.models import load_model
import matplotlib.pyplot as plt

# Load model
model = load_model("operator_model.h5")
class_map = ['+', '-', '*', '/']

def preprocess_image(path, debug=False):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Couldn't load image: {path}")

    # auto-invert if bg is light
    if np.mean(img) > 127:
        img = 255 - img

    _, img = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY)
    coords = cv2.findNonZero(img)
    if coords is None:
        raise ValueError("No symbol found")
    x, y, w, h = cv2.boundingRect(coords)

    # pad to keep small symbols from blowing up
    pad = int(max(w, h) * 0.75)
    x0 = max(x - pad, 0)
    y0 = max(y - pad, 0)
    x1 = min(x + w + pad, img.shape[1])
    y1 = min(y + h + pad, img.shape[0])
    img = img[y0:y1, x0:x1]

    # preserve aspect ratio into 20×20
    h0, w0 = img.shape
    if w0 > h0:
        new_w = 20
        new_h = int(h0 * 20 / w0)
    else:
        new_h = 20
        new_w = int(w0 * 20 / h0)

    img_small = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # if original box is very small, scale down by extra 50%
    if max(w0, h0) < 15:
        shrink = 0.5
        new_w = max(1, int(new_w * shrink))
        new_h = max(1, int(new_h * shrink))
        img_small = cv2.resize(img_small, (new_w, new_h), interpolation=cv2.INTER_AREA)
    # ───────────────────────────────────────

    # center on 28×28
    canvas = np.zeros((28, 28), dtype=np.uint8)
    x_start = (28 - new_w) // 2
    y_start = (28 - new_h) // 2
    canvas[y_start:y_start+new_h, x_start:x_start+new_w] = img_small

    if debug:
        plt.imshow(canvas, cmap='gray')
        plt.axis('off')
        plt.title("Final Preprocessed")
        plt.show()

    return canvas.reshape(1, 28, 28, 1) / 255.0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python predict_operator.py <image.png>")
        sys.exit(1)

    img_path = sys.argv[1]
    x = preprocess_image(img_path, debug=True)  # turn off debug=False in production
    pred = model.predict(x)[0]

    idx = np.argmax(pred)
    print(f"Predicted: {class_map[idx]}  (confidence: {pred[idx]:.2f})")
