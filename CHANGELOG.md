# Ændringslog

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
