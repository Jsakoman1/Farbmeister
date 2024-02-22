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

class Lieferanten:
    def __init__(self, name, adresse, note, verpackung, masse_x, masse_y, masse_z, masse_xyz, gewicht, kontakt, b_kontakt):
        self.name = name
        self.adresse = adresse
        self.note = note
        self.verpackung = verpackung
        self.masse_x = float(masse_x) if masse_x else None
        self.masse_y = float(masse_y) if masse_y else None
        self.masse_z = float(masse_z) if masse_z else None
        self.masse_xyz = float(masse_xyz) if masse_xyz else None
        self.gewicht = gewicht
        self.kontakt = kontakt
        self.b_kontakt = b_kontakt




class FarbmeisterApp:
    def __init__(self, inventar_file='inventar.json', lieferanten_file='lieferanten.json'):
        self.inventar_file = inventar_file
        self.lieferanten_file = lieferanten_file
        self.inventar_file_path = os.path.join(os.path.dirname(__file__), inventar_file)
        self.lieferanten_file_path = os.path.join(os.path.dirname(__file__), lieferanten_file)
        self.load_and_sort_inventar()
        self.load_lieferanten_data()
        self.check_json_files()  # Check and create JSON files if they don't exist

    def check_json_files(self):
        json_files = [self.inventar_file_path, self.lieferanten_file_path]
        for file_path in json_files:
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump([], f)


    def extract_numeric_parts(self, elco_nummer_part):
        try:
            if elco_nummer_part is not None:
                cleaned_part = elco_nummer_part.replace(" ", "")  # Remove whitespace
                return int(cleaned_part)
        except ValueError:
            return float('inf')

    def load_and_sort_inventar(self):
        try:
            with open(self.inventar_file_path, 'r') as file:
                inventar_data = [Rasterwalze(**item) for item in json.load(file)]
        except FileNotFoundError:
            print(f'File not found: {self.inventar_file_path}. Creating a new one.')
            inventar_data = []
        except json.decoder.JSONDecodeError:
            print(f'Error decoding JSON in file: {self.inventar_file_path}. Creating a new one.')
            inventar_data = []
        self.inventar_data = sorted(inventar_data, key=lambda item: ''.join(c for c in str(item.ELCO_Nummer) if not c.isspace()) if item.ELCO_Nummer is not None else 'x')

    def save_inventar(self):
        with open(self.inventar_file_path, 'w') as file:
            json.dump([vars(item) for item in self.inventar_data], file, indent=2)
        print(f'Inventar saved to {self.inventar_file_path}.')

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

    def load_lieferanten_data(self):
        try:
            with open(self.lieferanten_file_path, 'r') as file:
                lieferanten_data = json.load(file)['lieferanten']
                for lieferant in lieferanten_data:
                    self.lieferanten_data = lieferanten_data
        except FileNotFoundError:
            print(f'File not found: {self.lieferanten_file_path}. Initializing an empty list.')
            self.lieferanten_data = []

    def save_lieferanten_data(self):
        with open(self.lieferanten_file_path, 'w') as file:
            json.dump({'lieferanten': self.lieferanten_data}, file, indent=2)
        print(f'Lieferanten data saved to {self.lieferanten_file_path}.')

    def add_lieferant(self, lieferant):
        self.lieferanten_data.append(lieferant)
        self.save_lieferanten_data()
        self.create_lieferant_file(lieferant['name'])

    def create_lieferant_file(self, name):
    # Create a JSON file for the given Lieferant name if it doesn't exist
        file_name = f"{name}.json"
        full_path = os.path.join(os.path.dirname(__file__), file_name)  # Use the directory of app.py
        if not os.path.exists(full_path):
            with open(full_path, 'w') as f:
                json.dump([], f)

    def delete_lieferant_and_json(self, name):
    # Find the Lieferant based on the name
        lieferant = self.find_lieferant_by_name(name)

        if lieferant is not None:
        # Remove the Lieferant from the list
            self.lieferanten_data.remove(lieferant)
            # Save the updated Lieferanten data
            self.save_lieferanten_data()

            # Delete the corresponding JSON file
            json_filename = f"{name}.json"
            full_path_json = os.path.join(os.path.dirname(__file__), json_filename)  # Use the directory of app.py
            if os.path.exists(full_path_json):
                os.remove(full_path_json)
                print(f"Deleted {json_filename}.")

        return redirect(url_for('show_lieferanten'))

    def find_lieferant_by_name(self, name):  # Move this method inside the class
        for lieferant in self.lieferanten_data:
            if lieferant['name'] == name:
                return lieferant
        return None

    def update_lieferant_by_name(self, name, form_data):  # Move this method inside the class
        for lieferant in self.lieferanten_data:
            if lieferant['name'] == name:
                # Update Lieferant data
                lieferant.update({
                    "name": form_data.get('name'),  # Update the name field
                    "adresse": form_data.get('adresse'),
                    "note": form_data.get('note'),
                    "verpackung": form_data.get('verpackung'),
                    "masse_x": form_data.get('masse_x'),
                    "masse_y": form_data.get('masse_y'),
                    "masse_z": form_data.get('masse_z'),
                    "masse_xyz": form_data.get('masse_xyz'),
                    "gewicht": form_data.get('gewicht'),
                    "kontakt": form_data.get('kontakt'),
                    "b_kontakt": form_data.get('b_kontakt')
                })
                break




app = Flask(__name__)


farbmeister_app = FarbmeisterApp()

@app.context_processor
def inject_lieferanten_data():
    # Load the lieferanten data here
    farbmeister_app.load_lieferanten_data()
    return dict(lieferanten_data=farbmeister_app.lieferanten_data)


# Update the index route in your Flask application
@app.route('/')
def index():
    farbmeister_app.load_lieferanten_data()
    farbmeister_app.load_and_sort_inventar()



    # Pass the inventory data, lieferanten data, and the number of rows to the template
    return render_template('index.html', inventar_data=farbmeister_app.inventar_data,
                           lieferanten_data=farbmeister_app.lieferanten_data)


@app.route('/memo')
def memo():
    farbmeister_app.load_lieferanten_data()
    return render_template('memo.html',lieferanten_data=farbmeister_app.lieferanten_data)


@app.route('/add_item_page')
def add_item_page():
    farbmeister_app.load_lieferanten_data()
    return render_template('add_item.html',lieferanten_data=farbmeister_app.lieferanten_data)

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




def load_json_data(file_name):
    # Get the directory where the Python script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, file_name)

    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        return None
    except Exception as e:
        return None

def save_json_data(data, file_name):
    # Get the directory where the Python script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, file_name)

    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        pass





@app.route('/lieferanten', methods=['GET'])
def show_lieferanten():

    return render_template('lieferanten.html', lieferanten_data=farbmeister_app.lieferanten_data)

@app.route('/lieferanten/add', methods=['GET'])
def add_lieferant_page():
    farbmeister_app.load_lieferanten_data()
    

    return render_template('add_lieferant.html',lieferanten_data=farbmeister_app.lieferanten_data)

@app.route('/lieferanten/add', methods=['GET', 'POST'])
def add_lieferant():
    farbmeister_app.load_lieferanten_data()
    if request.method == 'POST':

        lieferant = {
            "name": request.form.get('name'),
            "adresse": request.form.get('adresse'),
            "note": request.form.get('note'),
            "verpackung": request.form.get('verpackung'),
            "kontakt": request.form.get('kontakt'),
            "b_kontakt": request.form.get('b_kontakt'),
            "verpackung": "",
            "masse_x": "",
            "masse_y": "",
            "masse_z": "",
            "masse_xyz": "",
            "gewicht": "",
        }
        farbmeister_app.add_lieferant(lieferant)
        return redirect(url_for('show_lieferanten'))  # Redirect to the show_lieferanten route
    else:
        # If the request method is GET, render the add_lieferant.html template
        return render_template('add_lieferant.html',lieferanten_data=farbmeister_app.lieferanten_data)


@app.route('/lieferanten/edit/<string:name>', methods=['GET'])
def edit_lieferant_page(name):
    farbmeister_app.load_lieferanten_data()
    # Find the Lieferant based on the name
    lieferant = farbmeister_app.find_lieferant_by_name(name)
    return render_template('edit_lieferant.html', lieferant=lieferant,lieferanten_data=farbmeister_app.lieferanten_data)


@app.route('/lieferanten/edit/<string:name>', methods=['GET', 'POST'])
def edit_lieferant(name):
    farbmeister_app.load_lieferanten_data()
    # Find the Lieferant based on the name
    lieferant = farbmeister_app.find_lieferant_by_name(name)

    if lieferant is None:
        return redirect(url_for('show_lieferanten'))

    if request.method == 'POST':
        # Update the Lieferant data based on form inputs
        lieferant['name'] = request.form.get('name')
        lieferant['adresse'] = request.form.get('adresse')
        lieferant['note'] = request.form.get('note')
        lieferant['kontakt'] = request.form.get('kontakt')
        lieferant['b_kontakt'] = request.form.get('b_kontakt')

        # Save the updated Lieferanten data
        farbmeister_app.save_lieferanten_data()

        # Rename the JSON file if the name has changed
        new_name = request.form.get('name')
        if new_name != name:
            old_filename = f"{name}.json"
            new_filename = f"{new_name}.json"
            old_file_path = os.path.join(os.path.dirname(__file__), old_filename)
            new_file_path = os.path.join(os.path.dirname(__file__), new_filename)
            if os.path.exists(old_file_path):
                os.rename(old_file_path, new_file_path)

        return redirect(url_for('show_lieferanten'))  # Redirect to the show_lieferanten route

    return render_template('edit_lieferant.html', lieferant=lieferant,lieferanten_data=farbmeister_app.lieferanten_data)




@app.route('/lieferanten/delete/<string:name>', methods=['POST'])
def delete_lieferant(name):
    return farbmeister_app.delete_lieferant_and_json(name)

@app.route('/lieferant/<lieferant_name>')
def lieferant_page(lieferant_name):
    lieferant_data = load_json_data(f"{lieferant_name}.json")
    lieferanten_data = load_json_data("lieferanten.json")["lieferanten"]
    return render_template('lieferant_page.html', lieferant_name=lieferant_name, lieferant_data=lieferant_data, lieferanten_data=lieferanten_data)

@app.route('/delete_item_lieferant/<lieferant_name>/<elco_nummer_delete>', methods=['POST'])
def delete_item_lieferant(lieferant_name, elco_nummer_delete):
    lieferant_data = load_json_data(f"{lieferant_name}.json")
    lieferant_data = [item for item in lieferant_data if item['ELCO_Nummer'] != elco_nummer_delete]
    save_json_data(lieferant_data, f"{lieferant_name}.json")
    return redirect(url_for('lieferant_page', lieferant_name=lieferant_name))

@app.route('/to_lieferant/<lieferant_name>', methods=['POST'])
def to_lieferant(lieferant_name):
    if request.method == 'POST':
        elco_nummer = request.form.get('elco_nummer')  # Assuming elco_nummer is submitted via form data

        # Load data for the specific lieferant
        lieferant_data = load_json_data(f"{lieferant_name}.json")

        # Check if the ELCO number already exists in the lieferant data
        if any(item['ELCO_Nummer'] == elco_nummer for item in lieferant_data):
            return redirect(url_for('lieferant_page', lieferant_name=lieferant_name))

        # Retrieve item from inventory data
        item_from_inventory = next((item for item in farbmeister_app.inventar_data if item.ELCO_Nummer == elco_nummer), None)
        if item_from_inventory:
            # Append the item to the lieferant data
            lieferant_data.append({
                "ELCO_Nummer": item_from_inventory.ELCO_Nummer,
                "Maschine": item_from_inventory.Maschine,
                "Mass": item_from_inventory.Mass,
                "Produktion_Nummer": item_from_inventory.Produktion_Nummer,
                "L_cm": item_from_inventory.L_cm,
                "my": item_from_inventory.my,
                "cm3": item_from_inventory.cm3,
                "seitl_rand": "",
                "qual": "",
                "schutzring": "",
                "text": "",
                "bemerkung": "",
                "datum": ""
            })
            save_json_data(lieferant_data, f"{lieferant_name}.json")

    # Redirect to the corresponding lieferant page after processing
    return redirect(url_for('lieferant_page', lieferant_name=lieferant_name))

@app.route('/save_changes_lieferant/<lieferant_name>', methods=['POST'])
def save_changes_lieferant(lieferant_name):
    data = request.json

    lieferant_data = load_json_data(f"{lieferant_name}.json")

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
        for item in lieferant_data:
            if item['ELCO_Nummer'] == elco_num:
                # Update the specified field
                item[field] = value
                break

    # Save the updated data back to the lieferant file
    save_json_data(lieferant_data, f"{lieferant_name}.json")

    # Return the updated data as a response
    return jsonify(lieferant_data)



@app.route('/lieferant_auftrag/<lieferant_name>')
def lieferant_auftrag(lieferant_name):
    try:
        # Load the data for the specified Lieferant
        lieferant_data = load_json_data(f"{lieferant_name}.json")
        lieferant = None
        lieferanten_data = load_json_data("lieferanten.json")["lieferanten"]  # Load lieferanten data
        # Find the lieferant with the specified name
        for item in lieferanten_data:
            if item["name"] == lieferant_name:
                lieferant = item
                break

        if lieferant:
            # Pass the data to the template for rendering
            return render_template('lieferant_auftrag.html', lieferant_name=lieferant_name, lieferant_data=lieferant_data, lieferant=lieferant)
        else:
            return "Lieferant not found."

    except Exception as e:
        # Handle any exceptions or errors
        print(f"An error occurred: {str(e)}")
        return "An error occurred while loading data."


@app.route('/lieferant_begleitschein/<lieferant_name>')
def lieferant_begleitschein(lieferant_name):
    try:
        # Load the data for the specified Lieferant
        lieferant_data = load_json_data(f"{lieferant_name}.json")
        lieferant = None
        lieferanten_data = load_json_data("lieferanten.json")["lieferanten"]  # Load lieferanten data
        # Find the lieferant with the specified name
        for item in lieferanten_data:
            if item["name"] == lieferant_name:
                lieferant = item
                break

        if lieferant:
            # Pass the data to the template for rendering
            return render_template('lieferant_begleitschein.html', lieferant_name=lieferant_name, lieferant_data=lieferant_data, lieferant=lieferant)
        else:
            return "Lieferant not found."

    except Exception as e:
        # Handle any exceptions or errors
        print(f"An error occurred: {str(e)}")
        return "An error occurred while loading data."





if __name__ == "__main__":

    app.run(host='0.0.0.0', port=5005)




