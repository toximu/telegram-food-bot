import sqlite3

con = sqlite3.connect('db.db')
cur = con.cursor()


def create_user_cart(username):
    global con, cur
    
    cur.execute('CREATE TABLE IF NOT EXISTS {key}(name_dish TEXT PRIMARY KEY, type, amount)'.format(key = str(username)))
    con.commit()

def add_to_cart(username1, name1, type1):
    global cur, con
    res = cur.execute('SELECT 1 from {} WHERE name_dish == "{}"'.format(username1, name1)).fetchone()
    if not res:
        
        cur.execute('INSERT INTO {} VALUES (?,?,?)'.format(username1), (name1, type1, 1))
        con.commit()
    else:
        amount = cur.execute('SELECT amount FROM {} WHERE name_dish == "{}"'.format(username1, name1)).fetchone()[0]
        print(amount)
        cur.execute('UPDATE {} SET amount = {} WHERE name_dish = "{}"'.format(username1, amount+1, name1))
        con.commit()
    print(cur.execute('SELECT * FROM {}'.format(username1)).fetchall())
def delete_users():
    global cur, con
    users = cur.execute("SELECT name FROM sqlite_master WHERE NOT name_dish == 'dishes'").fetchall()
    for i in users:
        cur.execute("DROP TABLE IF EXISTS {}".format(i[0]))
        con.commit()
def clear_cart(username):
    global cur, con
    cur.execute("DROP TABLE IF EXISTS {}".format(username))
    con.commit()

def get_cart(username):
    cart = ''
    summ = 0
    if cur.execute('SELECT name FROM sqlite_master where name == "{}"'.format(username)).fetchone():
        res = cur.execute("SELECT dishes.dish, dishes.price, {key}.amount FROM dishes INNER JOIN {key} ON dishes.dish = {key}.name_dish".format(key = username)).fetchall()
        
        for i in res:
            cart += f'{i[0]} {i[1]} руб. * {i[2]}\n'
            summ += i[1]*i[2]
        cart += f'\nИтого: {summ} руб.'
        return cart
    else:
        return 'Ваша корзина пуста!'
    
    



print(cur.execute('SELECT name FROM sqlite_master').fetchall())
