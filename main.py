from aiogram import executor, Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext

token_bot = '5884421857:AAGfRdo1BX6tLXSn3bCB_i6AWH_NaYbiotQ'

storage = MemoryStorage()

bot = Bot(token_bot)
dp = Dispatcher(bot=bot,
                storage=storage)

class ClientStatesGroup(StatesGroup):
    photo = State()
    desc = State()


def get_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton('Начать работу!'))

    return kb

def get_cancel() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Cancel'))


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message) -> None:
    await message.answer('Добро пожаловать',
                         reply_markup=get_keyboard())


@dp.message_handler(commands=['cancel'])
async def cmd_cancel(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        ...

    await message.reply('Отменил', reply_markup=get_keyboard())
    await state.finish()

@dp.message_handler(Text(equals='Начать работу!'), state=None)
async def start_work(message: types.Message) -> None:
    await ClientStatesGroup.photo.set()
    await message.answer('Сначала отправь нам фотографию!',
                         reply_markup=get_cancel())


@dp.message_handler(lambda message: not message.photo, state=ClientStatesGroup.photo)
async def check_photo(message: types.Message):
    return await message.reply('Это не фотография!')

@dp.message_handler(lambda message: message.photo, content_types=['photo'], state=ClientStatesGroup.photo)
async def load_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['photo'] = message.photo[0].file_id

    await ClientStatesGroup.next()
    await message.reply('А теперь отправь нам описание!')


@dp.message_handler(state=ClientStatesGroup.desc)
async def load_desc(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['desc'] = message.text

    await message.reply('Все добавлено!')

    async with state.proxy() as data:
        await bot.send_photo(chat_id=message.from_user.id,
                            photo=data['photo'],
                             caption=data['desc'])

    await state.finish()







if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)