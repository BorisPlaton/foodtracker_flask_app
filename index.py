from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        pass
    return render_template("index.html")


@app.route("/add_food", methods=["POST", "GET"])
def add_food():
    if request.method == "POST":
        pass
    return render_template("add_food.html")


@app.route("/day/<date>", methods=["POST", "GET"])
def day(date):
    if request.method == "POST":
        pass
    return render_template("add_food.html")


if __name__ == "__main__":
    app.run(debug=True)
