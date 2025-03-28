from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Expense Model
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.String(20), nullable=False)

# Create database
with app.app_context():
    db.create_all()

# Route to add an expense
@app.route('/add_expense', methods=['POST'])
def add_expense():
    data = request.json
    new_expense = Expense(category=data['category'], amount=data['amount'], date=data['date'])
    db.session.add(new_expense)
    db.session.commit()
    return jsonify({'message': 'Expense added successfully'})

# Route to get all expenses
@app.route('/get_expenses', methods=['GET'])
def get_expenses():
    expenses = Expense.query.all()
    return jsonify([{'id': e.id, 'category': e.category, 'amount': e.amount, 'date': e.date} for e in expenses])

if __name__ == '__main__':
    app.run(debug=True)
