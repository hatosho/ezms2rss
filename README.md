# ezms2rss

楽天証券 マーケットスピード II RSS を Python に接続するプロジェクト

## Requirements / 必要な資産

- Windows 10 以上
- python 3.11.0（2023/10/01 時点）
- Microsoft Excel デスクトップ版
- 楽天証券 マーケットスピード II
- マーケットスピード II RSS（Excel アドイン）
- 楽天証券の証券口座

## Installing / 利用準備（必須）

本プロジェクトでは
Python の "バージョン管理" を pyenv-win で、"パッケージ管理" を Poetry で行います。

▼ 参考

[Windows 10 で Python のインストールから Poetry と pyenv の利用](https://qiita.com/kerobot/items/3f4064d5174676080585)

[Windows で Poetry を使った Python 環境の構築方法。](https://qiita.com/IoriGunji/items/290db948c11fdc81046a)

### 1. pyenv-win

pyenv は WSL 以外の Windows 環境では利用できないため、代わりに pyenv-win を採用した。

#### 1-1. pyenv-win 導入（導入済みの場合はスキップ）

1. pyenv-win のソースコードをホームフォルダ直下に clone する。

```powershell :
git clone https://github.com/pyenv-win/pyenv-win.git "$HOME\.pyenv"
```

2. 環境変数 PYENV, PYENV_ROOT, PYENV_HOME を設定する。

```powershell :
[System.Environment]::SetEnvironmentVariable('PYENV',$env:USERPROFILE + "\.pyenv\pyenv-win\","User")
[System.Environment]::SetEnvironmentVariable('PYENV_ROOT',$env:USERPROFILE + "\.pyenv\pyenv-win\","User")
[System.Environment]::SetEnvironmentVariable('PYENV_HOME',$env:USERPROFILE + "\.pyenv\pyenv-win\","User")
```

3. 環境変数 PATH を設定する。

```powershell :
[System.Environment]::SetEnvironmentVariable('PATH', $env:USERPROFILE + "\.pyenv\pyenv-win\bin;" + $env:USERPROFILE + "\.pyenv\pyenv-win\shims;" + [System.Environment]::GetEnvironmentVariable('PATH', "User"),"User")
```

4. PowerShell を再起動すると環境変数の変更が反映され、以下のコマンドでインストール成功を確認できます。

```powershell :
pyenv --version
```

5. インストール可能な Python のバージョン確認

```powershell :
pyenv install --list
```

6. Python のインストール
   必要なバージョンの Python がインストールされていない場合のみ行います。
   上記のコマンドで出力された Python バージョンの中から必要なものを指定して、インストールしてください。
   2023/10/01 時点で 3.11.0 を採用します。

```powershell :
pyenv install [バージョン]
```

7. Pyenv の shims を再構成

```powershell :
pyenv rehash
```

8. セット可能な Python のバージョン確認
   インストールしたバージョンが選択可能であることを確認します。

```powershell :
pyenv versions
```

9. 指定したバージョンの Python をセット

```powershell :
pyenv local [バージョン]
pyenv global [バージョン]
```

### 2. poetory

#### 2-1. poetory 導入（導入済みの場合はスキップ）

1. poetry インストール（windows の場合）

```Powershell :
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

2. 環境変数 PATH を設定する。

```Powershell :
[System.Environment]::SetEnvironmentVariable('path', $env:APPDATA + "\Python\Scripts;" + [System.Environment]::GetEnvironmentVariable('path', "User"),"User")
```

3. PowerShell を再起動すると環境変数の変更が反映され、以下のコマンドでインストール成功を確認できます。

```Powershell :
poetry --version
```

4. poetry config コマンドを利用することで、Poetry の設定の変更や確認が行えます。

```Powershell :
poetry config --list
```

5. poetry の設定変更

   .venv 仮想環境ディレクトリをプロジェクト直下に変更

   pyenv で指定したバージョンを Poetry で利用するように変更

```Powershell :
poetry config virtualenvs.in-project true
poetry config virtualenvs.prefer-active-python true
```

6. この時点で Poetry を利用して Python のバージョンを確認しても、エラーが返ることを確認しておきます（任意）

```Powershell :
poetry run python -V
```

7. Python のバージョンを指定

   2023/10/01 時点で 3.11.0 を採用します。

```Powershell :
pyenv versions
pyenv local [バージョン]
```

8. .venv 仮想環境ディレクトリのパスを変更

```Powershell :
poetry config virtualenvs.in-project true --local
```

9. 仮想環境の構築と依存パッケージのインストールを行います。

```Powershell :
poetry install
```

10. Poetry を利用して Python を実行した際の Python バージョンを確認

    結果が返ってこればインストール成功

    poetry 環境情報を表示

```Powershell :
poetry run python -V
poetry env info
```

### 3. マーケットスピード II 導入（導入済みの場合はスキップ）

1. マーケットスピード II インストール

   [マーケットスピード II のインストール | マーケットスピード II RSS オンラインヘルプ | 楽天証券のトレーディングツール](https://marketspeed.jp/ms2_rss/onlinehelp/ohm_001/ohm_001_03.html)

### 4. Excel と Add-in の設定（導入済みの場合はスキップ）

1. Excel デスクトップ版 インストール

   [推奨環境 | マーケットスピード II RSS | 楽天証券のトレーディングツール](https://marketspeed.jp/ms2_rss/system_requirements/)

1. マーケットスピード II RSS アドイン インストール

   [アドイン登録 | マーケットスピード II RSS オンラインヘルプ | 楽天証券のトレーディングツール](https://marketspeed.jp/ms2_rss/onlinehelp/ohm_001/ohm_001_04.html)

1. ms2rss アドイン利用同意書

   [RSS 利用同意書 | マーケットスピード II RSS オンラインヘルプ | 楽天証券のトレーディングツール](https://marketspeed.jp/ms2_rss/onlinehelp/ohm_001/ohm_001_05.html)

1. ms2rss アドイン機能利用設定

   [注文機能利用時の設定 | マーケットスピード II RSS オンラインヘルプ | 楽天証券のトレーディングツール](https://marketspeed.jp/ms2_rss/onlinehelp/ohm_001/ohm_001_06.html)

### 5. LINE Notify 導入

処理の失敗や取引結果のサマリを通知するために LINE を利用する。

ここで取得したトークンを次の手順で設定ファイルに入力する。

1. LINE Notify

   https://notify-bot.line.me/ja/

### 6. 本プロジェクトの設定ファイル修正

1. config 修正 1：アプリケーションパス情報の設定
1. config 修正 2：認証情報の入力

## How to use / 利用方法

### 1. 動作確認

sample を用意しています。以下コマンドを順に実行してください。

```python :sample.py
poetry run python ./sample/sample.py
```

### 2. 実践（他プロジェクトからの呼び出し）

sample を参考にしてください。

## Develop / 開発（任意）

### 1. pyenv-win による Python 仮想環境バージョン管理（任意）

```Powershell :
pyenv --version
pyenv install --list
pyenv install [バージョン]
pyenv rehash
pyenv versions
pyenv local [バージョン]
pyenv global [バージョン]
pyenv --version
```

### 2. Poetry による Python パッケージ管理（任意）

インストールされているモジュールの確認

キーワードを含むパッケージの検索

モジュールの追加

```Powershell :
poetry show
poetry search [キーワード]
poetry add [モジュール名]
```

### 3. vscode の拡張機能（linter / formatter）

linter / formatter には vscode の拡張機能を利用する。

開発者間でこれらを統一するため、vscode の設定ファイルをバージョン管理に含める。設定ファイルは、.vscode 配下。

#### 3-1. vscode 拡張機能の導入方法

▼ 参考：チームで推奨する VSCode 拡張機能を共有する tips

https://future-architect.github.io/articles/20200828/#%E6%96%B0%E8%A6%8F%E5%8F%82%E7%94%BB%E8%80%85%E3%81%AE%E6%89%8B%E9%A0%86

1. vscode を起動して、ctrl + O
2. 拡張機能の推奨項目一覧が表示されるので導入する。

#### 3-2. linter / formatter

うえで導入した linter / formatter について簡単に説明する。

### 4. テスト方法

# Acknowledgments / 謝辞
