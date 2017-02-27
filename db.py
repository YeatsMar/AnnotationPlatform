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

    def number_labeled(self, account):
        result = self.query(
            "SELECT count(*) as number FROM label_system.scholar_list where labeler = %s and (label = 'sybil' OR label = 'reliable')",
            account)
        if result is None:
            print ("Error in count labeled#!")
        else:
            return result['number']

    def insert_user(self, email, username, password):
        self.sql_commit("INSERT INTO `label_system`.`userlist` (`email`, `name`, `password`) VALUES (%s, %s, %s)", (email, username, password))

    def get_name(self, email):
        result = self.query("SELECT name FROM label_system.userlist WHERE email = %s", email)
        if result is None:
            return False
        else:
            return result['name']

    def isNewAccount(self, email):
        result = self.query("SELECT * FROM label_system.userlist WHERE email = %s", email)
        if result is None:
            return True
        else:
            print ('Account Already Exist, Cannot Register!')
            return False

    def validate(self, email, password):
        result = self.query("SELECT password FROM label_system.userlist WHERE email = %s", email)
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
            print ('sql=%s\nexception is %s\n\n' % (sql, e))
            self.conn()
            self.query(sql, parameter)

    def query_many(self, sql, parameter):
        try:
            with self.connection.cursor() as cursor:
                # parameter can be tuple
                cursor.execute(sql, parameter)
                result = cursor.fetchall()
                return result
        except Exception as e:
            print ('sql=%s\nexception is %s\n\n' % (sql, e))
            self.conn()
            self.query_many(sql, parameter)

    def sql_commit(self, sql, parameter):
        try:
            with self.connection.cursor() as cursor:
                # Create a new record
                cursor.execute(sql, parameter)
            # connection is not autocommit by default. So you must commit to save
            # your changes.
            self.connection.commit()
        except Exception as e:
            self.conn()
            print ('sql=%s\nexception is %s\n\n' % (sql, e))
            self.sql_commit(sql, parameter)

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

    def get_records(self, account):
        records = self.query_many("SELECT filename, scholarname, label FROM label_system.scholar_list WHERE labeler=%s",
                             account)
        return records

    def nextfile(self):
        result = self.query(
            "SELECT filename FROM scholar_list WHERE label = 'unlabeled' and category = 'sybil' ORDER BY RAND() LIMIT 1",
            parameter=None)
        if result is None:
            return None  # todo: throw exception
        else:
            return result['filename']

    def next_file(self, account, mycursor=None):
        if mycursor is None:
            mycursor = self.query("SELECT `mycursor` FROM userlist WHERE email = %s", account)
            if mycursor is None:
                raise Exception('Get None MyCursor!')
            else:
                mycursor = mycursor['mycursor']
        entry = self.query("SELECT * from label_list WHERE `index` > %s ORDER BY `index` LIMIT 1", int(mycursor))
        if entry['reliable1'] is None and entry['sybil1'] is None:
            self.sql_commit("UPDATE userlist SET mycursor = %s WHERE email = %s", (mycursor + 1, account))
            return entry['filename']
        elif entry['reliable1'] is not None and entry['sybil1'] is None:
            if entry['reliable2'] is not None:
                # skip this entry
                return self.next_file(account, mycursor + 1)
            else:
                self.sql_commit("UPDATE userlist SET mycursor = %s WHERE email = %s", (mycursor + 1, account))
                return entry['filename']
        elif entry['reliable1'] is None and entry['sybil1'] is not None:
            if entry['sybil2'] is not None:
                # skip this entry
                return self.next_file(account, mycursor + 1)
            else:
                self.sql_commit("UPDATE userlist SET mycursor = %s WHERE email = %s", (mycursor + 1, account))
                return entry['filename']
        else:
            if entry['reliable2'] is None and entry['sybil2'] is None:
                self.sql_commit("UPDATE userlist SET mycursor = %s WHERE email = %s", (mycursor + 1, account))
                return entry['filename']
            elif entry['reliable2'] is not None and entry['sybil2'] is None:
                if entry['reliable3'] is not None:
                    # skip this entry
                    return self.next_file(account, mycursor + 1)
                else:
                    self.sql_commit("UPDATE userlist SET mycursor = %s WHERE email = %s", (mycursor + 1, account))
                    return entry['filename']
            elif entry['reliable2'] is None and entry['sybil2'] is not None:
                if entry['sybil3'] is not None:
                    # skip this entry
                    return self.next_file(account, mycursor + 1)
                else:
                    self.sql_commit("UPDATE userlist SET mycursor = %s WHERE email = %s", (mycursor + 1, account))
                    return entry['filename']
            elif entry['reliable3'] is None and entry['sybil3'] is None:
                self.sql_commit("UPDATE userlist SET mycursor = %s WHERE email = %s", (mycursor + 1, account))
                return entry['filename']
            elif entry['reliable3'] is not None and entry['sybil3'] is not None:
                # skip this entry
                return self.next_file(account, mycursor + 1)
            else:
                raise Exception('Over 4 labelers!')

    def