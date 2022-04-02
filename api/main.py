#! ./api/.venv/bin/python
# -*- coding: utf-8 -*-

# ---standard library---
from datetime import datetime
import os
import logging
from logging import DEBUG, INFO, getLogger
from unittest import result
import yaml

# ---third party library---
import uvicorn
from fastapi import FastAPI

# ---local library---
import config
from util.dbconnect import DatabaseConnect
from core.chatdataextractor import ChatDataExtractor

app = FastAPI()

@app.get('/')
def root():
    cde = ChatDataExtractor()
    return {'items':cde.search_chat('くしゃみ')}

@app.get('/serch/keyword')
async def search_from_word(channel_id: str='', keyword: str='', minscore: int=0):
    cde = ChatDataExtractor()
    res = {}
    result = []
    # video_ids = cde.search_video(keyword=keyword)
    # for video_id in video_ids:
    #     result.extend(cde.extract_from_keyword(video_id=video_id, keyword=keyword, minscore=minscore))
    result = cde.search_chat(keyword=keyword, minscore=minscore)
    print(result[0]['datetime'])
    res['items'] = sorted(result, key=lambda r: r['datetime'])
    return res

if __name__ == '__main__':
    logging.basicConfig(
        level=INFO,
        format='[ %(levelname)-8s] %(asctime)s | %(name)-24s %(funcName)-16s| %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logfile = f'{os.path.basename(__file__)}.log'
    logfile_path = f'api/log/{logfile}'
    fh = logging.FileHandler(filename=logfile_path, encoding='utf-8')
    fh.setLevel=DEBUG
    fh.setFormatter(logging.Formatter('[ %(levelname)-8s] %(asctime)s | %(name)-32s %(funcName)-24s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))

    logger = getLogger(__name__)
    logger.addHandler(fh)
    logger = getLogger('uvcorn')
    logger.addHandler(fh)

    uvicorn.run(app=app, host='localhost', port=8080)