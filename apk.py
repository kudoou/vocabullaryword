import os
from os.path import join, dirname
from dotenv import load_dotenv

from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
import requests
from datetime import datetime
from bson import ObjectId


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)

db = client[DB_NAME]

app = Flask(__name__)

# client = MongoClient('mongodb+srv://randhyar955:Ardiansyah955@cluster0.vr2df0r.mongodb.net/')
# db = client.dbword


@app.route('/')
def main():
    # Pada fungsi main dari app.py, lakukanlah query database pada kumpulan wordsuntuk menarik list penuh dari kata-kata 
    words_result = db.words.find({}, {'_id': False})
    # disini words sebagai variable yang menampung semua list
    # Kita perlu memodifikasi fungsi utama untuk menerima value msgpada string query
    words = []
    for word in words_result:
        definition = word['definitions'][0]['shortdef']
        definition = definition if type(definition) is str else definition[0]
        words.append({
            'word': word['word'],
            'definition': definition,
        })
        msg= request.args.get('msg')
    return render_template('index.html',words=words, msg=msg)

@app.route('/detail/<keyword>')
def detail(keyword):
    api_key = '25e04055-eb58-4447-906c-d32c3200310f'
    url = f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{keyword}?key={api_key}'
    response = requests.get(url)
    definitions = response.json()
    status = request.args.get('status_give', 'new')
    # Jika suatu kata tidak bisa ditemukan di kamus, mari kembali ke laman utama, dan munculkan popup kepada user berisi keterangan bahwa kata yang mereka cari tidak dapat ditemukan. Berikan saran juga kepada user kata yang bisa mereka coba.Jika suatu kata tidak bisa ditemukan di kamus, mari kembali ke laman utama, 
    # dan munculkan popup kepada user berisi keterangan bahwa kata yang mereka cari tidak dapat ditemukan. Berikan saran juga kepada user kata yang bisa mereka coba.
    if not definitions:
        return redirect(url_for(
            'error',
            word=keyword
        # 'main', ini menampilkan popup error yang menuju ke laman main
        # msg=f'Could not find {keyword}'
    ))
    if type(definitions[0]) is str:
        suggestions =','.join(definitions)
        return redirect(url_for(
            'error',
            word=keyword,
            suggestions=','.join(definitions)
            # 'main',
            # msg=f'Could not find {keyword}, did you mean {suggestions}?'
    ))
    return render_template(
        'detail.html',
        word=keyword,
        definitions=definitions,
        status=status
    )
    # return render_template("detail.html", word=keyword, definitions=definitions)

@app.route('/error')
def error():
    word = request.args.get('word')
    suggestions=request.args.get('suggestions')
    if suggestions:
        suggestions =suggestions.split(',')
        return render_template('error.html',word=word, suggestions=suggestions)

@app.route('/api/save_word', methods=['POST'])
def save_word():
    json_data = request.get_json()
    word = json_data.get('word_give')
    definitions =json_data.get('definitions_give')
    date = datetime.now().strftime('%Y-%m-%d')

    doc = {
        'word' : word,
        'definitions' :definitions,
        'date and time' : date 
    }
    db.words.insert_one(doc)
    #  This handler should save the word in the database
    return jsonify({'result': 'success', 
                    'msg': f'the word,{word}, was saved!!'})


@app.route('/api/delete_word', methods=['POST'])
def delete_word():
    word = request.form.get('word_give')
    db.words.delete_one({'word': word})
    db.examples.delete_many({'word':word})
    return jsonify({
        'result': 'success',
        'msg': f'your example for the word {word} was deleted'
    })
    #  This handler should delete the word from the database

@app.route('/api/get_exs', methods=['GET'])
def get_exs():
    word = request.args.get('word')
    example_data = db.examples.find({'word': word})
    examples = []
    for example in example_data:
        examples.append({
            'example' : example.get('example'),
            'id' :str(example.get('_id'))
        })
    return jsonify({'result': 'success', 'examples':examples})

@app.route('/api/save_ex', methods=['POST'])
def save_ex():
    word = request.form.get('word')
    example = request.form.get('example')

    doc ={
        'word' :word,
        'example':example,
    }
    db.examples.insert_one(doc)
    return jsonify({'result': 'success',
                    'msg' :f'your example, {example}, for the word, {word}, was saved'})

@app.route('/api/delete_ex', methods=['POST'])
def delete_ex():
    id = request.form.get('id')
    word = request.form.get('word')
    db.examples.delete_one({'_id':ObjectId(id)})
    return jsonify({'result': 'success',
                    'msg' :f'your word, {word}, was deleted!!'})

@app.route('/practise')
def practise():
    return render_template('practise.html')

if __name__ == '__main__':
    app.run('0.0.0.0',port=5000, debug=True)