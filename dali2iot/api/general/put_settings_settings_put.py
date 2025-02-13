from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.settings_model import SettingsModel
from ...types import Response


def _get_kwargs(
    *,
    body: SettingsModel,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/settings",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, SettingsModel]]:
    if response.status_code == 200:
        response_200 = SettingsModel.from_dict(response.json())

        return response_200
    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[HTTPValidationError, SettingsModel]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: SettingsModel,
) -> Response[Union[HTTPValidationError, SettingsModel]]:
    """Put Settings

     Updates the protocol settings

    Following parameters are set by default and not changable:
    ```
    send_during_initialize=False
    send_during_quiescent=False
    events=True
    send_frame_events=True
    recv_frame_events=True
    send_buffer_events=False
    macro_events=True
    tick_in_events=True
    line_in_events=True
    bus_power_supply=False
    ```

    Args:
        body (SettingsModel): Model for protocol settings.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, SettingsModel]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: SettingsModel,
) -> Optional[Union[HTTPValidationError, SettingsModel]]:
    """Put Settings

     Updates the protocol settings

    Following parameters are set by default and not changable:
    ```
    send_during_initialize=False
    send_during_quiescent=False
    events=True
    send_frame_events=True
    recv_frame_events=True
    send_buffer_events=False
    macro_events=True
    tick_in_events=True
    line_in_events=True
    bus_power_supply=False
    ```

    Args:
        body (SettingsModel): Model for protocol settings.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, SettingsModel]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: SettingsModel,
) -> Response[Union[HTTPValidationError, SettingsModel]]:
    """Put Settings

     Updates the protocol settings

    Following parameters are set by default and not changable:
    ```
    send_during_initialize=False
    send_during_quiescent=False
    events=True
    send_frame_events=True
    recv_frame_events=True
    send_buffer_events=False
    macro_events=True
    tick_in_events=True
    line_in_events=True
    bus_power_supply=False
    ```

    Args:
        body (SettingsModel): Model for protocol settings.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, SettingsModel]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: SettingsModel,
) -> Optional[Union[HTTPValidationError, SettingsModel]]:
    """Put Settings

     Updates the protocol settings

    Following parameters are set by default and not changable:
    ```
    send_during_initialize=False
    send_during_quiescent=False
    events=True
    send_frame_events=True
    recv_frame_events=True
    send_buffer_events=False
    macro_events=True
    tick_in_events=True
    line_in_events=True
    bus_power_supply=False
    ```

    Args:
        body (SettingsModel): Model for protocol settings.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, SettingsModel]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
