from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.device_model import DeviceModel
    from ..models.trigger_action_source import TriggerActionSource


T = TypeVar("T", bound="TriggerActionModel")


@_attrs_define
class TriggerActionModel:
    """
    Attributes:
        id (int):
        sources (list['TriggerActionSource']):
        targets (list['DeviceModel']):
        enabled (Union[Unset, bool]):  Default: True.
        name (Union[Unset, str]):  Default: ''.
    """

    id: int
    sources: list["TriggerActionSource"]
    targets: list["DeviceModel"]
    enabled: Union[Unset, bool] = True
    name: Union[Unset, str] = ""
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        sources = []
        for sources_item_data in self.sources:
            sources_item = sources_item_data.to_dict()
            sources.append(sources_item)

        targets = []
        for targets_item_data in self.targets:
            targets_item = targets_item_data.to_dict()
            targets.append(targets_item)

        enabled = self.enabled

        name = self.name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "sources": sources,
                "targets": targets,
            }
        )
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.device_model import DeviceModel
        from ..models.trigger_action_source import TriggerActionSource

        d = src_dict.copy()
        id = d.pop("id")

        sources = []
        _sources = d.pop("sources")
        for sources_item_data in _sources:
            sources_item = TriggerActionSource.from_dict(sources_item_data)

            sources.append(sources_item)

        targets = []
        _targets = d.pop("targets")
        for targets_item_data in _targets:
            targets_item = DeviceModel.from_dict(targets_item_data)

            targets.append(targets_item)

        enabled = d.pop("enabled", UNSET)

        name = d.pop("name", UNSET)

        trigger_action_model = cls(
            id=id,
            sources=sources,
            targets=targets,
            enabled=enabled,
            name=name,
        )

        trigger_action_model.additional_properties = d
        return trigger_action_model

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
