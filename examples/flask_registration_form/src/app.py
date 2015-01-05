from flask import Flask, redirect, render_template, url_for, flash
from .form import RegistrationForm
app = Flask(__name__)
app.secret_key = 'notsecret'
app.debug = True

import json
import requests
# Sends JSON POST of registration data to localhost:8000
def post_registration(data):
    print 'POST registration data to localhost:8000'
    url = 'http://localhost:8000'
    headers = {'content-type': 'application/json'}
    res = requests.post(url, data=json.dumps(data), headers=headers)
    if not res.ok:
        raise Exception(res.reason)

@app.route('/', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.is_submitted():
        if form.validate_on_submit():
            print 'Registered:', str(form.data)
            try:
                post_registration(form.data)
            except Exception as e:
                flash('Response from RegistrationHandler: {0}'.format(e.message))
                return redirect(url_for('register'))
            print 'Successfully registered!'
            return redirect(url_for('success'))
        else:
            flash('Missing fields.')
            return redirect(url_for('register'))
    return render_template('form.html', form=form)

@app.route('/success')
def success():
    return 'Successfully registered! See terminal for output.'
