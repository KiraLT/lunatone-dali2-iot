from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DimmableWithFadeData")


@_attrs_define
class DimmableWithFadeData:
    """
    Attributes:
        dim_value (float):
        fade_time (Union[Unset, float]):
    """

    dim_value: float
    fade_time: Union[Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        dim_value = self.dim_value

        fade_time = self.fade_time

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "dimValue": dim_value,
            }
        )
        if fade_time is not UNSET:
            field_dict["fadeTime"] = fade_time

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        dim_value = d.pop("dimValue")

        fade_time = d.pop("fadeTime", UNSET)

        dimmable_with_fade_data = cls(
            dim_value=dim_value,
            fade_time=fade_time,
        )

        dimmable_with_fade_data.additional_properties = d
        return dimmable_with_fade_data

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
