import sqlite3
from sqlite3 import Error

# bet settings
percentage_100 = 100
percentage_75 = 75
percentage_50 = 50


class AppData:
    def __init__(self):
        # account settings
        self.account_mother_name = ""
        self.account_mother_pass = ""

        self.accounts_son = [
            # {
            #     'name': 'test_name',
            #     'pass': 'test_pass'
            # },
            # {
            #     'name': '222',
            #     'pass': '333'
            # }
        ]

        # app status
        self.status_delay_in_seconds = 5
        self.status_is_running = 0
        self.status_percentage = percentage_100

    def read_data(self):
        try:
            with sqlite3.connect(database='database.db') as conn:
                cur = conn.cursor()
                cur.execute("SELECT name, pass FROM user WHERE is_mother = ?", (1,))
                users = cur.fetchall()
                for user in users:
                    print(user)
                    self.account_mother_name = user[0]
                    self.account_mother_pass = user[1]

                cur.execute("SELECT name, pass FROM user WHERE is_mother = ?", (0,))
                users = cur.fetchall()
                for user in users:
                    print(user)
                    account_son = {
                        'name': user[0],
                        'pass': user[1]
                    }
                    self.accounts_son.append(account_son)

                # read status
                cur.execute("SELECT percentage, is_running, delay_in_second FROM app_status WHERE id = ?", (1,))
                status_list = cur.fetchall()
                for status in status_list:
                    print(status)
                    self.status_delay_in_seconds = status[2]
                    self.status_is_running = status[1]
                    self.status_percentage = status[0]

        except Error as e:
            print(e)
            conn.rollback()
        finally:
            conn.close()

    def update_mother_data(self):
        try:
            with sqlite3.connect(database='database.db') as conn:
                cur = conn.cursor()
                sql = '''
                    UPDATE user
                    SET name = ?,
                        pass = ?
                    WHERE is_mother = 1
                '''
                cur.execute(sql, (self.account_mother_name, self.account_mother_pass))

        except Error as e:
            print(e)
            conn.rollback()
        finally:
            conn.close()

    def update_son_data(self):
        try:
            with sqlite3.connect(database='database.db') as conn:
                # delete all son accounts
                sql = 'DELETE FROM user WHERE is_mother = ?'
                cur = conn.cursor()
                cur.execute(sql, (0,))

                # insert son accounts
                for account_son in self.accounts_son:
                    cur = conn.cursor()
                    sql = 'INSERT INTO user (is_mother, name, pass) VALUES (?, ?, ?)'
                    cur.execute(sql, (0, account_son['name'], account_son['pass']))

        except Error as e:
            print(e)
            conn.rollback()
        finally:
            conn.close()

    def update_app_status(self):
        try:
            with sqlite3.connect(database='database.db') as conn:
                cur = conn.cursor()
                sql = '''
                    UPDATE app_status
                    SET percentage = ?,
                        is_running = ?,
                        delay_in_second = ?
                    WHERE id = 1
                '''
                cur.execute(sql, (self.status_percentage, self.status_is_running, self.status_delay_in_seconds))

        except Error as e:
            print(e)
            conn.rollback()
        finally:
            conn.close()

    def add_bet(self, bet_id):
        try:
            with sqlite3.connect(database='database.db') as conn:
                # insert bet
                cur = conn.cursor()
                cur.execute("SELECT is_duplicated FROM placed_bet WHERE bet_id = ?", (bet_id,))
                bets = cur.fetchall()
                if len(bets) == 0:
                    cur = conn.cursor()
                    sql = 'INSERT INTO placed_bet (bet_id, is_finished, is_duplicated) VALUES (?, ?, ?)'
                    cur.execute(sql, (bet_id, 0, 0))

        except Error as e:
            print(e)
            conn.rollback()
        finally:
            conn.close()

    def set_bet_duplicated(self, bet_id):
        try:
            with sqlite3.connect(database='database.db') as conn:
                cur = conn.cursor()
                sql = '''
                    UPDATE placed_bet
                    SET
                        is_duplicated = 1
                    WHERE bet_id = ?
                '''
                cur.execute(sql, (bet_id,))

        except Error as e:
            print(e)
            conn.rollback()
        finally:
            conn.close()

    def check_if_exists_or_duplicated(self, bet_id) -> bool:
        try:
            with sqlite3.connect(database='database.db') as conn:
                cur = conn.cursor()
                cur.execute("SELECT is_duplicated FROM placed_bet WHERE bet_id = ?", (bet_id,))
                bets = cur.fetchall()
                if len(bets) == 0:
                    return False
                for bet in bets:
                    if bet[0] != 0:
                        return True
                return False
        except Error as e:
            print(e)
            conn.rollback()

        finally:
            conn.close()

    def write_data(self):
        self.update_app_status()
        self.update_mother_data()
        self.update_son_data()

# app_data = AppData()
# app_data.update_mother_data()
# app_data.update_son_data()
# app_data.update_app_status()
# app_data.write_data()

# print(app_data)
