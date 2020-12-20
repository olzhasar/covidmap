import logging

log = logging.getLogger()

console = logging.StreamHandler()
log.addHandler(console)
log.setLevel(logging.INFO)
