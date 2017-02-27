import db
import random

mydb = db.DB()

def insert_label_list():
    # entries = mydb.query_many("SELECT filename, labeler, label FROM `label_system`.`scholar_list` WHERE labeler is NOT NULL", None)
    # for entry in entries:
    #     if entry['label'] == 'reliable':
    #         mydb.sql_commit("INSERT INTO `label_system`.label_list (filename, reliable1) VALUES (%s, %s)", (entry['filename'], entry['labeler']))
    #     elif entry['label'] == 'sybil':
    #         mydb.sql_commit("INSERT INTO `label_system`.label_list (filename, sybil1) VALUES (%s, %s)", (entry['filename'], entry['labeler']))
    # entries = mydb.query_many("SELECT filename, label FROM `label_system`.`scholar_list` WHERE labeler is NULL AND (label = 'reliable' OR label = 'sybil')", None)
    # for entry in entries:
    #     if entry['label'] == 'reliable':
    #         mydb.sql_commit("INSERT INTO `label_system`.label_list (filename, reliable1) VALUES (%s, %s)", (entry['filename'], '2497913316@qq.com'))
    #     elif entry['label'] == 'sybil':
    #         mydb.sql_commit("INSERT INTO `label_system`.label_list (filename, sybil1) VALUES (%s, %s)", (entry['filename'], '2497913316@qq.com'))
    entries = mydb.query_many(
        "SELECT filename FROM `label_system`.`scholar_list` WHERE (label = 'unlabeled' OR label = 'ambiguous') and labeler is NULL and category = 'sybil'",
        None)
    for entry in entries:
        mydb.sql_commit("INSERT INTO `label_system`.label_list (filename) VALUES (%s)", entry['filename'])


def index_label_list():
    data = mydb.query_many("SELECT * from `label_system`.label_list", None)
    random.shuffle(data)
    i = 0
    for entry in data:
        mydb.sql_commit("UPDATE `label_system`.`label_list` SET `index` = %s WHERE `filename` = %s", (int(i), entry['filename']))
        i = i + 1

if __name__ == '__main__':
    insert_label_list()
    index_label_list()