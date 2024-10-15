# research-project

## 起動方法

```bash
# 仮想環境がまだ作成されていない場合
python3 -m venv myenv

# 仮想環境の有効化
source myenv/bin/activate

# djangoのインストール
pip install django
```

以下、python3コマンドは仮想環境内で実行する。

```bash
# 起動する
python3 manage.py runserver

# ※終了時は `Ctrl + C` で終了してください。
```

@ref https://qiita.com/royal_straight_flush/items/f6b67281117c60c80879

## マイグレーション

以下の手順によりテーブルを追加することができる。

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

### その他コマンド

マイグレーションの状態を確認する。
```bash
python manage.py showmigrations
```

マイグレーションを特定の位置までロールバックする。
```bash
# 0001_initialのマイグレーションまで戻す（0001_initialはup状態）
python manage.py migrate app 0001_initial
```

アプリのマイグレーションをリセットする。
```bash
python manage.py migrate app zero
```
