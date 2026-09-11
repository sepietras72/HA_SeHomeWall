"""SeHomeWall — integracja notify konfigurowana przyciskiem (bez YAML).

Rejestruje KLASYCZNĄ usługę `notify.sehomewall` przez `async_load_platform`
(mechanizm "discovery") zamiast nowej, encjowej platformy `notify` — to ten
sam sposób, w jaki Companion App rejestruje `notify.mobile_app_<telefon>`.
Dzięki temu „SeHomeWall" pojawia się w akcji „Wyślij powiadomienie" jako
zwykła pozycja z opisem „Sends a notification message using the SeHomeWall
integration", identycznie jak dla telefonu/telewizora — bez wpisu w
configuration.yaml (discovery jest wywoływane z poziomu Pythona, tu, po
dodaniu integracji przyciskiem).

Druga, opcjonalna droga: własna akcja "SeHomeWall: Wyślij wiadomość"
(`sehomewall.send_message`, patrz services.yaml) — formularz z pickerem
ikony/koloru zamiast ręcznego wpisywania w sekcji "Dane".

Obie drogi kończą się tym samym zdarzeniem WebSocket `sehomewall_message`,
którego nasłuchuje apka na tablecie SeHomeWall (klocek Alarm + TTS).
"""
from __future__ import annotations

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.discovery import async_load_platform

from .const import DOMAIN

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
    # Klasyczna usługa notify.sehomewall — patrz KDoc notify.py. `discovery_info`
    # zamiast wpisu w configuration.yaml pod kluczem `notify:` — TEN SAM efekt,
    # bez YAML.
    hass.async_create_task(
        async_load_platform(hass, "notify", DOMAIN, {"name": "SeHomeWall"}, {})
    )

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
    if hass.services.has_service(DOMAIN, SERVICE_SEND_MESSAGE):
        hass.services.async_remove(DOMAIN, SERVICE_SEND_MESSAGE)
    # Legacy platforma notify załadowana przez discovery nie ma formalnego
    # mechanizmu "unload" w HA — zostaje zarejestrowana do restartu, tak samo
    # jak w każdej innej integracji używającej tego wzorca.
    return True
