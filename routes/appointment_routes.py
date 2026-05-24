import urllib.parse
from flask import (Blueprint, render_template, request,
                   flash, redirect, url_for)
from flask_login import current_user, login_required
from extensions import db, limiter
from models.appointment_model import Appointment
from utils.notifications import notify_appointment
from utils.sanitize import clean

appointment_bp  = Blueprint('appointment_bp', __name__)
WHATSAPP_NUMBER = '2347082815719'

SERVICES = [
    'Body Measurement Session',
    'Tailoring Consultation',
    'Style Selection',
    'Fabric Selection',
    'Fitting Session',
    'Order Pickup',
]

TIME_SLOTS = [
    '08:00 AM', '09:00 AM', '10:00 AM', '11:00 AM',
    '12:00 PM', '01:00 PM', '02:00 PM', '03:00 PM',
    '04:00 PM', '05:00 PM',
]

@appointment_bp.route('/appointment', methods=['GET', 'POST'])
@limiter.limit('10 per hour')
def book_appointment():
    if request.method == 'POST':
        name         = clean(request.form.get('name', ''))
        phone        = clean(request.form.get('phone', ''))
        email        = clean(request.form.get('email', ''))
        date         = clean(request.form.get('date', ''))
        time         = clean(request.form.get('time', ''))
        service_type = clean(request.form.get('service_type', ''))
        notes        = clean(request.form.get('notes', ''))

        if not name or not phone or not date or not time or not service_type:
            flash('Please fill in all required fields.', 'danger')
            return redirect(url_for('appointment_bp.book_appointment'))

        if service_type not in SERVICES:
            flash('Invalid service type selected.', 'danger')
            return redirect(url_for('appointment_bp.book_appointment'))

        if time not in TIME_SLOTS:
            flash('Invalid time slot selected.', 'danger')
            return redirect(url_for('appointment_bp.book_appointment'))

        existing = Appointment.query.filter_by(
            date=date, time=time, status='Confirmed'
        ).first()
        if existing:
            flash('That slot is already booked. Please choose another.',
                  'danger')
            return redirect(url_for('appointment_bp.book_appointment'))

        a = Appointment(
            user_id      = current_user.id
                           if current_user.is_authenticated else None,
            name         = name,
            phone        = phone,
            email        = email,
            date         = date,
            time         = time,
            service_type = service_type,
            notes        = notes,
            status       = 'Pending'
        )
        db.session.add(a)
        db.session.commit()

        notify_appointment(a)

        msg = (
            f"📅 *NEW APPOINTMENT — Kalamu Wahid*\n\n"
            f"👤 *Name:* {name}\n"
            f"📞 *Phone:* {phone}\n"
            f"📧 *Email:* {email or 'Not provided'}\n\n"
            f"🗓️ *Date:* {date}\n"
            f"⏰ *Time:* {time}\n"
            f"🧵 *Service:* {service_type}\n\n"
            f"📌 *Notes:* {notes or 'None'}"
        )
        wa_url = (f"https://wa.me/{WHATSAPP_NUMBER}?"
                  f"text={urllib.parse.quote(msg)}")

        flash('Appointment booked successfully!', 'success')
        return render_template('appointment/confirm.html',
                               appointment = a,
                               wa_url      = wa_url)

    booked       = Appointment.query.filter_by(status='Confirmed').all()
    booked_slots = [{'date': b.date, 'time': b.time} for b in booked]

    return render_template('appointment/book.html',
                           services     = SERVICES,
                           time_slots   = TIME_SLOTS,
                           booked_slots = booked_slots)

@appointment_bp.route('/my-appointments')
@login_required
def my_appointments():
    appointments = Appointment.query.filter_by(
        user_id=current_user.id
    ).order_by(Appointment.created_at.desc()).all()
    return render_template('appointment/my_appointments.html',
                           appointments=appointments)

@appointment_bp.route('/admin/appointments')
@login_required
def admin_appointments():
    if not current_user.is_admin():
        flash('Admin access required.', 'danger')
        return redirect(url_for('auth.login'))
    status = request.args.get('status', 'all')[:20]
    query  = Appointment.query
    if status != 'all':
        query = query.filter_by(status=status)
    appointments = query.order_by(
        Appointment.date, Appointment.time).all()
    return render_template('appointment/admin_appointments.html',
                           appointments   = appointments,
                           current_status = status)

@appointment_bp.route('/admin/appointments/update/<int:appt_id>',
                      methods=['POST'])
@login_required
def update_appointment(appt_id):
    if not current_user.is_admin():
        flash('Admin access required.', 'danger')
        return redirect(url_for('auth.login'))
    a        = Appointment.query.get_or_404(appt_id)
    a.status = clean(request.form.get('status', ''))
    db.session.commit()
    flash(f'Appointment #{appt_id} updated to {a.status}.', 'success')
    return redirect(url_for('appointment_bp.admin_appointments'))

@appointment_bp.route('/admin/appointments/delete/<int:appt_id>',
                      methods=['POST'])
@login_required
def delete_appointment(appt_id):
    if not current_user.is_admin():
        flash('Admin access required.', 'danger')
        return redirect(url_for('auth.login'))
    a = Appointment.query.get_or_404(appt_id)
    db.session.delete(a)
    db.session.commit()
    flash('Appointment deleted.', 'success')
    return redirect(url_for('appointment_bp.admin_appointments'))