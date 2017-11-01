# twitter_analytics

## 概要

[Twitter Analytics](https://analytics.twitter.com/)からデータをスクレイピングするツールです。

## 事前準備

1. お手持ちの環境に[PhantomJS](http://phantomjs.org/)をダウンロード、インストールしてください。
2. pipenvをインストールしてください。

```shell-session
$ pip install pipenv
```

3. 本プログラムをcloneし、設定ファイルを作成してください。

```shell-session
$ git clone https://github.com/sugitaka64/selenium.git
$ cd selenium/twitter_analytics/
$ cp config/conf_dummy.yml config/conf.yml
$ vi config/conf.yml
```
Twitter ID/PASS、およびTwitter AnalyticsのオーディエンスインサイトページのURLを記載してください。
オーディエンスインサイトページのデータを取得しない場合は、`audience_insights_url`を以下のように設定ください。

```shell-session
audience_insights_url:
```

## 使用方法

```shell-session
$ pipenv run python scripts/twitter_analytics.py \
  --conf_file_path=config/conf_test.yml \
  --output_dir_path=outputs/
```

`output_dir_path`に指定したディレクトリ内に、取得したデータがCSV形式で出力されます。

## 出力ファイル説明

- tweets_data.csv
  - 先月分のツイート
  - 先月分のインプレッション
  - 先月分のエンゲージメント
  - 先月分のエンゲージメント率
- attainment_data.csv
  - 現在のフォロワー数
  - 先月分の総ツイート数
  - 先月分の総インプレッション数
  - 先月分の総リツイート数
  - 先月分の総いいね数
  - 先月分のエンゲージメント率
  - 先月分の1日あたりのエンゲージメント率
  - 先月分の1日あたりのインプレッション数
  - 先月分の1日あたりの平均リツイート数
  - 先月分の1日あたりの平均いいね数
- audience_insights_data.csv
  - オーディエンスインサイトのフォロワーの人口特性情報
