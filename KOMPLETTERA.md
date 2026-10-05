# Att bygga vidare på PB Korpus

Webbplatsen är en växande utgåva. Källor, råtext, redaktionella textversioner och register hålls åtskilda. Lägg till nya uppgifter i källdatan och bygg sedan om webbplatsens export. Redigera inte den genererade `docs/edition.json` eller `docs/assets/edition.js` direkt.

## Fyra identiteter

| Del | Identitet och funktion |
|---|---|
| Verk | `editorial/works.json` har ett beständigt verk-ID och länkar till dokumentversioner. En ny filversion kan knytas till samma verk. |
| Originalfil | Dokument-ID bygger på SHA-256. Nytt filinnehåll får ett nytt dokument-ID. Äldre filer och sidkopplingar behålls. |
| PDF-sida | Sid-ID består av dokument-ID och PDF-sidans position, exempelvis `PB-2AA72AC4BCC169AA:p0009`. |
| Textrevision och belägg | En sida har numrerade revisioner. Belägget har ett eget ID; registerhänvisningen anger även den granskade revisionen. |

Samma tryckta sidnummer kan förekomma i flera häften eller utgåvor. Hänvisa därför alltid till dokumentversion och PDF-sida. `pageMap` anger tryckt sidnummer för varje transkriberad boksida; null betyder att ett nummer inte syns. Det är inte en gissning om vad sidnumret borde vara.

## Lägg till eller rätta en sida

1. Öppna rätt PDF-version och granska sidbilden. Registrera vad som faktiskt syns, inklusive noter och eventuella osäkerheter. Bevara äldre stavning.
2. Kopiera sidans senaste revisionsfil till en arbetsfil. För en ny sida skapas revision 1 med `parentRevision: null`. För en rättning ökas revisionsnumret med ett och föräldern blir den senaste revisionen.
3. Fyll i text, granskare, datum, ändringsorsak, sidkoppling och osäkerheter. Status `selected` betyder utvald; `partial` betyder att bara angivna avsnitt är granskade; `proofread` kräver en genomgång av all tryckt löptext och noter inom transkriptionspolicyn. En separat sakkontroll eller oberoende dubbelgranskning anges i granskaruppgiften.
4. `segments` innehåller en sträng per boksida. Frassökningen korsar inte dessa sidgränser. Bilder, handskrivna inslag och stämplar ingår inte i denna utgåvas löptexttranskription. Ange avgränsningar i anteckningarna.
5. Kontrollera `rawTextSha256` mot den oförändrade råtexten, inte mot en tidigare korrekturläsning. `sourceSha256` ska avse original-PDF:n. Nytt original får nya sid-ID.
6. Lägg till revisionen med verktyget nedan. Det vägrar skriva över en befintlig revision och validerar källkopplingarna före export. Alternativet `--keep-active` sparar en ny revision i historiken utan att göra den till den aktiva lästexten.

```sh
python3 scripts/add_revision.py '/sokvag/till/ny-revision.json' --corpus '/sokvag/till/PB Korpus'
```

Tidigare revisioner ska aldrig skrivas om. Uppdatera utgåvans `release` i `editorial/edition.json` när en ny sammanhållen version släpps. Granska och spara webbplatsens förändringar i Git så att även register och urvalsbeslut får versionshistorik.

## Komplettera registret

Registret finns i `editorial/register.json`. Varje post har ett beständigt ID, en rubrik, sökvarianter, typ och en redaktionell beskrivning. Ett belägg består av ordagrann text i sidrevisionens `passages`. Hänvisa med både belägg-ID och revision:

```json
{"id": "E-K09-KEXEL", "revision": 2}
```

En senare sidrevision flyttar inte automatiskt denna hänvisning. Bedöm belägget igen innan registret hänvisas till den nya revisionen. Olika uppgifter från källor bevaras med separata belägg. Fyll inte i personidentiteter från antaganden; namnen Gustav Stiernecrantz och Arvid Adrian Stjernecrantz har exempelvis skilda registerposter. Mytologiska gestalter och skämtsamma berättelser behandlas som motiv, inte historiska medlemsuppgifter.

Öka utgåvans `release` före en registerändring som ska sparas som en ny version i korpusen. Registerkopiorna i `05_lexikon` och `06_entiteter` har versionsnummer och får inte skrivas över med ändrat innehåll. Bygg om efter registerändringar:

```sh
python3 scripts/build_edition.py --corpus '/sokvag/till/PB Korpus'
python3 tests/test_edition.py
```

## Lägg till fler verk eller filversioner

1. Bevara det nya originalet och registrera källadress, filversion, rättigheter och kontrollsumma i korpusens manifest. Äldre original lämnas kvar.
2. Uppdatera katalogen med `scripts/update_catalog.py`.
3. Den fullständiga grundextraktionen tar alla PDF-källor ur korpusens manifest. `editorial/text_sources.json` gäller det äldre pilotverktyget; använd `extract_corpus.py` för den utbyggda korpusen. Nya verk kräver inte ändringar i sökgränssnittet.
4. Kör den fullständiga grundextraktionen. Befintliga dokument och deras råtext/läsordning behålls om de redan finns; varje original kontrolleras mot manifestets kontrollsumma. Bygg en ny OCR-plan för nya skannade sidor och ge körningen en uttrycklig tidsgräns. Redaktionella revisioner ligger i egna filer och bevaras.
5. Lägg till dokument-ID i rätt verkpost i `editorial/works.json`, eller skapa ett nytt verk-ID. Granska nya sidrevisioner och bygg om utgåvan.

```sh
python3 scripts/extract_corpus.py '/sokvag/till/PB Korpus' --pdftotext /sokvag/till/pdftotext
python3 scripts/build_ocr_plan.py '/sokvag/till/PB Korpus' --pdfimages /sokvag/till/pdfimages
# Kör ocr_batch.py med aktuell sidplan, OCR-motor, modeller och tidsgräns.
python3 scripts/export_ocr.py '/sokvag/till/PB Korpus'
python3 scripts/build_edition.py --corpus '/sokvag/till/PB Korpus'
```

Urvalsberättelsen och metodrapportens historiska uppgifter uppdateras när arbetssättet förändras. Gränssnittets aktuella gransknings- och registersiffror beräknas från data. Webbplatsen är statisk HTML med dynamiska funktioner i webbläsaren; ändrade lokala filer visas offentligt först efter en ny GitHub-publicering.

## Vad sparas var?

| Innehåll | Webbprojekt | Lokal korpus |
|---|---|---|
| Redaktionellt urval och aktiv revision | `editorial/edition.json` | `04_metadata/editorial_edition.json` |
| Revisionsfiler som inte skrivs över | `editorial/revisions/` | `03_normaliserad_text/reviews/` |
| Register | `editorial/register.json` | `04_metadata/editorial_register.json` |
| Verk och dokumentversioner | `editorial/works.json` | `04_metadata/editorial_works.json` |
| Versionskopior av begrepp och personer | Ingår i registerkälldatan | `05_lexikon/begreppsregister-<version>.json`, `06_entiteter/personregister-<version>.json` |
| Genererad webbexport | `docs/edition.json`, `docs/assets/edition.js` | Byggs från ovanstående källdata |

En oberoende säkerhetskopia av originalarkivet behöver fortfarande ordnas. Publicering på GitHub är ett separat steg; inga filer har laddats upp av denna bearbetning.

Granskningsbilderna för version 0.2.0 sparas i korpusens `09_arbetsfiler/granskning-0.2.0`. En kontrolljournal i `04_metadata/editorial_review_checks-0.2.0.json` kopplar sidbild, original och revisionsfil via kontrollsummor.

Maskinell OCR är en separat textversion och blir aldrig korrekturläst genom exporten. Kandidatfiler återanvänds bara när original- och modellkontrollsummor stämmer. Parametrar och motorversion måste också kontrolleras vid återstart; vid ändrad metod används en ny versionsmapp. `verify_bulk.py` kontrollerar original, bevarad råtext och arkiverade revisioner. Uppdatera därefter körningsrapporten med `build_bulk_report.py`.

## Bellman som jämförelsetext

Språkbankens XML exporteras separat med `scripts/export_bellman.py KORPUSMAPP` och kontrolleras med `scripts/verify_bellman.py KORPUSMAPP`. Samtliga 452 030 ordtoken bevaras, med ordpositioner och meningsidentifierare. Sidangivelserna gäller datakällan, inte PDF-filerna. `docs/reference-texts/` och Bellman-sökningen ingår i webbplatsen. Källangivelse, DOI och CC BY 4.0 måste följa med vid publicering. Ändrade källfiler ska få en ny kontrollsumma och kräver en ny jämförelse.
