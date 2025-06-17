import sys
import cv2
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt

# Config
DIGIT_MODEL_PATH     = "digit_model.h5"
OP_MODEL_PATH        = "operator_model.h5"
OPERATORS            = ['+', '—', '•', '/']
MIN_BOX_AREA         = 200            # drop tiny noise
MORPH_KERNEL         = (7, 7)         # for merging “+” strokes during segmentation
SHRINK_FACTOR        = 0.5            # how much to shrink tiny/dot symbols
OPERATOR_THRESHOLD   = 1.5            # operator must be this × more confident than digit
MIN_OPERATOR_CONF    = 0.6            # operator must be at least this confident

# Load models
digit_model    = tf.keras.models.load_model(DIGIT_MODEL_PATH)
operator_model = tf.keras.models.load_model(OP_MODEL_PATH)

# Segment
def segment_symbols(img_path):
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Cannot load {img_path}")
    # ensure black-on-white
    if img.mean() > 127:
        img = 255 - img
    _, bin_img = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY)

    # close only for segmentation (merges the “+”)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, MORPH_KERNEL)
    seg = cv2.morphologyEx(bin_img, cv2.MORPH_CLOSE, kernel)

    cnts, _ = cv2.findContours(seg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes = []
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        if w * h < MIN_BOX_AREA:
            continue
        boxes.append((x, y, w, h))
    boxes.sort(key=lambda b: b[0])

    # crop from the raw binary so dots stay tiny
    return [bin_img[y:y+h, x:x+w] for x, y, w, h in boxes]

# Preprocess
def preprocess_symbol(crop, debug=False):
    img = crop.copy()
    if img.mean() > 127:
        img = 255 - img
    _, img = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY)

    coords = cv2.findNonZero(img)
    if coords is None:
        raise ValueError("No symbol found")
    x, y, w, h = cv2.boundingRect(coords)
    raw_w, raw_h = w, h

    # pad around the symbol
    pad = int(max(w, h) * 0.75)
    x0 = max(x - pad, 0)
    y0 = max(y - pad, 0)
    x1 = min(x + w + pad, img.shape[1])
    y1 = min(y + h + pad, img.shape[0])
    img = img[y0:y1, x0:x1]

    # resize to fit in a 20×20 box
    h0, w0 = img.shape
    if w0 > h0:
        new_w = 20
        new_h = max(1, int(h0 * 20 / w0))
    else:
        new_h = 20
        new_w = max(1, int(w0 * 20 / h0))
    img_small = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # shrink very small or dot‐shaped symbols
    if max(raw_w, raw_h) < 15 or abs(raw_w - raw_h) < 4:
        new_w = max(1, int(new_w * SHRINK_FACTOR))
        new_h = max(1, int(new_h * SHRINK_FACTOR))
        img_small = cv2.resize(img_small, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # center on 28×28 canvas
    canvas = np.zeros((28, 28), dtype=np.uint8)
    x_off = (28 - new_w) // 2
    y_off = (28 - new_h) // 2
    canvas[y_off:y_off+new_h, x_off:x_off+new_w] = img_small

    if debug:
        plt.imshow(canvas, cmap='gray')
        plt.axis('off')
        plt.title(f"Preprocessed (raw {raw_w}×{raw_h})")
        plt.show()

    return canvas, (raw_w, raw_h)

# Predict
def predict_symbol(crop, debug=False):
    canvas, (raw_w, raw_h) = preprocess_symbol(crop, debug)
    inp = canvas.reshape(1, 28, 28, 1) / 255.0

    d_conf_arr = digit_model.predict(inp, verbose=0)[0]
    o_conf_arr = operator_model.predict(inp, verbose=0)[0]
    d_idx, d_conf = d_conf_arr.argmax(), d_conf_arr.max()
    o_idx, o_conf = o_conf_arr.argmax(), o_conf_arr.max()

    d_pred = str(d_idx)
    o_pred = OPERATORS[o_idx]

    # dot override to force multiplication dot
    if max(raw_w, raw_h) < 15 and abs(raw_w - raw_h) < 4:
        return d_pred, d_conf, '•', o_conf

    return d_pred, d_conf, o_pred, o_conf

# Merge
def merge_digits(symbols):
    merged = []
    buf = ""
    for s in symbols:
        if s.isdigit():
            buf += s
        else:
            if buf:
                merged.append(buf)
                buf = ""
            merged.append(s)
    if buf:
        merged.append(buf)
    return merged

# Solve
def solve_expression(tokens):
    expr = "".join(t.replace('•', '*').replace('—', '-') for t in tokens)
    try:
        return expr, eval(expr)
    except Exception:
        return expr, "ERROR"

# Main
def main(img_path, debug=False):
    crops = segment_symbols(img_path)
    preds = []

    for i, crop in enumerate(crops):
        d_pred, d_conf, o_pred, o_conf = predict_symbol(crop, debug)

        # require operator to be significantly more confident AND above min confidence
        if o_conf > d_conf * OPERATOR_THRESHOLD and o_conf > MIN_OPERATOR_CONF:
            pick = o_pred
        else:
            pick = d_pred

        if debug:
            print(f"Sym#{i}: digit={d_pred}@{d_conf:.2f}, op={o_pred}@{o_conf:.2f} → pick={pick}")

        preds.append(pick)

    tokens = merge_digits(preds)
    expr, result = solve_expression(tokens)

    print("Tokens:    ", tokens)
    print("Expression:", expr)
    print("Result:    ", result)

if __name__ == "__main__":
    debug = "--debug" in sys.argv
    if debug:
        sys.argv.remove("--debug")
    if len(sys.argv) != 2:
        print("Usage: python expression_solver.py [--debug] path/to/image.png")
    else:
        main(sys.argv[1], debug)
