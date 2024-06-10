import asyncio
import logging.config

from telegram import *
from dispatcher import *


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
    # Загружаем настройки логирования из файла конфигурации
    logging.config.fileConfig('logging.conf')
    connection.close()