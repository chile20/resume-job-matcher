from app import create_app

app = create_app()

# Handling missing CSS
@app.route('/styles.css')
@app.route('/styles.css.map')
def handle_missing_css():
    return "This resource is not used.", 200

if __name__ == '__main__':
    app.run(debug=True)