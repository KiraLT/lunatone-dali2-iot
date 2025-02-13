from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.info_model_errors import InfoModelErrors
    from ..models.info_model_lines import InfoModelLines
    from ..models.yn_descriptor import YnDescriptor
    from ..models.yn_device_info import YnDeviceInfo


T = TypeVar("T", bound="InfoModel")


@_attrs_define
class InfoModel:
    """
    Attributes:
        name (Union[Unset, str]):  Default: 'dali-iot'.
        version (Union[Unset, str]):  Default: 'vU.V.W/X.Y.Z'.
        tier (Union[Unset, str]):  Default: 'basic'.
        emergency_light (Union[Unset, bool]):  Default: False.
        node_red (Union[Unset, bool]):  Default: False.
        errors (Union[Unset, InfoModelErrors]):
        descriptor (Union[Unset, YnDescriptor]):
        device (Union[Unset, YnDeviceInfo]):
        lines (Union[Unset, InfoModelLines]):
    """

    name: Union[Unset, str] = "dali-iot"
    version: Union[Unset, str] = "vU.V.W/X.Y.Z"
    tier: Union[Unset, str] = "basic"
    emergency_light: Union[Unset, bool] = False
    node_red: Union[Unset, bool] = False
    errors: Union[Unset, "InfoModelErrors"] = UNSET
    descriptor: Union[Unset, "YnDescriptor"] = UNSET
    device: Union[Unset, "YnDeviceInfo"] = UNSET
    lines: Union[Unset, "InfoModelLines"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        version = self.version

        tier = self.tier

        emergency_light = self.emergency_light

        node_red = self.node_red

        errors: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.errors, Unset):
            errors = self.errors.to_dict()

        descriptor: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.descriptor, Unset):
            descriptor = self.descriptor.to_dict()

        device: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.device, Unset):
            device = self.device.to_dict()

        lines: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.lines, Unset):
            lines = self.lines.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if version is not UNSET:
            field_dict["version"] = version
        if tier is not UNSET:
            field_dict["tier"] = tier
        if emergency_light is not UNSET:
            field_dict["emergencyLight"] = emergency_light
        if node_red is not UNSET:
            field_dict["nodeRed"] = node_red
        if errors is not UNSET:
            field_dict["errors"] = errors
        if descriptor is not UNSET:
            field_dict["descriptor"] = descriptor
        if device is not UNSET:
            field_dict["device"] = device
        if lines is not UNSET:
            field_dict["lines"] = lines

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.info_model_errors import InfoModelErrors
        from ..models.info_model_lines import InfoModelLines
        from ..models.yn_descriptor import YnDescriptor
        from ..models.yn_device_info import YnDeviceInfo

        d = src_dict.copy()
        name = d.pop("name", UNSET)

        version = d.pop("version", UNSET)

        tier = d.pop("tier", UNSET)

        emergency_light = d.pop("emergencyLight", UNSET)

        node_red = d.pop("nodeRed", UNSET)

        _errors = d.pop("errors", UNSET)
        errors: Union[Unset, InfoModelErrors]
        if isinstance(_errors, Unset):
            errors = UNSET
        else:
            errors = InfoModelErrors.from_dict(_errors)

        _descriptor = d.pop("descriptor", UNSET)
        descriptor: Union[Unset, YnDescriptor]
        if isinstance(_descriptor, Unset):
            descriptor = UNSET
        else:
            descriptor = YnDescriptor.from_dict(_descriptor)

        _device = d.pop("device", UNSET)
        device: Union[Unset, YnDeviceInfo]
        if isinstance(_device, Unset):
            device = UNSET
        else:
            device = YnDeviceInfo.from_dict(_device)

        _lines = d.pop("lines", UNSET)
        lines: Union[Unset, InfoModelLines]
        if isinstance(_lines, Unset):
            lines = UNSET
        else:
            lines = InfoModelLines.from_dict(_lines)

        info_model = cls(
            name=name,
            version=version,
            tier=tier,
            emergency_light=emergency_light,
            node_red=node_red,
            errors=errors,
            descriptor=descriptor,
            device=device,
            lines=lines,
        )

        info_model.additional_properties = d
        return info_model

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
