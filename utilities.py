import arrow

date_fmt = "YYYY-MM-DDTHH:mm:ss"


def fmt_time(time=arrow.utcnow()):
    return arrow.get(time).format(date_fmt) + 'Z'


def get_time(time):
    return arrow.get(time).datetime
