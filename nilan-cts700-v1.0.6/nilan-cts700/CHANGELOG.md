# Ændringslog

## 1.0.6

- Varmepumpens Til/Fra-knap bevarer nu den senest udførte kommando på AIR9-
  firmware, som accepterer skrivningen, men fortsat returnerer `0` ved aflæsning.
  Det gør også næste `toggle`-kommando korrekt og får dashboardknappen til at
  skifte mellem grå og grøn.
- Ventilationsvælgeren bevarer nu det senest valgte trin. Picture Elements-
  grafikken følger derfor `Slukket` og trin 1–4 i stedet for at falde tilbage
  til trin 2 ud fra den målte ventilatorprocent.

## 1.0.5

- Gendannet det komplette `nilan_panel.png`, som ved en tidligere pakning blev
  afkortet og derfor gav en sort nederste halvdel i Picture Elements-kortet.
- Tilføjet automatisk validering af PNG-signatur, datastruktur, CRC og
  afsluttende IEND-blok for alle frontendbilleder.

## 1.0.4

- Rettet start efter `Slukket`: ventilationspausen frigives nu, før CTS700 får
  kommandoen for det valgte blæsertrin.
- En afvist hastighedskommando kan derfor ikke længere efterlade anlægget låst
  i ventilationspause indtil genstart.

## 1.0.3

- Kontakter viser nu den skrevne tilstand straks uden at vente på en komplet
  genlæsning af alle Modbus-registre.
- Ventilationsvælgeren viser det valgte trin optimistisk og bekræfter det
  efterfølgende mod den målte ventilatorhastighed.
- Ventilationskommandoen genlæses i baggrunden, så dashboardet ikke låses under
  en langsom CTS700-opdatering.

## 1.0.2

- Rettet alle entity-id'er i Picture Elements-dashboardet til Home Assistants
  enhedsbaserede navngivning for Compact P og AIR9.
- Dashboard-YAML følger nu med HACS-installationen under
  `custom_components/nilan_cts700/dashboard/`.

## 1.0.1

- Rettet registerlæsning på CTS700-firmware, der afviser brede områder med
  ubrugte eller ikke-understøttede registre.
- Et enkelt ikke-understøttet register gør ikke længere resten af gruppens
  sensorer utilgængelige.

## 1.0.0

- Første HACS-klare udgave.
- Opsætning via Home Assistant-brugerfladen.
- Native sensor-, binary sensor-, switch-, number-, select-, climate- og
  button-entiteter.
- Optimeret Modbus-bloklæsning for Compact P og AIR9.
- Grafisk Nilan-panel med automatisk leverede billeder.
