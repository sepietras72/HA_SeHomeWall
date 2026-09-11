"""Encja notify „SeHomeWall".

Akcja „Wyślij powiadomienie" -> cel „SeHomeWall" (albo usługa
`notify.send_message` z `entity_id: notify.sehomewall`) jest przekazywana
dalej jako zdarzenie WebSocket `sehomewall_message` — apka na tablecie
SeHomeWall już go nasłuchuje. Wpis trafia na
klocek Alarm na tablecie i jest ZAWSZE czytany na głos, z ustaloną z góry
ikoną (DEFAULT_ICON) — celowo zero dodatkowych pól do wypełnienia, żeby
zwykły użytkownik miał dokładnie tyle samo kroków co przy wysyłaniu
powiadomienia na telefon: wiadomość (+ opcjonalnie tytuł) i wysyłka.
"""
from __future__ import annotations

from homeassistant.components.notify import NotifyEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DEFAULT_ICON, DOMAIN

EVENT_TYPE = "sehomewall_message"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([SeHomeWallNotifyEntity(entry)])


class SeHomeWallNotifyEntity(NotifyEntity):
    # Bez `_attr_supported_features` (NotifyEntityFeature) — niepotwierdzone
    # API, ryzyko błędu importu przy starcie integracji (dokładnie to,
    # podejrzewane jako przyczyna, że encja nigdy się nie tworzyła). Tytuł
    # i tak działa: `async_send_message` przyjmuje `title` niezależnie od
    # jakiejkolwiek flagi.
    _attr_has_entity_name = True
    _attr_name = None

    def __init__(self, entry: ConfigEntry) -> None:
        self._attr_unique_id = f"{entry.entry_id}_notify"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="SeHomeWall",
            manufacturer="SeHomeWall",
        )

    async def async_send_message(self, message: str, title: str | None = None) -> None:
        text = f"{title}: {message}" if title else message
        self.hass.bus.async_fire(EVENT_TYPE, {"text": text, "icon": DEFAULT_ICON})
