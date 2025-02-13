from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CircadianStep")


@_attrs_define
class CircadianStep:
    """
    Attributes:
        hour (int):
        dimmable (Union[Unset, float]):  Example: 50.0.
        enable_dimmable (Union[Unset, bool]):  Example: True.
        color_kelvin (Union[Unset, float]):  Example: 4000.0.
        enable_kelvin (Union[Unset, bool]):  Example: True.
    """

    hour: int
    dimmable: Union[Unset, float] = UNSET
    enable_dimmable: Union[Unset, bool] = UNSET
    color_kelvin: Union[Unset, float] = UNSET
    enable_kelvin: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        hour = self.hour

        dimmable = self.dimmable

        enable_dimmable = self.enable_dimmable

        color_kelvin = self.color_kelvin

        enable_kelvin = self.enable_kelvin

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "hour": hour,
            }
        )
        if dimmable is not UNSET:
            field_dict["dimmable"] = dimmable
        if enable_dimmable is not UNSET:
            field_dict["enableDimmable"] = enable_dimmable
        if color_kelvin is not UNSET:
            field_dict["colorKelvin"] = color_kelvin
        if enable_kelvin is not UNSET:
            field_dict["enableKelvin"] = enable_kelvin

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        hour = d.pop("hour")

        dimmable = d.pop("dimmable", UNSET)

        enable_dimmable = d.pop("enableDimmable", UNSET)

        color_kelvin = d.pop("colorKelvin", UNSET)

        enable_kelvin = d.pop("enableKelvin", UNSET)

        circadian_step = cls(
            hour=hour,
            dimmable=dimmable,
            enable_dimmable=enable_dimmable,
            color_kelvin=color_kelvin,
            enable_kelvin=enable_kelvin,
        )

        circadian_step.additional_properties = d
        return circadian_step

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
