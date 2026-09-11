"""Klasyczna usługa notify „SeHomeWall".

Rejestrowana dynamicznie przez `async_load_platform` w __init__.py (patrz
KDoc tam) — DOKŁADNIE ten sam mechanizm co np. `notify.mobile_app_telefon`.
Dzięki temu w akcji „Wyślij powiadomienie" pojawia się jako osobna pozycja
„SeHomeWall" z opisem „Sends a notification message using the SeHomeWall
integration" — identycznie jak każdy telefon/telewizor z Companion App,
zamiast nowego, „encjowego" `notify.send_message`.

Każde wywołanie jest przekazywane dalej jako zdarzenie WebSocket
`sehomewall_message`, którego apka na tablecie SeHomeWall nasłuchuje
bezpośrednio. Pole „Dane" (sekcja "Data" akcji) przyjmuje opcjonalnie:
  tts:   true/false  — przeczytaj na głos (domyślnie: true)
  icon:  "mdi:xxx"   — ikona wpisu na klocku Alarm
  color: "#RRGGBB"   — kolor kreski wpisu w dzienniku
"""
from __future__ import annotations

from typing import Any

from homeassistant.components.notify import BaseNotificationService
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

EVENT_TYPE = "sehomewall_message"


async def async_get_service(
    hass: HomeAssistant,
    config: ConfigType,
    discovery_info: DiscoveryInfoType | None = None,
) -> "SeHomeWallNotificationService":
    return SeHomeWallNotificationService(hass)


class SeHomeWallNotificationService(BaseNotificationService):
    """Przekazuje `notify.sehomewall` dalej jako zdarzenie `sehomewall_message`."""

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass

    async def async_send_message(self, message: str = "", **kwargs: Any) -> None:
        title = kwargs.get("title")
        text = f"{title}: {message}" if title else message

        data = kwargs.get("data") or {}
        event_data: dict[str, Any] = {"text": text}
        for key in ("tts", "icon", "color"):
            if key in data:
                event_data[key] = data[key]

        self.hass.bus.async_fire(EVENT_TYPE, event_data)
