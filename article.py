#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib.request
import feedparser
import sys
import re
import os
import mysql
from readability.readability import Document

#日本語、英語それぞれのgoogle news のRSSフィードを取得
ja_pre_url = "https://news.google.co.jp/news?hl=ja&ned=us&ie=UTF-8&oe=UTF-8&output=rss&topic="
en_pre_url = "https://news.google.com/news/section?cf=all&hl=en&pz=1&ned=us&output=rss&topic="

#国際、政治などの情報を指定
type = ["y","w","b","p","e","s","t"] 

#収集したテキストデータの保存場所
ja_dir = "/home/minecraft/ja_documents"
en_dir = "/home/minecraft/en_documents"

#htmlソースから本文を抽出し、タグを除去する
def get_text(html):
    try:
        source = urllib.request.urlopen(html).read()
        readable_title = Document(source).short_title()
        readable_article = Document(source).summary()
        text = re.sub('<.+?>', '', readable_article)
        text = re.sub('[\s]+', ' ', text) # 改行や空白の連続を回避
        return readable_title, text
    except urllib.error.HTTPError as e:
        print('Page not found')
        return '', ''


def main():
    pattern = re.compile(r'.+url=(.+)') #掲載元のリンクを取得
    conn = mysql.MySQL('library') #使用するデータベース名

    for topic in type:
        en_url = en_pre_url + topic
        en_response = feedparser.parse(en_url) #google newsのRSSを取得
        ja_url = ja_pre_url + topic
        ja_response = feedparser.parse(ja_url) #日本語版
  
        print('*-----------------*')

        #英語
        for entry in en_response.entries:
            sub = pattern.match(entry.link) #google newsのurlを取得
            article = sub.group(1) #掲載元のurlを正規表現で抜き取る
            date = entry.published
            title, text = get_text(article)
            if not(title) : continue
            print(article)
            where = 'url = "%s"' % article
            #urlがデータベースに登録されていなければ新規に登録する
            if not (conn.select('En_News', 'url', where)):
                num = conn.select('En_News','count(id)','') #取得済記事の総数
                filename = 1 + int(num[0][0]) #ファイル名は取得した順番+.txtとする
                urllib.request.urlretrieve(article, "%s/%s.txt"  % (en_dir ,str(filename)) )
                sql = "insert into En_News (url, publish_time, text, title) values (%s,%s,%s,%s);" 
                conn.param_sql(sql, (article, date, text, title)) #urlの重複が起こらないように登録する

        #日本語
        for entry in ja_response.entries:
            sub = pattern.match(entry.link) #google newsのurlを取得
            article = sub.group(1) #掲載元のurlを正規表現で抜き取る
            date = entry.published
            title, text = get_text(article)
            if not(title) : continue
            print(article)
            where = 'url = "%s"' % article
            #urlがデータベースに登録されていなければ新規に登録する
            if not (conn.select('Ja_News', 'url', where)):
                num = conn.select('Ja_News','count(id)','') #取得済記事の総数
                filename = 1 + int(num[0][0]) #ファイル名は取得した順番+.txtとする
                urllib.request.urlretrieve(article, "%s/%s.txt"  % (ja_dir ,str(filename)) )
                sql = "insert into Ja_News (url, publish_time, text, title) values (%s,%s,%s,%s);" 
                conn.param_sql(sql, (article, date, text, title)) #urlの重複が起こらないように登録する

if __name__ == '__main__':
    main()

