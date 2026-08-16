# Nilan CTS700 Compact P + AIR9 til Home Assistant

Uofficiel Home Assistant-integration til lokal styring og overvågning af en
Nilan Compact P med CTS700-styring og valgfri AIR9 via Modbus TCP.

![Nilan-panel](custom_components/nilan_cts700/frontend/nilan_panel.png)

## Funktioner

- Opsætning direkte fra Home Assistants brugerflade; ingen package-YAML.
- Compact P på Modbus slave-id 1 og AIR9 på slave-id 4 som standard.
- 3 temperaturstyringer, 5 kontakter, 9 binære sensorer, 46 sensorer,
  5 talindstillinger, ventilationsvælger og alarmnulstilling.
- Effektiv bloklæsning med justerbart opdateringsinterval.
- Det medfølgende grafiske panel og alle billeder leveres af integrationen.
- Kommunikation foregår lokalt. Ingen cloudkonto er nødvendig.

Registerkortet er baseret på *Nilan CTS700 Modbus brugervejledning 30030066,
revision 3*. Andre anlæg eller firmwareversioner kan have andre registre.

## Krav

- Home Assistant 2026.7.0 eller nyere.
- HACS installeret.
- Modbus TCP aktiveret på CTS700-anlægget.
- Home Assistant skal kunne nå anlæggets IP-adresse og TCP-port 502.

## Installation med HACS

Indtil repositoryet er optaget i HACS' standardkatalog, tilføjes det som et
brugerdefineret repository:

1. Åbn **HACS**.
2. Vælg menuen med de tre prikker og **Custom repositories**.
3. Indsæt `https://github.com/YOUR_GITHUB_USERNAME/nilan-cts700`.
4. Vælg kategorien **Integration** og tryk **Add**.
5. Find **Nilan CTS700 Compact P + AIR9**, vælg **Download**, og genstart
   Home Assistant.
6. Gå til **Indstillinger → Enheder og tjenester → Tilføj integration** og søg
   efter `Nilan CTS700`.
7. Indtast anlæggets IP-adresse. Standardværdierne er port 502, Compact P
   slave-id 1 og AIR9 slave-id 4.

## Dashboard

1. Åbn et dashboard og vælg **Rediger dashboard**.
2. Tilføj et **Manuelt** kort.
3. Kopiér indholdet fra [`dashboard/nilan_panel.yaml`](dashboard/nilan_panel.yaml).

Billederne installeres sammen med integrationen og hentes fra
`/nilan_cts700_static/`; de skal ikke kopieres til `/config/www`.

Hvis Home Assistant tidligere har oprettet entitets-id'er med suffikser som
`_2`, skal id'erne i kortet tilpasses, eller de gamle, utilgængelige entiteter
skal slettes før integrationen tilføjes igen.

## Migrering fra den gamle package-YAML

1. Tag en Home Assistant-backup.
2. Fjern eller deaktiver den gamle Nilan-package og en eventuel anden
   `modbus:`-hub med navnet `nilan`.
3. Genstart Home Assistant.
4. Slet gamle utilgængelige Nilan-entiteter fra entitetsregistret, hvis de
   blokerer de forventede entitets-id'er.
5. Installer denne integration og tilføj den fra brugerfladen.

Kør ikke den gamle package og denne integration samtidigt. Det giver dublerede
entiteter og to Modbus-klienter, der spørger det samme anlæg.

## Indstillinger

Under integrationens **Konfigurer**-knap kan opdateringsintervallet ændres fra
10 til 300 sekunder. Standard er 30 sekunder. Pausen mellem Modbus-kald kan
ændres fra 0 til 1000 ms; standard er 50 ms.

## Fejlfinding

- Kontrollér, at port 502 er tilgængelig fra Home Assistant-maskinen.
- Kontrollér slave-id'erne. Compact P er normalt 1, og AIR9 er normalt 4.
- Slå AIR9 fra under første opsætning, hvis installationen ikke har en AIR9.
- Hvis kun enkelte entiteter er utilgængelige, kan registeret mangle på den
  aktuelle firmware. Andre registerblokke fortsætter med at fungere.
- Aktivér debuglogning med:

  ```yaml
  logger:
    logs:
      custom_components.nilan_cts700: debug
  ```

## Ansvar og licens

Projektet er ikke udviklet, godkendt eller supporteret af Nilan A/S. Brug af
skrivbare Modbus-registre sker på eget ansvar. Start med konservative
temperaturgrænser, og behold anlæggets indbyggede sikkerhedsfunktioner aktive.

Koden udgives under MIT-licensen. Billeder og varemærker tilhører deres
respektive ejere og bruges alene til identifikation af det understøttede anlæg.

