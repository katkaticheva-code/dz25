from flask import Flask, request, redirect, url_for, render_template_string
import sqlite3
from datetime import datetime

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            author TEXT,
            description TEXT,
            year INTEGER,
            image_url TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

base_html = """
<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <title>Бібліотека</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            background: #f7f7f7;
        }
        header {
            background: #333;
            padding: 15px 20px;
        }
        header a {
            color: white;
            text-decoration: none;
            margin-right: 20px;
            font-weight: bold;
        }
        .container {
            max-width: 900px;
            margin: 30px auto;
            background: white;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0,0,0,0.08);
            border-radius: 8px;
        }
        .book {
            border: 1px solid #ccc;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            background: #fafafa;
        }
        .book img {
            margin-top: 10px;
            margin-bottom: 10px;
        }
        input, textarea {
            display: block;
            width: 100%;
            max-width: 500px;
            margin: 8px 0 15px 0;
            padding: 10px;
            box-sizing: border-box;
        }
        button {
            background: #333;
            color: white;
            border: none;
            padding: 10px 16px;
            cursor: pointer;
            border-radius: 4px;
        }
    </style>
</head>
<body>

<header>
    <a href="/">Головна</a>
    <a href="/author">Про автора</a>
    <a href="/library">Бібліотека</a>
</header>

<div class="container">
    {{ content|safe }}
</div>

</body>
</html>
"""

@app.route("/")
def index():
    content = """
    <h1>Веб-додаток "Бібліотека"</h1>
    <p>Це навчальний проєкт на Flask + SQLite.</p>
    <p>Тут можна додавати книги, переглядати список книг, видаляти книги та дивитися детальну інформацію.</p>
    <a href="/library">Перейти до бібліотеки</a>
    """
    return render_template_string(base_html, content=content)

@app.route("/author")
def author():
    content = """
    <h2>Про автора</h2>
    <p><b>Ім'я:</b> Катерина </p>
    <p><b>Місто:</b> Дніпро</p>
    <p><b>Чим займаюсь:</b> Студент / навчаюсь програмуванню</p>
    <p><b>Навички або інтереси:</b> Python, Flask, HTML, CSS</p>
    <p><b>Контакт:</b> Katerina@gmail.com</p>
    """
    return render_template_string(base_html, content=content)

@app.route("/library")
def library():
    conn = get_db()
    books = conn.execute("SELECT * FROM books ORDER BY created_at DESC").fetchall()
    conn.close()

    books_html = ""

    for book in books:
        image_html = ""
        if book["image_url"]:
            image_html = f"<img src='{book['image_url']}' width='100'>"

        books_html += f"""
        <div class="book">
            <h3>{book['title']}</h3>
            <p><b>Автор:</b> {book['author']}</p>
            <p><b>Рік:</b> {book['year']}</p>
            {image_html}
            <a href="/book/{book['id']}">Детальніше</a>
            <a href="/delete/{book['id']}">Видалити</a>
        </div>
        """

    content = f"""
    <h2>Бібліотека</h2>

    <h3>Додати книгу</h3>
    <form action="/add_book" method="post">
        <input name="title" placeholder="Назва книги" required>
        <input name="author" placeholder="Автор" required>
        <input name="year" placeholder="Рік видання" required>
        <input name="image_url" placeholder="URL картинки">
        <textarea name="description" placeholder="Опис"></textarea>
        <button type="submit">Додати</button>
    </form>

    <hr>

    <h3>Список книг</h3>
    {books_html if books else "<p>Книг поки немає</p>"}
    """

    return render_template_string(base_html, content=content)

@app.route("/add_book", methods=["POST"])
def add_book():
    conn = get_db()
    conn.execute("""
        INSERT INTO books (title, author, description, year, image_url, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        request.form["title"],
        request.form["author"],
        request.form["description"],
        request.form["year"],
        request.form["image_url"],
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()
    return redirect(url_for("library"))

@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db()
    conn.execute("DELETE FROM books WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("library"))

@app.route("/book/<int:id>")
def book(id):
    conn = get_db()
    book = conn.execute("SELECT * FROM books WHERE id = ?", (id,)).fetchone()
    conn.close()

    if not book:
        content = "<h2>Книгу не знайдено</h2><a href='/library'>Назад</a>"
        return render_template_string(base_html, content=content)

    image_html = ""
    if book["image_url"]:
        image_html = f"<img src='{book['image_url']}' width='300'>"

    content = f"""
    <h2>{book['title']}</h2>
    <p><b>Автор:</b> {book['author']}</p>
    <p><b>Рік:</b> {book['year']}</p>
    <p><b>Опис:</b> {book['description']}</p>
    {image_html}
    <br><br>
    <a href="/library">Назад до бібліотеки</a>
    """

    return render_template_string(base_html, content=content)

if __name__ == "__main__":
    app.run(debug=True)
