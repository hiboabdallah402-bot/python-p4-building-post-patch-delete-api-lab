#!/usr/bin/env python3

from flask import Flask, request, make_response
from flask_migrate import Migrate

from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)


with app.app_context():
    db.create_all()
    if not Bakery.query.first():
        bakery = Bakery(name='ABC Bakery')
        db.session.add(bakery)
        db.session.commit()


@app.route('/')
def home():
    return '<h1>Bakery GET-POST-PATCH-DELETE API</h1>'


@app.route('/bakeries')
def bakeries():
    bakeries = [bakery.to_dict() for bakery in Bakery.query.all()]
    return make_response(bakeries, 200)


@app.route('/bakeries/<int:id>')
def bakery_by_id(id):
    bakery = Bakery.query.filter_by(id=id).first()
    if not bakery:
        return make_response({'error': 'Bakery not found'}, 404)

    bakery_serialized = bakery.to_dict()
    return make_response(bakery_serialized, 200)


@app.route('/bakeries/<int:id>', methods=['PATCH'])
def update_bakery(id):
    bakery = Bakery.query.filter_by(id=id).first()
    if not bakery:
        return make_response({'error': 'Bakery not found'}, 404)

    data = request.get_json(silent=True) or request.form or {}
    if 'name' in data:
        bakery.name = data['name']

    db.session.commit()
    return make_response(bakery.to_dict(), 200)


@app.route('/baked_goods', methods=['POST'])
def create_baked_good():
    data = request.get_json(silent=True) or request.form or {}
    name = data.get('name')
    price = data.get('price')
    bakery_id = data.get('bakery_id')

    if not name or price is None:
        return make_response({'error': 'Name and price are required'}, 400)

    baked_good = BakedGood(name=name, price=price, bakery_id=bakery_id)
    db.session.add(baked_good)
    db.session.commit()
    return make_response(baked_good.to_dict(), 201)


@app.route('/baked_goods/<int:id>', methods=['DELETE'])
def delete_baked_good(id):
    baked_good = BakedGood.query.filter_by(id=id).first()
    if not baked_good:
        return make_response({'error': 'Baked good not found'}, 404)

    payload = baked_good.to_dict()
    db.session.delete(baked_good)
    db.session.commit()
    return make_response(payload, 200)


@app.route('/baked_goods/by_price')
def baked_goods_by_price():
    baked_goods_by_price = BakedGood.query.order_by(BakedGood.price.desc()).all()
    baked_goods_by_price_serialized = [
        bg.to_dict() for bg in baked_goods_by_price
    ]
    return make_response(baked_goods_by_price_serialized, 200)


@app.route('/baked_goods/most_expensive')
def most_expensive_baked_good():
    most_expensive = BakedGood.query.order_by(BakedGood.price.desc()).limit(1).first()
    most_expensive_serialized = most_expensive.to_dict()
    return make_response(most_expensive_serialized, 200)


if __name__ == '__main__':
    app.run(port=5555, debug=True)