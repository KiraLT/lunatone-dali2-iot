from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DimmableWAFData")


@_attrs_define
class DimmableWAFData:
    """Data model for the ``colorWAF`` feature.

    Attributes:
        w (Union[Unset, float]): Relative white value in the [0, 1] interval.
        a (Union[Unset, float]): Relative amber value in the [0, 1] interval. Example: 0.5.
        f (Union[Unset, float]): Relative free color value in the [0, 1] interval. Example: 1.0.
        dimmable (Union[Unset, float]): Percentage in the [0, 100] interval to dim a device to. Default: 50.0.
    """

    w: Union[Unset, float] = UNSET
    a: Union[Unset, float] = UNSET
    f: Union[Unset, float] = UNSET
    dimmable: Union[Unset, float] = 50.0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        w = self.w

        a = self.a

        f = self.f

        dimmable = self.dimmable

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if w is not UNSET:
            field_dict["w"] = w
        if a is not UNSET:
            field_dict["a"] = a
        if f is not UNSET:
            field_dict["f"] = f
        if dimmable is not UNSET:
            field_dict["dimmable"] = dimmable

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        w = d.pop("w", UNSET)

        a = d.pop("a", UNSET)

        f = d.pop("f", UNSET)

        dimmable = d.pop("dimmable", UNSET)

        dimmable_waf_data = cls(
            w=w,
            a=a,
            f=f,
            dimmable=dimmable,
        )

        dimmable_waf_data.additional_properties = d
        return dimmable_waf_data

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
