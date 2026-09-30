# Taaklog API v1.1.1

Deze versie ondersteunt het certSIGN intermediate certificaat zowel als:

- PEM
- binair DER / `.crt`

Het bestand op GitHub wordt als `application/octet-stream` aangeboden.
Daarom wordt het lokaal opgeslagen als:

`/config/taaklog_api/certsign-webcag2.crt`

en indien nodig automatisch geconverteerd naar:

`/config/taaklog_api/certsign-webcag2.pem`

De PEM-versie wordt vervolgens toegevoegd aan een eigen SSL-context voor de
Taaklog API-verbinding.

SSL-verificatie en hostnamecontrole blijven actief.
Er wordt geen `ssl=False` gebruikt.
