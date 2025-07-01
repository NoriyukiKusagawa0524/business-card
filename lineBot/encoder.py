import sys
import json
import base64
import os
from dotenv import load_dotenv; load_dotenv()

# メイン関数
def main(filename: str):
    # JSONパス
    dir_path = os.path.dirname(__file__)
    file_path = os.path.join(dir_path, filename)

    # JSONオブジェクト
    with open (file_path, "r") as file:
        data = json.load(file)

    # JSONオブジェクトを文字列に変換
    json_str = json.dumps(data)

    # 文字列をバイト列に変換してBase64エンコード
    encoded_bytes = base64.b64encode(json_str.encode('utf-8'))

    # エンコードされたバイト列を文字列に変換
    encoded_str = encoded_bytes.decode('utf-8')

    # デバッグ用出力
    print("エンコードされたBase64文字列:")
    print(encoded_str)

    # テキストファイルに保持
    savefile = filename.replace(".json",".txt")

    # 新規 or 上書きで書き込み
    with open(savefile, 'w') as textfile:
        textfile.write(encoded_str)

# コマンドから実行
if __name__ == '__main__':
    # 引数を取得
    args = sys.argv

    # 対象を設定
    file = ""
    if 2 == len(args):
        # 引数が1つだけの場合は、そのまま設定。
        file = args[1]
    else:
        # 引数なし or 不正な場合は固定値
        file = "aaaaaa.json"
    
    # 処理の実行
    main(file)


