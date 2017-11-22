## 機能

### scripts/tenshoku_kaigi.py

https://jobtalk.jp/ から特定企業のクチコミをスクレイピングし、MySQLに保存する。

### scripts/morphological_analysis.py

MySQLに保存したクチコミを形態素解析し、結果をMySQL内の別のテーブルに保存する。  
（2文字以上の名詞のみ保存される。）

### scripts/analyze_sentiment.py

MySQLに保存したクチコミを、[Google Cloud Natural Language API](https://cloud.google.com/natural-language/?hl=ja)を使ってポジネガ判定を行う。結果はMySQL内の別のテーブルに保存される。

### scripts/word_count.py

形態素解析した単語のワードカウントを行う。結果はCSVファイルで出力される。

### scripts/tf_idf.py

形態素解析した単語のtf-idfスコアを求める。結果はCSVファイルで出力される。

## 使用方法

### 前提

以下がインストールされていること

* Python 3.6.x
* pip
* MySQL

### DB設定

MySQLにテーブルを作成してください。

```sql
mysql> CREATE DATABASE tenshoku_kaigi;

mysql> USE tenshoku_kaigi;

mysql> CREATE TABLE `word_of_mouth_comment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `company_id` int(11) NOT NULL,
  `comment` longtext NOT NULL,
  `raiting` varchar(1) DEFAULT NULL,
  `review_id` varchar(32) NOT NULL,
  `post_date` datetime(6) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `word_of_mouth_comment_company_id_2933f996` (`company_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

mysql> CREATE TABLE `word_of_mouth_analyzesentiment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `score` decimal(14,4) NOT NULL,
  `magnitude` decimal(14,4) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `comment_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `word_of_mouth_analyz_comment_id_6ae94447_fk_word_of_m` (`comment_id`),
  CONSTRAINT `word_of_mouth_analyz_comment_id_6ae94447_fk_word_of_m` FOREIGN KEY (`comment_id`) REFERENCES `word_of_mouth_comment` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

mysql> CREATE TABLE `morphological_analysis` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `word_of_mouth_id` int(11) NOT NULL,
  `word` varchar(32) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `word_of_mouth_id` (`word_of_mouth_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
```

### 環境構築

#### Pythonパッケージのインストール

```shell-session
$ pip install pipenv flake8 flake8-docstrings flake8-polyfill hacking
```

#### clone、及びpipenv実行

```shell-session
$ git clone https://github.com/sugitaka64/selenium.git
$ cd selenium/tenshoku_kaigi/
$ pipenv update
```

#### configファイルの作成

```shell-session
$ cp config/conf_dummy.yml config/conf.yml
```

`conf.yml`の各項目の説明は以下を参照。

```
login_id: https://jobtalk.jp/ のログインID
login_pw: https://jobtalk.jp/ のログインパスワード
company_id: スクレイピング対象の企業ID（https://jobtalk.jp/company/xxx のxxx部分）
mysql_host: MySQLのホスト名
mysql_user: MySQLのユーザ名
mysql_pw: MySQLのパスワード
```

### 実行

#### scripts/tenshoku_kaigi.py

```
$ pipenv run python scripts/tenshoku_kaigi.py \
    --conf_file_path=<conf_file_path>
```

* conf_file_path: 上記で作成したYAMLファイル
* 結果はMySQL内の`word_of_mouth_comment`テーブルに保存される

#### scripts/morphological_analysis.py

```
$ pipenv run python scripts/morphological_analysis.py \
    --conf_file_path=<conf_file_path>
```

* conf_file_path: 上記で作成したYAMLファイル
* 結果はMySQL内の`morphological_analysis`テーブルに保存される

#### scripts/analyze_sentiment.py

```
$ pipenv run python scripts/analyze_sentiment.py \
    --conf_file_path=<conf_file_path>
```

* conf_file_path: 上記で作成したYAMLファイル
* 結果はMySQL内の`word_of_mouth_analyzesentiment`テーブルに保存される

#### scripts/word_count.py

```
$ pipenv run python scripts/word_count.py \
    --conf_file_path=<conf_file_path>
    --output_dir_path=<output_dir_path>
```

* conf_file_path : 上記で作成したYAMLファイル
* output_dir_path: 結果のCSVファイル（word_count.csv）を出力するディレクトリ
* CSVファイルフォーマット
  * ヘッダ行あり
  * 1列目がクチコミのID、2列目以降が各単語のワードカウント数

#### scripts/tf_idf.py

```
$ pipenv run python scripts/tf_idf.py \
    --conf_file_path=<conf_file_path>
    --output_dir_path=<output_dir_path>
```

* conf_file_path : 上記で作成したYAMLファイル
* output_dir_path: 結果のCSVファイル（tf_idf.csv）を出力するディレクトリ
* CSVファイルフォーマット
  * ヘッダ行あり
  * 1列目がクチコミのID、2列目以降が各単語のtf-idfスコア

## その他

### テスト方法

```shell-session
$ pipenv run python -m unittest tests/test_get_data_from_twitter_analytics.py
```

