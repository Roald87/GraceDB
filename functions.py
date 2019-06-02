import sys


def progress_bar(count: int, total: int, prefix: str = '') -> None:
    """
    Display a progress bar in the terminal.

    Parameters
    ----------
    count : int
        Should run from 0 or 1 to `total`.
    total : int
        Total number of counts which represent 100%.
    prefix : str
        Optional text which is placed left of the progress bar.

    Returns
    -------
    None.

    Source
    ------
    https://stackoverflow.com/a/27871113/6329629

    """
    bar_len = 30
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total))
    bar = '=' * filled_len + ' ' * (bar_len - filled_len)

    sys.stdout.write(f'\r{prefix}: [{bar}] {percents}%')
    sys.stdout.flush()


def mpc_to_mly(num_in_mpc: float) -> float:
    """
    Convert a number from megaparsec to million light years.

    Parameters
    ----------
    num_in_mpc : float
        Distance in megaparsec to convert.

    Returns
    -------
    float
        Distance in million light years.
    """
    return num_in_mpc * 3.2637977445371
