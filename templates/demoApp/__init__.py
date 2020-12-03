##contains application application factory and indicates that demo directory should be treated as a package
##Flask application is an instance of the Flask class

import os
from flask import Flask

def create_app(test_config = None):
    #create and configure the application
    app = Flask(__name__, instance_relative_config = True)
    app.config.from_mapping(
        SECRET_KEY ='dev',
        DATABASE = os.path.join(app.instance_path, 'demoApp.sqlite'),
    )

    if test_config is None:
        #load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent = True)
    else:
        #load the test config if passed in
        app.config.from_mapping(test_config)
    
    #check that the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    #simple hello world page
    @app.route('/hello')
    def hello():
        return 'Hello, World!'
    
    from . import db 
    db.init_app(app)

    
    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint = 'index')

    return app