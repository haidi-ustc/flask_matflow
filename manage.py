from app import create_app

app = create_app('server')
#app = create_app('laptop')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1234, debug=app.config['DEBUG'])

