from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.color_xy_data import ColorXYData


T = TypeVar("T", bound="ColorXYWithFadeData")


@_attrs_define
class ColorXYWithFadeData:
    """
    Attributes:
        color (ColorXYData): Data model for the ``colorXY`` feature.
        fade_time (Union[Unset, float]):
    """

    color: "ColorXYData"
    fade_time: Union[Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        color = self.color.to_dict()

        fade_time = self.fade_time

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "color": color,
            }
        )
        if fade_time is not UNSET:
            field_dict["fadeTime"] = fade_time

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.color_xy_data import ColorXYData

        d = src_dict.copy()
        color = ColorXYData.from_dict(d.pop("color"))

        fade_time = d.pop("fadeTime", UNSET)

        color_xy_with_fade_data = cls(
            color=color,
            fade_time=fade_time,
        )

        color_xy_with_fade_data.additional_properties = d
        return color_xy_with_fade_data

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
