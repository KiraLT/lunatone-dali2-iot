from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="YnDescriptor")


@_attrs_define
class YnDescriptor:
    """
    Attributes:
        lines (int):
        buffer_size (int):
        tick_resolution (int):
        max_yn_frame_size (int):
        implemented_macros (list[int]):
        device_list_specifier (int):
        protocol_version_major (int):
        protocol_version_minor (int):
        power_supply_implemented (bool):
    """

    lines: int
    buffer_size: int
    tick_resolution: int
    max_yn_frame_size: int
    implemented_macros: list[int]
    device_list_specifier: int
    protocol_version_major: int
    protocol_version_minor: int
    power_supply_implemented: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        lines = self.lines

        buffer_size = self.buffer_size

        tick_resolution = self.tick_resolution

        max_yn_frame_size = self.max_yn_frame_size

        implemented_macros = self.implemented_macros

        device_list_specifier = self.device_list_specifier

        protocol_version_major = self.protocol_version_major

        protocol_version_minor = self.protocol_version_minor

        power_supply_implemented = self.power_supply_implemented

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "lines": lines,
                "bufferSize": buffer_size,
                "tickResolution": tick_resolution,
                "maxYnFrameSize": max_yn_frame_size,
                "implementedMacros": implemented_macros,
                "deviceListSpecifier": device_list_specifier,
                "protocolVersionMajor": protocol_version_major,
                "protocolVersionMinor": protocol_version_minor,
                "powerSupplyImplemented": power_supply_implemented,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        lines = d.pop("lines")

        buffer_size = d.pop("bufferSize")

        tick_resolution = d.pop("tickResolution")

        max_yn_frame_size = d.pop("maxYnFrameSize")

        implemented_macros = cast(list[int], d.pop("implementedMacros"))

        device_list_specifier = d.pop("deviceListSpecifier")

        protocol_version_major = d.pop("protocolVersionMajor")

        protocol_version_minor = d.pop("protocolVersionMinor")

        power_supply_implemented = d.pop("powerSupplyImplemented")

        yn_descriptor = cls(
            lines=lines,
            buffer_size=buffer_size,
            tick_resolution=tick_resolution,
            max_yn_frame_size=max_yn_frame_size,
            implemented_macros=implemented_macros,
            device_list_specifier=device_list_specifier,
            protocol_version_major=protocol_version_major,
            protocol_version_minor=protocol_version_minor,
            power_supply_implemented=power_supply_implemented,
        )

        yn_descriptor.additional_properties = d
        return yn_descriptor

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
