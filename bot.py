import config
import logging
import os
from aiogram import Bot, Dispatcher, executor, types, utils
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlighter import SQLighter

logging.basicConfig(level=logging.INFO)

bot=Bot(token=config.API_TOKEN)
dp=Dispatcher(bot)

db = SQLighter("db.db")

@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):

	await message.answer("Вітаю, " + message.from_user.first_name + "!\nДля того, щоб почати роботу, зареєструйтеся:\n/teacher - для реєстрації як учитель\n/group - для реєстрації групи \n/help - для перегляду всіх команд.")

@dp.message_handler(commands=['help'])
async def help_info(message: types.Message):
	await message.answer("Нижче подано список усіх наявних команд для кожної ролі.\n\nУчитель:\n/teacher - реєстрація/зміна ролі на вчителя\n"+
	"/me - перегляд інформації про Вас\n" +
	"/name - зміна імені, що відображатиметься для груп\n/status - зміна Вашого статусу (прийом активний - Ви готові приймати групи, "+
	"прийому немає - черга до Вас очищується, записатися в неї неможливо)\n/time - зміна орієнтовного часу прийому однієї групи\n"+
	"/queue - перегляд черги до Вас\n/next - створення запрошення для Вас і першої групи в черзі на конференцію\n" + 
	"/link - перегляд/зміна посилання на конференцію \n\nГрупа:\n"+
	"/group - реєстрація/зміна ролі на групу\n" + 
	"/me - перегляд інформації про групу" +
	"/name - зміна назви групи, що відображатиметься для вчителів\n"+ 
	"/status - зміна статусу групи (активний - ви отримаєте запрошення на конференцію в порядку черги, неактивний - ви залишаєтеся в черзі, але не отримаєте запрошення)\n" + 
	"/enter - запис у чергу до вчителів\n/exit - вихід із черги\n"+"/queue - перегляд вашої позиції в черзі до записаних учителів")

@dp.message_handler(commands = ['me'])
async def set_name(message: types.Message):
	status = {
			0 : "активний",
			1 : "неактивний"
		}
	if(db.user_exists(message.chat.id, "teachers")):
		await message.answer("Роль: учитель" +
			"\nІм'я: " + str(db.get("name", "teachers", "id", message.chat.id)) +  
			"\nСтатус: " + status[db.get("status", "teachers", "id", message.chat.id)] +
			"\nЧас прийому: " + str(db.get("time", "conferences", "id", db.get("conference_id", "teachers", "id", message.chat.id))) + " хв." + 
			"\nПосилання на конференцію: " + str(db.get("link", "conferences", "id", db.get("conference_id", "teachers", "id", message.chat.id))))
	elif(db.user_exists(message.chat.id, "groups")):
		await message.answer("Поль: група" +
			"\nНазва: " + str(db.get("name", "groups", "id", message.chat.id)) +  
			"\nСтатус: " + status[db.get("status", "groups", "id", message.chat.id)])
	else:
		await message.answer("Для використання цієї команди зареєструйтеся як група: /group, або вчитель: /teacher")

@dp.message_handler(commands = ['teacher'])
async def add_teacher(message: types.Message):
	status = {
			0 : "Прийому немає",
			1 : "Прийом активний"
		}
	if (db.user_exists(message.chat.id, "teachers")):
		await message.answer("Ви уже зареєстровані як учитель з іменем " + str(db.get("name", "teachers", "id", message.chat.id)) + 
		"\n(Для зміни - команда /name)\n" + 
		"Ваш статус: " + status[db.get("status", "teachers", "id", message.chat.id)] +
		"\n(Для зміни - команда /status)\n" +
		"Час прийому: " + str(db.get("time", "conferences", "id", db.get("conference_id", "teachers", "id", message.chat.id))) + " хв." +
		"\n(Для зміни - команда /time)" + 
		"\nДля перегляду посилання на конференцію та її зміни - команда /link" + 
		"\nДля того, щоб переглянути чергу до Вас - /queue\nДля початку прийому першої групи в черзі - /next")

	elif (db.user_exists(message.chat.id, "groups")):
		db.delete(message.chat.id, "groups")
		
		if(os.path.getsize("links.txt")!=0):
			with open('links.txt', 'r') as fin:
				links = fin.read().splitlines(True)
			with open('links.txt', 'w') as fout:
				fout.writelines(links[1:])
			link = links[0]
		else:
			link = ""
			
		db.add_teacher(0, message.chat.id, message.from_user.first_name, 15, link)
		await message.answer("Ви успішно змінили свою роль на учителя\n" + 
		"Ваше ім'я - " + str(db.get("name", "teachers", "id", message.chat.id)) + 
		"\n(Для зміни - команда /name)\n" + 
		"Ваш статус: " + status[db.get("status", "teachers", "id", message.chat.id)] +
		"\n(Для зміни - команда /status)\n" +
		"Час прийому: " + str(db.get("time", "conferences", "id", db.get("conference_id", "teachers", "id", message.chat.id))) + " хв." + 
		"\n(Для зміни - команда /time)" +
		"\nДля перегляду посилання на конференцію та її зміни - команда /link" + 
		"\nДля того, щоб переглянути чергу до Вас - /queue\nДля початку прийому першої групи в черзі - /next")

	else:
		if(os.path.getsize("links.txt")!=0):
			with open('links.txt', 'r') as fin:
				links = fin.read().splitlines(True)
			with open('links.txt', 'w') as fout:
				fout.writelines(links[1:])
			link = links[0]
		else:
			link = ""
		db.add_teacher(0, message.chat.id, message.from_user.first_name, 15, link)
		await message.answer("Ви успішно зареструвалися як учитель\n" + 
		"Ваше ім'я - " + str(db.get("name", "teachers", "id", message.chat.id)) +
		"\n(Для зміни команда /name)\n" + 
		"Ваш статус: " + status[db.get("status", "teachers", "id", message.chat.id)] +
		"\n(Для зміни команда /status)\n" +
		"Час прийому: " + str(db.get("time", "conferences", "id", db.get("conference_id", "teachers", "id", message.chat.id))) + " хв." +
		"\n(Для зміни команда /time)" +
		"\nДля перегляду посилання на конференцію та її зміни - команда /link" + 
		"\nДля того, щоб переглянути чергу до Вас - /queue\nДля початку прийому першої групи в черзі - /next")

@dp.message_handler(commands = ['group'])
async def add_group(message: types.Message):

	if (db.user_exists(message.chat.id, "groups")):
		await message.answer("Ви уже зареєстровані як група з назвою " + str(db.get("name", "groups", "id", message.chat.id)) + 
		"\n(Для зміни команда /name)\n")

	elif (db.user_exists(message.chat.id, "teachers")):
		
		db.delete(message.chat.id, "teachers")

		db.add_group(1, message.chat.id, message.from_user.first_name)
		await message.answer("Ви успішно змінили свою роль на групу\n" + 
		"Ваша назва - " + str(db.get("name", "groups", "id", message.chat.id)) + 
		"\n(Для зміни команда /name)\nВаш статус - \"активний\"\n(Для зміни - команда /status)\nДля запису в чергу - /enter")

	else:
		db.add_group(1, message.chat.id, message.from_user.first_name)
		await message.answer("Ви успішно зареструвалися як група\n" + 
		"Ваша назва - " + str(db.get("name", "groups", "id", message.chat.id)) + 
		"\n(Для зміни команда /name)\nВаш статус - \"активний\"\n(Для зміни - команда /status)\nДля запису в чергу - /enter")

@dp.message_handler(commands = ['name'])
async def set_name(message: types.Message):
	name = message.text.split(" ",1)
	if(db.user_exists(message.chat.id, "teachers")):
		role = "teachers"
	elif(db.user_exists(message.chat.id, "groups")):
		role = "groups"
	else:
		await message.answer("Для використання цієї команди зареєструйтеся як група: /group, або вчитель: /teacher")
		return

	if (len(name) < 2):
		if (role == "groups"):
			await message.answer("Для зміни назви групи укажіть її у наступному вигляді:\n" +
			"/name _назва групи_", parse_mode = "Markdown")
		else:
			await message.answer("Для зміни відображуваного імені укажіть його у наступному вигляді:\n" +
			"/name _моє ім'я_", parse_mode = "Markdown")
	else:
		if (role == "groups"):
			db.update("groups", message.chat.id, "name", name[1])
			await message.answer("Зміни збережено.\nТепер назва групи - " + str(db.get("name", role, "id", message.chat.id)))
		else:
			db.update("teachers", message.chat.id, "name", name[1])
			await message.answer("Зміни збережено.\nТепер Ваше ім'я - " + str(db.get("name", role, "id", message.chat.id)))

@dp.message_handler(commands = ['status'])
async def change_status(message: types.Message):
	if(db.user_exists(message.chat.id, "groups")):
		current_status = db.get("status", "groups", "id", message.chat.id)
		if current_status == 1:
			db.update("groups", message.chat.id, "status", 0)
			await message.answer("Ваш статус змінено на \"неактивний\". Ви не отримаєте запрошення на конференцію, поки не зміните його на протилежний (команда /status).")
		else:

			for teacher_id in db.get_groups_queue(message.chat.id):
				if len(db.get_active_teachers_queue(teacher_id[0]))==0:
					await bot.send_message(teacher_id[0], "З'явилася активна група в черзі.\nДля того, щоб зв'язатися з першою готовою групою - /next (Вам, а також групі прийде посилання на конференцію)")

			db.update("groups", message.chat.id, "status", 1)
			await message.answer("Ваш статус змінено на \"активний\". Ви отримаєте запрошення на конференцію в порядку своєї черги.")
		db.get("status", "groups", "id", message.chat.id)
	elif(db.user_exists(message.chat.id, "teachers")):
		current_status = db.get("status", "teachers", "id", message.chat.id)
		if current_status == 1:
			if (len(db.get_teachers_queue(message.chat.id))!=0):
				confirm_buttons = InlineKeyboardMarkup()
				confirm_buttons.add(InlineKeyboardButton("Так", callback_data = "/confirm1"))
				confirm_buttons.add(InlineKeyboardButton("Ні", callback_data = "/confirm0"))
				await message.answer("У черзі ще залишилися неприйняті групи. Ви впевнені, що хочете завершити прийом? (Черга буде очищена)", reply_markup = confirm_buttons)
			else:
				db.update("teachers", message.chat.id, "status", 0)
				await message.answer("Ваш статус змінено на \"прийому немає\". Для того, щоб почати прийом знову - команда /status")
		else:
			db.update("teachers", message.chat.id, "status", 1)
			await message.answer("Ваш статус змінено на \"прийом активний\". Тепер групи зможуть записатися до Вас на прийом.\nДля перегляду черги на даний момент - /queue\nЯк тільки в черзі з'явиться перша група - Ви отримаєте відповідне повідомлення.\nДля того, щоб зв'язатися з першою готовою групою - /next (Вам, а також групі прийде посилання на конференцію)\nДля того, щоб завершити прийом - команда /status")
		db.get("status", "teachers", "id", message.chat.id)

@dp.callback_query_handler(lambda c: c.data and c.data.startswith("/confirm"))
async def clean_queue(callback_query: types.CallbackQuery):
	answer  = callback_query.data[8:]
	if (not int(answer)):
		await callback_query.message.delete()
		await bot.send_message(callback_query.message.chat.id, "Для перегляду черги на даний момент - /queue")
	else:
		await callback_query.message.delete()
		for group_id in db.get_teachers_queue(callback_query.message.chat.id):
			db.delete_queue(callback_query.message.chat.id, group_id[0])
			await bot.send_message(group_id[0], "Учитель " + db.get("name", "teachers", "id", callback_query.message.chat.id) + " завершив прийом. Для перегляду активних учителів - команда /enter")
		db.update("teachers", callback_query.message.chat.id, "status", 0)
		await bot.send_message(callback_query.message.chat.id, "Ваш статус змінено на \"прийому немає\". Для того, щоб почати прийом знову - команда /status")
		db.get("status", "teachers", "id", callback_query.message.chat.id)

@dp.message_handler(commands = ['queue'])
async def send_queue(message: types.Message):
	
	status = {
			1 : "🟢",
			0 : "🔴"
		}
	if (db.user_exists(message.chat.id, "teachers")):
		queue_id = db.get_teachers_queue(message.chat.id)
		if len(queue_id)==0:
			await message.answer("На даний момент черга відсутня.")
			return
		queue = ""
		for id in queue_id:
			queue += db.get("name", "groups", "id", id[0]) + " " + status[db.get("status", "groups", "id", id[0])] + "\n"
		await message.answer("Черга до Вас:\n\n" + queue + "\nАктивна група - 🟢, неактивна - 🔴\nДля того, щоб зв'язатися з першою готовою групою - /next (Вам, а також групі прийде посилання на конференцію)")
	elif (db.user_exists(message.chat.id, "groups")):
		if len(db.get_groups_queue(message.chat.id))==0:
			await message.answer("Ви не знаходитеся в черзі.\nДля того, щоб записатися до вчителя, команда /enter")
			return
		msg = ""
		for teacher_id in db.get_groups_queue(message.chat.id):
			position = find_position_in_queue(message.chat.id, teacher_id[0])
			time = position * db.get("time", "conferences", "id", db.get("conference_id", "teachers", "id", teacher_id[0]))
			msg += "Ваша позиція в черзі до вчителя " + db.get("name", "teachers", "id", teacher_id[0]) + " - " + str(position) + " (~" + str(time) + " хв.)\n"
		await message.answer(msg)
	else:
		await message.answer("Для використання цієї команди зареєструйтеся як група: /group, або вчитель: /teacher")

	if (len(str(db.get("link", "conferences", "id", db.get("conference_id", "teachers", "id", message.chat.id))))==0):
		await message.answer("У Вас відсутнє посилання на конференцію. Ви не зможете почати прийом. Для його встановлення - команда /link")

def find_position_in_queue(group_id, teacher_id):
	position = 1
	for g_id in db.get_teachers_queue(teacher_id):
		if g_id[0] == group_id:
			return position
		position += 1

@dp.message_handler(commands = ['enter'])
async def join_queue(message: types.Message):
	if(db.user_exists(message.chat.id, "teachers")):
		await message.answer("Команда доступна тільки групам.")
		return
	elif(not db.user_exists(message.chat.id, "groups")):
		await message.answer("Для використання цієї команди зареєструйтеся як група: /group")
		return
	teacher_name_buttons = InlineKeyboardMarkup()
	if (len(db.get_active_teachers()) == 0):
		await message.answer("Наразі відсутні активні вчителі. Спробуйте пізніше.")
		return

	for name in db.get_active_teachers():
		teacher_name_buttons.add(InlineKeyboardButton(str(name[0]), callback_data = "/enter" + str(name[0])))

	await message.answer("Список активних учителів подано нижче.\nНатисніть на одну з кнопок, щоб записатися.", reply_markup = teacher_name_buttons)

@dp.callback_query_handler(lambda c: c.data and c.data.startswith("/enter"))
async def enter_queue(callback_query: types.CallbackQuery):

	name  = callback_query.data[6:]

	teacher_id = db.get("id","teachers", "name", name)

	if (db.get("status", "teachers", "id", teacher_id) == 0):
		await bot.answer_callback_query(callback_query.id)
		await bot.send_message(callback_query.message.chat.id, "Учитель " + name + " уже завершив прийом. Для перегляду активних учителів - команда /enter")
		return
	group_id = callback_query.message.chat.id
	position = 1
	
	for id in db.get_teachers_queue(teacher_id):
		if id[0] == group_id:
			await bot.answer_callback_query(callback_query.id)
			await bot.send_message(callback_query.message.chat.id, "Ви уже записані до цього вчителя\nВаша позиція в черзі - " + str(position) + "\nДля виходу з черги - /exit")
			return
		position +=1

	db.add_queue(teacher_id, group_id)
	db.update("groups", callback_query.message.chat.id, "status", 1)
	db.get("status", "groups", "id", callback_query.message.chat.id)
	position = len(db.get_teachers_queue(teacher_id))

	if (position == 1):
		await bot.send_message(teacher_id, "У Вас з'явилася група в черзі. Для перегляду - команда /queue\nДля того, щоб зв'язатися з першою готовою групою - /next (Вам, а також групі прийде посилання на конференцію)")
	elif (len(db.get_active_teachers_queue(teacher_id)) == 1):
		await bot.send_message(teacher_id, "З'явилася активна група в черзі.\nДля того, щоб зв'язатися з першою готовою групою - /next (Вам, а також групі прийде посилання на конференцію)")
	
	time = position * db.get("time", "conferences", "id", db.get("conference_id", "teachers", "id", teacher_id))

	await bot.answer_callback_query(callback_query.id)
	await bot.send_message(callback_query.message.chat.id, "Ви успішно записалися до вчителя " + name + ".\nВаша позиція в черзі: " + str(position) + "\nПриблизний час очікування: " + str(time) + " хв.\nВаш статус автоматично змінено на \"активний\" (для зміни - /status)." + "\nДля виходу з черги - /exit")

@dp.message_handler(commands = ['exit'])
async def exit_queue(message: types.Message):
	if(db.user_exists(message.chat.id, "teachers")):
		await message.answer("Команда доступна тільки групам.")
		return
	elif(not db.user_exists(message.chat.id, "groups")):
		await message.answer("Для використання цієї команди зареєструйтеся як група: /group")
		return
	teacher_name_buttons = InlineKeyboardMarkup()
	entered_queues = db.get_groups_queue(message.chat.id)
	if (len(entered_queues) == 0):
		await message.answer("Ви ще не записані в чергу.\nДля перегляду активних учителів /enter")
		return

	for id in entered_queues:
		name = db.get("name", "teachers", "id", id[0])
		teacher_name_buttons.add(InlineKeyboardButton(name, callback_data = "/exit" + name))

	await message.answer("Список активних черг подано нижче.\nНатисніть на одну з кнопок, щоб покинути її.", reply_markup = teacher_name_buttons)

@dp.callback_query_handler(lambda c: c.data and c.data.startswith("/exit"))
async def exit_queue(callback_query: types.CallbackQuery):
	name = callback_query.data[5:]
	teacher_id = db.get("id","teachers", "name", name)
	queue_exists = False
	for id in db.get_groups_queue(callback_query.message.chat.id):
		if id[0] == teacher_id:
			queue_exists = True
	if queue_exists == False:
		await bot.answer_callback_query(callback_query.id)
		await bot.send_message(callback_query.message.chat.id, "Ви вже покинули цю чергу.")
		return
	
	group_id = callback_query.message.chat.id

	db.delete_queue(teacher_id, group_id)

	await bot.answer_callback_query(callback_query.id)
	await bot.send_message(callback_query.message.chat.id, "Успішно. Ви покинули чергу вчителя " + name + ".")

@dp.message_handler(commands = ['next'])
async def next_queue(message: types.Message):
	
	if(db.user_exists(message.chat.id, "groups")):
		await message.answer("Команда доступна тільки вчителям.")
		return

	elif(not db.user_exists(message.chat.id, "teachers")):
		await message.answer("Для використання цієї команди зареєструйтеся як учитель: /teacher")
		return

	if (len(db.get_teachers_queue(message.chat.id))==0):
		await message.answer("Черга відсутня. Як тільки в неї запишеться група - Ви отримаєте відповідне повідомлення.")
		if (len(str(db.get("link", "conferences", "id", db.get("conference_id", "teachers", "id", message.chat.id))))==0):
			await message.answer("У Вас відсутнє посилання на конференцію. Ви не зможете почати прийом. Для його встановлення - команда /link")
		return

	if (len(str(db.get("link", "conferences", "id", db.get("conference_id", "teachers", "id", message.chat.id))))==0):
		await message.answer("Ви не можете почати прийом, адже у Вас відсутнє посилання на конференцію. Для його встановлення - команда /link")
		return
	queue = db.get_teachers_queue(message.chat.id)
	for id in queue:
		if (not db.get("status", "groups", "id", id[0])):
			if (not len(db.get_active_teachers_queue(message.chat.id)) == 0):
				await bot.send_message(id[0], "Ви пропустили свою чергу до вчителя " + db.get("name", "teachers", "id", message.chat.id) + ", адже ваш статус - \"неактивний\".\nЯкщо ви готові - змініть його командою /status і очікуйте посилання на конференцію в порядку черги.")
		else:

			time = db.get("time", "conferences", "id", db.get("conference_id", "teachers", "id", message.from_user.id))
			conf_id = db.get("conference_id", "teachers", "id", message.chat.id)
			await message.answer("Посилання на конференцію з групою " + db.get("name", "groups", "id", id[0]) + ": \n" + db.get("link", "conferences", "id", conf_id))
			await bot.send_message(id[0], "Посилання на конференцію з учителем " + db.get("name", "teachers", "id", message.chat.id) + ": " +  db.get("link", "conferences", "id", conf_id) + 
			"\nВаш статус автоматично змінено на \"неактивний\". Для зміни - команда /status")
			db.delete_queue(message.chat.id, id[0])

			return
	
	await message.answer("На даний момент у черзі немає готових груп. Зачекайте, або завершіть прийом (/status).\nЯк тільки з'явиться готова група - Ви отримаєте відповідне повідомлення.")
	for id in queue:
		await bot.send_message(id[0], "Наразі в черзі до вчителя " + db.get("name", "teachers", "id", message.chat.id) + " залишилися лише неактивні групи. Якщо ви вже готові - змініть свій статус /status")

@dp.message_handler(commands=['time'])
async def set_time(message: types.Message):
	if (db.user_exists(message.chat.id, "groups")):
		await message.answer("Команда доступна тільки вчителям.")
		return
	elif (not db.user_exists(message.chat.id, "teachers")):
		await message.answer("Для використання цієї команди зареєструйтеся як учитель: /teacher")
		return
	time =  message.text.split(" ",1)
	if(len(time) < 2):
		await message.answer("Для зміни часу прийому укажіть його у хвилинах цілим додатнім числом після команди, наприклад:\n" +
		"/time _10_", parse_mode = "Markdown")
	else:
		if (not time[1].isdigit() or time[1]=='0'):
			await message.answer("Час прийому має бути цілим додатнім числом.")
			return
		conference_id = db.get("conference_id", "teachers", "id", message.chat.id)
		db.update("conferences", conference_id, "time", time[1])
		await message.answer("Успішно змінено. Час прийому: " + str(db.get("time", "conferences", "id", conference_id)) + " хв.")

@dp.message_handler(commands=['link'])
async def set_time(message: types.Message):
	if (db.user_exists(message.chat.id, "groups")):
		await message.answer("Команда доступна тільки вчителям.")
		return
	elif (not db.user_exists(message.chat.id, "teachers")):
		await message.answer("Для використання цієї команди зареєструйтеся як учитель: /teacher")
		return
	link =  message.text.split(" ",1)
	if(len(link) < 2):
		curr_link = str(db.get("link", "conferences", "id", db.get("conference_id", "teachers", "id", message.chat.id)))
		if(len(curr_link)==0):
			await message.answer("На даний момент посилання не задано.\nДля встановлення посилання на конференцію укажіть його після команди, наприклад:\n" + 
			"/link _https://meet.google.com/..._", parse_mode = "Markdown")
		else:
			await message.answer("Ваше поточне посилання на конференцію: " + curr_link + "\nДля зміни укажіть нове після команди, наприклад:\n" + 
			"/link _https://meet.google.com/..._", parse_mode = "Markdown")
	else:
		curr_link = str(db.get("link", "conferences", "id", db.get("conference_id", "teachers", "id", message.chat.id)))
		conference_id = db.get("conference_id", "teachers", "id", message.chat.id)
		db.update("conferences", conference_id, "link", link[1])
		if(len(curr_link)==0):
			await message.answer("Успішно. Поточне посилання на конференцію: " + str(db.get("link", "conferences", "id", conference_id)))
		else:
			await message.answer("Ваше минуле посилання " + curr_link + " успішно змінене.\nПоточне посилання на конференцію: " + str(db.get("link", "conferences", "id", conference_id)))

if __name__ == '__main__':

	executor.start_polling(dp, skip_updates=True)