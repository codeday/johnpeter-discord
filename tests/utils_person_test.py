from utils import person

class TestPerson:
    def __init__(self, user_id):
        self.user_id = user_id

def get_users_list(count):
    return ["aaaaa" for x in range(0,count)]

def test_get_user_id():
    assert person.get_user_id(6) == "6"
    assert person.get_user_id("6") == "6"
    assert person.get_user_id(TestPerson(6)) == "6"
    assert person.get_user_id({"user_id": 6}) == "6"
    assert person.get_user_id({}) == None

def test_truncate_list_length():
    test_list = ("foo", "bar", "baz")
    assert person.truncate_list_length(test_list, 5) == test_list[0:1]
    assert person.truncate_list_length(test_list, 6) == test_list[0:2]
    assert person.truncate_list_length(test_list, 7) == test_list[0:2]
    assert person.truncate_list_length(test_list, 9, add_per_element=1) == test_list[0:2]

def assert_mention_users(users, max_count, max_str_count, offset, expected):
    trunc_message = '_...and {} more._'
    message_len = len(trunc_message.format(str(len(users))))
    user_len = len(users[0])
    outStr = person.mention_users(
        users,
        100,
        message_len+(user_len*max_str_count)+(5*max_str_count)+offset,
        join=",", prefix="-"
    )
    expectedStr = ','.join(
            [f'-<@{user}>' for user in get_users_list(expected)]
        )+','+trunc_message.format(len(users) - expected)
    assert outStr == expectedStr

def test_mention_users():
    users = get_users_list(100)
    assert_mention_users(users, 100, 2, 0, 2)
    assert_mention_users(users, 100, 2, -1, 1)
    assert_mention_users(users, 100, 2, 1, 2)

    assert person.mention_users(users, 2, 100000, join=",", prefix="-") \
        == ','.join([f'-<@{user}>' for user in get_users_list(2)])+',_...and 98 more._'
