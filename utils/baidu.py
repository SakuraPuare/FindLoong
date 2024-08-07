import asyncio
import os
import pathlib
import time
from io import BytesIO

import aiotieba as tb
import httpx
import imagehash
import tqdm
from aiotieba import Client
from PIL import Image

BDUSS = os.environ.get("BDUSS")
BDUSS_LIST = os.environ.get("BDUSS_LIST")
STOKEN = os.environ.get("STOKEN")
STOKEN_LIST = os.environ.get("STOKEN_LIST")

client_list = []

target = "龙玉涛"

idx = -1


def get_client() -> Client:
    assert len(client_list) > 0, "No client available"
    global idx
    idx += 1
    return client_list[idx % len(client_list)]


async def login():
    global client_list

    if BDUSS:
        if STOKEN:
            client = tb.Client(BDUSS, STOKEN)
        else:
            client = tb.Client(BDUSS)
        client_list.append(client)

    for bduss, stoken in zip(BDUSS_LIST.split(','), STOKEN_LIST.split(',')):
        if stoken:
            client = tb.Client(bduss, stoken)
        else:
            client = tb.Client(bduss)
        client_list.append(client)


async def print_info():
    for client in client_list:
        print(await client.get_self_info())


async def release():
    for client in client_list:
        await client.__aexit__()


async def get_threads(name: str):
    resp = await get_client().get_threads(name)
    threads_count = resp.page.total_count
    page_size = 100

    # 对于贴吧里帖子列表的每一页
    for thread_page in tqdm.trange(status.get('current_page', 1), threads_count // page_size + 1, desc='Page'):
        thread = await get_client().get_threads(name, rn=page_size, pn=thread_page)

        # 对于每个帖子
        for idx, thread in tqdm.tqdm(enumerate(thread.objs), total=page_size, desc='Thread'):
            if idx + 1 < status.get('current_thread_idx', 1):
                continue

            resp = await get_client().get_posts(thread.tid)
            post_count = resp.page.total_page * resp.page.page_size

            # 对于每个帖子里的每一页
            for post_page in tqdm.trange(1, post_count // page_size + 1, desc='Post'):
                posts = await get_client().get_posts(thread.tid, pn=post_page, rn=page_size)
                for post in posts.objs:
                    for img in post.contents.imgs:
                        await get_image(img.origin_src)

                status['current_post_idx'] = post_page
            status['current_thread_idx'] = idx + 1
        status['current_page_idx'] = thread_page


async def get_image(url: str, **kwargs):
    async with limit:
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(url)
                resp.raise_for_status()

                img = Image.open(BytesIO(resp.content))
                img.convert('RGBA')
                hash_ = imagehash.phash(img)

                with open(download_path / f"{hash_}.png", 'wb') as f:
                    f.write(resp.content)

            except Exception as e:
                tqdm.tqdm.write(f"Error: {e}")
                time.sleep(1)
                return await get_image(url, **kwargs)


async def main():
    await login()
    await print_info()

    try:
        await get_threads(target)
    except Exception as e:
        print(e)
    finally:
        await release()
        print(status)


status = {
    'current_page_idx': 1,
    'current_thread_idx': 2,
    'current_post_idx': 1
}

limit = asyncio.Semaphore(5)
download_path = pathlib.Path(__file__).parent / "../download"
download_path.mkdir(exist_ok=True)


if __name__ == "__main__":
    asyncio.run(main())
