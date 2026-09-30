# Taaklog API for Home Assistant

HACS custom integration voor het periodiek versturen van Taaklog-statusmeldingen.

## SSL / certSIGN

`website.venlo.nl` levert momenteel het intermediate certificaat niet volledig mee.
Daarom downloadt deze integratie bij iedere start automatisch:

`https://raw.githubusercontent.com/mooizopunt/taaklogapi/main/certsign-webcag2.crt`

Het bestand wordt persistent opgeslagen als:

`/config/taaklog_api/certsign-webcag2.crt`

Daarna maakt de integratie een eigen SSL-context waarin:

- de normale Home Assistant / Python CA trust store actief blijft;
- `certSIGN Web CA G2` aanvullend wordt vertrouwd;
- hostname-verificatie actief blijft;
- certificaatcontrole NIET wordt uitgeschakeld.

Er wordt dus nergens `ssl=False` gebruikt.

## Werking

Bij het laden:

1. downloadt de integratie het CA-certificaat;
2. slaat het op in `/config/taaklog_api/`;
3. bouwt een SSL-context;
4. voert direct één Taaklog API-call uit;
5. herhaalt de API-call standaard iedere 5 minuten.

## HACS repositorystructuur

De root van branch `main`:

```text
hacs.json
README.md
custom_components/
└── taaklog_api/
    ├── __init__.py
    ├── config_flow.py
    ├── const.py
    ├── manifest.json
    ├── sensor.py
    ├── strings.json
    ├── brand/
    │   └── icon.png
    └── translations/
        ├── en.json
        └── nl.json
```

## Standaard Taaklog waarden

- URL: `https://website.venlo.nl/taaklogapi`
- Naam: `Controle website`
- Soort: `Webcontrole`
- Resultaat: `OK`
- ServerName: `VNLAPPL060`
- TaskId: `159`
- Interval: `5` minuten
