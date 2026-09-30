# Taaklog API voor Home Assistant / HACS

Deze custom integration stuurt periodiek een JSON POST naar de Taaklog API.

Standaard voorbeeld:

```json
{
  "Naam": "Controle website",
  "Soort": "Webcontrole",
  "Resultaat": "OK",
  "ServerName": "VNLAPPL060",
  "TaskId": 159
}
```

Headers:

- `X-API-User`
- `X-API-Key`

## Installatie handmatig

Kopieer:

`custom_components/taaklog_api`

naar:

`/config/custom_components/taaklog_api`

Herstart Home Assistant.

Ga daarna naar:

**Instellingen > Apparaten & diensten > Integratie toevoegen > Taaklog API**

Vul in:

- URL: `https://website.venlo.nl/taaklogapi`
- API gebruiker: bijvoorbeeld `mijnapp`
- API sleutel
- Naam
- Soort
- Resultaat
- ServerName
- TaskId
- Interval: `5`

## Installatie via HACS

Plaats deze repository in GitHub en voeg hem in HACS toe als aangepaste repository:

**HACS > Integraties > drie puntjes > Aangepaste repositories**

Type:

`Integration`

Daarna kan de integratie via HACS worden geïnstalleerd.

## Gedrag

De API wordt direct bij laden één keer aangeroepen en vervolgens volgens het ingestelde interval.
Standaard is dit 5 minuten.

Er wordt een sensor aangemaakt:

`sensor.taaklog_api_status`

met status `OK` of `Fout`, plus attributen met HTTP status, response en request.
