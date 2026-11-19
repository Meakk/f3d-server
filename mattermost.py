import os
from mattermostdriver import Driver

_mat = Driver({
    'url': os.getenv('MATTERMOST_URL'),
    'login_id': os.getenv('MATTERMOST_BOT_LOGIN'),
    'password': os.getenv('MATTERMOST_BOT_PASSWORD'),
    'scheme': 'http',
})

_mat.login()

_channel_id = _mat.channels.get_channel_by_name_and_team_name(
    os.getenv('MATTERMOST_SERVER_NAME'), os.getenv('MATTERMOST_CHANNEL_NAME'))['id']


def post(message):
    _mat.posts.create_post(options={
        'channel_id': _channel_id,
        'message': message})
