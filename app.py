import json
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for

class Rasterwalze:
    def __init__(self, Maschine, Mass, Elco_Nummer, Produktion_Nummer, L_cm, my, cm3, wo, erneuert, int_ausgang, int_eingang, bemerkung, prod_nr_2, alte_nummer, Cheshire, Apex, Praxair, Ersetzt):
        self.Maschine = Maschine
        self.Mass = Mass
        self.ELCO_Nummer = Elco_Nummer
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

@app.route('/')
def index():
    farbmeister_app.load_and_sort_inventar()
    return render_template('index.html', inventar_data=farbmeister_app.inventar_data)

@app.route('/add_item', methods=['POST'])
def add_item():
    item = {
        "Maschine": request.form['maschine'],
        "Mass": request.form['mass'],
        "ELCO_Nummer": request.form["elco_nummer"],
        "Produktion_Nummer": request.form['produktion_nummer'],
        "L_cm": request.form['l_cm'],
        "my": request.form['my'] if request.form['my'] else None,
        "cm3": request.form['cm3']
    }

    farbmeister_app.add_item(item)
    return redirect(url_for('index'))

@app.route('/delete_item/<elco_nummer>', methods=['POST'])
def delete_item(elco_nummer):
    farbmeister_app.delete_item(elco_nummer)
    return redirect(url_for('index'))

@app.route('/pass', methods=['GET', 'POST'])
def pass_page():
    if request.method == 'POST':
        # Get the item elco_nummer from the form data
        elco_nummer = request.form['elco_nummer']

        # Retrieve the specific item from the inventory data
        item_to_pass = next((item for item in farbmeister_app.inventar_data if item.ELCO_Nummer == elco_nummer), None)

        if item_to_pass:
            # Render the 'pass.html' template with the item data
            return render_template('pass.html', item=item_to_pass)

    # If the request method is not POST or the item was not found, redirect to the main page
    return redirect(url_for('index'))

@app.route('/magnet', methods=['GET', 'POST'])
def magnet_page():
    if request.method == 'POST':
        # Get the item elco_nummer from the form data
        elco_nummer = request.form['elco_nummer']

        # Retrieve the specific item from the inventory data
        item_for_magnet = next((item for item in farbmeister_app.inventar_data if item.ELCO_Nummer == elco_nummer), None)

        if item_for_magnet:
            # Add a default_date field to the item containing today's date
            item_for_magnet.default_date = datetime.now().strftime('%d.%m.%Y')

            # Render the 'magnet.html' template with the item data
            return render_template('magnet.html', item=item_for_magnet)

    # If the request method is not POST or the item was not found, redirect to the main page
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True, port=5001)
