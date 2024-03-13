from flask import Flask, request, jsonify
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId
import os
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()
"""
DATA BASE
"""
mongodb_uri = os.getenv("MONGODB_URI")
sncf = MongoClient(mongodb_uri)
db = sncf.get_database()
col_objets = db['objets']

"""
ROUTES
"""


@app.route('/')
def home():
    return 'Application SNCF'


@app.route('/datas')
def get_all_data():
    try:
        fiels = {
            "date": 1,
            "gc_obo_date_heure_restitution_c": 1,
            "gc_obo_gare_origine_r_name": 1,
            "gc_obo_gare_origine_r_code_uic_c": 1,
            "gc_obo_nature_c": 1,
            "gc_obo_type_c": 1,
            "gc_obo_nom_recordtype_sc_c": 1
        }
        datas = col_objets.find_one({}, fiels)
        datas['_id'] = str(datas['_id'])
        return jsonify(datas), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "Oups erreurs"}), 500


@app.route('/rand_data')
def get_data_rand():
    try:
        pipeline = [{'$sample': {'size': 25}}]
        datas = list(col_objets.aggregate(pipeline))
        for data in datas:
            data['_id'] = str(data['_id'])
        return jsonify({'datas': datas}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "Oups erreurs"}), 500


@app.route('/add_data', methods=['POST'])
def add_data():
    data = request.json
    try:
        col_objets.insert_one(data)
        return jsonify({"message': 'Ajout d'un objet trouvé avec succès"}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "Une erreur s'est produite lors de la declaration d'objet trouvé"}), 500


@app.route('/data/<string:id>', methods=['GET'])
def get_one_data(id):
    try:
        data = col_objets.find_one({'_id': ObjectId(id)})
        data['_id'] = str(data['_id'])
        return jsonify({'donnee': data}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "Objet non trouvé"}), 404


@app.route('/data/<string:id>', methods=['PUT'])
def update_data(id):
    data = request.json
    col_objets.update_one({'_id': ObjectId(id)}, {'$set': data})
    return jsonify({"message": "Information de l'objet mis à jour avec succès"}), 200


@app.route('/data/<string:id>', methods=['DELETE'])
def delete_donnee(id):
    try:
        col_objets.delete_one({'_id': ObjectId(id)})
        return jsonify({'message': "Objet supprimé avec succès"})
    except Exception as e:
        print(e)
        return jsonify({"message": "Oups une erreur"}), 500


@app.route('/search', methods=['GET'])
def search():
    date = request.args.get('date')
    gare = request.args.get('gare')
    if not date or not gare:
        return jsonify({'message': 'Veuillez fournir une date et une gare.'}), 400
    try:
        date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S%z")
        objets = list(col_objets.find({
            'date': date,
            'gc_obo_gare_origine_r_name': gare
        }))
        return jsonify({'objets': objets})
    except Exception as e:
        print(e)
        return jsonify({"message": "Oups une erreur"}), 500

@app.route('/types', methods=['GET'])
def get_types():
    try:
        types = col_objets.distinct('gc_obo_type_c')
        return jsonify({'types': types}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "Oups une erreur."}), 500


@app.route('/gares_list', methods=['GET'])
def get_gares_list():
    try:
        list_gare = col_objets.distinct('gc_obo_gare_origine_r_name')
        return jsonify({'get_gares_list': list_gare}),200
    except Exception as e:
        print(e)
        return jsonify({"message": "Oups une erreurs"}), 500

