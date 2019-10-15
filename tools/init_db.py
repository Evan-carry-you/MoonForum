from apps.users.models import User

from peewee import MySQLDatabase

db = MySQLDatabase("MoonForum",
                   host="127.0.0.1",
                   port=3306,
                   user="root",
                   password=""
                   )


def init_db():
  db.create_tables([User])

if __name__ == "__main__":
  init_db()
