from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.scheduler_response import SchedulerResponse


T = TypeVar("T", bound="AllScheduleResponse")


@_attrs_define
class AllScheduleResponse:
    """
    Attributes:
        schedulers (list['SchedulerResponse']):
    """

    schedulers: list["SchedulerResponse"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        schedulers = []
        for schedulers_item_data in self.schedulers:
            schedulers_item = schedulers_item_data.to_dict()
            schedulers.append(schedulers_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "schedulers": schedulers,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.scheduler_response import SchedulerResponse

        d = src_dict.copy()
        schedulers = []
        _schedulers = d.pop("schedulers")
        for schedulers_item_data in _schedulers:
            schedulers_item = SchedulerResponse.from_dict(schedulers_item_data)

            schedulers.append(schedulers_item)

        all_schedule_response = cls(
            schedulers=schedulers,
        )

        all_schedule_response.additional_properties = d
        return all_schedule_response

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
