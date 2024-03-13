from flask import Flask, request, jsonify
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
        return jsonify(datas)
    except Exception as e:
        print(e)
        return jsonify({"message": "Oups erreurs"})


@app.route('/rand_data')
def get_data_rand():
    try:
        pipeline = [{'$sample': {'size': 25}}]
        datas = list(col_objets.aggregate(pipeline))
        for data in datas:
            data['_id'] = str(data['_id'])
        return jsonify({'datas': datas})
    except Exception as e:
        print(e)
        return jsonify({"message": "Oups erreurs"})


@app.route('/add_data', methods=['POST'])
def add_data():
    data = request.json
    try:
        col_objets.insert_one(data)
        return jsonify({"message': 'Ajout d'un objet trouvé avec succès"})
    except Exception as e:
        print(e)
        return jsonify({"message": "Une erreur s'est produite lors de la declaration d'objet trouvé"})


@app.route('/data/<string:id>', methods=['GET'])
def get_one_data(id):
    try:
        data = col_objets.find_one({'_id': ObjectId(id)})
        data['_id'] = str(data['_id'])
        return jsonify({'donnee': data})
    except Exception as e:
        print(e)
        return jsonify({"message": "Objet non trouvé"})


@app.route('/data/<string:id>', methods=['PUT'])
def update_data(id):
    data = request.json
    col_objets.update_one({'_id': ObjectId(id)}, {'$set': data})
    return jsonify({"message": "Information de l'objet mis à jour avec succès"})


@app.route('/data/<string:id>', methods=['DELETE'])
def delete_donnee(id):
    try:
        col_objets.delete_one({'_id': ObjectId(id)})
        return jsonify({'message': "Objet supprimé avec succès"})
    except Exception as e:
        print(e)
        return jsonify({"message": "Oups une erreur"})

