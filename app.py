from flask import Flask, render_template, request, jsonify, redirect, url_for
from main import main  # Import chatbot function from chatbot module
from helpers import get_initial_conversation_history, retrieve  # Import get_initial_conversation_history function from helpers module
from werkzeug.utils import secure_filename
import os

app = Flask(__name__, template_folder='./frontend/templates', static_folder='./frontend/static')

UPLOAD_FOLDER = 'uploaded_files'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route Webpages
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_page')
def upload_page():
    return render_template('upload.html')

@app.route('/betting_page')
def betting_page():
    return render_template('betting.html')
##### Finished Webpages


# Route Upload Docs
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Read the Excel file using pandas
            #excel_file = pd.read_excel(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Analyze the data from the Excel file
            #analysis = analyze_data(excel_file)

            # Save or display the analysis
            # ...

            return redirect(url_for('index'))

        return redirect(request.url)
    elif request.method == 'GET':
        return render_template('upload.html')



#def analyze_data(data):
    # Convert the Excel data to a CSV string
#    csv_data = data.to_csv(index=False)
    
    # Send the CSV data to the chatbot for analysis
#    analysis = analyze_with_chatbot(csv_data)

    #return analysis
###### Finished Upload

# Routes for chatbot and helpers
@app.route("/api/chat", methods=["POST"])
def api_chat():
    user_input = request.json["message"]
    # chatbot_response = chatbot(user_input)  # Call the chatbot function
    #return jsonify({"response": chatbot_response})
    response = main(user_input)

    chatbot_response = response["chatbot_response"]

    return jsonify(response=chatbot_response)

@app.route('/api/initial_conversation_history', methods=['GET'])
def api_initial_conversation_history():
    initial_conversation_history = get_initial_conversation_history()
    return jsonify(initial_conversation_history=initial_conversation_history)


@app.route('/api/retrieve', methods=['POST'])
def retrieve_route():
    data = request.json
    num_messages_to_fetch = data.get('num_messages_to_fetch', 5)
    recent_messages = retrieve(num_messages_to_fetch)
    return jsonify(recent_messages=recent_messages)



# All functions and things should go above this
if __name__ == "__main__":
    app.run(debug=True)