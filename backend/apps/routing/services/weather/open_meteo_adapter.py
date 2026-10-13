
from __future__ import annotations

import math
from datetime import datetime, timezone
from numbers import Real
from typing import Any, ClassVar, Final

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from apps.routing.services.weather.base import (
    WIND_UNIT,
    HourlyWeather,
    WeatherInputError,
    WeatherProvider,
    WeatherProviderError,
)


_USER_AGENT: Final = "truckersafe-weather/1.0"
_RETRY_STATUSES: Final = frozenset({429, 500, 502, 503, 504})
_HOURLY_FIELDS: Final = "wind_speed_10m,precipitation,snowfall"


class OpenMeteoAdapter(WeatherProvider):
    """Fetch normalized hourly forecasts from Open-Meteo."""

    name: str = "Open-Meteo"
    BASE_URL: ClassVar[str] = (
        "https://api.open-meteo.com/v1/forecast"
    )
    DEFAULT_TIMEOUT_SECONDS: ClassVar[float] = 10.0

    def __init__(
        self,
        *,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        session: requests.Session | None = None,
        base_url: str | None = None,
        max_retries: int = 2,
    ) -> None:
        if isinstance(timeout, bool) or not isinstance(timeout, Real):
            raise ValueError("timeout must be a positive finite number.")

        try:
            timeout_value = float(timeout)
        except (OverflowError, TypeError, ValueError) as exc:
            raise ValueError(
                "timeout must be a positive finite number."
            ) from exc

        if not math.isfinite(timeout_value) or timeout_value <= 0:
            raise ValueError("timeout must be a positive finite number.")

        if (
            isinstance(max_retries, bool)
            or not isinstance(max_retries, int)
            or max_retries < 0
        ):
            raise ValueError(
                "max_retries must be a non-negative integer."
            )

        if base_url is not None and (
            not isinstance(base_url, str) or not base_url.strip()
        ):
            raise ValueError("base_url must be a non-empty string.")

        self.timeout = timeout_value
        self.base_url = (base_url or self.BASE_URL).rstrip("/")
        self._owns_session = session is None
        self._session = session if session is not None else requests.Session()

        headers = getattr(self._session, "headers", None)
        if headers is not None and hasattr(headers, "setdefault"):
            headers.setdefault("User-Agent", _USER_AGENT)

        # Only configure retries on a session owned by this adapter.
        if self._owns_session and max_retries:
            self._install_retries(max_retries)

    def _install_retries(self, max_retries: int) -> None:
        retry = Retry(
            total=max_retries,
            connect=max_retries,
            read=max_retries,
            status=max_retries,
            backoff_factor=0.3,
            status_forcelist=_RETRY_STATUSES,
            allowed_methods=frozenset({"GET"}),
            respect_retry_after_header=True,
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self._session.mount("https://", adapter)
        self._session.mount("http://", adapter)

    def get_hourly_forecast(
        self,
        latitude: float,
        longitude: float,
        start: datetime,
        end: datetime,
    ) -> list[HourlyWeather]:
        """Fetch weather records within the requested time window."""
        self._validate_request(latitude, longitude, start, end)

        params = self._build_params(latitude, longitude, start, end)
        payload = self._fetch(params)

        return self._parse_response(payload, start, end)

    def _build_params(
        self,
        latitude: float,
        longitude: float,
        start: datetime,
        end: datetime,
    ) -> dict[str, Any]:
        start_utc = start.astimezone(timezone.utc)
        end_utc = end.astimezone(timezone.utc)

        return {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": _HOURLY_FIELDS,
            "wind_speed_unit": WIND_UNIT,
            "precipitation_unit": "inch",
            "timezone": "UTC",
            "start_date": start_utc.date().isoformat(),
            "end_date": end_utc.date().isoformat(),
        }

    def _fetch(self, params: dict[str, Any]) -> dict[str, Any]:
        try:
            response = self._session.get(
                self.base_url,
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.Timeout as exc:
            raise WeatherProviderError(
                f"{self.name} request timed out after "
                f"{self.timeout:g} seconds."
            ) from exc
        except requests.RequestException as exc:
            raise WeatherProviderError(
                f"{self.name} network request failed: {exc}"
            ) from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise WeatherProviderError(
                f"{self.name} returned invalid JSON."
            ) from exc

        if not isinstance(payload, dict):
            raise WeatherProviderError(
                f"{self.name} response must be a JSON object."
            )

        return payload

    def _parse_response(
        self,
        payload: dict[str, Any],
        start: datetime,
        end: datetime,
    ) -> list[HourlyWeather]:
        hourly = payload.get("hourly")

        if not isinstance(hourly, dict):
            raise WeatherProviderError(
                f"{self.name} response is missing hourly data."
            )

        times = self._extract_series(hourly, "time")
        wind = self._extract_series(hourly, "wind_speed_10m")
        precipitation = self._extract_series(hourly, "precipitation")
        snowfall = self._extract_series(hourly, "snowfall")

        if not times:
            raise WeatherProviderError(
                f"{self.name} returned no hourly timestamps."
            )

        for label, values in (
            ("wind_speed_10m", wind),
            ("precipitation", precipitation),
            ("snowfall", snowfall),
        ):
            if len(values) != len(times):
                raise WeatherProviderError(
                    f"{self.name} returned mismatched {label} data."
                )

        start_utc = start.astimezone(timezone.utc)
        end_utc = end.astimezone(timezone.utc)

        records: list[HourlyWeather] = []
        previous: datetime | None = None

        for index, raw_time in enumerate(times):
            timestamp = self._parse_timestamp(raw_time, index)

            if previous is not None and timestamp <= previous:
                raise WeatherProviderError(
                    f"{self.name} timestamps are not strictly "
                    f"increasing at index {index}."
                )

            previous = timestamp

            if not start_utc <= timestamp <= end_utc:
                continue

            records.append(
                HourlyWeather(
                    timestamp=timestamp,
                    wind_mph=self._parse_measurement(
                        wind[index], "wind speed", index
                    ),
                    precipitation_inches=self._parse_measurement(
                        precipitation[index], "precipitation", index
                    ),
                    snowfall_inches=self._parse_measurement(
                        snowfall[index], "snowfall", index
                    ),
                )
            )

        return records

    def _extract_series(
        self,
        hourly: dict[str, Any],
        key: str,
    ) -> list[Any]:
        values = hourly.get(key)

        if not isinstance(values, list):
            raise WeatherProviderError(
                f"{self.name} response is missing the {key!r} list."
            )

        return values

    def _parse_timestamp(
        self,
        raw: Any,
        index: int,
    ) -> datetime:
        if not isinstance(raw, str):
            raise WeatherProviderError(
                f"{self.name} timestamp at index {index} "
                "must be a string."
            )

        try:
            cleaned = (
                raw[:-1] + "+00:00"
                if raw.endswith("Z")
                else raw
            )
            timestamp = datetime.fromisoformat(cleaned)
        except ValueError as exc:
            raise WeatherProviderError(
                f"{self.name} timestamp at index {index} is malformed."
            ) from exc

        if timestamp.tzinfo is None or timestamp.utcoffset() is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        return timestamp.astimezone(timezone.utc)

    @staticmethod
    def _parse_measurement(
        value: Any,
        label: str,
        index: int,
    ) -> float | None:
        """Preserve nulls and reject invalid measurements."""
        if value is None:
            return None

        if isinstance(value, bool) or not isinstance(value, Real):
            raise WeatherProviderError(
                f"{label} at index {index} must be numeric or null."
            )

        try:
            number = float(value)
        except (OverflowError, TypeError, ValueError) as exc:
            raise WeatherProviderError(
                f"{label} at index {index} is invalid."
            ) from exc

        if not math.isfinite(number) or number < 0:
            raise WeatherProviderError(
                f"{label} at index {index} must be finite "
                "and non-negative."
            )

        return number

    def close(self) -> None:
        """Close only the HTTP session created by this adapter."""
        if self._owns_session:
            self._session.close()

    def __enter__(self) -> OpenMeteoAdapter:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    def __repr__(self) -> str:
        return (
            f"<{type(self).__name__} name={self.name!r} "
            f"base_url={self.base_url!r}>"
        )
