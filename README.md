# Taaklog API

De root van de `main` branch moet direct deze structuur bevatten:

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

Belangrijk: zet niet eerst nog een extra map boven `custom_components`.

De integratie doet direct bij laden een POST en daarna iedere 5 minuten.
