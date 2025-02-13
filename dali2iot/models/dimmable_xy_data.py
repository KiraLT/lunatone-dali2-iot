from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DimmableXYData")


@_attrs_define
class DimmableXYData:
    """Data model for the ``colorXY`` feature.

    Attributes:
        x (Union[Unset, float]): X coordinate in the CIE color chromaticity space. Example: 0.432.
        y (Union[Unset, float]): Y coordinate in the CIE color chromaticity space. Example: 0.15.
        dimmable (Union[Unset, float]): Percentage in the [0, 100] interval to dim a device to. Default: 50.0.
    """

    x: Union[Unset, float] = UNSET
    y: Union[Unset, float] = UNSET
    dimmable: Union[Unset, float] = 50.0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        x = self.x

        y = self.y

        dimmable = self.dimmable

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if x is not UNSET:
            field_dict["x"] = x
        if y is not UNSET:
            field_dict["y"] = y
        if dimmable is not UNSET:
            field_dict["dimmable"] = dimmable

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        x = d.pop("x", UNSET)

        y = d.pop("y", UNSET)

        dimmable = d.pop("dimmable", UNSET)

        dimmable_xy_data = cls(
            x=x,
            y=y,
            dimmable=dimmable,
        )

        dimmable_xy_data.additional_properties = d
        return dimmable_xy_data

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
