from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.scan_model import ScanModel
from ...models.start_scan_model import StartScanModel
from ...types import Response


def _get_kwargs(
    *,
    body: StartScanModel,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/dali/scan",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, ScanModel]]:
    if response.status_code == 200:
        response_200 = ScanModel.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, ScanModel]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: StartScanModel,
) -> Response[Union[HTTPValidationError, ScanModel]]:
    """Start Scan

     Start a new dali scan.

    Note:

    - If ``newInstallation`` is ``true``, all dali devices will be deleted prior to performing the scan.
    - If a scan is already active, this will not start a new one!
    - ``useLines`` can be used to only scan on a set of line numbers.

    Args:
        body (StartScanModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, ScanModel]]
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
    body: StartScanModel,
) -> Optional[Union[HTTPValidationError, ScanModel]]:
    """Start Scan

     Start a new dali scan.

    Note:

    - If ``newInstallation`` is ``true``, all dali devices will be deleted prior to performing the scan.
    - If a scan is already active, this will not start a new one!
    - ``useLines`` can be used to only scan on a set of line numbers.

    Args:
        body (StartScanModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, ScanModel]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: StartScanModel,
) -> Response[Union[HTTPValidationError, ScanModel]]:
    """Start Scan

     Start a new dali scan.

    Note:

    - If ``newInstallation`` is ``true``, all dali devices will be deleted prior to performing the scan.
    - If a scan is already active, this will not start a new one!
    - ``useLines`` can be used to only scan on a set of line numbers.

    Args:
        body (StartScanModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, ScanModel]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: StartScanModel,
) -> Optional[Union[HTTPValidationError, ScanModel]]:
    """Start Scan

     Start a new dali scan.

    Note:

    - If ``newInstallation`` is ``true``, all dali devices will be deleted prior to performing the scan.
    - If a scan is already active, this will not start a new one!
    - ``useLines`` can be used to only scan on a set of line numbers.

    Args:
        body (StartScanModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, ScanModel]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
