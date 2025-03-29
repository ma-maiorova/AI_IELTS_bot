from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

persistent_keyboard = ReplyKeyboardMarkup(
    [
        ["/help", "/task_new_topic", "/task_same_topic", "/next_part_of_task"]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

topic_keyboard = [
    [InlineKeyboardButton("Listening", callback_data="listening")],
    [InlineKeyboardButton("Speaking", callback_data="speaking")],
    [InlineKeyboardButton("Reading", callback_data="reading")],
    [InlineKeyboardButton("Writing", callback_data="writing")]
]

inline_keyboard_next_part = InlineKeyboardMarkup([
    [InlineKeyboardButton("Следующая часть задания из топика", callback_data="next_part")]
])

inline_keyboard_end_part = InlineKeyboardMarkup([
    [InlineKeyboardButton("Новый топик", callback_data="new_topic")],
    [InlineKeyboardButton("Повторить задание", callback_data="same_topic")]
])
