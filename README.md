# SeHomeWall

Integracja `notify` dla Home Assistant — pozwala wysyłać powiadomienia na
tablet **SeHomeWall** przez standardową akcję **„Wyślij powiadomienie"**.

Każda wiadomość jest przekazywana jako zdarzenie WebSocket
`sehomewall_message`, którego apka na tablecie nasłuchuje bezpośrednio —
pojawia się na klocku Alarm dashboardu i jest czytana na głos.

## Instalacja przez HACS

1. HACS → trzy kropki w prawym górnym rogu → **„Niestandardowe repozytoria"**
2. URL repozytorium: `https://github.com/sepietras72/HA_SeHomeWall`, kategoria: **Integracja**
3. **Dodaj** → znajdź „SeHomeWall" na liście → **Pobierz**
4. Uruchom ponownie Home Assistant
5. **Ustawienia → Urządzenia i usługi → Dodaj integrację → SeHomeWall**

## Użycie

W dowolnej automatyzacji/skrypcie: akcja **„Wyślij powiadomienie"** → cel
**SeHomeWall** → wiadomość (opcjonalnie tytuł) → wyślij.
