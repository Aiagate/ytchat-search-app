#! ./.venv/bin/python
# -*- coding: utf-8 -*-

# ---standard library---
import logging
from logging import getLogger

# ---third party library---

# ---local library---
from util.dbconnect import DatabaseConnect
import config


class ChatDataExtractor():
    def __init__(self):
        self.logger = getLogger(__name__)
        self.table_name = 'yt_chatdata'
    
    def search_video(self, keyword):
        with DatabaseConnect('youtube_chat') as db:
            try:
                db.cursor.execute(f'SELECT DISTINCT video_id FROM {self.table_name} where message like \"%{keyword}%\";')
                result = db.cursor.fetchall()
            except Exception as e:
                raise e
        video_ids = []
        for video_id in result:
            video_ids.append(video_id[0])
        return video_ids

    def search_chat(self, keyword, minscore=0):
        with DatabaseConnect('youtube_chat') as db:
            try:
                db.cursor.execute(
                    f'SELECT video_id,elapsedTime,datetime\
                    FROM {self.table_name} where message like \"%{keyword}%\" order by video_id,elapsedTime;')
                result = db.cursor.fetchall()
            except Exception as e:
                raise e
        search_result = []
        for video_id in set([r[0] for r in result]):
            chat = sorted([r for r in result if r[0] == video_id], key=lambda c: c[1])
            datetime = chat[0][2]
            nexttime = 0
            for c in chat:
                t = int(c[1])
                if (t < 0):
                    continue
                elif (nexttime < t):
                    seektime = t
                    nexttime = t + 10
                    score = 1
                    for endtime in chat:
                        if (seektime < endtime[1] and endtime[1] < nexttime):
                            nexttime += 10
                            score += 1
                            continue
                        elif (endtime[1] > nexttime):
                            break
                    if (score < minscore): break

                    url = f'https://youtu.be/{video_id}'
                    search_result.append(
                        {
                            'video_id':f'{video_id}',
                            'datetime':datetime,
                            'url':f'{url}?t={seektime - config.SEEK_TIME_OFFSET}',
                            'seektime':seektime - config.SEEK_TIME_OFFSET,
                            'score':score
                        }
                    )
                    self.logger.info(f'Search Result {url}?t={seektime - config.SEEK_TIME_OFFSET} score={score}')
        return search_result

if __name__ == '__main__':
    import logging
    from logging import DEBUG, INFO, Logger, getLogger
    logging.basicConfig(
        level=INFO,
        format='[ %(levelname)-8s] %(asctime)s | %(name)-24s %(funcName)-16s| %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    fh = logging.FileHandler(filename='log/chat_data_search_system.log', encoding='utf-8')
    fh.setLevel=DEBUG
    fh.setFormatter(logging.Formatter('[ %(levelname)-8s] %(asctime)s | %(name)-32s %(funcName)-24s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))

    logger = getLogger(__name__)
    logger.addHandler(fh)

    cde = ChatDataExtractor()
    cde.search_chat('くしゃみ')#,input('keyword:'))
