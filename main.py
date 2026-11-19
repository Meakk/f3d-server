#!/opt/sweetbot/venv/bin/python3

from flask import Flask, request
import hashlib
import hmac
import json
import os
from mattermostdriver import Driver

app = Flask(__name__)

mat = Driver({
    'url': os.getenv('MATTERMOST_URL'),
    'login_id': os.getenv('MATTERMOST_BOT_LOGIN'),
    'password': os.getenv('MATTERMOST_BOT_PASSWORD'),
    'scheme': 'http',
})

mat.login()

channel_id = mat.channels.get_channel_by_name_and_team_name(os.getenv('MATTERMOST_SERVER_NAME'), os.getenv('MATTERMOST_CHANNEL_NAME'))['id']

mat.posts.create_post(options={
'channel_id': channel_id,
'message': 'I\'m back online! :wave:'})

@app.route('/github', methods=['POST'])
def github():
    secret = os.getenv('MATTERMOST_GITHUB_TOKEN', '')
    expected = 'sha256=' + hmac.new(secret.encode(), request.get_data(), hashlib.sha256).hexdigest()
    signature = request.headers.get('X-Hub-Signature-256', '')
    if not secret or not hmac.compare_digest(signature, expected):
        print('Invalid or missing X-Hub-Signature-256', flush=True)
        return '', 403

    data = request.get_json()
    event = request.headers.get('X-GitHub-Event')

    action = str(data.get("action"))
    username = '[' + str(data.get("sender").get("login")) + '](' + str(data.get("sender").get("html_url")) + ')'
    repo = data.get("repository").get("name")

    if event is not None:
        print(event + ' (' + action + ') from ' + str(data.get("sender").get("login")), flush=True)

    if event == 'star' and action == 'created' and repo == 'f3d':
        count = data.get("repository").get("stargazers_count")

        mat.posts.create_post(options={
        'channel_id': channel_id,
        'message': ':star: from ' + username + '! Total is now ' + str(count) + '! :tada:'})

    if event == 'release' and action == 'published' and repo == 'f3d':
        tag = '[' + data.get("release").get("tag_name") + '](' + data.get("release").get("html_url") + ')'

        mat.posts.create_post(options={
        'channel_id': channel_id,
        'message': ':tada: :tada: NEW RELEASE IS PUBLISHED: ' + tag})

    if event == 'issues' and action == 'opened':
        title = '[' + data.get("issue").get("title") + '](' + data.get("issue").get("html_url") + ')'

        mat.posts.create_post(options={
        'channel_id': channel_id,
        'message': ':ladybug: A new issue on ' + repo + ' has been opened by ' + username + ': ' + title})

    if event == 'pull_request':
        title = data.get("pull_request").get("title")
        id = '[#' + str(data.get("pull_request").get("number")) + '](' + data.get("pull_request").get("html_url") + ')'

        icon = ":f3d:"
        if repo == "f3d-superbuild":
            icon = ":package:"
        if repo == "f3d-website":
            icon = ":globe_with_meridians:"
        if repo == "f3d-docker-images":
            icon = ":whale:"
        if repo == "f3d-android":
            icon = ":robot_face:"

        if action == 'opened':
            mat.posts.create_post(options={
            'channel_id': channel_id,
            'message': icon + ' A new PR ' + id + ' has been opened by ' + username + ': ' + title})

        if action == 'closed' and data.get("pull_request").get("merged") == True:
            mat.posts.create_post(options={
            'channel_id': channel_id,
            'message': icon + ' PR ' + id + ' has been :large_green_circle: merged by ' + username})

        if action == 'closed' and data.get("pull_request").get("merged") == False:
            mat.posts.create_post(options={
            'channel_id': channel_id,
            'message': icon + ' PR ' + id + ' has been :red_circle: closed by ' + username})

    if event == 'workflow_run' and action == 'completed':
        wr = data.get("workflow_run")
        concl = wr.get("conclusion")
        icon = ":white_check_mark:" if concl == "success" else ":skull:"
        if repo == 'f3d-superbuild' and data.get("workflow").get("name") == 'Nightly':
            mat.posts.create_post(options={
            'channel_id': channel_id,
            'message': icon + " Nightly packaging [" + concl + "](" + wr.get("html_url") + ")"})
        if repo == 'f3d' and data.get("workflow").get("name") == 'Nightly VTK master':
            mat.posts.create_post(options={
                'channel_id': channel_id,
                'message': icon + " Nighly VTK master [" + concl + "](" + wr.get("html_url") + ")"})
        if repo == 'f3d' and concl == "failure" and wr.get("head_branch") == "master":
            mat.posts.create_post(options={
            'channel_id': channel_id,
            'message': icon + " Workflow [failed](" + wr.get("html_url") + ") on master!"})

    return "Success"

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)

