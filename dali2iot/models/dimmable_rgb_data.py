from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DimmableRGBData")


@_attrs_define
class DimmableRGBData:
    """Data model for the ``colorRGB`` feature.

    Attributes:
        r (Union[Unset, float]): Relative red value in the [0, 1] interval.
        g (Union[Unset, float]): Relative green value in the [0, 1] interval. Example: 0.5.
        b (Union[Unset, float]): Relative blue value in the [0, 1] interval. Example: 1.0.
        dimmable (Union[Unset, float]): Percentage in the [0, 100] interval to dim a device to. Default: 50.0.
    """

    r: Union[Unset, float] = UNSET
    g: Union[Unset, float] = UNSET
    b: Union[Unset, float] = UNSET
    dimmable: Union[Unset, float] = 50.0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        r = self.r

        g = self.g

        b = self.b

        dimmable = self.dimmable

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if r is not UNSET:
            field_dict["r"] = r
        if g is not UNSET:
            field_dict["g"] = g
        if b is not UNSET:
            field_dict["b"] = b
        if dimmable is not UNSET:
            field_dict["dimmable"] = dimmable

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        r = d.pop("r", UNSET)

        g = d.pop("g", UNSET)

        b = d.pop("b", UNSET)

        dimmable = d.pop("dimmable", UNSET)

        dimmable_rgb_data = cls(
            r=r,
            g=g,
            b=b,
            dimmable=dimmable,
        )

        dimmable_rgb_data.additional_properties = d
        return dimmable_rgb_data

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
