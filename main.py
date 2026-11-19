#!/opt/sweetbot/venv/bin/python3

from flask import Flask
import github
import mattermost
import upload

app = Flask(__name__)
app.register_blueprint(github.bp)
app.register_blueprint(upload.bp)

# Maximum upload size: 5 MB
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

mattermost.post('I\'m back online! :wave:')

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)
