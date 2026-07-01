from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from models import db, Expense

app = Flask(__name__)
CORS(app)

# ── Database config ─────────────────────────────────────────────────────────
app.config["SQLALCHEMY_DATABASE_URI"]        = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()          # creates database.db on first run


# ── Serve frontend ───────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


# ── API: Get all expenses (with optional filters) ────────────────────────────
@app.route("/api/expenses", methods=["GET"])
def get_expenses():
    category = request.args.get("category")
    month    = request.args.get("month")   # format: YYYY-MM

    query = Expense.query

    if category and category != "All":
        query = query.filter_by(category=category)
    if month:
        query = query.filter(Expense.date.like(f"{month}%"))

    expenses = query.order_by(Expense.date.desc()).all()
    total    = sum(e.amount for e in expenses)

    return jsonify({
        "expenses": [e.to_dict() for e in expenses],
        "total":    round(total, 2),
        "count":    len(expenses),
    })


# ── API: Add expense ─────────────────────────────────────────────────────────
@app.route("/api/expenses", methods=["POST"])
def add_expense():
    data = request.get_json()

    if not data or not data.get("title") or not data.get("amount") or not data.get("date"):
        return jsonify({"error": "title, amount, and date are required"}), 400

    try:
        amount = float(data["amount"])
        if amount <= 0:
            raise ValueError
    except ValueError:
        return jsonify({"error": "amount must be a positive number"}), 400

    expense = Expense(
        title    = data["title"].strip(),
        amount   = amount,
        category = data.get("category", "Other"),
        date     = data["date"],
        note     = data.get("note", "").strip(),
    )
    db.session.add(expense)
    db.session.commit()

    return jsonify(expense.to_dict()), 201


# ── API: Update expense ──────────────────────────────────────────────────────
@app.route("/api/expenses/<int:expense_id>", methods=["PUT"])
def update_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    data    = request.get_json()

    if "title"    in data: expense.title    = data["title"].strip()
    if "amount"   in data: expense.amount   = float(data["amount"])
    if "category" in data: expense.category = data["category"]
    if "date"     in data: expense.date     = data["date"]
    if "note"     in data: expense.note     = data["note"].strip()

    db.session.commit()
    return jsonify(expense.to_dict())


# ── API: Delete expense ──────────────────────────────────────────────────────
@app.route("/api/expenses/<int:expense_id>", methods=["DELETE"])
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    db.session.delete(expense)
    db.session.commit()
    return jsonify({"message": "Deleted successfully"})


# ── API: Summary by category ─────────────────────────────────────────────────
@app.route("/api/summary", methods=["GET"])
def summary():
    expenses = Expense.query.all()
    breakdown = {}
    for e in expenses:
        breakdown[e.category] = round(breakdown.get(e.category, 0) + e.amount, 2)
    return jsonify(breakdown)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)