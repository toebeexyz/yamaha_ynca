from __future__ import annotations

from dataclasses import dataclass
import re
from typing import TYPE_CHECKING

from defusedxml import ElementTree as ET  # noqa: N817
from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
)
from homeassistant.const import SIGNAL_STRENGTH_DECIBELS
from homeassistant.helpers.entity import EntityCategory

import ynca

from .const import (
    CONF_SERIAL_URL,
    ZONE_ATTRIBUTE_NAMES,
    ZONE_MAX_VOLUME,
    ZONE_MIN_VOLUME,
)
from .entity import YamahaYncaSettingEntity

if TYPE_CHECKING:
    from collections.abc import Callable

    from aiohttp import ClientSession
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from . import YamahaYncaConfigEntry


def volume_native_max_value_fn(associated_zone: ynca.ZoneBase) -> float:
    return float(
        associated_zone.maxvol
        if associated_zone.maxvol is not None
        else ZONE_MAX_VOLUME
    )


@dataclass(frozen=True, kw_only=True)
class YncaNumberEntityDescription(NumberEntityDescription):
    function_names: list[str] | None = None
    """Function names which indicate updates for this entity. Only needed when it does not match `key.upper()`"""
    native_max_value_fn: Callable[[ynca.ZoneBase], float] | None = None
    """Function that returns max value. Use when a fixed number is not enough"""


ENTITY_DESCRIPTIONS = [
    # Suppress following mypy message, which seems to be not an issue as other values have defaults:
    # custom_components/yamaha_ynca/number.py:19: error: Missing positional arguments "entity_registry_enabled_default", "entity_registry_visible_default", "force_update", "icon", "has_entity_name", "unit_of_measurement", "max_value", "min_value", "step" in call to "NumberEntityDescription"  [call-arg]
    YncaNumberEntityDescription(
        key="maxvol",
        device_class=NumberDeviceClass.SIGNAL_STRENGTH,
        entity_category=EntityCategory.CONFIG,
        icon="mdi:volume-vibrate",
        native_min_value=-30,
        native_max_value=ZONE_MAX_VOLUME,
        native_step=0.5,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS,
    ),
    YncaNumberEntityDescription(
        key="vol",
        device_class=NumberDeviceClass.SIGNAL_STRENGTH,
        icon="mdi:volume-high",
        native_min_value=ZONE_MIN_VOLUME,
        native_max_value_fn=volume_native_max_value_fn,
        native_step=0.5,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS,
        function_names=["VOL", "MAXVOL"],
    ),
    YncaNumberEntityDescription(
        key="spbass",
        device_class=NumberDeviceClass.SIGNAL_STRENGTH,
        entity_category=EntityCategory.CONFIG,
        icon="mdi:speaker",
        native_min_value=-6,
        native_max_value=6,
        native_step=0.5,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS,
        entity_registry_enabled_default=False,
    ),
    YncaNumberEntityDescription(
        key="sptreble",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.SIGNAL_STRENGTH,
        icon="mdi:speaker",
        native_min_value=-6,
        native_max_value=6,
        native_step=0.5,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS,
        entity_registry_enabled_default=False,
    ),
    YncaNumberEntityDescription(
        key="hpbass",
        device_class=NumberDeviceClass.SIGNAL_STRENGTH,
        entity_category=EntityCategory.CONFIG,
        icon="mdi:headphones",
        native_min_value=-6,
        native_max_value=6,
        native_step=0.5,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS,
        entity_registry_enabled_default=False,
    ),
    YncaNumberEntityDescription(
        key="hptreble",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.SIGNAL_STRENGTH,
        icon="mdi:headphones",
        native_min_value=-6,
        native_max_value=6,
        native_step=0.5,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS,
        entity_registry_enabled_default=False,
    ),
]

InitialVolumeValueEntityDescription = YncaNumberEntityDescription(
    key="initvollvl",
    entity_category=EntityCategory.CONFIG,
    device_class=NumberDeviceClass.SIGNAL_STRENGTH,
    icon="mdi:knob",
    native_min_value=-80.0,
    native_max_value=ZONE_MAX_VOLUME,
    native_step=0.5,
    native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS,
    function_names=["INITVOLLVL", "INITVOLMODE"],
)


@dataclass(frozen=True, kw_only=True)
class SpeakerLevelDescription(NumberEntityDescription):
    xml_name: str


SPEAKER_LEVEL_DESCRIPTIONS = [
    SpeakerLevelDescription(
        key="speaker_front_left",
        translation_key="speaker_front_left",
        xml_name="Front_L",
        native_min_value=-10,
        native_max_value=10,
        native_step=0.5,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS,
        icon="mdi:speaker",
        entity_category=EntityCategory.CONFIG,
    ),
    SpeakerLevelDescription(
        key="speaker_front_right",
        translation_key="speaker_front_right",
        xml_name="Front_R",
        native_min_value=-10,
        native_max_value=10,
        native_step=0.5,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS,
        icon="mdi:speaker",
        entity_category=EntityCategory.CONFIG,
    ),
    SpeakerLevelDescription(
        key="speaker_center",
        translation_key="speaker_center",
        xml_name="Center",
        native_min_value=-10,
        native_max_value=10,
        native_step=0.5,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS,
        icon="mdi:speaker",
        entity_category=EntityCategory.CONFIG,
    ),
    SpeakerLevelDescription(
        key="speaker_surround_left",
        translation_key="speaker_surround_left",
        xml_name="Sur_L",
        native_min_value=-10,
        native_max_value=10,
        native_step=0.5,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS,
        icon="mdi:speaker",
        entity_category=EntityCategory.CONFIG,
    ),
    SpeakerLevelDescription(
        key="speaker_surround_right",
        translation_key="speaker_surround_right",
        xml_name="Sur_R",
        native_min_value=-10,
        native_max_value=10,
        native_step=0.5,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS,
        icon="mdi:speaker",
        entity_category=EntityCategory.CONFIG,
    ),
    SpeakerLevelDescription(
        key="speaker_surround_back_left",
        translation_key="speaker_surround_back_left",
        xml_name="Sur_Back_L",
        native_min_value=-10,
        native_max_value=10,
        native_step=0.5,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS,
        icon="mdi:speaker",
        entity_category=EntityCategory.CONFIG,
    ),
    SpeakerLevelDescription(
        key="speaker_surround_back_right",
        translation_key="speaker_surround_back_right",
        xml_name="Sur_Back_R",
        native_min_value=-10,
        native_max_value=10,
        native_step=0.5,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS,
        icon="mdi:speaker",
        entity_category=EntityCategory.CONFIG,
    ),
    SpeakerLevelDescription(
        key="speaker_subwoofer",
        translation_key="speaker_subwoofer",
        xml_name="Subwoofer_1",
        native_min_value=-10,
        native_max_value=10,
        native_step=0.5,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS,
        icon="mdi:subwoofer",
        entity_category=EntityCategory.CONFIG,
    ),
]


def receiver_http_url(serial_url: str) -> str | None:
    """Return the receiver HTTP base URL for a network YNCA URL."""
    if match := re.fullmatch(r"socket://([^:]+)(?::\d+)?", serial_url):
        return f"http://{match[1]}"
    return None


def speaker_level_xml(value: float | None = None, xml_name: str | None = None) -> str:
    """Build a speaker level GET or PUT request."""
    if value is None or xml_name is None:
        return "<System><Speaker_Preout><Pattern_1><Lvl>GetParam</Lvl></Pattern_1></Speaker_Preout></System>"
    encoded_value = round(value * 10)
    return (
        "<System><Speaker_Preout><Pattern_1><Lvl>"
        f"<{xml_name}><Val>{encoded_value}</Val><Exp>1</Exp><Unit>dB</Unit></{xml_name}>"
        "</Lvl></Pattern_1></Speaker_Preout></System>"
    )


async def async_get_speaker_levels(
    session: ClientSession, base_url: str
) -> dict[str, float]:
    """Read speaker levels from the receiver web API."""
    async with session.post(
        f"{base_url}/YamahaRemoteControl/ctrl",
        data=f'<YAMAHA_AV cmd="GET">{speaker_level_xml()}</YAMAHA_AV>',
        headers={"Content-Type": "text/xml"},
    ) as response:
        response.raise_for_status()
        root = ET.fromstring(await response.text())
    levels = root.find(".//Lvl")
    if levels is None:
        return {}
    return {
        child.tag: float(child.findtext("Val", "0")) / 10
        for child in levels
        if child.find("Val") is not None
    }


async def async_set_speaker_level(
    session: ClientSession,
    base_url: str,
    description: SpeakerLevelDescription,
    value: float,
) -> None:
    """Write a speaker level through the receiver web API."""
    async with session.post(
        f"{base_url}/YamahaRemoteControl/ctrl",
        data=f'<YAMAHA_AV cmd="PUT">{speaker_level_xml(value, description.xml_name)}</YAMAHA_AV>',
        headers={"Content-Type": "text/xml"},
    ) as response:
        response.raise_for_status()


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: YamahaYncaConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    domain_entry_data = config_entry.runtime_data

    entities = []
    for zone_attr_name in ZONE_ATTRIBUTE_NAMES:
        if zone_subunit := getattr(domain_entry_data.api, zone_attr_name):
            entities.extend(
                [
                    YamahaYncaNumber(
                        config_entry.entry_id, zone_subunit, entity_description
                    )
                    for entity_description in ENTITY_DESCRIPTIONS
                    if getattr(zone_subunit, entity_description.key, None) is not None
                ]
            )

            if zone_subunit.initvollvl is not None:
                entities.append(
                    YamahaYncaNumberInitialVolume(
                        config_entry.entry_id,
                        zone_subunit,
                        InitialVolumeValueEntityDescription,
                    )
                )

    if (base_url := receiver_http_url(config_entry.data.get(CONF_SERIAL_URL, ""))) and (
        main_zone := domain_entry_data.api.main
    ):
        from homeassistant.helpers.aiohttp_client import async_get_clientsession

        levels = await async_get_speaker_levels(async_get_clientsession(hass), base_url)
        entities.extend(
            YamahaSpeakerLevel(
                config_entry.entry_id,
                main_zone,
                description,
                SpeakerLevelState(
                    hass=hass,
                    base_url=base_url,
                    value=levels[description.xml_name],
                ),
            )
            for description in SPEAKER_LEVEL_DESCRIPTIONS
            if description.xml_name in levels
        )

    async_add_entities(entities)


class YamahaYncaNumber(YamahaYncaSettingEntity, NumberEntity):  # type: ignore[misc]
    """Representation of a number on a Yamaha Ynca device."""

    entity_description: YncaNumberEntityDescription

    @property
    def native_value(self) -> float | None:
        """Return the value reported by the number."""
        return getattr(self._subunit, self.entity_description.key, None)

    @property
    def native_max_value(self) -> float:
        """Return the maximum value."""
        if fn := self.entity_description.native_max_value_fn:
            return fn(self._associated_zone)
        return float(super().native_max_value)

    def set_native_value(self, value: float) -> None:
        setattr(self._subunit, self.entity_description.key, value)


class YamahaYncaNumberInitialVolume(YamahaYncaNumber):
    """Representation Initial Volume level.

    This is special as it is not always a number and can depend on InitLvlMode
    """

    @property
    def available(self) -> bool:
        return (
            super().available
            and isinstance(self._associated_zone.initvollvl, float)
            and self._associated_zone.initvolmode is not ynca.InitVolMode.OFF
        )


@dataclass
class SpeakerLevelState:
    hass: HomeAssistant
    base_url: str
    value: float


class YamahaSpeakerLevel(YamahaYncaSettingEntity, NumberEntity):  # type: ignore[misc]
    """Representation of a speaker level from the receiver web API."""

    entity_description: SpeakerLevelDescription

    def __init__(
        self,
        receiver_unique_id: str,
        subunit: ynca.ZoneBase,
        description: SpeakerLevelDescription,
        state: SpeakerLevelState,
    ) -> None:
        super().__init__(receiver_unique_id, subunit, description)
        self._speaker_level_state = state

    @property
    def native_value(self) -> float:
        return self._speaker_level_state.value

    async def async_set_native_value(self, value: float) -> None:
        from homeassistant.helpers.aiohttp_client import async_get_clientsession

        await async_set_speaker_level(
            async_get_clientsession(self._speaker_level_state.hass),
            self._speaker_level_state.base_url,
            self.entity_description,
            value,
        )
        self._speaker_level_state.value = value
        self.async_write_ha_state()
