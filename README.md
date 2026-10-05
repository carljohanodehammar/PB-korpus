# PB Korpus – webbplats för GitHub Pages

En publiceringsförberedd webbplats med katalogsökning, samlingsfilter, sortering, proveniens och rapporten **Så byggdes korpusen**. All besökarfunktion körs i webbläsaren. Ingen server, installation eller extern JavaScript-tjänst behövs.

## Förhandsvisa

Öppna `docs/index.html` i webbläsaren. Katalogen följer med i `docs/assets/catalog.js`, så även lokal förhandsvisning fungerar. Alternativt, kör från denna mapp:

```sh
python3 -m http.server 8000
```

Öppna sedan `http://localhost:8000/docs/`.

## Publicera på GitHub

1. Lägg innehållet i denna mapp i det GitHub-repository som ska äga webbplatsen.
2. Öppna repositoryts **Settings → Pages**.
3. Välj **Deploy from a branch**, den gren som innehåller filerna och mappen **/docs**.
4. Spara. GitHub visar webbplatsens adress när publiceringen är klar.

Alla interna länkar är relativa och fungerar även på en projektadress som `https://anvandare.github.io/repository/`. `.nojekyll` markerar att webbplatsen ska levereras som färdiga statiska filer. Ingen GitHub Actions-fil är nödvändig för denna publiceringsmetod.

Officiell vägledning: https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site

## Uppdatera korpusen

Efter att originalfiler och det lokala manifestet har uppdaterats:

```sh
python3 scripts/update_catalog.py '/sokvag/till/PB Korpus/04_metadata/corpus_manifest.json'
```

Granska ändringarna och för över dem till GitHub. Katalogen och omfattningssiffrorna uppdateras automatiskt vid nästa publicering. Metodrapportens historiska berättelse ändras manuellt när arbetssättet förändras. Det finns ingen schemalagd uppdatering från den lokala datorn.

`update_catalog.py` exporterar en uttrycklig lista av publika fält. Absoluta lokala sökvägar och interna arbetsfiler följer inte med. Katalogen använder innehållsbaserade dokument-ID; ändrad filversion får ett annat ID.

## Vad publiceras?

- `docs/index.html`: rapport och kataloggränssnitt.
- `docs/assets/style.css`: utseende, responsiv layout och tangentbordsfokus.
- `docs/assets/app.js`: filtrering, sortering och sidvisning.
- `docs/assets/catalog.js`: katalogdata för webbgränssnittet.
- `docs/catalog.json`: samma metadata i ett nedladdningsbart, maskinläsbart format.

Originalarkivet på cirka 4,50 GB ingår inte. Webbplatsen öppnar originalutgivarnas dokumentlänkar. GitHub Pages lämpar sig för den mindre webbplatsen och dess index, medan större originalfiler behöver en separat lagringslösning. Publicerade Pages-webbplatser har en storleksgräns på 1 GB: https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits

Källornas rättigheter är inte ett och samma tillstånd. Språkbankens Bellman-data har CC BY 4.0; övriga filer behöver rättighetsbedömas innan egen offentlig distribution. Denna förberedelse laddar inte upp originalfiler eller publicerar webbplatsen.

## Fulltext i hela PDF-korpusen

Fulltextsökning omfattar 220 PDF-källor med 6 629 sidor. Grundextraktionen gav text på 5 158 sidor; en separat OCR-körning kompletterar skannade och textlösa sidor. Aktuella resultat redovisas i metodrapportens avsnitt 10 och `docs/bulk-processing.json`. Sökningen fungerar utan server och läser textfiler vid första sökningen. Sökord på samma PDF-sida och sammanhängande fraser stöds.

`docs/texts/<document-id>.json` innehåller oförändrat extraherat textlager per PDF-sida. Motsvarande `.js` gör även lokal öppning från filsystemet möjlig. Tryckta sidnummer är inte antagna: `printedPage` är null. Originalets SHA-256 och extraktionsmetoden följer varje textversion.

För att extrahera hela PDF-korpusen med Poppler installerat:

```sh
python3 scripts/extract_corpus.py '/sokvag/till/PB Korpus' --pdftotext /sokvag/till/pdftotext
```

Grundextraktionen sparas i korpusens `02_ocr/full`; den tidigare piloten finns kvar i `02_ocr/pilot`. Rapporten redovisar åtta visuella stickprov. Originalen har inte ändrats. OCR-fel gör att sökningen kan missa ord och ge missvisande utdrag. Grundextraktionens läsordning följer det befintliga textlagret. Senare redaktionella tillägg används separat.

Vid fortsatt utbyggnad kan vi använda:

- `texts/<document-id>.json`: sidindelad text med `pdfPage`, `printedPage`, `text` och dokument-ID.
- `indexes/`: uppdelade sökindex som laddas efter behov.
- En separat, konfigurerad adress för originalfiler, så att sidbilder och belägg får beständiga länkar.

Bevara proveniens, dokumentversion och kopplingen mellan PDF-sida och tryckt sidnummer. Publicera inte interna texter via uppdateraren utan ett uttryckligt urval. Webbplatsen saknar autentisering; den är avsedd för offentligt material.

## Granskad läsordning

Tre visuellt kontrollerade uppslag har en separat `readingText`: Kinberg PDF 20 och 55 samt Handlingar PDF 20. Råfältet `text` är oförändrat. Sökning och utdrag använder korrekturläst revision först, därefter vald ny OCR, granskad läsordning eller råtext. Gränssnittet erbjuder båda versionerna. Alla ord från PDF:s positionsbaserade extraktion behålls exakt en gång; ingen OCR-teckenkorrigering görs.

Kör efter grundextraktionen:

```sh
python3 scripts/improve_reading_order.py '/sokvag/till/PB Korpus' --pdftotext /sokvag/till/pdftotext
```

Bearbetade korpustexter sparas i `03_normaliserad_text/pilot`; ändringsloggen i `04_metadata/pilot_reading_order.json` och webbplatsens `docs/reading-order.json`. Om grundextraktionen körs igen måste även detta steg köras igen.

## Växande granskad utgåva

Version 0.2.0 innehåller tio korrekturlästa PDF-sidors löptext och noter, synliga tryckta sidnummer, två revisionssteg per sida samt ett register med 15 personer, 14 begrepp/motiv och 40 belägg. Korrekturläst avser en AI-assisterad visuell genomgång. Originalets påståenden verifieras inte historiskt av textgranskningen.

Sökningen kan filtreras efter textkvalitet och använder redaktionell text före läsordningsbearbetning och råtext. Registret och sidläsaren stödjer beständiga länkar till en viss revision. `editorial/` är källdatan; `docs/edition.json` och `docs/assets/edition.js` är genererad export. Nya textkällor väljs i `editorial/text_sources.json`.

Se **[KOMPLETTERA.md](KOMPLETTERA.md)** för hur sidor, revisioner, verkversioner och registerposter läggs till. Validering och fyra historiktester:

```sh
python3 scripts/build_edition.py --corpus '/sokvag/till/PB Korpus'
python3 tests/test_edition.py
```

## Massbearbetning och fortsatt komplettering

`build_ocr_plan.py` skapar en ny sidplan från aktuellt manifest och screening, med pdfimages och pypdf. `extract_corpus.py` kontrollerar originalens SHA-256 och extraherar sidindelad råtext för hela manifestets PDF-urval. `ocr_batch.py` tar en explicit sidplan, lokal OCR-motor, modellmapp och absolut tidsgräns. Den sparar en separat kandidat per dokument-ID och PDF-sida i `02_ocr/tesseract-best-v2`. En återstart återanvänder redan färdiga sidor om original- och modellkontrollsummor matchar. En annan modellversion ska använda en ny versionsmapp. Den lokala OCR-installationen och originalen följer inte med webbplatsen.

`export_ocr.py` lägger till kandidater i webbplatsen och bevarar råfältet `text`. Alla kandidater har status ogranskad. `docs/ocr-quality.json` är den prioriterade granskningskön; maskinens säkerhet är ingen korrekthetsmätning. Gör relevanta passager till nya redaktionella revisioner enligt KOMPLETTERA.md.

Grundextraktionen finns även i `02_ocr/full`; uppgifter om urval och körning finns i `04_metadata`. Den aktuella samlingsstorleken och OCR-statistiken ska exporteras på nytt efter kompletteringar. Gamla textrevisioner och deras belägg behålls.

En separat `ocr_core.py` använder den kalibrerade svenska modellen för de två historiska kärnverken och sparar nya kandidater i `02_ocr/tesseract-core-v4`. `export_ocr.py` väljer denna version för dessa verk. Den generella massversionen bevaras parallellt. Arbetsfacit användes också för parameterkalibrering; metodtestet är därför inte en oberoende utvärdering.

Efter en ny körning:

```sh
python3 scripts/export_ocr.py '/sokvag/till/PB Korpus'
python3 scripts/build_edition.py --corpus '/sokvag/till/PB Korpus'
python3 scripts/verify_bulk.py '/sokvag/till/PB Korpus'
python3 scripts/build_bulk_report.py '/sokvag/till/PB Korpus'
```

## Bellman som jämförelsetext

Språkbankens XML exporteras separat med `scripts/export_bellman.py KORPUSMAPP` och kontrolleras med `scripts/verify_bellman.py KORPUSMAPP`. Samtliga 452 030 ordtoken bevaras, med ordpositioner och meningsidentifierare. Sidangivelserna gäller datakällan, inte PDF-filerna. `docs/reference-texts/` och Bellman-sökningen ingår i webbplatsen. Källangivelse, DOI och CC BY 4.0 måste följa med vid publicering. Ändrade källfiler ska få en ny kontrollsumma och kräver en ny jämförelse.

## Lokal bearbetning och AI-användning

Poppler, Tesseract, kontroller och webbexport körs lokalt. Agentens metodarbete, kodändringar och AI-assisterade visuella granskningar använder OpenAI genom appen och förbrukar befintlig användningskvot. Ingen extern betald OCR-tjänst eller separat betald API-modell anropas per PDF-sida. Användaren har uttryckligen angett att inga extra kostnader får beställas. Se `docs/processing-resources.json`.
