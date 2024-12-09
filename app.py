from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['house_management']
cauan = db['cauan']
cau_sieu = db['cau_sieu']

@app.route('/')
def index():
    return redirect(url_for('cauan_page'))

@app.route('/cauan')
def cauan_page():
    all_records = cauan.find()
    return render_template('prayer_book.html', 
                         records=all_records, 
                         active_tab='cauan', 
                         book_type='cauan',
                         search_performed=False)

@app.route('/cau_sieu')
def cau_sieu_page():
    all_records = cau_sieu.find()
    return render_template('prayer_book.html', 
                         records=all_records, 
                         active_tab='cau_sieu', 
                         book_type='cau_sieu',
                         search_performed=False)

@app.route('/add_record/<book_type>', methods=['POST'])
def add_record(book_type):
    record_name = request.form.get('record_name')
    collection = cauan if book_type == 'cauan' else cau_sieu
    collection.insert_one({'name': record_name, 'members': []})
    return redirect(url_for(f'{book_type}_page'))

@app.route('/find_record/<book_type>', methods=['GET'])
def find_record(book_type):
    record_name = request.args.get('record_name')
    collection = cauan if book_type == 'cauan' else cau_sieu
    found_records = collection.find({'name': {'$regex': record_name, '$options': 'i'}})
    return render_template('prayer_book.html', 
                         records=found_records, 
                         book_type=book_type, 
                         active_tab=book_type,
                         search_performed=True)

@app.route('/add_member/<book_type>/<record_id>', methods=['POST'])
def add_member_record(book_type, record_id):
    member_name = request.form.get('member_name')
    member_age = request.form.get('member_age')
    collection = cauan if book_type == 'cauan' else cau_sieu
    
    member_data = {
        'name': member_name,
        'age': int(member_age)
    }
    
    if book_type == 'cau_sieu':
        burial_place = request.form.get('burial_place')
        if burial_place:
            member_data['burial_place'] = burial_place
    
    collection.update_one(
        {'_id': ObjectId(record_id)},
        {'$push': {'members': member_data}}
    )
    return redirect(url_for(f'{book_type}_page'))

@app.route('/rename_record/<book_type>/<record_id>', methods=['POST'])
def rename_record(book_type, record_id):
    new_name = request.form.get('new_name')
    collection = cauan if book_type == 'cauan' else cau_sieu
    collection.update_one(
        {'_id': ObjectId(record_id)},
        {'$set': {'name': new_name}}
    )
    return redirect(url_for(f'{book_type}_page'))

@app.route('/delete_record/<book_type>/<record_id>')
def delete_record(book_type, record_id):
    collection = cauan if book_type == 'cauan' else cau_sieu
    collection.delete_one({'_id': ObjectId(record_id)})
    return redirect(url_for(f'{book_type}_page'))

@app.route('/find_member_record/<book_type>', methods=['GET'])
def find_member_record(book_type):
    member_name = request.args.get('member_name')
    collection = cauan if book_type == 'cauan' else cau_sieu
    found_records = collection.find({'members.name': {'$regex': member_name, '$options': 'i'}})
    return render_template('prayer_book.html', 
                         records=found_records, 
                         book_type=book_type, 
                         active_tab=book_type,
                         search_performed=True)

@app.route('/rename_member/<book_type>/<record_id>/<int:member_index>', methods=['POST'])
def rename_member(book_type, record_id, member_index):
    new_name = request.form.get('new_member_name')
    new_age = request.form.get('new_member_age')
    collection = cauan if book_type == 'cauan' else cau_sieu
    
    update_data = {
        f'members.{member_index}.name': new_name,
        f'members.{member_index}.age': int(new_age)
    }
    
    if book_type == 'cau_sieu':
        new_burial_place = request.form.get('new_burial_place')
        if new_burial_place:
            update_data[f'members.{member_index}.burial_place'] = new_burial_place
    
    collection.update_one(
        {'_id': ObjectId(record_id)},
        {'$set': update_data}
    )
    return redirect(url_for(f'{book_type}_page'))

@app.route('/delete_member/<book_type>/<record_id>/<int:member_index>')
def delete_member(book_type, record_id, member_index):
    collection = cauan if book_type == 'cauan' else cau_sieu
    collection.update_one(
        {'_id': ObjectId(record_id)},
        {'$unset': {f'members.{member_index}': 1}}
    )
    collection.update_one(
        {'_id': ObjectId(record_id)},
        {'$pull': {'members': None}}
    )
    return redirect(url_for(f'{book_type}_page'))

if __name__ == '__main__':
    app.run(debug=True)