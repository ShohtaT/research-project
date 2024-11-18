# research-project

## 初期設定

```bash
# 仮想環境がまだ作成されていない場合
python3 -m venv myenv
```

## 起動方法

```bash
# 仮想環境の有効化
source myenv/bin/activate

# 起動する
python3 manage.py runserver

# ※終了時は `Ctrl + C` で終了してください。
```

@ref https://qiita.com/royal_straight_flush/items/f6b67281117c60c80879

## 処理内容と実行

```bash
# main.pyの実行
python3 ./app/main.py
```

### 処理内容
1. 文字起こし（3分間）
   1. CSV ファイルが自動生成される
2. 生成した最新 CSV を用いて Gemini へリクエスト

[実行例]
<img src="./images/スクリーンショット%202024-11-18%2015.54.38.png">

<hr>

## その他コマンド

- テーブルの追加
```bash
# 実行例

# マイグレーションファイルの作成
(myenv) research-project % python manage.py makemigrations    
Migrations for 'app':
  app/migrations/0001_initial.py
    + Create model Book

# マイグレーションの実行
(myenv) research-project % python manage.py migrate       
Operations to perform:
  Apply all migrations: admin, app, auth, contenttypes, sessions
Running migrations:
  Applying app.0001_initial... OK
```

- マイグレーションの状態を確認する。
```bash
python manage.py showmigrations
```

- マイグレーションを特定の位置までロールバックする。
```bash
# 0001_initialのマイグレーションまで戻す（0001_initialはup状態）
python manage.py migrate app 0001_initial
```

- アプリのマイグレーションをリセットする。
```bash
python manage.py migrate app zero
```
