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
    #     elif entry['label'] == 'invalid':
    #         mydb.sql_commit("INSERT INTO `label_system`.label_list (filename, label) VALUES (%s, %s)", (entry['filename'], 'invalid'))
    # entries = mydb.query_many("SELECT filename, label FROM `label_system`.`scholar_list` WHERE labeler is NULL AND (label = 'reliable' OR label = 'sybil')", None)
    # for entry in entries:
    #     if entry['label'] == 'reliable':
    #         mydb.sql_commit("INSERT INTO `label_system`.label_list (filename, reliable1) VALUES (%s, %s)", (entry['filename'], '2497913316@qq.com'))
    #     elif entry['label'] == 'sybil':
    #         mydb.sql_commit("INSERT INTO `label_system`.label_list (filename, sybil1) VALUES (%s, %s)", (entry['filename'], '2497913316@qq.com'))
    # entries = mydb.query_many(
    #     "SELECT filename, label FROM `label_system`.`scholar_list` WHERE label = 'invalid'",
    #     None)
    # for entry in entries:
    #     mydb.sql_commit("INSERT INTO `label_system`.label_list (filename, label) VALUES (%s, 'invalid')", (entry['filename']))
    entries = mydb.query_many(
        "SELECT filename FROM `label_system`.`scholar_list` WHERE (label = 'unlabeled' OR label = 'ambiguous') and labeler is NULL and category = 'reliable' LIMIT 1500",
        None)
    random.shuffle(entries)
    for entry in entries:
        mydb.sql_commit("INSERT INTO `label_system`.label_list (filename) VALUES (%s)", entry['filename'])


# def index_label_list():
#     data = mydb.query_many("SELECT * from `label_system`.label_list", None)
#     random.shuffle(data)
#     i = 0
#     for entry in data:
#         mydb.sql_commit("UPDATE `label_system`.`label_list` SET `index` = %s WHERE `filename` = %s", (int(i), entry['filename']))
#         i = i + 1

def insert_labeled():
    results = mydb.query_many("SELECT * from scholar_list where label != 'labeling' AND label != 'unlabeled'", None)
    for entry in results:
        if entry['labeler'] is None:
            labeler = '2497913316@qq.com'
        else:
            labeler = entry['labeler']
        mydb.sql_commit("INSERT INTO labeled (labeler, filename, label, scholarname) VALUES (%s, %s, %s, %s)", (labeler, entry['filename'], entry['label'], entry['scholarname']))

def modify_label_list():
    # mydb.sql_commit("DELETE FROM label_list", None)
    # mydb.sql_commit("ALTER TABLE `label_system`.`label_list` CHANGE COLUMN `index` `index` INT(11) NULL AUTO_INCREMENT ", None)
    # mydb.sql_commit("DROP TABLE userlist", None)
    insert_labeled()


def decide_final_label():
    data = mydb.query_many("SELECT * from label_list ORDER BY `index`", None)
    for entry in data:
        reliable_count = 0
        sybil_count = 0
        for i in range(1, 4):
            reliable = "reliable%s" % i
            if entry[reliable] is not None:
                reliable_count = reliable_count + 1
            sybil = "sybil%s" % i
            if entry[sybil] is not None:
                sybil_count = sybil_count + 1
        if reliable_count >= 2 or sybil_count >= 2:
            if reliable_count > sybil_count:
                mydb.sql_commit("UPDATE label_list SET label='reliable' WHERE filename = %s", entry['filename'])
            elif sybil_count > reliable_count:
                mydb.sql_commit("UPDATE label_list SET label='sybil' WHERE filename = %s", entry['filename'])
            elif sybil_count == reliable_count and sybil_count == 3:
                mydb.sql_commit("UPDATE label_list SET label='warning' WHERE filename = %s", entry['filename']) #todo: select warning out


def labeler_accuracy(account):
    accurate_nb = 0.0
    data = mydb.query_many("SELECT * FROM labeled WHERE labeler = %s", account)
    total_nb = len(data)
    print ('total_nb=%d' % total_nb)
    for entry in data:
        result = mydb.query("SELECT * FROM label_list WHERE filename = %s", entry['filename'])
        if result is None:
            print entry['filename']
            continue
            # raise Exception("Cannot find file in labeler_accuracy()!")
        if entry['label'] == result['label']:
            accurate_nb += 1
    print accurate_nb
    return accurate_nb/total_nb



if __name__ == '__main__':
    insert_label_list()
    # decide_final_label()
    print ('Accuracy of WYL is ' + str(labeler_accuracy('2497913316@qq.com')))
