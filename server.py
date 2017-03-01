import tornado.ioloop
import tornado.web
import os.path
import db

mydb = db.DB()

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('login.html')

    def post(self):
        email = self.get_argument('account')
        password = self.get_argument('password')
        if not mydb.validate(email, password):
            self.add_header('LoginStatus', 'Error')

class LabelHandler(tornado.web.RequestHandler):
    def post(self):
        email = self.get_argument('account')
        name = mydb.get_name(email)
        filename = mydb.next_file(email)
        # filename = mydb.get_labeling(email)
        # if filename is None:
        #     filename = mydb.next_file(email)
            # mydb.update_labeled(filename, 'labeling', email)
        number = mydb.number_labeled(email)
        self.render('label.html', number=number, email=email, name=name, scholarID=filename.replace('.parse', ''))

    def get(self): # only for modify
        email = self.get_argument('account')
        name = mydb.get_name(email)
        filename = self.get_argument('filename')
        original = self.get_argument('original')
        number = mydb.number_labeled(email)
        self.render('modify_label.html', original=original, number=number, email=email, name=name, scholarID=filename.replace('.parse', ''))

class RegisterPageHandler(tornado.web.RequestHandler):
    def post(self):
        if self.request.headers["ValidateAccount"] == "true":
            email = self.get_argument('account')
            if not (mydb.isNewAccount(email)):
                self.add_header("RegisterStatus", "Already exist!")

    def get(self):
        self.render('register.html')

class RegisterHandler(tornado.web.RequestHandler):
    def post(self):
        email = self.get_argument('account')
        username = self.get_argument('username')
        password = self.get_argument('password')
        mydb.insert_user(email, username, password)
        self.render('login.html')

class ModifyHandler(tornado.web.RequestHandler):
    def post(self):
        filename = self.get_argument('filename')
        label = self.get_argument('label')
        account = self.get_argument('account')
        original_label = self.get_argument('original')
        mydb.modify_labeled(account, filename, label)
        try :
            mydb.modify_label_list(filename, original_label, label, account)
        except Exception as e:
            print e.message
        finally:
            # label the next
            name = mydb.get_name(account)
            filename = mydb.next_file(account)
            number = mydb.number_labeled(account)
            self.render('label.html', number=number, email=account, name=name, scholarID=filename.replace('.parse', ''))

class DatabaseHandler(tornado.web.RequestHandler):
    def post(self):
        filename = self.get_argument('filename')
        label = self.get_argument('label')
        account = self.get_argument('account')
        # mydb.update_labeled(filename, label, account)
        try:
            mydb.store_label(account, filename, label)
        except Exception as e:
            print e.message
        finally:
            # render label again
            name = mydb.get_name(account)
            filename = mydb.next_file(account)
            # mydb.update_labeled(filename, 'labeling', account)
            number = mydb.number_labeled(account)
            self.render('label.html', number=number, email=account, name=name, scholarID=filename.replace('.parse', ''))

class RecordHandler(tornado.web.RequestHandler):
    def get(self):
        account = self.get_argument('account')
        name = mydb.get_name(account)
        records = mydb.get_records(account)
        if records is None:
            self.write('No data has been labeled!')
        else:
            self.render('record.html', name=name, records=records, account=account)

class FileHandler(tornado.web.RequestHandler):
    def get(self):
        filename = self.get_argument('scholarID') + '.parse'
        a_file = open('/root/tornadotest/static/gs_data/' + filename, 'r')
        content = a_file.readlines()
        self.write('scholarID: ' + content[0] + '<br>')
        self.write('scholar name: ' + content[1] + '<br>')
        self.write('title/ affiliation: ' + content[2] + '<br>')
        self.write('research field: ' + content[3] + '<br>')
        self.write('verified email: ' + content[4] + '<br>')
        self.write('personal website: ' + content[5] + '<br>')
        self.write('photo: ' + content[6] + '<br>')
        self.write('citation indices: (total, h-index, i10-index)' + content[7] + '<br>')
        self.write('co-authors (scholarID:scholar name) divided by \',\': ' + content[8] + '<br>')
        self.write('values in the citation diagram: ' + content[9] + '<br>')
        self.write('corresponding year to the above: ' + content[10] + '<br>')
        self.write('citation of each article from the highest to the lowest excluding 0: ' + content[11] + '<br>')
        self.write('Article List: <br>'
                   'form: articleID(just ignore it), title, authors, publication, citation(if has), published year')
        for i in range(12, len(content)):
            self.write(content[i] + '<br>')

# class RecordModule(tornado.web.UIModule):
#     def render(self, record, account):
#         return self.render_string('modules/record_entry.html', account=account, record=record)

def make_app():
    return tornado.web.Application(
        [
            (r"/", MainHandler),
            (r'/label', LabelHandler),
            (r'/register', RegisterHandler),
            (r'/registerpage', RegisterPageHandler),
            (r'/store', DatabaseHandler),
            (r'/record', RecordHandler),
            (r'/file', FileHandler),
            (r'/modify', ModifyHandler),
        ],
        template_path = os.path.join(os.path.dirname(__file__), "templates"),
        static_path = os.path.join(os.path.dirname(__file__), "static"),
        # ui_modules={'Record': RecordModule},
        debug=True,
    )

if __name__ == "__main__":
    app = make_app()
    app.listen(80)
    tornado.ioloop.IOLoop.current().start()