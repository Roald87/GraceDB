import logging

logging_kwargs = dict(
    level=logging.INFO,
    format="%(asctime)s \t %(name)-12s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
