from waitress import serve
from app import application

if __name__ == '__main__':
    print('=' * 50)
    print('Kalamu Wahid Server Running')
    print('Open: http://127.0.0.1:5000')
    print('Press Ctrl+C to stop')
    print('=' * 50)
    serve(application, host='0.0.0.0', port=5000, threads=8)