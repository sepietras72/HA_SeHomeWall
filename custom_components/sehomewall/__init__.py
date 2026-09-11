"""SeHomeWall — integracja notify konfigurowana przyciskiem (bez YAML).

Dwie drogi wysyłki, obie kończą się tym samym zdarzeniem WebSocket
`sehomewall_message`, którego nasłuchuje apka na tablecie SeHomeWall (wpis na
klocku Alarm + odczyt na głos):

1. Wbudowana akcja "Wyślij powiadomienie" -> cel "SeHomeWall" (encja
   `notify.sehomewall`, patrz notify.py) — najprościej, ale tylko
   wiadomość/tytuł (sztywny schemat HA, nie da się dodać własnych pól).
2. Własna akcja "SeHomeWall: Wyślij wiadomość" (`sehomewall.send_message`,
   patrz services.yaml) — pełna kontrola: tekst, ikona (picker MDI), kolor
   (picker koloru), przeczytaj na głos (tak/nie). Szukana po nazwie w
   kreatorze akcji jak każda inna, zero YAML.
"""
from __future__ import annotations

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN

PLATFORMS: list[Platform] = [Platform.NOTIFY]

SERVICE_SEND_MESSAGE = "send_message"
EVENT_TYPE = "sehomewall_message"

# `color_rgb` w formularzu akcji zwraca listę [r, g, b] (0-255 każdy) —
# konwertowane niżej na "#RRGGBB", bo tego formatu oczekuje apka
# (GridViewModel.handleIncomingHaMessage -> android.graphics.Color.parseColor).
SEND_MESSAGE_SCHEMA = vol.Schema(
    {
        vol.Required("message"): cv.string,
        vol.Optional("icon"): cv.string,
        vol.Optional("color"): vol.All(cv.ensure_list, [vol.Coerce(int)]),
        vol.Optional("tts", default=True): cv.boolean,
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def _handle_send_message(call: ServiceCall) -> None:
        event_data: dict = {"text": call.data["message"]}
        if "icon" in call.data:
            event_data["icon"] = call.data["icon"]
        if "color" in call.data:
            r, g, b = call.data["color"][:3]
            event_data["color"] = f"#{r:02X}{g:02X}{b:02X}"
        event_data["tts"] = call.data.get("tts", True)
        hass.bus.async_fire(EVENT_TYPE, event_data)

    if not hass.services.has_service(DOMAIN, SERVICE_SEND_MESSAGE):
        hass.services.async_register(
            DOMAIN, SERVICE_SEND_MESSAGE, _handle_send_message, schema=SEND_MESSAGE_SCHEMA
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if hass.services.has_service(DOMAIN, SERVICE_SEND_MESSAGE):
        hass.services.async_remove(DOMAIN, SERVICE_SEND_MESSAGE)
    return unload_ok
