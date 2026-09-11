"""SeHomeWall — integracja notify konfigurowana przyciskiem (bez YAML).

Wpis w Ustawieniach -> Urządzenia i usługi -> Dodaj integrację -> "SeHomeWall"
tworzy jedną encję notify. Każde użycie akcji "Wyślij powiadomienie" -> cel
"SeHomeWall" jest przekazywane dalej jako zdarzenie WebSocket
`sehomewall_message` — dokładnie to, czego już nasłuchuje apka AuraWall
(patrz GridViewModel.handleIncomingHaMessage w projekcie AuraWall). Wpis
trafia na klocek Alarm na tablecie i jest czytany na głos.
"""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

PLATFORMS: list[Platform] = [Platform.NOTIFY]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
