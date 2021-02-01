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
        self.admin_list = [os.getenv("TELEGRAM_ADMIN")]
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

    def is_admin(self, user_id):
        self.user_id = user_id
        if self.user_id in self.admin_list:
            return True
        else:
            return False


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
                self.get_tits,
            ],
            "Попа": [
                "Попа",
                "Жопа",
                "Задница",
                "Попец",
                "Попка",
                "Жопка",
                self.get_ass,
            ],
            "Азия": [
                "Азия",
                "Азиатки",
                "Азиатку",
                "Азиатка",
                self.get_asian,
            ],
            "Рандом": [
                "Рандом",
                "Случайную",
                self.get_random,
            ],
            "Скромная": [
                "Приличная",
                "Скромная",
                "Приличную",
                "Скромную",
                self.get_decent,
            ],
        }

    def __new__(cls):
        """make singltone objects"""
        if not hasattr(cls, "instance"):
            cls.instance = super(Command, cls).__new__(cls)
        return cls.instance

    def get_tits(self):
        return self.tits_category.url

    def get_ass(self):
        return self.ass_category.url

    def get_asian(self):
        return self.asian_category.url

    def get_random(self):
        return self.random_girl_category.url

    def get_decent(self):
        return self.decent_category.url


if __name__ == "__main__":
    c = Command()
    buttons = tuple([button for button in c.index.keys()])
    t = Telegram(buttons)

    @t.dp.message_handler()
    async def send(message: types.Message):
        for value in c.index.values():
            for v in value[:-1]:
                if message.text.title() == v:
                    if datetime.datetime.now().strftime("%A") in ["Friday", "Saturday", "Sunday"] or t.is_admin(message.from_user.id):
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
                            text="У меня выходной, приходи в пятницу, субботу и воскресенье!",
                        )

    executor.start_polling(t.dp, skip_updates=True)
