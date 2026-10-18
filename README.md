# Door Entry BTicino C300X — Integrazione per Home Assistant

Integrazione custom (installabile via **HACS**) che porta il videocitofono BTicino/Legrand
Classe 300X in Home Assistant. Si accoppia all'**add-on** omonimo e crea automaticamente le
entità: sensore "sta suonando", "chiamata persa", telecamera, pulsanti serrature/luce, segreteria.

> Richiede l'add-on "Door Entry BTicino C300X" installato e avviato (repository separato):
> `https://github.com/finetd/ha-doorentry-bticino-c300x-addon`

## Installazione via HACS
1. HACS → Integrazioni → menu ⋮ → **Repository personalizzati**.
2. URL: `https://github.com/finetd/ha-doorentry-bticino-c300x` · Categoria: **Integration**.
3. Installa "Door Entry BTicino C300X", riavvia Home Assistant.
4. Impostazioni → Dispositivi e servizi → **Aggiungi integrazione** → "Door Entry BTicino C300X".
   Conferma l'host o inserisci l'IP di Home Assistant (porta 8099).

## Installazione manuale (senza HACS)
Copia `custom_components/doorentry_bticino_c300x/` in `config/custom_components/` e riavvia HA.

## Entità e uso
Vedi [`custom_components/doorentry_bticino_c300x/README.md`](custom_components/doorentry_bticino_c300x/README.md).

## Licenza
MIT — vedi [LICENSE](LICENSE).
