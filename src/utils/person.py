import inspect

def get_user_id(user_or_id):
    if (type(user_or_id) is str or type(user_or_id) is int):
        return str(user_or_id)
    elif (hasattr(user_or_id, '__getitem__') and 'user_id' in user_or_id):
        return str(user_or_id['user_id'])
    elif (hasattr(user_or_id, 'user_id')):
        return str(user_or_id.user_id)
    return None

def truncate_list_length(lst, length, *, add_per_element=0):
    total_length = 0
    for i, elem in enumerate(lst):
        total_length += len(elem) + add_per_element
        if (total_length > length):
            return lst[0:i]
    return lst

def mention_users(users, max_count, max_length, *, join="\n", prefix=" - "):
    trunc_users = users[0:max_count]
    trunc_message = '_...and {} more._'
    max_trunc_len = len(str(len(users)))
    max_message_len = len(trunc_message.format(' ' * max_trunc_len))
    final_max_len = max(0, max_length-max_message_len)

    user_strs = truncate_list_length(
        [f"{prefix}<@{get_user_id(user)}>" for user in trunc_users],
        final_max_len,
        add_per_element=len(join)
    )

    trunc_count = (len(users) - len(trunc_users)) + (len(trunc_users) - len(user_strs))


    out_msg = join.join(user_strs) + (trunc_message and join + trunc_message.format(trunc_count) or '')
    if (len(out_msg) > max_length) and final_max_len >= 3:
        return '...'
    elif (len(out_msg) > max_length):
        return ''
    else:
        return out_msg
