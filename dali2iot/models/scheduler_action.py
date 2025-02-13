from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.action_types import ActionTypes

if TYPE_CHECKING:
    from ..models.scheduler_action_data import SchedulerActionData


T = TypeVar("T", bound="SchedulerAction")


@_attrs_define
class SchedulerAction:
    """
    Attributes:
        type_ (ActionTypes): An enumeration.
        data (SchedulerActionData):
    """

    type_: ActionTypes
    data: "SchedulerActionData"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        data = self.data.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "data": data,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.scheduler_action_data import SchedulerActionData

        d = src_dict.copy()
        type_ = ActionTypes(d.pop("type"))

        data = SchedulerActionData.from_dict(d.pop("data"))

        scheduler_action = cls(
            type_=type_,
            data=data,
        )

        scheduler_action.additional_properties = d
        return scheduler_action

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
