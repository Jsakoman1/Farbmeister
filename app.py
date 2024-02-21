import json
import os
import sys
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import sys

    
class Rasterwalze:
    def __init__(self, Maschine, Mass, ELCO_Nummer, Produktion_Nummer, L_cm, my, cm3, wo, erneuert, int_ausgang, int_eingang, bemerkung, prod_nr_2, alte_nummer, Cheshire, Apex, Praxair, Ersetzt):
        self.ELCO_Nummer = ELCO_Nummer
        self.Maschine = Maschine
        self.Mass = Mass
        self.Produktion_Nummer = Produktion_Nummer
        self.L_cm = L_cm
        self.my = my
        self.cm3 = cm3
        self.wo = wo
        self.erneuert = erneuert
        self.int_ausgang = int_ausgang
        self.int_eingang = int_eingang
        self.bemerkung = bemerkung
        self.prod_nr_2 = prod_nr_2
        self.alte_nummer = alte_nummer
        self.Cheshire = Cheshire
        self.Apex = Apex
        self.Praxair = Praxair
        self.Ersetzt = Ersetzt


class FarbmeisterApp:
    def __init__(self, inventar_file='inventar.json'):
        self.inventar_file = inventar_file
        self.load_and_sort_inventar()
        self.check_json_files()  # Check and create JSON files if they don't exist

    def check_json_files(self):
        json_files = ['APEX.json', 'TLS.json', 'Cheshire.json', 'Zecher.json', 'inventar.json']
        for file_name in json_files:
            if not os.path.exists(file_name):
                with open(file_name, 'w') as f:
                    json.dump([], f)

    def extract_numeric_parts(self, elco_nummer_part):
        try:
            if elco_nummer_part is not None:
                cleaned_part = elco_nummer_part.replace(" ", "")  # Remove whitespace
                return int(cleaned_part)
        except ValueError:
            return float('inf')

    def load_and_sort_inventar(self):
        # Load inventory data from the file
        try:
            with open(self.inventar_file, 'r') as file:
                inventar_data = [Rasterwalze(**item) for item in json.load(file)]
        except FileNotFoundError:
            print(f'File not found: {self.inventar_file}. Creating a new one.')
            inventar_data = []
        except json.decoder.JSONDecodeError:
            print(f'Error decoding JSON in file: {self.inventar_file}. Creating a new one.')
            inventar_data = []

        # Sort the inventory data character by character
        self.inventar_data = sorted(
            inventar_data,
            key=lambda item: ''.join(c for c in str(item.ELCO_Nummer) if not c.isspace()) if item.ELCO_Nummer is not None else 'x'
        )

    def save_inventar(self):
        # Save the data to the file without sorting again
        with open(self.inventar_file, 'w') as file:
            json.dump([vars(item) for item in self.inventar_data], file, indent=2)

        print(f'Inventar saved to {self.inventar_file}.')

    def show_inventar(self):
        print("Current Inventar:")
        for item in self.inventar_data:
            print(f"ELCO_Nummer: {item.ELCO_Nummer}, Maschine: {item.Maschine}, Mass: {item.Mass}")

    def add_item(self, item):
        new_item = Rasterwalze(**item)  # Create a Rasterwalze object
        self.inventar_data.append(new_item)
        self.save_inventar()

    def delete_item(self, elco_nummer):
        self.inventar_data = [item for item in self.inventar_data if item.ELCO_Nummer != elco_nummer]
        self.save_inventar()


app = Flask(__name__)


farbmeister_app = FarbmeisterApp()



# Route for displaying the GUI and serving the web pages
@app.route('/')
def index():
    farbmeister_app.load_and_sort_inventar()

    return render_template('index.html', inventar_data=farbmeister_app.inventar_data)



@app.route('/memo')
def memo():

    return render_template('memo.html')


@app.route('/add_item_page')
def add_item_page():
    return render_template('add_item.html')

@app.route('/add_item', methods=['POST'])
def add_item():
    print(request.form)
    item = {
        "ELCO_Nummer": request.form.get('elco_nummer', 'null'),
        "Maschine": request.form.get('maschine', 'null'),  
        "Mass": request.form.get('mass', 'null'),          
        "Produktion_Nummer": request.form.get('produktion_nummer', 'null'), 
        "L_cm": request.form.get('l_cm', 'null'),          
        "my": request.form.get('my', 'null'),              
        "cm3": request.form.get('cm3', 'null'),
        "wo": request.form.get('wo', 'null'),
        "erneuert": request.form.get('erneuert', 'null'),
        "int_ausgang": request.form.get('int_ausgang', 'null'),
        "int_eingang": request.form.get('int_eingang', 'null'),
        "bemerkung": request.form.get('bemerkung', 'null'),
        "prod_nr_2": request.form.get('prod_nr_2', 'null'),
        "alte_nummer": request.form.get('alte_nummer', 'null'),
        "Cheshire": request.form.get('Cheshire', 'null'),
        "Apex": request.form.get('Apex', 'null'),
        "Praxair": request.form.get('Praxair', 'null'),
        "Ersetzt": request.form.get('Ersetzt', 'null')
    }
    
    farbmeister_app.add_item(item)
    return redirect(url_for('index'))

@app.route('/check_elco_nummer_exists', methods=['POST'])
def check_elco_nummer_exists():
    elco_nummer = request.json.get('elco_nummer')

    # Check if the ELCO number already exists in your data
    elco_exists = False
    for item in farbmeister_app.inventar_data:
        if item.ELCO_Nummer == elco_nummer:
            elco_exists = True
            break

    # Return JSON response indicating whether the ELCO number exists
    return jsonify({'exists': elco_exists})

@app.route('/delete_item/<elco_nummer_delete>', methods=['POST'])
def delete_item(elco_nummer_delete):
    farbmeister_app.delete_item(elco_nummer_delete)
    return redirect(url_for('index'))

@app.route('/edit_item/<elco_nummer_edit>', methods=['GET', 'POST'])
def edit_item(elco_nummer_edit):
    # Find the item to edit based on elco_nummer
    item_to_edit = None
    for item in farbmeister_app.inventar_data:
        if item.ELCO_Nummer == elco_nummer_edit:
            item_to_edit = item
            break
    
    if item_to_edit is None:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        if elco_nummer_edit is not None and elco_nummer_edit.strip() != '':
            item_to_edit.ELCO_Nummer = request.form.get('elco_nummer', 'null')
            item_to_edit.Maschine = request.form.get('maschine', 'null')
            item_to_edit.Mass = request.form.get('mass', 'null')
            item_to_edit.Produktion_Nummer = request.form.get('produktion_nummer', 'null')
            item_to_edit.L_cm = request.form.get('l_cm', 'null')
            item_to_edit.my = request.form.get('my', 'null')
            item_to_edit.cm3 = request.form.get('cm3', 'null')
            item_to_edit.wo = request.form.get('wo', 'null')
            item_to_edit.erneuert = request.form.get('erneuert', 'null')
            item_to_edit.int_ausgang = request.form.get('int_ausgang', 'null')
            item_to_edit.int_eingang = request.form.get('int_eingang', 'null')
            item_to_edit.bemerkung = request.form.get('bemerkung', 'null')
            item_to_edit.prod_nr_2 = request.form.get('prod_nr_2', 'null')
            item_to_edit.alte_nummer = request.form.get('alte_nummer', 'null')
            item_to_edit.Cheshire = request.form.get('Cheshire', 'null')
            item_to_edit.Apex = request.form.get('Apex', 'null')
            item_to_edit.Praxair = request.form.get('Praxair', 'null')
            item_to_edit.Ersetzt = request.form.get('Ersetzt', 'null')


        farbmeister_app.save_inventar()
    
        return redirect(url_for('index'))

    return render_template('edit_item.html', item=item_to_edit)

@app.route('/pass', methods=['GET', 'POST'])
def pass_page():
    if request.method == 'POST':
        # Get the item elco_nummer from the form data
        elco_nummer_pass = request.form['elco_nummer_pass']

        # Retrieve the specific item from the inventory data
        item_to_pass = next((item for item in farbmeister_app.inventar_data if item.ELCO_Nummer == elco_nummer_pass), None)

        if item_to_pass:
            # Render the 'pass.html' template with the item data
            return render_template('pass.html', item=item_to_pass)

    # If the request method is not POST or the item was not found, redirect to the main page
    return redirect(url_for('index'))

@app.route('/magnet', methods=['GET', 'POST'])
def magnet_page():
    if request.method == 'POST':
        # Get the item elco_nummer from the form data
        elco_nummer_magnet = request.form['elco_nummer_magnet']

        # Retrieve the specific item from the inventory data
        item_for_magnet = next((item for item in farbmeister_app.inventar_data if item.ELCO_Nummer == elco_nummer_magnet), None)

        if item_for_magnet:
            # Pass today's date to the HTML template
            today_date = datetime.now().strftime('%d.%m.%Y')

            # Render the 'magnet.html' template with the item data and today's date
            return render_template('magnet.html', item=item_for_magnet, default_date=today_date)

    # If the request method is not POST or the item was not found, redirect to the main page
    return redirect(url_for('index'))



def load_json_data(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        return None
    except Exception as e:
        return None

def save_json_data(data, file_path):
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        pass




@app.route('/tls_page')
def tls_page():

        
    tls_data = load_json_data('TLS.json')
    return render_template('TLS.html', tls_data=tls_data)


@app.route('/tls_auftrag')
def tls_auftrag():
    tls_data = load_json_data('TLS.json')
    return render_template('TLS_Auftrag.html', tls_data=tls_data)

@app.route('/tls_begleitschein')
def tls_begleitschein():
    tls_data = load_json_data('TLS.json')
    return render_template('TLS_Begleitschein.html', tls_data=tls_data)



@app.route('/to_tls', methods=['POST'])
def to_tls():
    if request.method == 'POST':
        elco_nummer_tls = request.form['elco_nummer_tls']
        tls_data = load_json_data('TLS.json')

        # Check if ELCO number already exists
        if any(item['ELCO_Nummer'] == elco_nummer_tls for item in tls_data):
            return redirect(url_for('tls_page'))

        # Retrieve item from inventory data
        item_to_tls = next((item for item in farbmeister_app.inventar_data if item.ELCO_Nummer == elco_nummer_tls), None)
        if item_to_tls:
            tls_data.append({
                "ELCO_Nummer": item_to_tls.ELCO_Nummer,
                "Maschine": item_to_tls.Maschine,
                "Mass": item_to_tls.Mass,
                "Produktion_Nummer": item_to_tls.Produktion_Nummer,
                "L_cm": item_to_tls.L_cm,
                "my": item_to_tls.my,
                "cm3": item_to_tls.cm3,
                "seitl_rand": "", 
                "qual": "",
                "schutzring": "",
                "text": "",
                "bemerkung": "",
                "datum": ""
            })
            save_json_data(tls_data, 'TLS.json')

    return redirect(url_for('tls_page'))

@app.route('/delete_item_TLS/<elco_nummer_delete>', methods=['POST'])
def delete_item_TLS(elco_nummer_delete):
    tls_data = load_json_data('TLS.json')
    tls_data = [item for item in tls_data if item['ELCO_Nummer'] != elco_nummer_delete]
    save_json_data(tls_data, 'TLS.json')
    return redirect(url_for('tls_page'))

@app.route('/save_changes_TLS', methods=['POST'])
def save_changes_TLS():
    data = request.json


    tls_data = load_json_data('TLS.json')

    # Update the existing data with the changes sent from the client
    for change in data:
        elco_num = change['elcoNum']
        field = change['field']
        value = change['value']

        # Clean the cell value: remove leading and trailing whitespace
        value = value.strip()

        # Replace '\n' with empty string if the value consists only of whitespace characters
        if value == '\n':
            value = ''

        # Find the item with the corresponding ELCO_Nummer
        for item in tls_data:
            if item['ELCO_Nummer'] == elco_num:
                # Update the specified field
                item[field] = value
                break

    # Save the updated data back to the APEX.json file
    save_json_data(tls_data, 'TLS.json')

    # Return the updated data as a response
    return jsonify(tls_data)



@app.route('/to_apex', methods=['POST'])
def to_apex():
    if request.method == 'POST':
        elco_nummer_apex = request.form['elco_nummer_apex']
        apex_data = load_json_data('APEX.json')

        # Check if ELCO number already exists
        if any(item['ELCO_Nummer'] == elco_nummer_apex for item in apex_data):
            return redirect(url_for('apex_page'))

        # Retrieve item from inventory data
        item_to_apex = next((item for item in farbmeister_app.inventar_data if item.ELCO_Nummer == elco_nummer_apex), None)
        if item_to_apex:
            apex_data.append({
                "ELCO_Nummer": item_to_apex.ELCO_Nummer,
                "Maschine": item_to_apex.Maschine,
                "Mass": item_to_apex.Mass,
                "Produktion_Nummer": item_to_apex.Produktion_Nummer,
                "L_cm": item_to_apex.L_cm,
                "my": item_to_apex.my,
                "cm3": item_to_apex.cm3,
                "seitl_rand": "", 
                "qual": "",
                "schutzring": "",
                "text": "",
                "bemerkung": "",
                "datum": ""
            })
            save_json_data(apex_data, 'APEX.json')

    return redirect(url_for('apex_page'))

@app.route('/delete_item_APEX/<elco_nummer_delete>', methods=['POST'])
def delete_item_APEX(elco_nummer_delete):
    apex_data = load_json_data('APEX.json')
    apex_data = [item for item in apex_data if item['ELCO_Nummer'] != elco_nummer_delete]
    save_json_data(apex_data, 'APEX.json')
    return redirect(url_for('apex_page'))

@app.route('/save_changes_APEX', methods=['POST'])
def save_changes_APEX():
    data = request.json  # Get the JSON data sent from the client

    # Load the existing data from APEX.json
    apex_data = load_json_data('APEX.json')

    # Update the existing data with the changes sent from the client
    for change in data:
        elco_num = change['elcoNum']
        field = change['field']
        value = change['value']

        # Clean the cell value: remove leading and trailing whitespace
        value = value.strip()

        # Replace '\n' with empty string if the value consists only of whitespace characters
        if value == '\n':
            value = ''

        # Find the item with the corresponding ELCO_Nummer
        for item in apex_data:
            if item['ELCO_Nummer'] == elco_num:
                # Update the specified field
                item[field] = value
                break

    # Save the updated data back to the APEX.json file
    save_json_data(apex_data, 'APEX.json')

    # Return the updated data as a response
    return jsonify(apex_data)

@app.route('/apex_page')
def apex_page():

    apex_data = load_json_data('APEX.json')
    return render_template('APEX.html', apex_data=apex_data)


@app.route('/apex_auftrag')
def apex_auftrag():
    apex_data = load_json_data('APEX.json')
    return render_template('APEX_Auftrag.html', apex_data=apex_data)


@app.route('/apex_begleitschein')
def apex_begleitschein():
    apex_data = load_json_data('APEX.json')
    return render_template('APEX_Begleitschein.html', apex_data=apex_data)



@app.route('/cheshire_page')
def cheshire_page():

    cheshire_data = load_json_data('Cheshire.json')
    return render_template('Cheshire.html', cheshire_data=cheshire_data)


@app.route('/cheshire_auftrag')
def cheshire_auftrag():
    cheshire_data = load_json_data('CHESHIRE.json')
    return render_template('Cheshire_Auftrag.html', cheshire_data=cheshire_data)

@app.route('/cheshire_begleitschein')
def cheshire_begleitschein():
    cheshire_data = load_json_data('Cheshire.json')
    return render_template('Cheshire_Begleitschein.html', cheshire_data=cheshire_data)

@app.route('/to_cheshire', methods=['POST'])
def to_cheshire():
    if request.method == 'POST':
        elco_nummer_cheshire = request.form['elco_nummer_cheshire']
        cheshire_data = load_json_data('Cheshire.json')

        # Check if ELCO number already exists
        if any(item['ELCO_Nummer'] == elco_nummer_cheshire for item in cheshire_data):
            return redirect(url_for('cheshire_page'))

        # Retrieve item from inventory data
        item_to_cheshire= next((item for item in farbmeister_app.inventar_data if item.ELCO_Nummer == elco_nummer_cheshire), None)
        if item_to_cheshire:
            cheshire_data.append({
                "ELCO_Nummer": item_to_cheshire.ELCO_Nummer,
                "Maschine": item_to_cheshire.Maschine,
                "Mass": item_to_cheshire.Mass,
                "Produktion_Nummer": item_to_cheshire.Produktion_Nummer,
                "L_cm": item_to_cheshire.L_cm,
                "my": item_to_cheshire.my,
                "cm3": item_to_cheshire.cm3,
                "seitl_rand": "", 
                "qual": "",
                "schutzring": "",
                "text": "",
                "bemerkung": "",
                "datum": ""
            })
            save_json_data(cheshire_data, 'Cheshire.json')

    return redirect(url_for('cheshire_page'))

@app.route('/delete_item_Cheshire/<elco_nummer_delete>', methods=['POST'])
def delete_item_Cheshire(elco_nummer_delete):
    cheshire_data = load_json_data('Cheshire.json')
    cheshire_data = [item for item in cheshire_data if item['ELCO_Nummer'] != elco_nummer_delete]
    save_json_data(cheshire_data, 'Cheshire.json')
    return redirect(url_for('cheshire_page'))

@app.route('/save_changes_Cheshire', methods=['POST'])
def save_changes_Cheshire():
    data = request.json


    cheshire_data = load_json_data('Cheshire.json')


    for change in data:
        elco_num = change['elcoNum']
        field = change['field']
        value = change['value']


        value = value.strip()

        # Replace '\n' with empty string if the value consists only of whitespace characters
        if value == '\n':
            value = ''

        # Find the item with the corresponding ELCO_Nummer
        for item in cheshire_data:
            if item['ELCO_Nummer'] == elco_num:
                # Update the specified field
                item[field] = value
                break

    # Save the updated data back to the APEX.json file
    save_json_data(cheshire_data, 'Cheshire.json')

    # Return the updated data as a response
    return jsonify(cheshire_data)



@app.route('/zecher_page')
def zecher_page():
    zecher_data= load_json_data('Zecher.json')
    return render_template('Zecher.html', zecher_data=zecher_data)


@app.route('/zecher_auftrag')
def zecher_auftrag():
    zecher_data = load_json_data('Zecher.json')
    return render_template('Zecher_Auftrag.html', zecher_data=zecher_data)

@app.route('/zecher_begleitschein')
def zecher_begleitschein():
    zecher_data = load_json_data('Zecher.json')
    return render_template('Zecher_Begleitschein.html', zecher_data=zecher_data)



@app.route('/to_zecher', methods=['POST'])
def to_zecher():
    if request.method == 'POST':
        elco_nummer_zecher = request.form['elco_nummer_zecher']
        zecher_data = load_json_data('Zecher.json')

        # Check if ELCO number already exists
        if any(item['ELCO_Nummer'] == elco_nummer_zecher for item in zecher_data):
            return redirect(url_for('zecher_page'))

        # Retrieve item from inventory data
        item_to_zecher = next((item for item in farbmeister_app.inventar_data if item.ELCO_Nummer == elco_nummer_zecher), None)
        if item_to_zecher:
            zecher_data.append({
                "ELCO_Nummer": item_to_zecher.ELCO_Nummer,
                "Maschine": item_to_zecher.Maschine,
                "Mass": item_to_zecher.Mass,
                "Produktion_Nummer": item_to_zecher.Produktion_Nummer,
                "L_cm": item_to_zecher.L_cm,
                "my": item_to_zecher.my,
                "cm3": item_to_zecher.cm3,
                "seitl_rand": "", 
                "qual": "",
                "schutzring": "",
                "text": "",
                "bemerkung": "",
                "datum": ""
            })
            save_json_data(zecher_data, 'Zecher.json')

    return redirect(url_for('zecher_page'))

@app.route('/delete_item_Zecher/<elco_nummer_delete>', methods=['POST'])
def delete_item_Zecher(elco_nummer_delete):
    zecher_data = load_json_data('Zecher.json')
    zecher_data = [item for item in zecher_data if item['ELCO_Nummer'] != elco_nummer_delete]
    save_json_data(zecher_data, 'Zecher.json')
    return redirect(url_for('zecher_page'))

@app.route('/save_changes_Zecher', methods=['POST'])
def save_changes_Zecher():
    data = request.json  # Get the JSON data sent from the client


    zecher_data = load_json_data('Zecher.json')

    # Update the existing data with the changes sent from the client
    for change in data:
        elco_num = change['elcoNum']
        field = change['field']
        value = change['value']

        # Clean the cell value: remove leading and trailing whitespace
        value = value.strip()

        # Replace '\n' with empty string if the value consists only of whitespace characters
        if value == '\n':
            value = ''

        # Find the item with the corresponding ELCO_Nummer
        for item in zecher_data:
            if item['ELCO_Nummer'] == elco_num:
                # Update the specified field
                item[field] = value
                break


    save_json_data(zecher_data, 'Zecher.json')

    # Return the updated data as a response
    return jsonify(zecher_data)





if __name__ == '__main__':
    app.run(debug=True, port=5001)




 