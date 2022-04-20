#! ./api/.venv/bin/python
# -*- coding: utf-8 -*-

# ---standard library---
import logging
from logging import DEBUG, INFO, ERROR, Logger, getLogger
import asyncio
import concurrent.futures
import csv

# ---third party library---

# ---local library---
from core.chatdatacollector import ChatDataCollector
from core.videocollector import VideoCollector

class Backend:
    def __init__(self) -> None:
        self.logger = getLogger(__name__)

    def input_channel_list(self):
        with open('databases/channel_id.csv', 'r', encoding='utf-8') as f:
            reader = csv.reader(filter(lambda row: row[0]!='#', f))#, comment='#')
            channelList = [row for row in reader]
        return channelList

    async def create_video_list(self):
        vc = VideoCollector()
        loop = asyncio.get_event_loop()
        executor = concurrent.futures.ProcessPoolExecutor(max_workers=16)
        for channel in self.input_channel_list():
            self.logger.info(f'{channel[0]}:{channel[1]}')
            gather = []
            gather.append(loop.run_in_executor(executor, vc.get_list, channel[0]))
        await asyncio.gather(*gather)

    async def update_video_list(self):
        vc = VideoCollector()
        loop = asyncio.get_event_loop()
        executor = concurrent.futures.ProcessPoolExecutor(max_workers=16)
        for channel in self.input_channel_list():
            self.logger.info(f'{channel[0]}:{channel[1]}')
            # vc.update_list(channel[0])
            gather = []
            gather.append(loop.run_in_executor(executor, vc.update_list, channel[0]))
        await asyncio.gather(*gather)

if __name__ == '__main__':
    logging.basicConfig(
        level=ERROR,
        format='[ %(levelname)-8s] %(asctime)s | %(name)-32s %(funcName)-24s| %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    fh = logging.FileHandler(filename='log/backend.log', encoding='utf-8')
    fh.setLevel=INFO
    fh.setFormatter(logging.Formatter('[ %(levelname)-8s] %(asctime)s | %(name)-32s %(funcName)-24s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))

    logger = getLogger(__name__)
    logger.addHandler(fh)

    backend = Backend()

    loop = asyncio.get_event_loop()
    # backend.update_video_list()
    loop.run_until_complete(backend.update_video_list())
    # loop.run_until_complete(cdc.input_channel_list())
    # loop.run_until_complete(cdc.create_chatdatabase())