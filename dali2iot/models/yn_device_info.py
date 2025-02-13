from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="YnDeviceInfo")


@_attrs_define
class YnDeviceInfo:
    """
    Attributes:
        serial (int):
        gtin (int):
        pcb (str):
        article_number (int):
        article_info (str):
        production_year (int):
        production_week (int):
    """

    serial: int
    gtin: int
    pcb: str
    article_number: int
    article_info: str
    production_year: int
    production_week: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        serial = self.serial

        gtin = self.gtin

        pcb = self.pcb

        article_number = self.article_number

        article_info = self.article_info

        production_year = self.production_year

        production_week = self.production_week

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "serial": serial,
                "gtin": gtin,
                "pcb": pcb,
                "articleNumber": article_number,
                "articleInfo": article_info,
                "productionYear": production_year,
                "productionWeek": production_week,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        serial = d.pop("serial")

        gtin = d.pop("gtin")

        pcb = d.pop("pcb")

        article_number = d.pop("articleNumber")

        article_info = d.pop("articleInfo")

        production_year = d.pop("productionYear")

        production_week = d.pop("productionWeek")

        yn_device_info = cls(
            serial=serial,
            gtin=gtin,
            pcb=pcb,
            article_number=article_number,
            article_info=article_info,
            production_year=production_year,
            production_week=production_week,
        )

        yn_device_info.additional_properties = d
        return yn_device_info

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
