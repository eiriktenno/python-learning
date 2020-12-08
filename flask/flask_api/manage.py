from app import create_app


app = create_app('test')


# HTTPIE (if self signed certificate): https --verify=no
if __name__ == '__main__':
    app.run(ssl_context='adhoc')
