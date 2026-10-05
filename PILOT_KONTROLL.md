# Kontroll av fulltextpiloten

Utförd 5 oktober 2026. Fyra original med verifierade SHA-256-kontrollsummor gav 672 PDF-sidor, varav 653 innehåller extraherbar text. Ingen ny OCR eller manuell rättning utfördes.

## Visuella stickprov

Två PDF-sidor per verk jämfördes med sidbilder:

| Verk | PDF-sidor | Bedömning |
|---|---|---|
| Sällskapet Par Bricole (1946) | 20, 185 | Läsbar text med fel i bokstäver och siffror. |
| Par Bricoles gustavianska period (Kinberg) | 20, 55 | Betydande OCR-fel och problem med läsordning i uppslag. |
| Handlingar ur Sällskapet P.B:s arkiv (1855) | 20, 53 | Betydande teckenfel och problem med läsordning. |
| Utvalda Historiska Barbaratal | 20, 42 | Övervägande läsbar text; enstaka OCR-fel. |

Stickproven är ingen fullständig kvalitetsgranskning. PDF-sidnummer är positioner i filen, inte tryckta sidnummer. Sidor utan extraherbar text kan vara blanka eller innehålla bilder.

## Kontroller i webbläsaren

- Frasen ”Bellmans ordensupptåg” gav fyra sidor i 1946 års verk, inklusive den visuellt kontrollerade PDF-sidan 20.
- ”Bacchi” i alla fyra verk gav 97 sidor; nästa resultatsida fungerade.
- ”FALKMAN” i Kinbergs verk gav PDF-sidorna 20, 25 och 102. Länkarna har motsvarande sidankare.
- Sidans fullständiga extraherade text kan öppnas i resultatet.
- En sökning utan träffar gav en tydlig förklaring.

Metodrapporten på webbplatsen redovisar omfattning och begränsningar. Materialet är ännu inte publicerat på GitHub.

## Förbättring av läsordning

Kinberg PDF 20 och 55 samt Handlingar PDF 20 har bearbetats utifrån ordpositioner. Vänster boksida läses före höger. Sammanlagt 1 669 ordtoken bevarades utan borttagning, tillägg eller teckenändring i denna omordning. De tre uppslagens ordning jämfördes med de renderade sidbilderna. Bearbetningen ändrar inga andra sidor. Råtexten finns kvar för jämförelse.

Frasen ”1753 t 30 juli 1802” ger efter omordningen träff på Kinbergs PDF-sida 20, utan att blanda in den högra boksidans text. Frassökning i de bearbetade uppslagen korsar inte gränsen mellan vänster och höger boksida. Samtliga pilottexters råfält jämfördes med den bevarade grundextraktionen och var oförändrade.

## Granskad utgåva 0.2.0

Tio PDF-sidors tryckta löptext och noter granskades mot renderade sidbilder i vänster och höger sidhalva: Kinberg 5, 6, 8, 9, 10 samt Handlingar 5, 19, 20, 21, 53. Transkriptionen bevarar äldre stavning, tryckets felformer och separata boksidor; prosa ombryts medan versrader behålls. Bilder, handskrivna bildtexter och signaturer, stämplar och arksignaturer ingår inte. Kvalitetsnivån innebär en AI-assisterad visuell genomgång, inte oberoende dubbelgranskning.

15 personposter och 14 begrepps- och motivposter har 40 belägg. Tryckta sidnummer registrerades där de syns; onumrerade sidor får inga antagna nummer. Årtalsavvikelsen för Sackenhjelms parentation (1777 hos Kinberg, 1778 i Handlingarnas rubrik) redovisas. Kinbergs egen rättelselista har inte tyst förts in i de andra sidorna.

Käll-PDF:ernas kontrollsummor stämmer med manifestet. Alla 672 råtexter är oförändrade. Fyra automatiska kontroller visar att en ny revision bevarar äldre versioner och äldre beläggshänvisningar, att fel originalversion och saknade belägg avvisas samt att en redan arkiverad revision inte kan skrivas över.

Webbläsarkontroll: registret filtrerar på Sackenhjelm och visar båda årtalen med läslänkar; sidläsaren växlar mellan urvalsrevision 1 och korrekturläsningsrevision 2 samt visar råtext för jämförelse. Frasen ”Bacchi giftermål” med kvalitetsfiltret korrekturläst ger Handlingarnas PDF-sida 53 med rättad rubrik och revisionslänk.
