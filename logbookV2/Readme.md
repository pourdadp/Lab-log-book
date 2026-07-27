# QuickLab: Labor-Logbuch- und Managementsystem 🧪
Das System **QuickLab** ist eine standardisierte, sichere und modulare Lösung zur Protokollierung von Ereignissen, zur Überwachung des Gerätestatus und zur Zugriffsverwaltung in Laboratorien. Dieses Projekt wurde entwickelt, um Datenerfassungsfehler zu reduzieren, die Systemstabilität zu erhöhen und die Informationssicherheit zu gewährleisten.
## 🖼️ Vorschau der Benutzeroberfläche (UI Preview)
```text
+-------------------------------------------------------------------+
| 🧪 QuickLab - Labor-Logbuch-System           [👤 Benutzer: admin]   |
+-------------------------------------------------------------------+
| Hauptmenü:                | Geräteübersicht und Status:           |
| 📝 Neuer Bericht           | +--------------+----------+----------+ |
| 🖥️ Geräte anzeigen        | | Gerätename   | Temp (°C)| Status   | |
| ⚙️ Geräte verwalten (Admin)| +--------------+----------+----------+ |
| 📊 Berichte & Druck       | | Spektralphotometer| 25.0| Gut      | |
+---------------------------+ | Inkubator      | 37.0     | Abweichung|
                            +--------------+----------+----------+ |

```
## ✨ Hauptmerkmale des Systems
 * **Datensicherheit:** Verwendung des Standard-Algorithmus bcrypt zum Hashing und Schutz von Benutzerpasswörtern.
 * **Modulare Architektur:** Trennung der Projektstruktur in separate Komponenten (database.py, auth.py, config.py, app.py) für eine einfachere Wartung und Weiterentwicklung.
 * **Aktivitätsprotokollierung (Audit Trail):** Genaue Aufzeichnung aller wichtigen Benutzeraktivitäten wie Anweisungen, An- und Abmeldungen sowie Datenbearbeitungen in einer Audit-Tabelle.
 * **Unterstützung des Solar-Hijri-Kalenders:** Volle Unterstützung für persische/solar-hijri Daten und Zeiten über die Bibliothek jdatetime.
 * **Erweiterte Berichterstattung und Druck:** Möglichkeit, nützliche Filter auf Berichte anzuwenden und eine standardmäßige HTML-Ausgabe mit automatischer Druckfunktion und Signaturbereich zu generieren.
 * **Datenbankstabilität:** Zentralisierte Verbindungsverwaltung und Fehlerbehandlung mit try-except-Blöcken zur Vermeidung unerwarteter Programmabstürze.
## 👥 Zielgruppen des Systems
### 🎯 Für Laborleiter
 * Vollständige Überwachung der Geräteleistung und der Kalibrierungsdaten.
 * Zugriff auf gefilterte Berichte und offizielle Ausgaben für Audits.
 * Vermeidung menschlicher Fehler durch integrierte Löschbestätigungen.
### 💻 Für Entwickler und Technik-Teams
 * Sauberer, strukturierter Code basierend auf Python und Streamlit.
 * Schnelle Erweiterbarkeit dank der Trennung von Logik- und Datenschichten.
 * Keine komplexe Hardware-Abhängigkeit und einfache Einrichtung mit einer leichten SQLite-Datenbank.
## 🚀 Schnellstartanleitung
 1. Erstellen Sie einen neuen Ordner namens lab_logbook.
 2. Platzieren Sie die Projektdateien (config.py, database.py, auth.py, app.py) darin.
 3. Installieren Sie die erforderlichen Abhängigkeiten:
   ```bash
   pip install streamlit pandas bcrypt jdatetime
   
   ```
 4. Starten Sie das Programm über das Terminal:
   ```bash
   streamlit run app.py
   
   ```
