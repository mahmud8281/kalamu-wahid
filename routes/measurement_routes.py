from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from extensions import db
from models.measurement_model import Measurement

measurement = Blueprint('measurement', __name__)

@measurement.route('/measurements')
@login_required
def view_measurements():
    m = Measurement.query.filter_by(user_id=current_user.id).first()
    return render_template('customer/measurements.html', measurement=m)

@measurement.route('/save-measurements', methods=['POST'])
@login_required
def save_measurements():
    m = Measurement.query.filter_by(user_id=current_user.id).first()
    fields = ['chest','shoulder','sleeve','waist','neck','hip','shirt_length','trouser_length']
    if m:
        for f in fields:
            setattr(m, f, request.form.get(f))
    else:
        m = Measurement(user_id=current_user.id)
        for f in fields:
            setattr(m, f, request.form.get(f))
        db.session.add(m)
    db.session.commit()
    flash('Measurements saved successfully.', 'success')
    return redirect(url_for('measurement.view_measurements'))