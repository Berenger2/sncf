from flask import Flask, request, jsonify
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId
import os
from dotenv import load_dotenv
from copy import deepcopy

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
        my_data = col_objets.find({}, fiels).limit(1000)
        datas = [data for data in my_data]
        for data in datas:
            data['_id'] = str(data['_id'])
        return jsonify(datas), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "Oups erreurs"}), 500


@app.route('/datas_f')
def all_data():
    try:
        fiels = {
            "gc_obo_date_heure_restitution_c": 1,
            "gc_obo_gare_origine_r_name": 1,
            "gc_obo_gare_origine_r_code_uic_c": 1,
            "gc_obo_nom_recordtype_sc_c": 1
        }
        my_data = col_objets.find({}, fiels)
        datas = [data for data in my_data]
        for data in datas:
            data['_id'] = str(data['_id'])
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
        data_copy = deepcopy(data)
        for key, value in data_copy.items():
            if 'gc_obo_date_heure_restitution_c' not in data:
                data_copy['gc_obo_date_heure_restitution_c'] = None

            if isinstance(value, set):
                data[key] = list(value)

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
    gare = request.args.get('gare')
    if not gare:
        return jsonify({'message': 'Veuillez fournir le nom de la gare.'}), 400
    try:
        objets = list(col_objets.find({
            'gc_obo_gare_origine_r_name': gare
        }))
        for obj in objets:
            obj['_id'] = str(obj['_id'])
        return jsonify({'objets': objets})
    except Exception as e:
        print(e)
        return jsonify({"message": "Oups une erreur"}), 500


@app.route('/search_cat', methods=['GET'])
def search_cat():
    category = request.args.get('category')
    if not category:
        return jsonify({'message': 'Veuillez fournir une catégorie.'}), 400
    try:
        objects = list(col_objets.find({'gc_obo_type_c': category}))
        for obj in objects:
            obj['_id'] = str(obj['_id'])

        return jsonify({'objects': objects})
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
        return jsonify({'get_gares_list': list_gare}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "Oups une erreurs"}), 500


@app.route('/sum_object', methods=['GET'])
def sum_object():
    try:
        sum_objects = col_objets.count_documents({})
        return jsonify({'objects': sum_objects}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "Oups une erreur"}), 500


@app.route('/sum_gares', methods=['GET'])
def sum_gare():
    try:
        sum_gares = col_objets.distinct('gc_obo_gare_origine_r_name')
        return jsonify({'sum_gares': len(sum_gares)}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "Oups une erreur"}), 500


@app.route('/sum_types', methods=['GET'])
def sum_type():
    try:
        sum_types = col_objets.distinct('gc_obo_type_c')
        return jsonify({'sum_types': len(sum_types)}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "Oups une erreur"}), 500


@app.route('/sum_obj_gare', methods=['GET'])
def sum_obj_gare():
    dat_obj_gar = col_objets.find({}).limit(3000)
    sum_ob_gar = {}
    for objet in dat_obj_gar:
        gare = objet['gc_obo_gare_origine_r_name']
        sum_ob_gar[gare] = sum_ob_gar.get(gare, 0) + 1

    return jsonify(sum_ob_gar)


@app.route('/top_gares', methods=['GET'])
def top_gares():
    dat_obj_gar = col_objets.find({}).limit(3000)
    sum_ob_gar = {}
    for objet in dat_obj_gar:
        gare = objet['gc_obo_gare_origine_r_name']
        sum_ob_gar[gare] = sum_ob_gar.get(gare, 0) + 1

    my_top_gare = sorted(sum_ob_gar.items(), key=lambda x: x[1], reverse=True)[:10]

    return jsonify(my_top_gare)