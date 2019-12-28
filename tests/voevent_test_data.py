from ligo.gracedb.exceptions import HTTPError


def read_xml(filename):
    with open(filename) as file:
        data = file.readlines()

    return data


expected_event_json = {
    "start": 0,
    "numRows": 2,
    "voevents": [
        {
            "voevent_type": "PR",
            "file_version": 0,
            "ivorn": "ivo://gwnet/LVC#S190521r-1-Preliminary",
            "created": "2019-05-21 07:50:19 UTC",
            "issuer": "emfollow",
            "filename": "S190521r-1-Preliminary.xml",
            "N": 1,
            "links": {
                "self": "https://gracedb.ligo.org/api/superevents/S190521r/voevents/1/",
                "file": "https://gracedb.ligo.org/api/superevents/S190521r/files/S190521r-1-Preliminary.xml,0",
            },
        },
        {
            "voevent_type": "IN",
            "file_version": 0,
            "ivorn": "ivo://gwnet/LVC#S190521r-2-Initial",
            "created": "2019-05-21 08:17:49 UTC",
            "issuer": "emfollow",
            "filename": "S190521r-2-Initial.xml",
            "N": 2,
            "links": {
                "self": "https://gracedb.ligo.org/api/superevents/S190521r/voevents/2/",
                "file": "https://gracedb.ligo.org/api/superevents/S190521r/files/S190521r-2-Initial.xml,0",
            },
        },
    ],
    "links": {
        "self": "http://gracedb.ligo.org/api/superevents/S190521r/voevents/",
        "first": "http://gracedb.ligo.org/api/superevents/S190521r/voevents/",
        "last": "http://gracedb.ligo.org/api/superevents/S190521r/voevents/",
    },
}

unsorted_json_S190521r = [
    {
        "voevent_type": "PR",
        "file_version": 0,
        "ivorn": "ivo://gwnet/LVC#S190521r-1-Preliminary",
        "created": "2019-05-21 07:50:19 UTC",
        "issuer": "emfollow",
        "filename": "S190521r-1-Preliminary.xml",
        "N": 1,
        "links": {
            "self": "https://gracedb.ligo.org/api/superevents/S190521r/voevents/1/",
            "file": "https://gracedb.ligo.org/api/superevents/S190521r/files/S190521r-1-Preliminary.xml,0",
        },
    },
    {
        "voevent_type": "IN",
        "file_version": 0,
        "ivorn": "ivo://gwnet/LVC#S190521r-2-Initial",
        "created": "2019-05-21 08:17:49 UTC",
        "issuer": "emfollow",
        "filename": "S190521r-2-Initial.xml",
        "N": 2,
        "links": {
            "self": "https://gracedb.ligo.org/api/superevents/S190521r/voevents/2/",
            "file": "https://gracedb.ligo.org/api/superevents/S190521r/files/S190521r-2-Initial.xml,0",
        },
    },
]


sorted_json_S190521r = [
    {
        "voevent_type": "IN",
        "file_version": 0,
        "ivorn": "ivo://gwnet/LVC#S190521r-2-Initial",
        "created": "2019-05-21 08:17:49 UTC",
        "issuer": "emfollow",
        "filename": "S190521r-2-Initial.xml",
        "N": 2,
        "links": {
            "self": "https://gracedb.ligo.org/api/superevents/S190521r/voevents/2/",
            "file": "https://gracedb.ligo.org/api/superevents/S190521r/files/S190521r-2-Initial.xml,0",
        },
    },
    {
        "voevent_type": "PR",
        "file_version": 0,
        "ivorn": "ivo://gwnet/LVC#S190521r-1-Preliminary",
        "created": "2019-05-21 07:50:19 UTC",
        "issuer": "emfollow",
        "filename": "S190521r-1-Preliminary.xml",
        "N": 1,
        "links": {
            "self": "https://gracedb.ligo.org/api/superevents/S190521r/voevents/1/",
            "file": "https://gracedb.ligo.org/api/superevents/S190521r/files/S190521r-1-Preliminary.xml,0",
        },
    },
]

voevents_S190521r = {
    "https://gracedb.ligo.org/api/superevents/S190521r/files/S190521r-2-Initial.xml,0": read_xml(
        "./data/S190521r-2-Initial.xml"
    )
}

sorted_json_S190517h = [
    {
        "voevent_type": "IN",
        "file_version": 0,
        "ivorn": "ivo://gwnet/LVC#S190517h-3-Initial",
        "created": "2019-05-17 06:57:41 UTC",
        "issuer": "emfollow",
        "filename": "S190517h-3-Initial.xml",
        "N": 3,
        "links": {
            "self": "https://gracedb.ligo.org/api/superevents/S190517h/voevents/3/",
            "file": "https://gracedb.ligo.org/api/superevents/S190517h/files/S190517h-3-Initial.xml,0",
        },
    },
    {
        "voevent_type": "IN",
        "file_version": 0,
        "ivorn": "ivo://gwnet/LVC#S190517h-2-Initial",
        "created": "2019-05-17 06:31:44 UTC",
        "issuer": "emfollow",
        "filename": "S190517h-2-Initial.xml",
        "N": 2,
        "links": {
            "self": "https://gracedb.ligo.org/api/superevents/S190517h/voevents/2/",
            "file": "https://gracedb.ligo.org/api/superevents/S190517h/files/S190517h-2-Initial.xml,0",
        },
    },
    {
        "voevent_type": "PR",
        "file_version": 0,
        "ivorn": "ivo://gwnet/LVC#S190517h-1-Preliminary",
        "created": "2019-05-17 06:26:44 UTC",
        "issuer": "emfollow",
        "filename": "S190517h-1-Preliminary.xml",
        "N": 1,
        "links": {
            "self": "https://gracedb.ligo.org/api/superevents/S190517h/voevents/1/",
            "file": "https://gracedb.ligo.org/api/superevents/S190517h/files/S190517h-1-Preliminary.xml,0",
        },
    },
]
