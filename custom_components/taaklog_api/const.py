"""Constants for the Taaklog API integration."""

DOMAIN = "taaklog_api"

CONF_URL = "url"
CONF_API_USER = "api_user"
CONF_API_KEY = "api_key"
CONF_NAAM = "naam"
CONF_SOORT = "soort"
CONF_RESULTAAT = "resultaat"
CONF_SERVER_NAME = "server_name"
CONF_TASK_ID = "task_id"
CONF_INTERVAL = "interval"
CONF_CA_URL = "ca_url"

DEFAULT_URL = "https://website.venlo.nl/taaklogapi"
DEFAULT_NAAM = "Controle website"
DEFAULT_SOORT = "Webcontrole"
DEFAULT_RESULTAAT = "OK"
DEFAULT_SERVER_NAME = "VNLAPPL060"
DEFAULT_TASK_ID = 159
DEFAULT_INTERVAL = 5

DEFAULT_CA_URL = (
    "https://raw.githubusercontent.com/"
    "mooizopunt/taaklogapi/main/certsign-webcag2.crt"
)

CA_DIRECTORY = "taaklog_api"
CA_SOURCE_FILENAME = "certsign-webcag2.crt"
CA_PEM_FILENAME = "certsign-webcag2.pem"
