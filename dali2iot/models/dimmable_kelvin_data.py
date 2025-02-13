from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DimmableKelvinData")


@_attrs_define
class DimmableKelvinData:
    """
    Attributes:
        dimmable (Union[Unset, float]): Percentage in the [0, 100] interval to dim a device to. Default: 50.0.
        kelvin (Union[Unset, float]): Color temperature in Kelvin. Default: 4000.0.
    """

    dimmable: Union[Unset, float] = 50.0
    kelvin: Union[Unset, float] = 4000.0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        dimmable = self.dimmable

        kelvin = self.kelvin

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if dimmable is not UNSET:
            field_dict["dimmable"] = dimmable
        if kelvin is not UNSET:
            field_dict["kelvin"] = kelvin

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        dimmable = d.pop("dimmable", UNSET)

        kelvin = d.pop("kelvin", UNSET)

        dimmable_kelvin_data = cls(
            dimmable=dimmable,
            kelvin=kelvin,
        )

        dimmable_kelvin_data.additional_properties = d
        return dimmable_kelvin_data

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
