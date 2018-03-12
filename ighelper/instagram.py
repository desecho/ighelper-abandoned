from InstagramAPI import InstagramAPI


def get_followers(username, password, instagram_id):
    api = InstagramAPI(username, password)
    api.login()
    api.getUserFollowers(instagram_id)
    followers = api.LastJson['users']
    return [{
        'id': x['pk'],
        'username': x['username'],
        'name': x['full_name'],
        'avatar': x['profile_pic_url']
    } for x in followers]
