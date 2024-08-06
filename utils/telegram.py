import asyncio
import io
import os
import pathlib
import re
import time

import ffmpeg
import imagehash
import tqdm
import tqdm.asyncio
from PIL import Image
from telegram import Bot
from telegram.error import TimedOut
from telegram.ext import ApplicationBuilder

loong_sticker_name_list = [
    'https://t.me/addstickers/dragonpic',
    'https://t.me/addstickers/p0_wmtz2103953167_by_wumingv2bot',
    "https://t.me/addstickers/longtuc",
    "https://t.me/addstickers/skdjj6680_by_fstikbot",
    "https://t.me/addstickers/longtucs",
    "https://t.me/addstickers/kirinlongtu_by_favorite_stickers_bot"
]


download_path = pathlib.Path(__file__).parent / '../data/loong'
download_path.mkdir(parents=True, exist_ok=True)

temp_path = download_path.parent / "temp"
temp_path.mkdir(parents=True, exist_ok=True)


async def download_sticker(sticker):
    try:
        file = await get_bot().get_file(sticker.file_id)
        byte = io.BytesIO()
        await file.download_to_memory(byte)
        byte.seek(0)

        if sticker.is_animated:
            pass
            return
        if sticker.is_video:
            process = (
                ffmpeg.input('pipe:0')
                .output(str(temp_path / f"temp_%d.png"))
                .run_async(pipe_stdin=True, pipe_stdout=True, pipe_stderr=True)
            )
            process.communicate(input=byte.read())

            # count frames
            frames = len(list(temp_path.glob("*.png")))

            for i in range(1, frames + 1):
                # compute hash
                img = Image.open(temp_path / f"temp_{i}.png").convert('RGBA')
                hash_ = imagehash.phash(img)
                img.save(
                    download_path / f"{hash_}.png", "PNG")

            # clean temp files
            for f in temp_path.glob("*.png"):
                f.unlink()
            return

        img = Image.open(byte).convert('RGBA')
        hash_ = imagehash.phash(img)
        img.save(
            download_path / f"{hash_}.png", "PNG")
    except TimedOut as e:
        time.sleep(1)
        return await download_sticker(sticker)
    # except Exception as e:
    #     tqdm.tqdm.write(f"Error: {e}")
    #     time.sleep(1)
    #     return await download_sticker(sticker)


async def download_sticker_set(sticker_set_name: str) -> list:
    # parse url
    if re.match(r"https://t.me/addstickers/.*", sticker_set_name):
        sticker_set_name = sticker_set_name.split('/')[-1]

    sticker_set = await get_bot().get_sticker_set(sticker_set_name)

    for sticker in tqdm.tqdm(sticker_set.stickers):
        await download_sticker(sticker)


async def main():
    for sticker_set_name in tqdm.tqdm(loong_sticker_name_list):
        await download_sticker_set(sticker_set_name)


def get_bot():
    global idx
    idx += 1
    return bot_list[idx % len(bot_list)]


idx = -1

token_list = [i for i in os.environ.get("TELEGRAM_TOKEN_LIST").split(',') if i]
bot_list = [Bot(token) for token in token_list]

limit = asyncio.Semaphore(32)

ApplicationBuilder().connection_pool_size(512)

if __name__ == "__main__":
    asyncio.run(main())


temp_path.rmdir()
