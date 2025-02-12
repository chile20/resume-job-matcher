from app import create_app
import os
from dotenv import load_dotenv

load_dotenv()
app = create_app()
# app.secret_key = os.environ.get('SECRET_KEY')

# Handling missing CSS
@app.route('/styles.css')
@app.route('/styles.css.map')
def handle_missing_css():
    return "This resource is not used.", 200

if __name__ == '__main__':
    app.run(debug=True)