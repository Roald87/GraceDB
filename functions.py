import sys

def progress_bar(count, total, suffix=''):
    """

    Parameters
    ----------
    count
    total
    suffix

    Returns
    -------

    Source
    ------
    https://stackoverflow.com/a/27871113/6329629

    """
    bar_len = 30
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total))
    bar = '=' * filled_len + ' ' * (bar_len - filled_len)

    sys.stdout.write(f'\r{suffix}: [{bar}] {percents}%')
    if total - count < 1:
        sys.stdout.write('\n')
    sys.stdout.flush()  # As suggested by Rom Ruben