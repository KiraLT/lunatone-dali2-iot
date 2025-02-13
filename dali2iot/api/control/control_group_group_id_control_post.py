from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.control_data import ControlData
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    field_id: int,
    *,
    body: ControlData,
    field_line: Union[Unset, int] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["_line"] = field_line

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/group/{field_id}/control",
        "params": params,
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, HTTPValidationError]]:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, HTTPValidationError]]:
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
    body: ControlData,
    field_line: Union[Unset, int] = UNSET,
) -> Response[Union[Any, HTTPValidationError]]:
    """Control Group

     *Control the features of one group by id*

    Args:
        field_id (int):
        field_line (Union[Unset, int]):
        body (ControlData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        field_id=field_id,
        body=body,
        field_line=field_line,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    field_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: ControlData,
    field_line: Union[Unset, int] = UNSET,
) -> Optional[Union[Any, HTTPValidationError]]:
    """Control Group

     *Control the features of one group by id*

    Args:
        field_id (int):
        field_line (Union[Unset, int]):
        body (ControlData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, HTTPValidationError]
    """

    return sync_detailed(
        field_id=field_id,
        client=client,
        body=body,
        field_line=field_line,
    ).parsed


async def asyncio_detailed(
    field_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: ControlData,
    field_line: Union[Unset, int] = UNSET,
) -> Response[Union[Any, HTTPValidationError]]:
    """Control Group

     *Control the features of one group by id*

    Args:
        field_id (int):
        field_line (Union[Unset, int]):
        body (ControlData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        field_id=field_id,
        body=body,
        field_line=field_line,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    field_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: ControlData,
    field_line: Union[Unset, int] = UNSET,
) -> Optional[Union[Any, HTTPValidationError]]:
    """Control Group

     *Control the features of one group by id*

    Args:
        field_id (int):
        field_line (Union[Unset, int]):
        body (ControlData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            field_id=field_id,
            client=client,
            body=body,
            field_line=field_line,
        )
    ).parsed
