from flask import Flask, request
from flask_cors import CORS
import numpy as np
import cv2
import base64
import math

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['POST'])
def count_pai():
    # リクエストボディから画像データを取得
    data_url = request.json['image']
    encoded_data = data_url.split(",")[1]

    # # Base64デコード
    decoded_data = base64.b64decode(encoded_data)

    # # バイナリデータから画像を読み込む
    origin_image = cv2.imdecode(np.frombuffer(decoded_data, dtype=np.uint8), cv2.IMREAD_COLOR)

    # 画像をグレースケールに変換
    origin_gray = cv2.cvtColor(origin_image, cv2.COLOR_BGR2GRAY)

    # 画像を2値化
    _, thresh = cv2.threshold(origin_gray, 100, 255, cv2.THRESH_BINARY)

    # 最初に見つかった白いピクセルのy座標を取得(上から下に向かって探索)
    y_index = np.where(thresh == 255)[0]
    y_position = y_index[0]
    # 最初に見つかった白いピクセルのy座標を取得(下から上に向かって探索)
    y_index_reverse = np.where(thresh == 255)[0][::-1]
    y_position_reverse = y_index_reverse[0]
    # 背景画像をトリミングして除去
    cropped_image = origin_image[y_position:y_position_reverse]

    # トリミングした画像の高さと幅を取得
    height, width = cropped_image.shape[:2]
    # トリミング比率の計算
    upper_ratio = 0.83
    left_ratio = 0.45
    right_ratio = 0.05
    trim_width = int(width * left_ratio)
    trim_height = int(height * upper_ratio)
    trim_width_right = width - int(width * right_ratio)
    
    # 麻雀の牌以外の部分をトリミングして除去
    roi = cropped_image[trim_height:, trim_width:trim_width_right]
    # 画像をグレースケールに変換
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    # 画像を2値化
    _, threshed_pai = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)

    # 画像をぼかす
    kernel = np.ones((5,5),np.uint8)
    dilation = cv2.dilate(threshed_pai, kernel, iterations = 10)

    # 輪郭を検出
    contours, _ = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 画像の幅を取得
    image_width = dilation.shape[1]
    # 鳴いた牌が存在するか判定するための距離を取得
    right_ratio = 0.03
    distance_from_right = int(image_width * right_ratio)

    # 鳴いた牌の輪郭を見つける
    target_contour = None
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if x + w >= image_width - distance_from_right:
            target_contour = contour
            break
    # 鳴いた牌が見つかった場合の処理
    if target_contour is not None:
        x, y, width, height = cv2.boundingRect(target_contour)
        call1_width = math.floor(image_width / 2.47)
        call2_width = math.floor(image_width / 1.57)
        call3_width = math.floor(image_width / 1.15)

        # 横幅に基づいて処理を分岐
        if width < call1_width:
            result = 1
        elif call1_width <= width < call2_width:
            result = 2
        elif call2_width <= width < call3_width:
            result = 3
        else:
            result = 4
    else:
        result = 0

    # 牌の数を返す
    return {"count": result}

if __name__ == "__main__":
    app.run(port="8090", debug=True)
