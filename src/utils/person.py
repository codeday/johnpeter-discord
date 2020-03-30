
def get_user_id(user_or_id):
    if (type(user_or_id) is str or type(user_or_id) is int):
        return user_or_id
    if (type(user_or_id) is dict and 'user_id' in user_or_id):
        return user_or_id['user_id']
    return None


def truncate_list_length(lst, length, *, add_per_element=0):
    total_length = 0
    for i, elem in enumerate(lst):
        total_length += len(elem) + add_per_element
        if (total_length > length):
            return lst[0:i-1]
    return lst


def mention_users(users, max_count, max_length, *, join="\n", prefix=" - "):
    trunc_users = users[0:max_count]
    trunc_count = len(users) - len(trunc_users)
    trunc_message = (f'_...and {trunc_count} more._' if trunc_count > 0 else None)

    user_strs = truncate_list_length(
        [f"{prefix}<@{get_user_id(user)}>" for user in trunc_users],
        max_length,
        add_per_element=len(join)
    )

    return join.join(user_strs)


def id_from_mention(mention):
    try:
        return int(mention.replace('<', '').replace('!', '').replace('>', '').replace('@', ''))
    except:
        return False
