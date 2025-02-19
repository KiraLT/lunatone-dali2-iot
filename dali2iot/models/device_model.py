from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.device_type import DeviceType
from ..types import UNSET, Unset

T = TypeVar("T", bound="DeviceModel")


@_attrs_define
class DeviceModel:
    """
    Attributes:
        type_ (Union[Unset, DeviceType]): An enumeration.
        id (Union[Unset, int]):
    """

    type_: Union[Unset, DeviceType] = UNSET
    id: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_: Union[Unset, str] = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        id = self.id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if type_ is not UNSET:
            field_dict["type"] = type_
        if id is not UNSET:
            field_dict["id"] = id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        _type_ = d.pop("type", UNSET)
        type_: Union[Unset, DeviceType]
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = DeviceType(_type_)

        id = d.pop("id", UNSET)

        device_model = cls(
            type_=type_,
            id=id,
        )

        device_model.additional_properties = d
        return device_model

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
