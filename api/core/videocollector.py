#! ./.venv/bin/python
# -*- coding: utf-8 -*-

# ---standard library---
import asyncio
import concurrent.futures
from datetime import datetime, timedelta
import logging
from logging import DEBUG, INFO, Logger, getLogger
import json
import csv
import time

# ---third party library---
import yt_dlp
from yt_dlp.utils import DateRange
import pandas

# ---local library---
from util.dbconnect import DatabaseConnect
from util.youtubeapi import YoutubeApi
from core.chatdatamodule import ChatDataModule
import config

class VideoCollector():
    def __init__(self) -> None:
        self.logger = getLogger(__name__)
        self.videolist_table = 'yt_videolist'
        self.chatdata_table = 'yt_chatdata'
        self.ytdl_ops = {'cookiefile':'cookie/cookies.txt'}

        with DatabaseConnect('youtube_chat') as db:
            try:
                db.cursor.execute(f'CREATE TABLE IF NOT EXISTS {self.videolist_table} ' + config.VIDEO_DATALIST)
                db.cursor.execute(f'CREATE TABLE IF NOT EXISTS {self.chatdata_table} ' + config.CHAT_DATALIST)
            except Exception as e:
                raise e

    def get_list(self, channel_id):
        # Youtube-DLから動画情報を取得
        # info = yt_dlp.YoutubeDL().extract_info(f'https://www.youtube.com/channel/{channel_id}', download=False)
        for i in range(10): # タイムアウト等を考慮し、10回まで取得に挑戦する
            try:
                info = yt_dlp.YoutubeDL(self.ytdl_ops).extract_info(f'https://www.youtube.com/channel/{channel_id}', download=False)
                self.logger.debug(json.dumps(info, indent=4))
                break
            except yt_dlp.utils.DownloadError as e: #チャンネルURLが有効でない場合にエラーを返す
                self.logger.error(e)
            except Exception as e:
                self.logger.error(e)
            time.sleep(10)

        for video in info['entries']:
            with DatabaseConnect('youtube_chat') as db:
                try:
                    #ボトルネック
                    db.cursor.execute(f'SELECT COUNT(video_id) FROM {self.videolist_table} WHERE video_id = \"{video.get("id")}\";')
                except Exception as e:
                    raise e
                if db.cursor.fetchone()[0] != 0:
                    self.logger.info(f'{video.get("id")} skip! already getted info.')
                    continue

            if video['is_live'] == 'True':
                self.logger.info(f'{video.get("id")} skip! video has live now. ')
                continue

            title       = video.get('fulltitle')
            description = video.get('description')
            timestamp   = datetime.fromtimestamp(int(video.get('release_timestamp'))) if video.get('release_timestamp') != None else datetime.strptime(video.get('upload_date') , '%Y%m%d')
            is_live     = video.get('was_live')
            live_chat   = 'live_chat' in video.get('subtitles').keys() if video.get('subtitles') != None else False

            sql = f'INSERT INTO {self.videolist_table} VALUES (%s, %s, %s, %s, %s, %s, %s)'
            with DatabaseConnect('youtube_chat') as db:
                try:
                    db.cursor.execute(sql,(video.get('id'), channel_id, title, description, timestamp.strftime('%Y-%m-%d %H:%M:%S'), is_live, live_chat))
                except Exception as e:
                    raise e

    def update_list(self, channel_id):
        # Youtube-DLから動画情報を取得
        # info = yt_dlp.YoutubeDL().extract_info(f'https://www.youtube.com/channel/{channel_id}', download=False)
        ytdl_ops = {
            'cookiefile':'cookie/cookies.txt',
            'daterange': DateRange('20220419','20220420'),
            'playliststart':1,
            'playlistend':10
        }
        for i in range(10):
            try:
                info = yt_dlp.YoutubeDL(ytdl_ops).extract_info(f'https://www.youtube.com/channel/{channel_id}', download=False)
                self.logger.debug(json.dumps(info, indent=4))
                break
            except yt_dlp.utils.DownloadError as e: #チャンネルURLが有効でない場合にエラーを返す
                self.logger.error(e)
                raise e
            except Exception as e:
                print(e)
            time.sleep(10)

        for video in info['entries']:
            with DatabaseConnect('youtube_chat') as db:
                try:
                    #ボトルネック
                    db.cursor.execute(f'SELECT COUNT(video_id) FROM {self.videolist_table} WHERE video_id = \"{video.get("id")}\";')
                except Exception as e:
                    raise e
                if db.cursor.fetchone()[0] != 0:
                    print(f'{video.get("id")} skip! already getted info.')
                    continue

            if video['is_live'] == 'True':
                print(f'{video.get("id")} skip! video has live now. ')
                continue

            title       = video.get('fulltitle')
            description = video.get('description')
            timestamp   = datetime.fromtimestamp(int(video.get('release_timestamp'))) if video.get('release_timestamp') != None else datetime.strptime(video.get('upload_date') , '%Y%m%d')
            is_live     = video.get('was_live')
            live_chat   = 'live_chat' in video.get('subtitles').keys() if video.get('subtitles') != None else False

            sql = f'INSERT INTO {self.videolist_table} VALUES (%s, %s, %s, %s, %s, %s, %s)'
            with DatabaseConnect('youtube_chat') as db:
                try:
                    db.cursor.execute(sql,(video.get('id'), channel_id, title, description, timestamp.strftime('%Y-%m-%d %H:%M:%S'), is_live, live_chat))
                except Exception as e:
                    raise e
