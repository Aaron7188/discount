from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import random
import string
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/discount'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class LotteryCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(6), unique=True, nullable=False)
    kwai_id = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DiscountCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), unique=True, nullable=False)
    kwai_id = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    redeemed = db.Column(db.Boolean, default=False)

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(6), unique=True, nullable=False)
    status = db.Column(db.Boolean, default=False)

with app.app_context():
    db.create_all()

def generate_code(length, chars):
    return ''.join(random.choice(chars) for _ in range(length))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate_lottery_code', methods=['POST'])
def generate_lottery_code():
    data = request.get_json()
    kwai_id = data.get('kwai_id')
    code = generate_code(6, string.ascii_lowercase + string.digits)
    new_code = LotteryCode(code=code, kwai_id=kwai_id)
    db.session.add(new_code)
    db.session.commit()
    return jsonify({'code': code, 'created_at': new_code.created_at, 'kwai_id': kwai_id})

@app.route('/generate_discount_code', methods=['POST'])
def generate_discount_code():
    data = request.get_json()
    kwai_id = data.get('kwai_id')
    code = generate_code(8, string.ascii_letters)
    new_code = DiscountCode(code=code, kwai_id=kwai_id)
    db.session.add(new_code)
    db.session.commit()
    return jsonify({'code': code, 'created_at': new_code.created_at, 'kwai_id': kwai_id})

@app.route('/redeem_discount_code', methods=['POST'])
def redeem_discount_code():
    data = request.get_json()
    code = data.get('code')
    discount_code = DiscountCode.query.filter_by(code=code).first()
    if discount_code and not discount_code.redeemed:
        discount_code.redeemed = True
        db.session.commit()
        return jsonify({'message': 'Code redeemed successfully'})
    return jsonify({'message': 'Invalid or already redeemed code'}), 400

@app.route('/draw')
def draw_page():
    return render_template('draw.html')

@app.route('/draw_lottery', methods=['POST'])
def draw_lottery():
    result = Result.query.filter_by(status=False).first()
    if result:
        result.status = True
        db.session.commit()
        return jsonify({'code': result.code})
    return jsonify({'message': 'No more available codes'}), 400

if __name__ == '__main__':
    app.run(debug=True)
