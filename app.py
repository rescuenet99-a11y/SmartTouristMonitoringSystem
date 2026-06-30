from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__)

# Routes for each dashboard page
@app.route('/')
def home():
    # Redirect to admin dashboard as default
    return render_template('admin_dashboard.html')

@app.route('/admin')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/tourist')
def tourist_dashboard():
    return render_template('tourist_dashboard.html')

@app.route('/analytics')
def analytics():
    return render_template('analytics.html')

@app.route('/heatmaps')
def heatmaps():
    return render_template('heatmaps.html')

@app.route('/reports')
def reports():
    return render_template('reports.html')

# Serve static files (Flask does this automatically under /static)

if __name__ == '__main__':
    # Enable debug for development; production will use a proper WSGI server.
    app.run(debug=True, host='0.0.0.0', port=5000)
