from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.trigger_action_model import TriggerActionModel
from ...models.update_trigger_action_model import UpdateTriggerActionModel
from ...types import Response


def _get_kwargs(
    field_id: int,
    *,
    body: UpdateTriggerActionModel,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/automations/triggerAction/{field_id}",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, TriggerActionModel]]:
    if response.status_code == 200:
        response_200 = TriggerActionModel.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, TriggerActionModel]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    field_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UpdateTriggerActionModel,
) -> Response[Union[HTTPValidationError, TriggerActionModel]]:
    """Update Trigger Action

    Args:
        field_id (int):
        body (UpdateTriggerActionModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, TriggerActionModel]]
    """

    kwargs = _get_kwargs(
        field_id=field_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    field_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UpdateTriggerActionModel,
) -> Optional[Union[HTTPValidationError, TriggerActionModel]]:
    """Update Trigger Action

    Args:
        field_id (int):
        body (UpdateTriggerActionModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, TriggerActionModel]
    """

    return sync_detailed(
        field_id=field_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    field_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UpdateTriggerActionModel,
) -> Response[Union[HTTPValidationError, TriggerActionModel]]:
    """Update Trigger Action

    Args:
        field_id (int):
        body (UpdateTriggerActionModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, TriggerActionModel]]
    """

    kwargs = _get_kwargs(
        field_id=field_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    field_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UpdateTriggerActionModel,
) -> Optional[Union[HTTPValidationError, TriggerActionModel]]:
    """Update Trigger Action

    Args:
        field_id (int):
        body (UpdateTriggerActionModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, TriggerActionModel]
    """

    return (
        await asyncio_detailed(
            field_id=field_id,
            client=client,
            body=body,
        )
    ).parsed
