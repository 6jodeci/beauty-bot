import asyncio
import logging.config

from telegram import *
from dispatcher import *


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
    logging.config.fileConfig('logging.conf')
    # Загружаем настройки логирования из файла конфигурации
    connection.close()