#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cgi
import urllib
import optparse
import feedparser


#日本語、英語それぞれのgoogle news のRSSフィードを取得
ja_url = "https://news.google.com/news?hl=ja&ned=us&ie=UTF-8&oe=UTF-8&output=rss&topic="
en_url = "https://news.google.com/news?hl=en&cf=all&ned=us&cf=all&ie=UTF-8&oe=UTF-8&output=rss&topic="
type = ["y","w","b","p","e","s","t"] #国際、政治などの情報を指定
#収集したテキストデータの保存場所
ja_dir = "/home/minecraft/ja_documents"
en_dir = "/home/minecraft/en_documents"


def collect_article():
    global ja_url, en_url
    import os, mysql, re
    pattern = re.compile(r'.+url=(.+)') #掲載元のリンクを取得
    conn = mysql.MySQL('library') #使用するデータベース名
    for topic in type:
        ja_url = ja_url + topic
        ja_response = feedparser.parse(ja_url)
        en_url = en_url + topic
        en_response = feedparser.parse(en_url)
        print '*-----------------*'

        #日本語
        for topic in ja_response.entries:
            filename = 1 + len(os.listdir(ja_dir))#記事の保存場所
            sub = pattern.match(topic.link)
            article = sub.group(1)
            urllib.urlretrieve(article, "%s/%s.txt"  % (ja_dir ,str(filename)) )
            sql = "insert ignore ja_articles value(%s, '%s')" % (filename, article)
            print topic.title
            conn.exec_sql(sql)

        #英語
        for topic in en_response.entries:
            filename = 1 + len(os.listdir(en_dir))#記事の保存場所
            sub = pattern.match(topic.link)
            article = sub.group(1)
            urllib.urlretrieve(article, "%s/%s.txt"  % (en_dir ,str(filename)) )
            sql = "insert ignore en_articles value(%s, '%s')" % (filename, article)
            print topic.title #取得したページのタイトルを表示
            conn.exec_sql(sql)


if __name__ == '__main__':
    collect_article()

