import datetime
import logging
import os
import random
import time
from collections import deque

import requests
from aiogram import Bot, Dispatcher, executor, types

logging.basicConfig(level=logging.DEBUG)


class Category:
    def __init__(self, vk_ids: list) -> None:
        """Init queue"""
        self.vk_ids = vk_ids
        self.queue = deque(self.get_url_from_vk())

    def __str__(self) -> str:
        """Return items count in deque"""
        return f"Items in stack: {len(self.queue)}"

    def get_url_from_vk(self) -> list:
        """Get photo url from vk group"""
        self.urls = []
        for self.i in self.vk_ids:
            self.response = requests.get(
                f"https://api.vk.com/method/wall.get?owner_id=-{self.i}&count=100&filter=owner&extended=1&access_token={os.getenv('VKONTAKTE_TOKEN')}&v=5.126"
            )
            time.sleep(0.33)
            for self.r in self.response.json()["response"]["items"]:
                if self.r.get("attachments"):
                    self.attachments = self.r["attachments"][0]
                    if self.attachments.get("type") == "photo":
                        self.urls.append(self.attachments["photo"]["sizes"][-1]["url"])
        random.shuffle(self.urls)
        return self.urls

    def get_url(self) -> str:
        """Getter for url"""
        if len(self.queue) > 0:
            return self.queue.pop()
        else:
            self.queue.extend(self.get_url_from_vk())
            return self.queue.pop()

    url = property(get_url)


class Telegram:
    def __init__(self, buttons: tuple) -> None:
        """Create bot object and dispatcher"""
        self.bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
        self.dp = Dispatcher(self.bot)
        self.exclude_users = deque()
        self.buttons = buttons

    def simple_keyboard(self):
        """Generate keyboard for telegram chat menu"""
        self.keyboard_markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True,
            row_width=3,
            one_time_keyboard=False,
            selective=True,
        )
        self.keyboard_markup.row(
            *(types.KeyboardButton(self.text) for self.text in self.buttons)
        )
        return self.keyboard_markup

    def add_exclude_users(self, from_user_id, to_user_id, counter):
        self.user_id = to_user_id
        self.from_user_id = from_user_id
        self.counter = counter
        self.exclude_users.append((to_user_id, self.counter))


class Command:
    def __init__(self) -> None:
        """Make command index"""
        self.decent_category = Category(
            ["41515536", "48410284", "55682860", "18876721", "56473407"]
        )
        self.ass_category = Category(
            ["170989088", "63996148", "89034623", "165009163", "147498239"]
        )
        self.tits_category = Category(
            ["10698161", "75564179", "10698161", "41217948", "66760160"]
        )
        self.random_girl_category = Category(
            ["28592774", "112063288", "51744520", "163618600", "22162327"]
        )
        self.asian_category = Category(
            ["165058238", "106947487", "196988750", "112115472", "99949199", "11695248"]
        )
        self.index = {
            "Сиська": [
                "Сиська",
                "Сиськи",
                "Грудь",
                "Титька",
                "Титьки",
                self.tits_category.url,
            ],
            "Попа": [
                "Попа",
                "Жопа",
                "Задница",
                "Попец",
                "Попка",
                "Жопка",
                self.ass_category.url,
            ],
            "Азия": [
                "Азия",
                "Азиатки",
                self.asian_category.url,
            ],
            "Рандом": [
                "Рандом",
                "Случайную",
                self.random_girl_category.url,
            ],
            "Скромная": [
                "Приличная",
                "Скромная",
                "Приличную",
                "Скромную",
                self.decent_category.url,
            ],
        }

    def __new__(cls):
        """make singltone objects"""
        if not hasattr(cls, "instance"):
            cls.instance = super(Command, cls).__new__(cls)
        return cls.instance


if __name__ == "__main__":
    c = Command()
    t = Telegram(tuple([k for k, v in c.index.items()]))

    @t.dp.message_handler()
    async def send(message: types.Message):
        for key, value in c.index.items():
            for v in value[:-1]:
                if message.text.title() == v:
                    if datetime.datetime.now().strftime("%A") in [
                        "Friday",
                        "Saturday",
                        "Sunday",
                    ]:
                        await t.bot.send_photo(
                            message.chat.id,
                            types.InputFile.from_url(value[-1]()),
                            reply_to_message_id=message.message_id,
                            reply_markup=t.simple_keyboard(),
                        )
                        break
                    else:
                        await t.bot.send_message(
                            message.chat.id,
                            reply_to_message_id=message.message_id,
                            text="Рабочие дни: пт-вс.",
                        )

    executor.start_polling(t.dp, skip_updates=True)
