import os

print("TEST ENV:", os.getenv("GOOGLE_CREDENTIALS"))
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import gspread
from oauth2client.service_account import ServiceAccountCredentials

TOKEN = "8743669525:AAHLZkAnLV1ZKDhqXmmqO7d5SgLUCvhqV5o"
GROUP_ID = -1002235821304

TOPICS = {
    1: 1268,
    2: 1270,
    3: 1272
}
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)

# 🔹 Google Sheets
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

import os
import json
from oauth2client.service_account import ServiceAccountCredentials

creds_json = os.getenv("GOOGLE_CREDENTIALS")

if not creds_json:
    raise Exception("GOOGLE_CREDENTIALS is EMPTY ❌")

try:
    creds_dict = json.loads(creds_json)
except Exception as e:
    raise Exception(f"JSON ERROR ❌: {e}")
client = gspread.authorize(creds)
sheet = client.open("children_data").sheet1
orders_sheet=client.open("orders_data").sheet1
def get_invoice():
    records = orders_sheet.get_all_records()
    if not records:
        return 1001
    return int(records[-1]["Invoice_ID"]) + 1

# 🔥 جميع الكروبات + القصص (كما هي)
STORIES = {
    "قادة المستقبل": [
        ("بطاطا الكنبة", 15000),
        ("البيضة الجيدة", 15000),
        ("أنا وخوف", 14000)
    ],
    "أبطال المعرفة": [
        ("مشوار", 10000),
        ("الصقور في المطار", 12500),
        ("هيا بدلتي الخارقة", 14000)
    ],
    "عقول واعدة": [
        ("جسمي يخبرني", 11000),
        ("الكل ينتظر دوره", 12500),
        ("ماذا لو", 11000)
    ],
    "نوارس العقل": [
        ("شعري منكوش أحمر", 11000),
        ("من أكل قميصي", 11000),
        ("صديقي رجل آلي", 11000)
    ],
    "زهور الإبداع": [
        ("شعري منكوش أحمر", 11000),
        ("من أكل قميصي", 11000),
        ("صديقي رجل آلي", 11000)
    ],
    "النجوم المتألقة": [
        ("الا اف", 12000),
        ("مع بعضنا", 11000),
        ("أخيرا نام غزيلان", 15000)
    ],
    "براعم التميز": [
        ("ادم ومشمش اصوات الحيوانات", 9000),
        ("ادم ومشمش الحيوانات", 9000),
        ("ادم ومشمش الاشكال", 9000)
    ],
    "الأمل الكبير": [
        ("حوته تسبح", 17000),
        ("كناري يطير", 17000),
        ("هوتوت يقفز", 17000)
    ]
}

# 🔥 الحالة
user_state = {}

# 🔥 البداية (كما طلبتي)
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(
        "أهلاً وسهلاً بكِ 🌸\n"
        "نرحّب بكِ في بوت حجز القصص الخاص بنادي القارئ المبدع المستوى الاول لعام ٢٠٢٦ للأطفال 📚✨\n\n"
        "هذا البوت مخصص لتثبيت حجز طلبكِ للقصص، وتنظيم الطلبات بكل سهولة وسرعة 💡\n"
        "من خلاله يمكنكِ تسجيل طلبكِ وتثبيته بشكل آلي\n\n"
        "يرجى اتباع الخطوات وإدخال المعلومات المطلوبة بدقة لضمان تثبيت الحجز بشكل صحيح ✅\n\n"
        "نحن سعداء بانضمامكِ إلى النادي، ونتمنى لطفلكِ تجربة ممتعة ومفيدة 💛\n\n"
        "📱 يرجى إدخال رقم الهاتف المسجل:"
    )

# 🔥 إدخال الرقم
@dp.message_handler(lambda m: m.from_user.id not in user_state)
async def get_phone(message: types.Message):
    phone = message.text.strip()

    data = sheet.get_all_records()
    children = [row for row in data if str(row['Phone']) == phone]

    if not children:
        await message.answer("❌ الرقم غير موجود")
        return

    user_id = message.from_user.id

    user_state[user_id] = {
        "children": children,
        "current": 0,
        "orders": [],
        "main_phone": phone
    }

    await ask_type(message, user_id)

# 🔹 عرض الطفل
async def ask_type(message, user_id):
    state = user_state[user_id]

    if state["current"] >= len(state["children"]):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("نعم", callback_data="extra_yes"))
        keyboard.add(InlineKeyboardButton("لا", callback_data="extra_no"))

        await message.answer(
            "هل تريدين إضافة قصص خارج النادي؟\nليتم التواصل معكم من قبل موظفة الحجوزات",
            reply_markup=keyboard
        )
        return

    child = state["children"][state["current"]]

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("📚 حجز قصص", callback_data="stories"))
    keyboard.add(InlineKeyboardButton("✨ أنشطة فقط", callback_data="activity"))

    await message.answer(
        f"👶 {child['Child_Name']} ({child['Birth_Year']})\n"
        f"📌 {child['Group']}\n\nاختاري نوع الطلب:",
        reply_markup=keyboard
    )

# 🔹 اختيار النوع
@dp.callback_query_handler(lambda c: c.data in ["stories", "activity"])
async def choose_type(callback: types.CallbackQuery):
    await callback.answer()

    user_id = callback.from_user.id
    state = user_state[user_id]
    child = state["children"][state["current"]]

    if callback.data == "activity":
        state["orders"].append({
            "child": child['Child_Name'],
            "type": "أنشطة فقط",
            "items": [],
            "total": 0
        })

        state["current"] += 1
        await ask_type(callback.message, user_id)
        return

    state["selected"] = []
    await show_stories(callback.message, user_id)

# 🔹 عرض القصص
async def show_stories(message, user_id):
    state = user_state[user_id]
    child = state["children"][state["current"]]

    group = child['Group'].strip()

    stories = None
    for key in STORIES:
        if key.strip() == group:
            stories = STORIES[key]
            break

    if not stories:
        await message.answer(f"❌ لا توجد قصص لهذا الكروب: {group}")
        return

    keyboard = InlineKeyboardMarkup()

    for name, price in stories:
        mark = "✅" if name in state["selected"] else "⬜"
        keyboard.add(
            InlineKeyboardButton(
                text=f"{mark} {name} - {price}",
                callback_data=f"toggle_{name}"
            )
        )

    keyboard.add(InlineKeyboardButton("✔ تم", callback_data="done"))

    await message.answer("📚 اختاري القصص:", reply_markup=keyboard)

# 🔹 اختيار متعدد
@dp.callback_query_handler(lambda c: c.data.startswith("toggle_"))
async def toggle(callback: types.CallbackQuery):
    await callback.answer()

    user_id = callback.from_user.id
    state = user_state[user_id]

    story = callback.data.replace("toggle_", "")

    if story in state["selected"]:
        state["selected"].remove(story)
    else:
        state["selected"].append(story)

    await show_stories(callback.message, user_id)

# 🔹 تأكيد القصص
@dp.callback_query_handler(lambda c: c.data == "done")
async def done(callback: types.CallbackQuery):
    await callback.answer()

    user_id = callback.from_user.id
    state = user_state[user_id]
    child = state["children"][state["current"]]

    group = child['Group'].strip()

    stories = None
    for key in STORIES:
        if key.strip() == group:
            stories = STORIES[key]
            break

    selected_items = []
    total = 0

    for name, price in stories:
        if name in state["selected"]:
            selected_items.append(name)
            total += price

    if not selected_items:
        await callback.message.answer("❗ اختاري قصة واحدة على الأقل")
        return

    state["orders"].append({
        "child": child['Child_Name'],
        "type": "قصص",
        "items": selected_items,
        "total": total
    })

    state["current"] += 1
    await ask_type(callback.message, user_id)

# 🔹 القصص الخارجية
@dp.callback_query_handler(lambda c: c.data in ["extra_yes", "extra_no"])
async def extra_choice(callback: types.CallbackQuery):
    await callback.answer()

    user_id = callback.from_user.id
    state = user_state[user_id]

    state["extra"] = True if callback.data == "extra_yes" else False
    state["step"] = "address"

    await callback.message.answer("📍 أدخلي العنوان:")

# 🔹 العنوان
@dp.message_handler(lambda m: user_state.get(m.from_user.id, {}).get("step") == "address")
async def get_address(message: types.Message):
    user_id = message.from_user.id
    user_state[user_id]["address"] = message.text
    user_state[user_id]["step"] = "shipping"

    await message.answer("📞 أدخلي رقم هاتف الشحن:")

# 🔹 رقم الشحن + الفاتورة
@dp.message_handler(lambda m: user_state.get(m.from_user.id, {}).get("step") == "shipping")
async def get_phone_shipping(message: types.Message):
    user_id = message.from_user.id
    state = user_state[user_id]

    state["shipping_phone"] = message.text
    invoice = get_invoice()
    state["invoice"]=invoice
    total = sum(o["total"] for o in state["orders"]) + 5000
    date_now = datetime.now().strftime("%Y-%m-%d")

    text = f"🧾 رقم الفاتورة:{invoice}\n\n"
    text += f"📅 التاريخ: {date_now}\n"
    text += f"📱 الرقم الأساسي: {state['main_phone']}\n"
    text += f"📞 رقم الشحن: {state['shipping_phone']}\n"
    text += f"📍 العنوان: {state['address']}\n\n"

    for o in state["orders"]:
        text += f"👶 {o['child']} - {o['type']}\n"
        for item in o["items"]:
            text += f"   - {item}\n"
        text += f"💰 {o['total']}\n\n"

    if state.get("extra"):
        text += "🟡 طلب قصص خارج النادي (سيتم التواصل)\n\n"

    text += f"🚚 التوصيل: 5000\n"
    text += f"💵 المجموع: {total}\n\n"
    text += "هل تأكيد الطلب؟"

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("✅ تأكيد", callback_data="confirm"))

    await message.answer(text, reply_markup=keyboard)

# 🔹 تأكيد
@dp.callback_query_handler(lambda c: c.data == "confirm")
async def confirm(callback: types.CallbackQuery):
    await callback.answer()

    user_id = callback.from_user.id
    state = user_state[user_id]

    await callback.message.answer("🎉 تم استلام الطلب بنجاح")

    orders_sheet.append_row([
        state["invoice"],
        state["main_phone"],
        datetime.now().strftime("%Y-%m-%d"),
        callback.from_user.id
    ])

    # 🔥 من هنا يبدأ النص (كلشي مزاح بمسافة وحدة)
    children_count = len(state["children"])
    thread_id = TOPICS[children_count]

    text = "🧾 طلب جديد\n\n"

    text += f"🆔 رقم الفاتورة: {state['invoice']}\n"
    text += f"📱 الهاتف: {state['main_phone']}\n\n"

    for o in state["orders"]:
        text += f"👶 {o['child']} - {o['type']}\n"

        if o["items"]:
            for item in o["items"]:
                text += f"   - {item}\n"

        text += f"💰 {o['total']}\n\n"

    if state.get("extra"):
        text += "🟡 يوجد طلب قصص خارج النادي\n\n"

    text += f"📍 العنوان: {state['address']}\n"
    text += f"📞 هاتف الشحن: {state['shipping_phone']}\n\n"

    total = sum(o["total"] for o in state["orders"]) + 5000

    text += f"🚚 التوصيل: 5000\n"
    text += f"💵 المجموع: {total}\n"

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("📦 تم التجهيز", callback_data="ready"))
    keyboard.add(InlineKeyboardButton("🚚 تم الشحن", callback_data="shipped"))

    await bot.send_message(
        chat_id=GROUP_ID,
        text=text,
        message_thread_id=thread_id,
        reply_markup=keyboard
    )
@dp.callback_query_handler(lambda c: c.data.startswith(("ready|", "shipped|")))
async def update_status(callback: types.CallbackQuery):
    await callback.answer()

    data = callback.data.split("|")
    action = data[0]
    invoice = data[1]

    if action == "ready":
        await callback.message.answer(f"📦 تم تجهيز الطلب رقم {invoice}")

    elif action == "shipped":
        await callback.message.answer(f"🚚 تم شحن الطلب رقم {invoice}")
# 🔹 تشغيل
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
