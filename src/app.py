from flask import Flask

app = Flask(__name__)

"""
ROUTES
"""


@app.route('/')
def home():
    return 'Application SNCF'
