# Integrazione: Door Entry BTicino C300X

Integrazione custom di Home Assistant che si accoppia all'add-on **Door Entry BTicino C300X** e
crea automaticamente le entità del videocitofono. Nessuna configurazione YAML manuale.

## Entità create
- **binary_sensor** "Sta suonando" — attivo mentre qualcuno suona.
- **binary_sensor** "Chiamata persa" — si accende quando scatta la cattura di riserva.
- **camera** "Videocitofono" — ultima istantanea catturata.
- **button** "Apri ..." — uno per ogni serratura rilevata.
- **button** "Luce scale".
- **switch** "Segreteria" (risponditore, stato ottimistico).
- **sensor** informativi (Dispositivi attivo; Impianto e Gateway disattivati di default).

## Installazione
1. Copia la cartella `doorentry_bticino_c300x/` dentro `config/custom_components/` di Home Assistant.
2. Riavvia Home Assistant.
3. Impostazioni → Dispositivi e servizi → **Aggiungi integrazione** → "Door Entry BTicino C300X".
4. Conferma l'host proposto; se non si collega, inserisci l'IP di Home Assistant e la porta 8099.
   L'host si modifica anche dopo, da **Configura**, senza rimuovere l'integrazione.

## Requisiti
- L'add-on "Door Entry BTicino C300X" deve essere installato e avviato sulla stessa istanza di HA.
- L'integrazione interroga l'add-on sulla porta configurata (default 8099).

## Note
- Le serrature sono rilevate dall'add-on: i pulsanti compaiono/spariscono in automatico. Un
  pulsante di una serratura non più presente risulta "non disponibile" ed è eliminabile.
- Il pulsante "Apri porta" apre davvero la serratura.
