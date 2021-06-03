import sqlite3

class SQLighter:

	def __init__(self, database_file):
		self.connection = sqlite3.connect(database_file)
		self.cursor = self.connection.cursor()
	
	def add_teacher(self, status, user_id, name, time, link):
		with self.connection:
			self.cursor.execute("INSERT INTO `conferences` (`time`, `link`) VALUES (?,?)", (time, link))
			conference_id = self.cursor.execute("SELECT `id` FROM `conferences` WHERE rowid = last_insert_rowid();").fetchone()[0]
			self.cursor.execute("INSERT INTO `teachers` (`id`, `name`, `status`, `conference_id`) VALUES (?,?,?,?)", (user_id,name,status,conference_id))
	
	def add_group(self, status, user_id, name):
		with self.connection:
			self.cursor.execute("INSERT INTO `groups` (`id`, `name`, `status`) VALUES (?,?,?)", (user_id,name,status))
	
	def add_queue(self, teacher_id, group_id):
		with self.connection:
			self.cursor.execute("INSERT INTO `queues` (`teacher_id`, `group_id`) VALUES (?,?)", (teacher_id,group_id))

	def user_exists(self, user_id, role):
		with self.connection:
			result = self.cursor.execute("SELECT * FROM `" + role + "` WHERE `id` = ?", (user_id,)).fetchall()
			return bool(len(result))

	def delete(self, user_id, role):
		with self.connection:
			if (role == "teachers"):
				conference_id = self.cursor.execute("SELECT `conference_id` FROM `teachers` WHERE `id` = ?", (user_id,)).fetchone()[0]
				self.cursor.execute("DELETE FROM `conferences` WHERE `id` = ?", (conference_id,))
			else:
				self.cursor.execute("DELETE FROM `queues` WHERE `group_id` = ?", (user_id,))
			self.cursor.execute("DELETE FROM `" + role + "` WHERE `id` = ?", (user_id,))
		
	def delete_queue(self, teacher_id, group_id):
		with self.connection:
			self.cursor.execute("DELETE FROM `queues` WHERE `teacher_id` = ? AND `group_id` = ?", (teacher_id,group_id))

	def get(self, to_get, from_table, known, known_value):
		with self.connection:
			return self.cursor.execute("SELECT `" + to_get + "` FROM `" + from_table + "` WHERE `" + known + "` = ?", (known_value,)).fetchone()[0]

	def get_active_teachers(self):
		with self.connection:
			return self.cursor.execute("SELECT `name` FROM `teachers` WHERE `status` = ?", (1,)).fetchall()

	def get_teachers_queue(self, teacher_id):
		with self.connection:
			return self.cursor.execute("SELECT `group_id` FROM `queues` WHERE `teacher_id` = ?", (teacher_id,)).fetchall()
	
	def get_active_teachers_queue(self, teacher_id):
		with self.connection:
			return self.cursor.execute("SELECT `group_id` FROM `queues` WHERE `teacher_id` = ? EXCEPT SELECT `id` FROM `groups` WHERE `status` = 0", (teacher_id,)).fetchall()

	def get_groups_queue(self, group_id):
		with self.connection:
			return self.cursor.execute("SELECT `teacher_id` FROM `queues` WHERE `group_id` = ?", (group_id,)).fetchall()
			
	def update(self, table, id, to_update, to_update_value):
		return self.cursor.execute("UPDATE `" + table + "` SET `" + to_update + "` = ? WHERE `id` = ?", (to_update_value, id))

	def close(self):
		"""Closing connection to DB"""
		self.connection.close()