# AGY-Handoff — CompText Codex 6 / Sprint C

## Ausgangspunkt
- Repository: ProfRandom92/comptext-codex
- Zielbranch: experiment/codex-v6-catalog-gate-20261122
- Draft-PR #58; main nicht verändern, nicht mergen.
- Katalog: 415 Datensätze, 81 Quarantäne, 334 ungeprüft. Originaldigest f51e00d712c9466e32071872bb2e220194d06d2af080915806e482ad5df41ebc.
- Review-Quelle: review/legacy-aa59150-quarantine-81.md (relativ zu diesem Dokument).

## Auftrag an Antigravity
Implementiere einen isolierten, rein deklarativen Compiler-Prototyp für zehn harmlose, fachlich überprüfbare Kernoperationen. Keine Toolausführung, keine Shell, kein Netzwerk, keine Änderungen an Berechtigungen oder externen Systemen. Benutze ausschließlich synthetische Fixtures. Bestehenden historischen Katalog nicht verändern.

### Arbeitspakete
1. Lies Repository-Instruktionen, aktuelle Tests, Kataloggenerator und MCP-Adapter. Dokumentiere Ausgangscommit und Baseline-Tests.
2. Prüfe alle 21 P0-Einträge auf Mehrdeutigkeit, Herkunft, Seiteneffekte und Dokumentationslücken. Halte EXEC, CALL, TOOL, MCP_TOOL, DEPLOY, ROLLBACK, CONFIG_SET und sonstige zustandsändernde Operationen ausdrücklich gesperrt. Erfinde keine Legacy-Semantik.
3. Entwirf zehn rein deklarative Kernoperationen (Vorschläge: LOOKUP, DESCRIBE, SUMMARIZE, CLASSIFY, COMPARE, FORMAT, VALIDATE, CITE, OUTLINE, REPORT). Ordne vorhandene IDs nur bei belegter Übereinstimmung zu; sonst separate vNext-Namespace-Definitionen ohne Legacy-Alias. Kein Eintrag erhält Ausführungsrechte.
4. Erstelle Registry-Schema mit versionierter ID, Beschreibung, typisierten Pflicht-/Optionalparametern, positiven/negativen Beispielen, Quellenreferenz, Reviewstatus und deklarativem Seiteneffektprofil.
5. Compiler akzeptiert ausschließlich strukturierte Daten, validiert strikt und erzeugt einen kanonischen, deterministischen Plan. Keine freien Shellstrings, Tool-Dispatcher, dynamischen Imports oder automatische Ausführung. Unbekannte Felder, Typen, IDs, Mehrdeutigkeiten und nicht unterstützte Versionen ablehnen. Autorisierung bleibt extern; Ausgabe enthält keine Freigabe.
6. Implementiere Tests mit synthetischen Daten; dokumentiere Ergebnisse, Fehler und offene Grenzen. Keine produktiven Schlüssel oder Witness-Änderungen.

### Abnahme
- Historische 415 Datensätze und 81 Quarantänefälle unverändert; keine automatische Freischaltung.
- 10 dokumentierte deklarative Operationen mit mindestens einem positiven und zwei negativen Tests je Operation.
- Byte-identische kanonische Ausgabe bei semantisch identischen Eingaben.
- Nachweis, dass ungültige Eingaben nicht stillschweigend gekürzt oder umgedeutet werden.
- Alle bestehenden Regressionstests und Catalog Gate erfolgreich; Python 3.10–3.12.
- Dokumentiere Testbefehle, Testanzahl, Ausgangs-/Endcommit und Diff.
- Keine Änderungen an main, Cloudflare, Wave Memory, Secrets oder Berechtigungen. Kein Deployment und kein Merge.

## Übergabeprozess
AGY erstellt einen separaten Arbeitsbranch vom oben genannten Zielbranch, liefert einen Commit und optional einen Draft-PR gegen diesen Zielbranch. ChatGPT prüft Diff und Tests unabhängig. Erst nach expliziter Abnahme wird die spätere Integration gesondert geplant.

## Startprompt
Lies diese Datei vollständig und arbeite die Arbeitspakete in der angegebenen Reihenfolge ab. Prüfe den tatsächlichen Repository-Zustand vor Änderungen. Melde zuerst Baseline, dann implementiere den isolierten Prototyp samt Tests. Stoppe bei Scope-Konflikten; ändere niemals Berechtigungen oder führe deklarierte Operationen aus. Liefere am Ende reproduzierbare Testbefehle, Testergebnisse, Commit und offene Punkte.
