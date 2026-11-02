"""Costanti dell'integrazione Door Entry BTicino C300X."""

DOMAIN = "doorentry_bticino_c300x"

CONF_HOST = "host"
CONF_PORT = "port"

# host interno predefinito dell'add-on (raggiungibile da Home Assistant Core).
# Se non funziona, l'utente può inserire l'IP di Home Assistant nella config.
DEFAULT_HOST = "local-doorentry-bticino-c300x"
DEFAULT_PORT = 8099

# ogni quanto interrogare l'add-on (secondi)
UPDATE_INTERVAL = 2

# mappa comandi -> endpoint dell'add-on
CMD_ANSWERING_ON = "answering_on"
CMD_ANSWERING_OFF = "answering_off"
CMD_LIGHT = "light"
CMD_DOOR = "door"

# Percorsi dei file prodotti dall'add-on. /share e' montato anche in Home Assistant Core,
# quindi l'integrazione puo' leggerli direttamente e servirli al browser con il login di HA.
SHARE_DIR = "/share/doorentry_bticino_c300x"
RECORDINGS_DIR = f"{SHARE_DIR}/recordings"
SNAPSHOT_FILE = f"{SHARE_DIR}/doorbell.jpg"
API_BASE = f"/api/{DOMAIN}"
