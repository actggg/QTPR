import sys
import pymorphy2
import csv
import time
import sqlite3
from threading import Timer
import random
from PyQt5.QtGui import QIntValidator
from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QInputDialog



class MainWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('Начальный Экран.ui', self)
        self.mistakes.hide()
        self.going.clicked.connect(self.allowance)
        self.registrationbutton.clicked.connect(self.register)

    def allowance(self):
        introduced_password = self.input_password.text()
        introduced_login = self.input_login.text()
        con = sqlite3.connect("аккаунты.db")
        cur = con.cursor()
        result = cur.execute(
            f""" Select money, login from Acc where Acc.login = '{introduced_login}'
            and Acc.password='{introduced_password}'""").fetchall()
        if result:
            for elem in result:
                self.open_game = Open_Game(elem[0], elem[1])
                self.open_game.show()
                self.hide()
        else:
            self.mistakes.show()
        con.close()

    def register(self):
        self.registration = Registration()
        self.registration.show()
        self.hide()


class Registration(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('регистрация.ui', self)
        self.registration.clicked.connect(self.register_an_account)
        self.license_agreement.clicked.connect(self.license_agreement_open)

    def password_verification(self, password):
        lit_ang_connections = 'qwertyuiop        asdfghjkl      zxcvbnm'
        lit_rus_connections = 'йцукенгшщзхъ     фывапролджэё      ячсмитьбю'
        if list(set(list(password)) & set(['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'])) == []:
            return 1
        elif len(password) <= 8:
            return 2
        elif password.isdigit():
            return 3
        elif password.isupper() or password.islower():
            return 4
        else:
            mini_password = password.lower()
            for i in lit_ang_connections.split() + lit_rus_connections.split():
                g = len(i) - 2
                for j in range(g):
                    if i[j: j + 3] in mini_password:
                        return 5
        return 0

    def register_an_account(self):
        password_errors = {
            1: 'в пароле должны содержаться цифры',
            2: 'пароль должен сосотоять из более чем 8 символов',
            3: 'в пароле должны содержаться буквы',
            4: 'в пароле должны содержаться большие и маленькие буквы',
            5: 'слишком простой пароль'
        }
        login_acc = self.login.text()
        password_acc = self.password.text()
        if login_acc != '' and password_acc != '' and self.password_2.text() != '':
            if self.statement.isChecked():
                if self.password.text() == self.password_2.text():
                    if self.password_verification(password_acc) == 0:
                        con = sqlite3.connect("аккаунты.db")
                        cursor = con.cursor()
                        cursor.execute("INSERT INTO Acc(login, password) VALUES(?, ?)", (login_acc, password_acc))
                        con.commit()
                        cursor.close()
                        con.close()
                        self.go_home = MainWidget()
                        self.go_home.show()
                        self.hide()
                    else:
                        self.error_message.setText(password_errors[self.password_verification(password_acc)])
                else:
                    self.error_message.setText('пароли не совпадают')
            else:
                self.error_message.setText('вы забыли лицензионное соглашение')
        else:
            self.error_message.setText('не все поля заполнены')



    def license_agreement_open(self):
        self.setWindowTitle('Input dialog')
        self.show()
        text, ok = QInputDialog.getText(self, 'Лицензионное соглашение',
                                        f'Хоть кто то это прочитал, оставте свой отзыв')
        k = open('output.dat', 'w')
        k.write(text)


class Open_Game(QMainWindow):
    def __init__(self, *accaunt):
        super().__init__()
        uic.loadUi('казино.ui', self)
        self.LineEdit.setValidator(QIntValidator(0, 2147483647, self))
        self.accaunt = accaunt
        self.balans.setText(str(self.accaunt[0]))
        self.label_52.hide()
        self.label_54.hide()
        self.plainTextEdit.setEnabled(False)
        self.count = 0
        self.count_to_twist = 0
        self.count_to_twist_list = []
        self.toolittel.hide()
        self.rocket_is_flying.hide()
        self.pushButton_2.clicked.connect(self.roulette)
        self.pushButton.clicked.connect(self.twist)
        self.pushButton_3.clicked.connect(self.fly)
        self.win = {'999': 20000, '888': 10000,
                    '777': 5000, '666': 2000,
                    '555': 1000, '444': 500,
                    '333': 300, '222': 150,
                    '111': 50, '123': 5,
                    '234': 5, '345': 5,
                    '456': 5, '567': 5,
                    '678': 5, '789': 5}

    def roulette(self):
        self.roll = Roulette(self.accaunt[1], self.balans.text())
        self.roll.show()
        self.hide()

    def saveStat(self):
        con = sqlite3.connect("аккаунты.db")
        cur = con.cursor()
        cur.execute(f"""UPDATE Acc Set money = {self.balans.text()} Where login = '{self.accaunt[1]}'""")
        con.commit()
        con.close()

    def fly(self):
        self.go = Quiz(self.accaunt[1], self.balans.text())
        self.go.show()
        self.hide()

    def twist(self):
        try:
            self.label_52.hide()
            self.toolittel.setReadOnly(True)
            self.pushButton_3.setEnabled(False)
            self.LineEdit.setEnabled(False)
            self.pushButton.setEnabled(False)
            self.pushButton_2.setEnabled(False)
            self.label_3.setText('')
            self.count_to_twist += 1
            self.rocket_is_flying.show()
            self.rocket_is_standing.hide()
            self.toolittel.hide()
            self.bet = int(self.LineEdit.text())
            self.count_to_twist_list.append(self.bet)
            if self.bet not in range(1, int(self.balans.text()) + 1):
                self.toolittel.show()
                self.LineEdit.setEnabled(True)
                self.pushButton.setEnabled(True)
                self.pushButton_2.setEnabled(True)
                self.pushButton_3.setEnabled(True)
                return 0
            else:
                self.balans.setText(str(int(self.balans.text()) - self.bet))
            self.twists = 0
            self.digit = '123456789'
        except Exception as e:
            print(e)


        def taskmanager():
            self.saveStat()
            self.count += 3
            self.rocket_is_flying.move(40, 590 - self.count)
            self.twists += 1
            self.slot_1.setText(random.choice(str(self.digit)))
            self.slot_2.setText(random.choice(str(self.digit)))
            self.slot_3.setText(random.choice(str(self.digit)))
            if self.twists <= 10:
                t = Timer(0.05, taskmanager)
                t.start()
            elif self.twists <= 20:
                t = Timer(0.2, taskmanager)
                t.start()
            elif self.twists <= 25:
                t = Timer(0.5, taskmanager)
                t.start()
            else:
                if self.slot_1.text() + self.slot_2.text() + self.slot_3.text() in self.win:
                    self.balans.setText(str(int(self.balans.text()) + int(self.bet) * self.win[self.slot_1.text() + self.slot_2.text() + self.slot_3.text()]))
                    self.label_3.setText(str(int(self.bet) * self.win[
                        self.slot_1.text() + self.slot_2.text() + self.slot_3.text()]))
                    if self.slot_1.text() == self.slot_2.text() and self.slot_1.text() == self.slot_3.text():
                        len_win = len(self.label_3.text())
                        self.label_54.setText(' ' * ((12 - len_win) // 2) + self.label_3.text() + ' ' * ((12 - len_win) // 2))
                        self.label_52.show()
                        self.label_54.show()
                        time.sleep(2)
                        self.label_52.hide()
                        self.label_54.hide()
                elif self.slot_1.text() + self.slot_2.text() == '11' or self.slot_2.text() + self.slot_3.text() == '11':
                    self.balans.setText(str(int(self.balans.text()) + int(self.bet) * 5))
                    self.label_3.setText(str(int(self.bet) * 5))
                elif self.slot_1.text() == '1' or self.slot_2.text() == '1' or self.slot_3.text() == '1':
                    self.balans.setText(str(int(self.balans.text()) + int(self.bet) * 2))
                    self.label_3.setText(str(int(self.bet) * 2))
                self.LineEdit.setEnabled(True)
                self.pushButton.setEnabled(True)
                self.pushButton_2.setEnabled(True)
                self.pushButton_3.setEnabled(True)
                if self.count_to_twist % 7 == 0:
                    self.balans.setText(str(int(self.balans.text()) + sum(self.count_to_twist_list) // 7))
                    self.rocket_is_flying.move(40, 590)
                    self.count = 0
                    self.rocket_is_flying.hide()
                    self.rocket_is_standing.show()
                self.saveStat()

        taskmanager()


class Roulette(QMainWindow):
    def __init__(self, *accaunt):
        super().__init__()
        uic.loadUi('рулетка.ui', self)
        self.bet_yellow.setValidator(QIntValidator(0, 1000000000, self))
        self.bet_blue.setValidator(QIntValidator(0, 1000000000, self))
        self.bet_violet.setValidator(QIntValidator(0, 1000000000, self))
        self.bet_red.setValidator(QIntValidator(0, 1000000000, self))
        self.bet_orange.setValidator(QIntValidator(0, 1000000000, self))
        self.plainTextEdit.setReadOnly(True)
        self.attempt = 0
        self.mistake.show()
        self.barabans.clicked.connect(self.drums)
        self.balance.setText(accaunt[1])
        self.spin.clicked.connect(self.twist)
        self.accaunt = accaunt
        self.incorrectbid_digit.hide()
        self.incorrectbid_digit_2.hide()
        self.incorrectbid_digit_3.hide()
        self.incorrectbid_digit_4.hide()
        self.incorrectbid_digit_5.hide()
        self.digit = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                      21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]

        self.digits_button = [self.digit_1, self.digit_2, self.digit_3, self.digit_4, self.digit_5, self.digit_6,
                  self.digit_7, self.digit_8, self.digit_9, self.digit_10, self.digit_11, self.digit_12,
                  self.digit_13, self.digit_14, self.digit_15, self.digit_16, self.digit_17, self.digit_18,
                  self.digit_19, self.digit_20, self.digit_21, self.digit_22, self.digit_23, self.digit_24,
                  self.digit_25, self.digit_26, self.digit_27, self.digit_28, self.digit_29, self.digit_30,
                  self.digit_31, self.digit_32, self.digit_33, self.digit_34, self.digit_35, self.digit_36]

        self.range = [self.even, self.odd, self.range_3_36,
                      self.range_2_35, self.range_1_34,self.range_1_12, self.range_13_24,
                      self.range_25_36, self.range_1_18, self.range_19_36]
        for i in self.range:
            i.clicked.connect(self.place_a_bet)

        for i in self.digits_button:
            i.clicked.connect(self.place_a_bet)


    def saveStat(self):
        con = sqlite3.connect("аккаунты.db")
        cur = con.cursor()
        cur.execute(f"""UPDATE Acc Set money = {self.balance.text()} Where login = '{self.accaunt[0]}'""")
        con.commit()
        con.close()

    def place_a_bet(self):
        all_True = True
        mistake_x = 0
        color = ''
        if self.cliner.isChecked():
            color = '#f0f0f0'
            self.sender().setStyleSheet(f'QPushButton {{background-color: {color}; color: black;}}')
        if self.yellow_point.isChecked():
            color = 'yellow'
        elif self.orange_point.isChecked():
            color = 'orange'
        elif self.red_point.isChecked():
            color = 'red'
        elif self.blue_point.isChecked():
            color = 'blue'
        elif self.violet_point.isChecked():
            color = 'violet'
        else:
            all_True = False
        if all_True:
            self.sender().setStyleSheet(f'QPushButton {{background-color: {color}; color: black;}}')
            self.mistake.hide()

    def twist(self):
        mistake_x = 0
        for i in self.digits_button:
            if str(i.palette().window().color().name()) != '#f0f0f0':
                mistake_x = 1
        for i in self.range:
            if str(i.palette().window().color().name()) != '#f0f0f0':
                mistake_x = 1
        if mistake_x == 1:
            self.mistake.hide()
        else:
            self.mistake.show()
            return 0
        check_color = False
        for i in self.digits_button:
            if str(i.palette().window().color().name()) != '#f0f0f0':
                check_color = True
        for i in self.range:
            if str(i.palette().window().color().name()) != '#f0f0f0':
                check_color = True
        if not check_color:
            return 0
        self.won_now.setText('0')
        mistake = False
        self.incorrected = [self.incorrectbid_digit, self.incorrectbid_digit_2, self.incorrectbid_digit_3,
                            self.incorrectbid_digit_4, self.incorrectbid_digit_5]
        for i in self.incorrected:
            i.hide()
        self.color_and_rate = {'#ffff00': self.bet_yellow.text(),
                                             '#0000ff': self.bet_blue.text(),
                                             '#ff0000': self.bet_red.text(),
                                             '#ee82ee': self.bet_violet.text(),
                                             '#ffa500': self.bet_orange.text()}
        for digit in self.digits_button:
            color = str(digit.palette().window().color().name())
            if color == '#ffff00' and self.bet_yellow.text() == '':
                self.incorrectbid_digit.show()
                mistake = True
            if color == '#0000ff' and self.bet_blue.text() == '':
                self.incorrectbid_digit_2.show()
                mistake = True
            if color == '#ff0000' and self.bet_red.text() == '':
                self.incorrectbid_digit_3.show()
                mistake = True
            if color == '#ee82ee' and self.bet_violet.text() == '':
                self.incorrectbid_digit_4.show()
                mistake = True
            if color == '#ffa500' and self.bet_orange.text() == '':
                self.incorrectbid_digit_5.show()
                mistake = True

        for i in self.range:
            color = str(i.palette().window().color().name())
            if color == '#ffff00' and self.bet_yellow.text() == '':
                self.incorrectbid_digit.show()
                mistake = True
            if color == '#0000ff' and self.bet_blue.text() == '':
                self.incorrectbid_digit_2.show()
                mistake = True
            if color == '#ff0000' and self.bet_red.text() == '':
                self.incorrectbid_digit_3.show()
                mistake = True
            if color == '#ee82ee' and self.bet_violet.text() == '':
                self.incorrectbid_digit_4.show()
                mistake = True
            if color == '#ffa500' and self.bet_orange.text() == '':
                self.incorrectbid_digit_5.show()
                mistake = True
        if not mistake:
            all_bet = 0
            for digit in self.digits_button:
                if str(digit.palette().window().color().name()) != '#f0f0f0':
                    all_bet += int(self.color_and_rate[str(digit.palette().window().color().name())])
            for digit in self.range:
                if str(digit.palette().window().color().name()) != '#f0f0f0':
                    all_bet += int(self.color_and_rate[str(digit.palette().window().color().name())])
            if int(self.balance.text()) - all_bet < 0:
                return 0
            self.spiner.setText(str(random.choice(self.digit)))
            self.balance.setText(str(int(self.balance.text()) - all_bet))
            for digit in self.digits_button:
                    if digit.text() == self.spiner.text() and str(digit.palette().window().color().name()) in self.color_and_rate:
                        self.won_now.setText(str(36 * int(self.color_and_rate[str(digit.palette().window().color().name())])))
            for digit in self.range:
                if str(digit.palette().window().color().name()) != '#f0f0f0':
                    if digit == self.even and int(self.spiner.text()) % 2 == 1:
                        self.won_now.setText(str(int(self.won_now.text()) + 2 * int(self.color_and_rate[str(digit.palette().window().color().name())])))
                    if digit == self.odd and int(self.spiner.text()) % 2 == 0:
                        self.won_now.setText(str(int(self.won_now.text()) + 2 * int(self.color_and_rate[str(digit.palette().window().color().name())])))
                    if digit == self.range_1_18 and int(self.spiner.text()) in range(1, 19):
                        self.won_now.setText(str(int(self.won_now.text()) + 2 * int(self.color_and_rate[str(digit.palette().window().color().name())])))
                    if digit == self.range_19_36 and int(self.spiner.text()) in range(19, 37):
                        self.won_now.setText(str(int(self.won_now.text()) + 2 * int(self.color_and_rate[str(digit.palette().window().color().name())])))
                    if digit == self.range_1_34 and int(self.spiner.text()) % 3 == 1:
                        self.won_now.setText(str(int(self.won_now.text()) + 3 * int(self.color_and_rate[str(digit.palette().window().color().name())])))
                    if digit == self.range_2_35 and int(self.spiner.text()) % 3 == 2:
                        self.won_now.setText(str(int(self.won_now.text()) + 3 * int(self.color_and_rate[str(digit.palette().window().color().name())])))
                    if digit == self.range_3_36 and int(self.spiner.text()) % 3 == 0:
                        self.won_now.setText(str(int(self.won_now.text()) + 3 * int(self.color_and_rate[str(digit.palette().window().color().name())])))
                    if digit == self.range_1_12 and int(self.spiner.text()) in range(1, 13):
                        self.won_now.setText(str(int(self.won_now.text()) + 3 * int(self.color_and_rate[str(digit.palette().window().color().name())])))
                    if digit == self.range_13_24 and int(self.spiner.text()) in range(13, 25):
                        self.won_now.setText(str(int(self.won_now.text()) + 3 * int(self.color_and_rate[str(digit.palette().window().color().name())])))
                    if digit == self.range_25_36 and int(self.spiner.text()) in range(25, 37):
                        self.won_now.setText(str(int(self.won_now.text()) + 3 * int(self.color_and_rate[str(digit.palette().window().color().name())])))
            self.attempt += 1
            tab_len = (10 - len(str(self.attempt))) * ' '
            self.plainTextEdit.appendPlainText(f'№{self.attempt},{tab_len} {self.won_now.text()}')
            self.balance.setText(str(int(self.balance.text()) + int(self.won_now.text())))

        self.saveStat()



    def drums(self):
        self.open_game = Open_Game(int(self.balance.text()), self.accaunt[0])
        self.open_game.show()
        self.hide()


class Quiz(QMainWindow):
    def __init__(self, *accaunt):
        super().__init__()
        uic.loadUi('викторина.ui', self)
        self.accaunt = accaunt
        self.label_11.setText(str(accaunt[1]))
        self.pushButton.clicked.connect(self.drums)
        self.math_combo = [self.m_100, self.m_200, self.m_300, self.m_400]
        self.rus_combo = [self.r_100, self.r_200, self.r_300, self.r_400]
        self.logic_combo = [self.log_100, self.log_200, self.log_300, self.log_400]
        self.history_combo = [self.h_100, self.h_200, self.h_300, self.h_400]
        for num, i in enumerate(self.math_combo):
            i.clicked.connect(self.showDialogM)
        for num, i in enumerate(self.logic_combo):
            i.clicked.connect(self.showDialogL)
        for num, i in enumerate(self.rus_combo):
            i.clicked.connect(self.showDialogR)
        for num, i in enumerate(self.history_combo):
            i.clicked.connect(self.showDialogH)


    def showDialogM(self):
        complexity = int(self.sender().text())
        sing = '+'
        self.setGeometry(550, 220, 800, 600)
        self.setWindowTitle('Input dialog')
        self.show()
        first, second = 0, 0
        if complexity == 100:
            sing = '+'
            first, second = random.choice(range(1, 10)), random.choice(range(1, 20))
        if complexity == 200:
            sing = '+'
            first, second = random.choice(range(22, 30)), random.choice(range(10, 20))
        if complexity == 300:
            sing = '-'
            first, second = random.choice(range(20, 30)), random.choice(range(1, 20))
        if complexity == 400:
            sing = '*'
            first, second = random.choice(range(1, 10)), random.choice(range(1, 20))
        text, ok = QInputDialog.getText(self, 'Математика',
                                        f'решите пример: {first}{sing}{second}')

        if ok:
            if text == str(eval(f'{first}{sing}{second}')):
                self.label_11.setText(str(int(self.label_11.text()) + complexity))
                self.saveStat()
            else:
                print(2)


    def showDialogR(self):
        morph = pymorphy2.MorphAnalyzer()
        words = ['сердец', 'курица', 'королеве', 'о жуке', 'меч', 'выдрой']
        for i in words:
            p = morph.parse(i)[0]
            print(p.tag.case)
        complexity = int(self.sender().text())
        self.setGeometry(550, 220, 800, 600)
        self.setWindowTitle('Input dialog')
        self.show()
        word = random.choice(words)
        p = morph.parse(word)[0]
        k = p.tag.case
        text, ok = QInputDialog.getText(self, 'Русский язык',
                                        f'Укажите падеж: "{word}"')
        d = {'именительный': 'nomn', 'родительный': 'gent',
             'дательный': 'datv', 'винительный': 'accs',
             'творительный': 'ablt', 'предложный': 'loct'}
        if ok:
            print(text, k, d[text.lower()])
            if text.lower() in d and d[text.lower()] == k:
                self.label_11.setText(str(int(self.label_11.text()) + complexity))
                self.saveStat()
            else:
                print(2)


    def showDialogL(self):
        complexity = int(self.sender().text())
        self.setGeometry(550, 220, 800, 600)
        self.setWindowTitle('Input dialog')
        self.show()
        with open('папка с вопросами/Файл с загадками.txt', encoding="utf8") as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='"')
            line_list = []
            for line in reader:
                line_list.append(line)
            random01 = random.choice(line_list)
        text, ok = QInputDialog.getText(self, 'Логика',
                                        f'{random01[0]}')

        if ok:
            if text == str(f'{random01[1]}'):
                self.label_11.setText(str(int(self.label_11.text()) + complexity))
                self.saveStat()
            else:
                print(2)


    def showDialogH(self):
        complexity = int(self.sender().text())
        self.setGeometry(550, 220, 800, 600)
        self.setWindowTitle('Input dialog')
        self.show()
        with open('папка с вопросами/Файл с вопросами по истории.txt', encoding="utf8") as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='"')
            line_list = []
            for line in reader:
                line_list.append(line)
        print(line_list[2:4])
        print(complexity)
        if complexity == 100:
            random01 = random.choice(line_list[:2])
        if complexity == 200:
            random01 = random.choice(line_list[2:4])
        if complexity == 300:
            random01 = random.choice(line_list[4:6])
        if complexity == 400:
            random01 = random.choice(line_list[6:8])
        text, ok = QInputDialog.getText(self, 'История',
                                        f'{random01[0]}')

        if ok:
            if text == str(f'{random01[1]}'):
                self.label_11.setText(str(int(self.label_11.text()) + complexity))
                self.saveStat()
            else:
                print(f'{random01[1]}', 2)

    def saveStat(self):
        con = sqlite3.connect("аккаунты.db")
        cur = con.cursor()
        cur.execute(f"""UPDATE Acc Set money = {self.label_11.text()} Where login = '{self.accaunt[0]}'""")
        con.commit()
        con.close()

    def drums(self):
        self.open_game = Open_Game(int(self.label_11.text()), self.accaunt[0])
        self.open_game.show()
        self.hide()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWidget()
    ex.show()
    sys.exit(app.exec_())
