from flask import Blueprint, request
import hashlib
import hmac
import os
import mattermost

bp = Blueprint('github', __name__)


@bp.route('/github', methods=['POST'])
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

        mattermost.post(':star: from ' + username + '! Total is now ' + str(count) + '! :tada:')

    if event == 'release' and action == 'published' and repo == 'f3d':
        tag = '[' + data.get("release").get("tag_name") + '](' + data.get("release").get("html_url") + ')'

        mattermost.post(':tada: :tada: NEW RELEASE IS PUBLISHED: ' + tag)

    if event == 'issues' and action == 'opened':
        title = '[' + data.get("issue").get("title") + '](' + data.get("issue").get("html_url") + ')'

        mattermost.post(':ladybug: A new issue on ' + repo + ' has been opened by ' + username + ': ' + title)

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
            mattermost.post(icon + ' A new PR ' + id + ' has been opened by ' + username + ': ' + title)

        if action == 'closed' and data.get("pull_request").get("merged") == True:
            mattermost.post(icon + ' PR ' + id + ' has been :large_green_circle: merged by ' + username)

        if action == 'closed' and data.get("pull_request").get("merged") == False:
            mattermost.post(icon + ' PR ' + id + ' has been :red_circle: closed by ' + username)

    if event == 'workflow_run' and action == 'completed':
        wr = data.get("workflow_run")
        concl = wr.get("conclusion")
        icon = ":white_check_mark:" if concl == "success" else ":skull:"
        if repo == 'f3d-superbuild' and data.get("workflow").get("name") == 'Nightly':
            mattermost.post(icon + " Nightly packaging [" + concl + "](" + wr.get("html_url") + ")")
        if repo == 'f3d' and data.get("workflow").get("name") == 'Nightly VTK master':
            mattermost.post(icon + " Nighly VTK master [" + concl + "](" + wr.get("html_url") + ")")
        if repo == 'f3d' and concl == "failure" and wr.get("head_branch") == "master":
            mattermost.post(icon + " Workflow [failed](" + wr.get("html_url") + ") on master!")

    return "Success"
