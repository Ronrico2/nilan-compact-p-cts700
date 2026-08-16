# Udgiv repositoryet på GitHub og HACS

Projektmappen er klar til et offentligt GitHub-repository. Følgende skal udføres
af repositoryets ejer én gang.

## 1. Tilpas GitHub-navnet

Erstat `YOUR_GITHUB_USERNAME` i disse filer med dit GitHub-brugernavn:

- `README.md`
- `custom_components/nilan_cts700/manifest.json`

Tilføj også dit brugernavn til `codeowners` i `manifest.json`, eksempelvis:

```json
"codeowners": ["@mit-navn"]
```

## 2. Opret repositoryet

Opret et offentligt repository med navnet `nilan-cts700`, og upload hele
indholdet af denne mappe til repositoryets rod.

Anbefalet GitHub-beskrivelse:

> Home Assistant integration for Nilan CTS700 Compact P + AIR9 via Modbus TCP

Anbefalede topics:

- `home-assistant`
- `hacs`
- `nilan`
- `cts700`
- `modbus`
- `heat-pump`

Issues skal være aktiveret.

## 3. Kontrollér valideringen

GitHub Actions-filen kører både HACS-validering og Hassfest. Begge jobs skal
være grønne. Ret eventuelle fejl, før der oprettes en release.

## 4. Opret release

Opret en rigtig GitHub Release, ikke kun et tag:

- Tag: `v1.0.1`
- Titel: `Nilan CTS700 v1.0.1`
- Target: standardbranchens seneste commit

## 5. Brug som brugerdefineret HACS-repository

Repositoryet kan straks bruges gennem HACS:

1. HACS → menu med tre prikker → **Custom repositories**.
2. Indsæt repositoryets GitHub-URL.
3. Vælg kategorien **Integration**.

## 6. Valgfrit: søg optagelse i HACS' standardkatalog

Når repositoryet er offentligt, valideret og har en release, kan ejeren sende
en pull request til `hacs/default` under kategorien `integration`. Dette er ikke
nødvendigt for brugerdefineret installation og kan have lang behandlingstid.
