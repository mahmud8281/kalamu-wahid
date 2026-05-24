from flask import Blueprint, session, redirect, request

lang_bp = Blueprint('lang_bp', __name__)

LANGUAGES = {
    'en': 'English',
    'ha': 'Hausa',
}

@lang_bp.route('/set-language/<lang>')
def set_language(lang):
    if lang in LANGUAGES:
        session['lang'] = lang
    return redirect(request.referrer or '/')