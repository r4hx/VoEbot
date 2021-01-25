import logging
import random
import time
from collections import deque
import os

import requests
from aiogram import Bot, Dispatcher, executor, types

logging.basicConfig(level=logging.DEBUG)

bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
dp = Dispatcher(bot)

vk_token = os.getenv("VKONTAKTE_TOKEN")

vk_decent_girl_queue = deque()
vk_tits_girl_queue = deque()
vk_random_girl_queue = deque()

vk_decent_girl_group_id_list = [
    "41515536",
    "48410284",
    "55682860",
    "18876721",
    "56473407",
]
vk_tits_girl_group_id_list = [
    "10698161",
    "75564179",
    "10698161",
    "41217948",
    "66760160",
]
vk_random_girl_group_id_list = [
    "28592774",
    "112063288",
    "51744520",
    "163618600",
    "22162327",
]


def get_image_from_vk(group_id_list):
    url_list = []
    for group_id in group_id_list:
        response = requests.get(
            f"https://api.vk.com/method/wall.get?owner_id=-{group_id}&count=100&filter=owner&extended=1&access_token={vk_token}&v=5.126"
        )
        time.sleep(0.4)
        for res in response.json()["response"]["items"]:
            if res.get("attachments"):
                attachments = res["attachments"][0]
                if attachments.get("type") == "photo":
                    url_list.append(attachments["photo"]["sizes"][-1]["url"])
    random.shuffle(url_list)
    return url_list


@dp.message_handler(
    text=[
        "Приличную",
        "приличную",
        "Приличная",
        "приличная",
        "Скромную",
        "скромную",
        "Скромная",
        "скромная",
    ]
)
async def send_decent_girl(message: types.Message):
    if len(vk_decent_girl_queue) > 0:
        await bot.send_photo(
            message.chat.id, types.InputFile.from_url(vk_decent_girl_queue.pop())
        )
    else:
        vk_decent_girl_queue.extend(get_image_from_vk(vk_decent_girl_group_id_list))
        if len(vk_decent_girl_queue) == 0:
            await message.reply("Приличных не осталось!")
        else:
            await bot.send_photo(
                message.chat.id, types.InputFile.from_url(vk_decent_girl_queue.pop())
            )
    print(f"decent girl count: {len(vk_decent_girl_queue)}")


@dp.message_handler(
    text=[
        "Титьку",
        "титьку",
        "Титька",
        "титька",
        "Сиську",
        "сиську",
        "Сиська",
        "сиська",
    ]
)
async def send_tits_girl(message: types.Message):
    if len(vk_tits_girl_queue) > 0:
        await bot.send_photo(
            message.chat.id, types.InputFile.from_url(vk_tits_girl_queue.pop())
        )
    else:
        vk_tits_girl_queue.extend(get_image_from_vk(vk_tits_girl_group_id_list))
        if len(vk_tits_girl_queue) == 0:
            await message.reply("Сиськи закончились!")
        else:
            await bot.send_photo(
                message.chat.id, types.InputFile.from_url(vk_tits_girl_queue.pop())
            )
    print(f"tits girl count: {len(vk_tits_girl_queue)}")


@dp.message_handler(
    text=[
        "Случайную",
        "Случайно",
        "Рандом",
        "Рандомную",
        "случайную",
        "случайно",
        "рандом",
        "рандомную",
    ]
)
async def send_random_girl(message: types.Message):
    if len(vk_random_girl_queue) > 0:
        await bot.send_photo(
            message.chat.id, types.InputFile.from_url(vk_random_girl_queue.pop())
        )
    else:
        vk_random_girl_queue.extend(get_image_from_vk(vk_random_girl_group_id_list))
        if len(vk_random_girl_queue) == 0:
            await message.reply("Случайных больше нет!")
        else:
            await bot.send_photo(
                message.chat.id, types.InputFile.from_url(vk_random_girl_queue.pop())
            )
    print(f"random girl count: {len(vk_random_girl_queue)}")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
