import pymysql

class DB:
    connection = None

    def __init__(self):
        self.conn()

    def conn(self):
        self.connection = pymysql.connect(host='localhost',
                                     user='root',
                                     password='abcd1234!',
                                     db='label_system',
                                     charset='utf8',
                                     cursorclass=pymysql.cursors.DictCursor)

    # def number_labeled(self, account):
    #     result = self.query(
    #         "SELECT count(*) as number FROM label_system.scholar_list where labeler = %s and (label = 'sybil' OR label = 'reliable')",
    #         account)
    #     if result is None:
    #         print ("Error in count labeled#!")
    #     else:
    #         return result['number']

    def number_labeled(self, account):
        result = self.query(
            "SELECT count(*) as number FROM labeled where labeler = %s",
            account)
        if result is None:
            print ("Error in count labeled#!")
        else:
            return result['number']

    def insert_user(self, email, username, password):
        self.sql_commit("INSERT INTO `label_system`.`user_list` (`email`, `name`, `password`) VALUES (%s, %s, %s)", (email, username, password))

    def get_name(self, email):
        result = self.query("SELECT name FROM label_system.user_list WHERE email = %s", email)
        if result is None:
            return False
        else:
            return result['name']

    def isNewAccount(self, email):
        result = self.query("SELECT * FROM label_system.user_list WHERE email = %s", email)
        if result is None:
            return True
        else:
            print ('Account Already Exist, Cannot Register!')
            return False

    def validate(self, email, password):
        result = self.query("SELECT password FROM label_system.user_list WHERE email = %s", email)
        if result is None:
            return False
        elif result['password'] != password:
            return False
        else:
            return True

    def query(self, sql, parameter):
        try:
            with self.connection.cursor() as cursor:
                # parameter can be tuple
                cursor.execute(sql, parameter)
                result = cursor.fetchone()
                return result
        except Exception as e:
            if e[0] == 2006 or e[0] ==2013 or 'gone away' in e.message: # OperationalError(2006, "MySQL server has gone away
                self.conn()
                return self.query(sql, parameter)
            else:
                print ('sql=%s\nexception is %s\n\n' % (sql, e))

    def query_many(self, sql, parameter):
        try:
            with self.connection.cursor() as cursor:
                # parameter can be tuple
                cursor.execute(sql, parameter)
                result = cursor.fetchall()
                return result
        except Exception as e:
            if e[0] == 2006 or e[0] ==2013 or 'gone away' in e.message: # OperationalError(2006, "MySQL server has gone away
                self.conn()
                return self.query_many(sql, parameter)
            else:
                print ('sql=%s\nexception is %s\n\n' % (sql, e))

    def sql_commit(self, sql, parameter):
        try:
            with self.connection.cursor() as cursor:
                # Create a new record
                cursor.execute(sql, parameter)
            # connection is not autocommit by default. So you must commit to save
            # your changes.
            self.connection.commit()
        except Exception as e:
            if e[0] == 2006 or e[0] ==2013 or 'gone away' in e.message: # OperationalError(2006, "MySQL server has gone away
                self.conn()
                self.sql_commit(sql, parameter)
            else:
                print ('sql=%s\nexception is %s\n\n' % (sql, e))


    def get_labeling(self, account):
        result = self.query("SELECT filename FROM label_system.scholar_list WHERE labeler=%s and label = 'labeling'",
                       account)
        if result is None:
            return None
        else:
            return result['filename']

    def update_labeled(self, filename, label, account):
        self.sql_commit("UPDATE `label_system`.`scholar_list` SET `label` = %s, `labeler` = %s WHERE `filename` = %s",
                   (label, account, filename))

    # def get_records(self, account):
    #     records = self.query_many("SELECT filename, scholarname, label FROM label_system.scholar_list WHERE labeler=%s",
    #                          account)
    #     return records

    def get_records(self, account):
        return self.query_many("SELECT filename, scholarname, label FROM labeled WHERE labeler=%s",
                                  account)

    # def nextfile(self):
    #     result = self.query(
    #         "SELECT filename FROM scholar_list WHERE label = 'unlabeled' and category = 'sybil' ORDER BY RAND() LIMIT 1",
    #         parameter=None)
    #     if result is None:
    #         return None  # todo: throw exception
    #     else:
    #         return result['filename']

    def next_file(self, account, mycursor=None):
        if mycursor is None:
            mycursor = self.query("SELECT `mycursor` FROM user_list WHERE email = %s", account)
            if mycursor is None:
                raise Exception('Get None MyCursor!')
            else:
                mycursor = mycursor['mycursor']
        entry = self.query("SELECT * from label_list WHERE `index` >= %s ORDER BY `index` LIMIT 1", int(mycursor))
        print entry['filename']
        if entry['reliable1'] is None and entry['sybil1'] is None:
            return entry['filename']
        elif entry['reliable1'] is not None and entry['sybil1'] is None:
            if entry['reliable2'] is not None:
                # skip this entry
                return self.next_file(account, mycursor + 1)
            else:
                return entry['filename']
        elif entry['reliable1'] is None and entry['sybil1'] is not None:
            if entry['sybil2'] is not None:
                # skip this entry
                return self.next_file(account, mycursor + 1)
            else:
                return entry['filename']
        else:
            if entry['reliable2'] is None and entry['sybil2'] is None:
                return entry['filename']
            elif entry['reliable2'] is not None and entry['sybil2'] is None:
                if entry['reliable3'] is not None:
                    # skip this entry
                    return self.next_file(account, mycursor + 1)
                else:
                    return entry['filename']
            elif entry['reliable2'] is None and entry['sybil2'] is not None:
                if entry['sybil3'] is not None:
                    # skip this entry
                    return self.next_file(account, mycursor + 1)
                else:
                    return entry['filename']
            elif entry['reliable3'] is None and entry['sybil3'] is None:
                return entry['filename']
            elif entry['reliable3'] is not None and entry['sybil3'] is not None:
                # skip this entry
                return self.next_file(account, mycursor + 1)
            else:
                raise Exception('Over 4 labelers!')

    def modify_labeled(self, account, filename, label):
        self.sql_commit("UPDATE labeled SET label = %s WHERE filename = %s AND labeler = %s", (label, filename, account))

    def modify_label_list(self, filename, original_label, label, accout):
        entry = self.query("SELECT * FROM label_list WHERE filename = %s", filename)
        # delete original
        moveforward = False
        i = 1
        while i < 4:
            labelstr = original_label + str(i)
            if entry[labelstr] == accout or moveforward:
                if entry[labelstr] == accout:
                    moveforward = True
                if i != 3 and entry[label+str(i+1)] is not None:
                    # move forward and cover
                    sql = "UPDATE label_list SET %s = '%s' WHERE filename='%s'" % (labelstr, entry[label+str(i+1)], filename)
                    self.sql_commit(sql, None)
                else:
                    # empty
                    sql = "UPDATE label_list SET %s = '%s' WHERE filename='%s'" % (
                    labelstr, '', filename)
                    self.sql_commit(sql, None)
                    break
            i = i + 1
        if i == 4:
            raise Exception('modify error!')
        # insert into new label slot
        # the same as store_label() except for not update cursor
        if label == 'invalid':
            self.sql_commit("UPDATE label_list SET label='invalid' WHERE filename=%s", filename)
        else:
            result = self.query("SELECT scholarname FROM scholar_list WHERE filename =%s", filename)
            if result is None:
                raise Exception('Cannot find this scholar! in db.py store_label()')
            scholarname = result['scholarname']
            self.sql_commit("INSERT INTO labeled (labeler, filename, label, scholarname) VALUES (%s, %s, %s, %s)", (account, filename, label, scholarname))
            if label == 'ambiguous':
                return
            entry = self.query("SELECT * from label_list WHERE filename = %s", filename)
            if entry is None:
                raise Exception("File cannot find!")
            else:
                for i in range(1, 4):
                    labelstr = label + str(i)
                    if entry[labelstr] is None:
                        sql = "UPDATE label_list SET %s = '%s' WHERE filename='%s'" % (labelstr, account, filename)
                        self.sql_commit(sql, None)
                        break

    def store_label(self, account, filename, label):
        # store
        if label == 'invalid':
            self.sql_commit("UPDATE label_list SET label='invalid' WHERE filename=%s", filename)
        else:
            result = self.query("SELECT scholarname FROM scholar_list WHERE filename =%s", filename)
            if result is None:
                raise Exception('Cannot find this scholar! in db.py store_label()')
            scholarname = result['scholarname']
            self.sql_commit("INSERT INTO labeled (labeler, filename, label, scholarname) VALUES (%s, %s, %s, %s)", (account, filename, label, scholarname))
            if label == 'ambiguous':
                return
            entry = self.query("SELECT * from label_list WHERE filename = %s", filename)
            if entry is None:
                raise Exception("File cannot find!")
            else:
                for i in range(1, 4):
                    labelstr = label + str(i)
                    if entry[labelstr] is None:
                        sql = "UPDATE label_list SET %s = '%s' WHERE filename='%s'" % (labelstr, account, filename)
                        self.sql_commit(sql, None)
                        break
        # update cursor
        mycursor = self.query("SELECT `mycursor` FROM user_list WHERE email = %s", account)
        if mycursor is None:
            raise Exception('Get None MyCursor!')
        else:
            mycursor = mycursor['mycursor']
        self.sql_commit("UPDATE user_list SET mycursor = %s WHERE email = %s", (mycursor + 1, account))