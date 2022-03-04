from flask import Flask, render_template, request, url_for, redirect, g
import datetime, sqlite3

app = Flask(__name__)


def connect_db():  # Подключение базы данных
    sql = sqlite3.connect("food.db")
    sql.row_factory = sqlite3.Row
    return sql


def get_db():  # Получение базы данных
    if not hasattr(g, "sqlite3"):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):  # Закрытие соединения с базой данных при получении страницы
    if hasattr(g, "sqlite_db"):
        g.sqlite_db.close()


@app.route("/", methods=["POST", "GET"])
def index():
    """Главная страница"""
    db = get_db()

    if request.method == "POST":    # Если пользователь добавляет новый день
        date_log = request.form["date"]

        try:  # Проверяем ввод даты, в ином случае возвращаем на главную страницу
            date = datetime.datetime.strptime(date_log, "%Y-%m-%d")
            date_sql = datetime.datetime.strftime(date, "%Y-%m-%d")
            db.execute("""
                INSERT INTO log_date (entry_date)
                VALUES
                    (?);
            """, [date_sql])
            db.commit()
            return redirect(url_for("index"))
        except ValueError:
            return redirect(url_for("index"))   # Возвращаем страницу если неверно введены данные

    cur = db.execute("""
        SELECT entry_date, IFNULL(SUM(fat), 0) as fat_, IFNULL(SUM(protein), 0) as protein_, IFNULL(SUM(carbohydates), 0) as carbohydates_, IFNULL(SUM(calories), 0) as calories_ 
        FROM log_date 
            LEFT JOIN food_date ON log_date.log_id = food_date.log_id
            LEFT JOIN food ON food_date.food_id = food.food_id
        GROUP BY entry_date
        ORDER BY entry_date DESC;
    """)
    results = cur.fetchall()  # Получаем даты для преобразования в другой вид
    user_date = []

    for i in results:
        info = {}
        pd = datetime.datetime.strptime(str(i['entry_date']), "%Y-%m-%d")
        info["entry_pretty_date"] = datetime.datetime.strftime(pd, "%B %d, %Y")
        info["date"] = i['entry_date']
        info["fat"] = i['fat_']
        info['protein'] = i['protein_']
        info['carbohydates'] = i['carbohydates_']
        info['calories'] = i['calories_']
        user_date.append(info)

    return render_template("index.html", results=user_date)


@app.route("/add_food", methods=["POST", "GET"])
def add_food():
    """Страница добавление нового типа еды"""
    db = get_db()
    if request.method == "POST":
        try:    # Валидация данных, в ином случае возвращаем на ту же страницу
            name = request.form["food_name"]
            protein = int(request.form["protein"])
            carbo = int(request.form["carbo"])
            fat = int(request.form["fat"])
            db.execute("""
            INSERT INTO food (food_name, fat, protein, carbohydates)
            VALUES
                (?, ?, ?, ?);
            """, [name, fat, protein, carbo])   # Записываем данные если валидация прошла успешно
            db.commit()
        except ValueError:
            return redirect(url_for('add_food'))

    cur = db.execute("""
        SELECT * FROM food;
    """)
    results = cur.fetchall()

    return render_template("add_food.html", results=results)


@app.route("/day/<date>", methods=["POST", "GET"])
def day(date):
    """Показывает список еды за день"""
    db = get_db()

    if request.method == "POST":
        cur = db.execute("""
            SELECT log_id FROM log_date WHERE entry_date = (?);
        """, [date])
        date_id = cur.fetchone()["log_id"]
        db.execute("""
            INSERT INTO food_date (food_id, log_id)
            VALUES
                (?, ?);
        """, [request.form["food_id"], date_id])
        db.commit()

    cur = db.execute("""
        SELECT * FROM
            log_date JOIN
            food_date USING(log_id),
            food USING(food_id)
        WHERE log_date.entry_date = (?);
    """, [date])
    results = cur.fetchall()    # Таблица списка еды в выбранный день

    cur = db.execute("""
        SELECT * FROM food;
    """)
    food_list = cur.fetchall()  # Список всей доступной еды

    _ = datetime.datetime.strptime(date, "%Y-%m-%d")
    pretty_date = datetime.datetime.strftime(_, "%B %m, %Y")

    return render_template("day.html", food_list=food_list, date=date, results=results, pretty_date=pretty_date)


if __name__ == "__main__":
    app.run(debug=True)
