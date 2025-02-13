from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.mail_settings import MailSettings
from ...models.mail_settings_response import MailSettingsResponse
from ...types import Response


def _get_kwargs(
    *,
    body: MailSettings,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/email",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, MailSettingsResponse]]:
    if response.status_code == 200:
        response_200 = MailSettingsResponse.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, MailSettingsResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: MailSettings,
) -> Response[Union[HTTPValidationError, MailSettingsResponse]]:
    """Update Email Settings

     Updates the stored email settings.

    Individual settings are optional and will only be updated when they are sent in the request
    body. Settings must be explicitly set to ``null`` to delete a stored record.

    Args:
        body (MailSettings): A complete set of mail settings, made of sender configuration and
            notifications.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, MailSettingsResponse]]
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
    body: MailSettings,
) -> Optional[Union[HTTPValidationError, MailSettingsResponse]]:
    """Update Email Settings

     Updates the stored email settings.

    Individual settings are optional and will only be updated when they are sent in the request
    body. Settings must be explicitly set to ``null`` to delete a stored record.

    Args:
        body (MailSettings): A complete set of mail settings, made of sender configuration and
            notifications.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, MailSettingsResponse]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: MailSettings,
) -> Response[Union[HTTPValidationError, MailSettingsResponse]]:
    """Update Email Settings

     Updates the stored email settings.

    Individual settings are optional and will only be updated when they are sent in the request
    body. Settings must be explicitly set to ``null`` to delete a stored record.

    Args:
        body (MailSettings): A complete set of mail settings, made of sender configuration and
            notifications.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, MailSettingsResponse]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: MailSettings,
) -> Optional[Union[HTTPValidationError, MailSettingsResponse]]:
    """Update Email Settings

     Updates the stored email settings.

    Individual settings are optional and will only be updated when they are sent in the request
    body. Settings must be explicitly set to ``null`` to delete a stored record.

    Args:
        body (MailSettings): A complete set of mail settings, made of sender configuration and
            notifications.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, MailSettingsResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
