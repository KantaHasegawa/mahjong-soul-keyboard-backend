from flask import Flask, request
import numpy as np
import cv2
import base64

app = Flask(__name__)

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
    left_ratio = 0.11
    right_ratio = 0.16
    trim_width = int(width * left_ratio)
    trim_height = int(height * upper_ratio)
    trim_width_right = width - int(width * right_ratio)
    
    # 麻雀の牌以外の部分をトリミングして除去
    roi = cropped_image[trim_height:, trim_width:trim_width_right]
    # 画像をグレースケールに変換
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    # 画像を2値化
    _, threshed_pai = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)
    # 牌の輪郭を検出
    contours, _ = cv2.findContours(threshed_pai, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # 輪郭の中で最も右側のX座標を取得する
    x_rightmosts = []
    for cnt in contours:
        rightmost_point = tuple(cnt[cnt[:,:,0].argmax()][0])
        x_rightmosts.append(rightmost_point[0])

    # ソートして、輪郭のx座標を昇順に並べる
    x_coords_sorted = sorted(x_rightmosts)
    # 輪郭が一定の間隔以上離れているものを探す
    gap_threshold = 300
    cut_x = None

    for i in range(1, len(x_coords_sorted)):
        if x_coords_sorted[i] - x_coords_sorted[i-1] > gap_threshold:
            cut_x = x_coords_sorted[i - 1]
            break
    # もし間隔が一定以上開いている輪郭が見つかれば、その位置でトリミング
    # 鳴いた牌を除去するため
    if cut_x:
        threshed_pai = threshed_pai[:, :cut_x]
    
    # 牌の輪郭を検出
    trimmed_called_pai_contours, _ = cv2.findContours(threshed_pai, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 牌の輪郭の数をカウント
    pai_count = len(trimmed_called_pai_contours)

    # 牌の数を返す
    return {"count": pai_count}

if __name__ == "__main__":
    app.run(port="8090", debug=True)
