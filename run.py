from flaskblog import create_app
from logging.handlers import RotatingFileHandler
import os
import logging

app = create_app()

if not app.debug:
    # ...
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/flaskblog.log', 'a', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('flaskblog')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
