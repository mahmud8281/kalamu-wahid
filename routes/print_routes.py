from flask import Blueprint, make_response, redirect, url_for, flash
from flask_login import login_required, current_user
from models.user_model import User
from models.measurement_model import Measurement
from models.product_model import WalkInCustomer, WalkInMeasurement
from models.order_model import Order
from models.product_model import ProductOrder
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                Paragraph, Spacer, HRFlowable)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime

print_bp = Blueprint('print_bp', __name__)

def admin_required_check():
    return current_user.is_authenticated and current_user.is_admin()


# ── shared colors ────────────────────────────────────────────
GREEN = colors.HexColor('#1B4332')
GOLD  = colors.HexColor('#C9A84C')
CREAM = colors.HexColor('#FDF8EF')
LGRAY = colors.HexColor('#F8FAFC')


def base_styles():
    return {
        'title': ParagraphStyle('title', fontSize=20,
                                fontName='Helvetica-Bold',
                                textColor=GOLD, alignment=TA_CENTER,
                                spaceAfter=4),
        'sub':   ParagraphStyle('sub', fontSize=10,
                                fontName='Helvetica',
                                textColor=GREEN, alignment=TA_CENTER,
                                spaceAfter=2),
        'note':  ParagraphStyle('note', fontSize=8,
                                fontName='Helvetica',
                                textColor=colors.gray,
                                alignment=TA_CENTER),
        'head':  ParagraphStyle('head', fontSize=11,
                                fontName='Helvetica-Bold',
                                textColor=GREEN, spaceAfter=6),
    }


def header_block(story, subtitle):
    s = base_styles()
    story.append(Paragraph('KALAMU WAHID TAILORING SYNERGY', s['title']))
    story.append(Paragraph(subtitle, s['sub']))
    story.append(Paragraph(
        'Kano, Nigeria  ·  WhatsApp: +234 800 000 0000', s['note']))
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width='100%', thickness=2, color=GOLD))
    story.append(Spacer(1, 0.4*cm))


def footer_block(story, message):
    s = base_styles()
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width='100%', thickness=1, color=GOLD))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(message, s['note']))
    story.append(Paragraph(
        f'Printed on {datetime.now().strftime("%d %B %Y at %I:%M %p")}',
        s['note']))


def info_table(data):
    t = Table(data, colWidths=[3.5*cm, 6*cm, 2.5*cm, 5*cm])
    t.setStyle(TableStyle([
        ('FONTNAME',  (0,0),(-1,-1), 'Helvetica'),
        ('FONTNAME',  (0,0),(0,-1),  'Helvetica-Bold'),
        ('FONTNAME',  (2,0),(2,-1),  'Helvetica-Bold'),
        ('FONTSIZE',  (0,0),(-1,-1), 9),
        ('TEXTCOLOR', (0,0),(0,-1),  GREEN),
        ('TEXTCOLOR', (2,0),(2,-1),  GREEN),
        ('ROWBACKGROUNDS',(0,0),(-1,-1),[LGRAY, colors.white]),
        ('TOPPADDING',    (0,0),(-1,-1), 5),
        ('BOTTOMPADDING', (0,0),(-1,-1), 5),
        ('LEFTPADDING',   (0,0),(-1,-1), 6),
        ('GRID',(0,0),(-1,-1),0.3,colors.HexColor('#E2E8F0')),
    ]))
    return t


# ── measurement PDF ──────────────────────────────────────────
def build_measurement_pdf(customer_name, phone, address,
                           measurement, taken_by, is_walkin=False):
    buffer = BytesIO()
    doc    = SimpleDocTemplate(buffer, pagesize=A4,
                               topMargin=1.5*cm, bottomMargin=1.5*cm,
                               leftMargin=2*cm,  rightMargin=2*cm)
    s      = base_styles()
    story  = []

    header_block(story, 'Measurement Record Card')

    ctype    = 'Walk-in Customer' if is_walkin else 'Registered Customer'
    story.append(info_table([
        ['Customer Name:', customer_name,
         'Date:', datetime.now().strftime('%d %b %Y')],
        ['Phone Number:', phone,
         'Type:', ctype],
        ['Taken By:', taken_by or 'Admin',
         'Address:', address or 'N/A'],
    ]))
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width='100%', thickness=1,
                            color=colors.HexColor('#E2E8F0')))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        '📏  BODY MEASUREMENTS  (all in inches)',
        ParagraphStyle('mh', fontSize=10, fontName='Helvetica-Bold',
                       textColor=GREEN, spaceAfter=8)))

    fields = [
        ('Chest',          getattr(measurement, 'chest',          None)),
        ('Shoulder',       getattr(measurement, 'shoulder',       None)),
        ('Sleeve',         getattr(measurement, 'sleeve',         None)),
        ('Waist',          getattr(measurement, 'waist',          None)),
        ('Neck',           getattr(measurement, 'neck',           None)),
        ('Hip',            getattr(measurement, 'hip',            None)),
        ('Shirt Length',   getattr(measurement, 'shirt_length',   None)),
        ('Trouser Length', getattr(measurement, 'trouser_length', None)),
    ]

    m_data = [['Measurement', 'Value', 'Measurement', 'Value']]
    pairs  = [(fields[i], fields[i+1] if i+1 < len(fields) else ('',''))
              for i in range(0, len(fields), 2)]
    for (l1,v1),(l2,v2) in pairs:
        m_data.append([
            l1, f'{v1}"' if v1 else '—',
            l2, f'{v2}"' if v2 else '—',
        ])

    mt = Table(m_data, colWidths=[4.5*cm, 3.5*cm, 4.5*cm, 3.5*cm])
    mt.setStyle(TableStyle([
        ('BACKGROUND',    (0,0),(-1,0),  GREEN),
        ('TEXTCOLOR',     (0,0),(-1,0),  GOLD),
        ('FONTNAME',      (0,0),(-1,0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0,0),(-1,-1), 10),
        ('FONTNAME',      (0,1),(-1,-1), 'Helvetica'),
        ('FONTNAME',      (1,1),(1,-1),  'Helvetica-Bold'),
        ('FONTNAME',      (3,1),(3,-1),  'Helvetica-Bold'),
        ('TEXTCOLOR',     (1,1),(1,-1),  GREEN),
        ('TEXTCOLOR',     (3,1),(3,-1),  GREEN),
        ('ALIGN',         (1,0),(-1,-1), 'CENTER'),
        ('ROWBACKGROUNDS',(0,1),(-1,-1), [CREAM, colors.white]),
        ('TOPPADDING',    (0,0),(-1,-1), 8),
        ('BOTTOMPADDING', (0,0),(-1,-1), 8),
        ('LEFTPADDING',   (0,0),(-1,-1), 8),
        ('GRID',          (0,0),(-1,-1), 0.5,
         colors.HexColor('#E2E8F0')),
        ('LINEBELOW',     (0,0),(-1,0),  1.5, GOLD),
    ]))
    story.append(mt)

    if is_walkin and hasattr(measurement,'notes') and measurement.notes:
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph(
            f'<b>Notes:</b> {measurement.notes}',
            ParagraphStyle('n', fontSize=9, textColor=colors.gray)))

    footer_block(story,
        'Kalamu Wahid Tailoring Synergy  ·  Kano, Nigeria')
    doc.build(story)
    buffer.seek(0)
    return buffer


# ── tailoring order invoice ──────────────────────────────────
def build_invoice_pdf(o):
    buffer = BytesIO()
    doc    = SimpleDocTemplate(buffer, pagesize=A4,
                               topMargin=1.5*cm, bottomMargin=1.5*cm,
                               leftMargin=2*cm,  rightMargin=2*cm)
    s      = base_styles()
    story  = []

    header_block(story, 'Tailoring Receipt / Invoice')

    story.append(info_table([
        ['Invoice No:', f'KW-{o.id:05d}',
         'Date:', datetime.now().strftime('%d %b %Y')],
        ['Customer:', o.user.full_name,
         'Phone:', o.user.phone],
        ['Status:', o.status,
         'Payment:', o.payment_method],
    ]))
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph('Order Details', s['head']))
    det = [
        ['Style Type',  o.style_type],
        ['Description', o.description or 'N/A'],
        ['Delivery',    o.delivery_method],
        ['Address',     o.delivery_address or 'Shop Pickup'],
        ['Notes',       o.notes or 'None'],
    ]
    dt = Table(det, colWidths=[5*cm, 12*cm])
    dt.setStyle(TableStyle([
        ('FONTNAME',      (0,0),(-1,-1), 'Helvetica'),
        ('FONTNAME',      (0,0),(0,-1),  'Helvetica-Bold'),
        ('FONTSIZE',      (0,0),(-1,-1), 9),
        ('TEXTCOLOR',     (0,0),(0,-1),  GREEN),
        ('ROWBACKGROUNDS',(0,0),(-1,-1), [CREAM, colors.white]),
        ('TOPPADDING',    (0,0),(-1,-1), 5),
        ('BOTTOMPADDING', (0,0),(-1,-1), 5),
        ('LEFTPADDING',   (0,0),(-1,-1), 6),
        ('GRID',          (0,0),(-1,-1), 0.3,
         colors.HexColor('#E2E8F0')),
    ]))
    story.append(dt)
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph('Payment Summary', s['head']))
    bal = o.amount - o.amount_paid
    fin = [
        ['Total Amount', f'N{o.amount:,.0f}'],
        ['Amount Paid',  f'N{o.amount_paid:,.0f}'],
        ['Balance Due',  f'N{bal:,.0f}'],
    ]
    ft = Table(fin, colWidths=[8*cm, 9*cm])
    ft.setStyle(TableStyle([
        ('FONTNAME',      (0,0),(-1,-1), 'Helvetica'),
        ('FONTNAME',      (0,0),(0,-1),  'Helvetica-Bold'),
        ('FONTNAME',      (1,2),(1,2),   'Helvetica-Bold'),
        ('FONTSIZE',      (0,0),(-1,-1), 10),
        ('TEXTCOLOR',     (0,0),(0,-1),  GREEN),
        ('TEXTCOLOR',     (1,2),(1,2),
         colors.red if bal > 0 else colors.HexColor('#065F46')),
        ('BACKGROUND',    (0,2),(-1,2),  CREAM),
        ('ROWBACKGROUNDS',(0,0),(-1,1),  [LGRAY, colors.white]),
        ('TOPPADDING',    (0,0),(-1,-1), 7),
        ('BOTTOMPADDING', (0,0),(-1,-1), 7),
        ('LEFTPADDING',   (0,0),(-1,-1), 8),
        ('LINEBELOW',     (0,1),(-1,1),  1, GOLD),
        ('GRID',          (0,0),(-1,-1), 0.3,
         colors.HexColor('#E2E8F0')),
    ]))
    story.append(ft)

    footer_block(story,
        'Thank you for choosing Kalamu Wahid Tailoring Synergy!')
    doc.build(story)
    buffer.seek(0)
    return buffer


# ── product order invoice ────────────────────────────────────
def build_product_invoice_pdf(o):
    buffer = BytesIO()
    doc    = SimpleDocTemplate(buffer, pagesize=A4,
                               topMargin=1.5*cm, bottomMargin=1.5*cm,
                               leftMargin=2*cm,  rightMargin=2*cm)
    s      = base_styles()
    story  = []

    header_block(story, 'Product Order Receipt')

    story.append(info_table([
        ['Receipt No:', f'KWP-{o.id:05d}',
         'Date:', datetime.now().strftime('%d %b %Y')],
        ['Customer:', o.customer_name,
         'Phone:', o.customer_phone],
        ['Product:', o.product.name,
         'Category:', o.product.category],
        ['Quantity:', f'{o.quantity} {o.unit}(s)',
         'Delivery:', o.delivery_method],
    ]))
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph('Payment Summary', s['head']))
    bal = (o.total_price or 0) - o.amount_paid
    fin = [
        ['Total Amount',
         f'N{o.total_price:,.0f}' if o.total_price else 'On request'],
        ['Amount Paid', f'N{o.amount_paid:,.0f}'],
        ['Balance Due', f'N{bal:,.0f}' if o.total_price else 'TBD'],
    ]
    ft = Table(fin, colWidths=[8*cm, 9*cm])
    ft.setStyle(TableStyle([
        ('FONTNAME',      (0,0),(-1,-1), 'Helvetica'),
        ('FONTNAME',      (0,0),(0,-1),  'Helvetica-Bold'),
        ('FONTSIZE',      (0,0),(-1,-1), 10),
        ('TEXTCOLOR',     (0,0),(0,-1),  GREEN),
        ('BACKGROUND',    (0,2),(-1,2),  CREAM),
        ('ROWBACKGROUNDS',(0,0),(-1,1),  [LGRAY, colors.white]),
        ('TOPPADDING',    (0,0),(-1,-1), 7),
        ('BOTTOMPADDING', (0,0),(-1,-1), 7),
        ('LEFTPADDING',   (0,0),(-1,-1), 8),
        ('GRID',          (0,0),(-1,-1), 0.3,
         colors.HexColor('#E2E8F0')),
    ]))
    story.append(ft)

    footer_block(story,
        'Thank you for shopping at Kalamu Wahid Tailoring Synergy!')
    doc.build(story)
    buffer.seek(0)
    return buffer


# ── routes ───────────────────────────────────────────────────
@print_bp.route('/admin/print/measurement/registered/<int:user_id>')
@login_required
def print_registered(user_id):
    if not admin_required_check():
        flash('Admin access required.', 'danger')
        return redirect(url_for('auth.login'))
    customer    = User.query.get_or_404(user_id)
    measurement = Measurement.query.filter_by(user_id=user_id).first()
    if not measurement:
        flash('No measurements found.', 'danger')
        return redirect(url_for('admin_shop.measurements'))
    buf = build_measurement_pdf(
        customer_name = customer.full_name,
        phone         = customer.phone,
        address       = '',
        measurement   = measurement,
        taken_by      = 'Admin',
        is_walkin     = False
    )
    response = make_response(buf.read())
    response.headers['Content-Type']        = 'application/pdf'
    response.headers['Content-Disposition'] = \
        f'inline; filename=measurement_{customer.full_name.replace(" ","_")}.pdf'
    return response


@print_bp.route('/admin/print/measurement/walkin/<int:customer_id>')
@login_required
def print_walkin(customer_id):
    if not admin_required_check():
        flash('Admin access required.', 'danger')
        return redirect(url_for('auth.login'))
    customer    = WalkInCustomer.query.get_or_404(customer_id)
    measurement = WalkInMeasurement.query.filter_by(
                      customer_id=customer_id).first()
    if not measurement:
        flash('No measurements found.', 'danger')
        return redirect(url_for('admin_shop.measurements'))
    buf = build_measurement_pdf(
        customer_name = customer.full_name,
        phone         = customer.phone,
        address       = customer.address or '',
        measurement   = measurement,
        taken_by      = measurement.taken_by,
        is_walkin     = True
    )
    response = make_response(buf.read())
    response.headers['Content-Type']        = 'application/pdf'
    response.headers['Content-Disposition'] = \
        f'inline; filename=measurement_{customer.full_name.replace(" ","_")}.pdf'
    return response


@print_bp.route('/invoice/order/<int:order_id>')
@login_required
def invoice_order(order_id):
    o = Order.query.get_or_404(order_id)
    if not admin_required_check() and o.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('customer.dashboard'))
    buf      = build_invoice_pdf(o)
    response = make_response(buf.read())
    response.headers['Content-Type']        = 'application/pdf'
    response.headers['Content-Disposition'] = \
        f'inline; filename=invoice_order_{o.id}.pdf'
    return response


@print_bp.route('/invoice/product-order/<int:order_id>')
@login_required
def invoice_product_order(order_id):
    if not admin_required_check():
        flash('Access denied.', 'danger')
        return redirect(url_for('customer.dashboard'))
    o        = ProductOrder.query.get_or_404(order_id)
    buf      = build_product_invoice_pdf(o)
    response = make_response(buf.read())
    response.headers['Content-Type']        = 'application/pdf'
    response.headers['Content-Disposition'] = \
        f'inline; filename=invoice_product_{o.id}.pdf'
    return response