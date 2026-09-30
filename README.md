# Taaklog API v1.1.2

Belangrijkste wijziging:

- `/taaklogapi/` wordt automatisch genormaliseerd naar `/taaklogapi`
- redirects worden niet gevolgd
- de daadwerkelijk gebruikte API-URL wordt gelogd
- sensorattribuut `api_url` toont de gebruikte URL

Dit is nodig omdat de Layer7 API Gateway `/taaklogapi` en
`/taaklogapi/` als verschillende services behandelt.
