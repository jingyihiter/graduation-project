# -*- encoding:utf-8 -*

import sqlite3

qudb = sqlite3.connect("question.db")
cur = qudb.cursor()

try:
    cur.execute(
        "create table question(questionID int,question text,username text,groupname text, primary key(questionID))")
except Exception as e:
    pass
else:
    pass
finally:
    pass

try:
    cur.execute("create table answer(questionID int,answer text,username text,foreign key(questionID) references question(questionID))")
except Exception as e:
    pass
else:
    pass
finally:
    pass
