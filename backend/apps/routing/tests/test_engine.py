import itertools

import pytest

from apps.routing.services.risk.engine import (
    RiskBand,
    classify_checkpoint,
    classify_wind,
    classify_rain,
    classify_snow,
)



@pytest.mark.parametrize(
    ("wind", "expected"),
    [
        (0.0, RiskBand.LOW),
        (24.99, RiskBand.LOW),
        (25.0, RiskBand.MODERATE),
        (34.99, RiskBand.MODERATE),
        (35.0, RiskBand.HIGH),
        (44.99, RiskBand.HIGH),
        (45.0, RiskBand.SEVERE),
        (54.99, RiskBand.SEVERE),
        (55.0, RiskBand.NO_TRAVEL),
        (60.0, RiskBand.NO_TRAVEL),
    ],
)
def test_classify_wind_boundaries(wind, expected):
    assert classify_wind(wind) == expected


@pytest.mark.parametrize(
    ("rain", "expected"),
    [
        (0.0, RiskBand.LOW),
        (0.099, RiskBand.LOW),
        (0.10, RiskBand.MODERATE),
        (0.249, RiskBand.MODERATE),
        (0.25, RiskBand.HIGH),
        (0.499, RiskBand.HIGH),
        (0.50, RiskBand.SEVERE),
        (1.00, RiskBand.SEVERE),
        (1.001, RiskBand.NO_TRAVEL),
    ],
)
def test_classify_rain_boundaries(rain, expected):
    assert classify_rain(rain) == expected


@pytest.mark.parametrize(
    ("snow", "expected"),
    [
        (0.0, RiskBand.LOW),
        (0.499, RiskBand.LOW),
        (0.50, RiskBand.MODERATE),
        (0.999, RiskBand.MODERATE),
        (1.00, RiskBand.HIGH),
        (1.999, RiskBand.HIGH),
        (2.00, RiskBand.SEVERE),
        (3.00, RiskBand.SEVERE),
        (3.001, RiskBand.NO_TRAVEL),
    ],
)
def test_classify_snow_boundaries(snow, expected):
    assert classify_snow(snow) == expected


# --------------------------------------------------
# 2. All 125 combinations of representative weather
# --------------------------------------------------

WIND_SAMPLES = [10.0, 30.0, 40.0, 50.0, 60.0]
RAIN_SAMPLES = [0.05, 0.15, 0.35, 0.75, 1.25]
SNOW_SAMPLES = [0.1, 0.7, 1.5, 2.5, 3.5]

WEATHER_CASES = list(
    itertools.product(WIND_SAMPLES, RAIN_SAMPLES, SNOW_SAMPLES)
)


@pytest.mark.parametrize("wind,rain,snow", WEATHER_CASES)
def test_base_weather_risk_is_worst_of_three(wind, rain, snow):
    band, metadata = classify_checkpoint(
        wind_mph=wind,
        rain_in_hr=rain,
        snow_in_hr=snow,
        load_lb=20_000.0,
    )

    expected = max(
        classify_wind(wind),
        classify_rain(rain),
        classify_snow(snow),
    )

    assert metadata["base_band"] == expected.name
    assert band >= expected




@pytest.mark.parametrize(
    "load",
    [0.0, 5_000.0, 30_000.0, 40_001.0, 75_000.0],
)
def test_wind_55_or_higher_means_no_travel(load):
    band, metadata = classify_checkpoint(
        wind_mph=55.0,
        rain_in_hr=0.0,
        snow_in_hr=0.0,
        load_lb=load,
    )

    assert band == RiskBand.NO_TRAVEL
    assert metadata["final_band"] == "NO_TRAVEL"
    assert metadata["load_rule_triggered"] is True
    assert metadata["override_reason"] is not None





@pytest.mark.parametrize(
    ("load", "expected"),
    [
        (29_999.0, RiskBand.SEVERE),
        (30_000.0, RiskBand.SEVERE),
        (30_001.0, RiskBand.NO_TRAVEL),
        (40_000.0, RiskBand.NO_TRAVEL),
    ],
)
def test_heavy_load_rule_45_to_54_mph(load, expected):
    band, metadata = classify_checkpoint(
        wind_mph=50.0,
        rain_in_hr=0.0,
        snow_in_hr=0.0,
        load_lb=load,
    )

    assert band == expected
    assert metadata["final_band"] == expected.name




@pytest.mark.parametrize(
    ("load", "expected"),
    [
        (39_999.0, RiskBand.HIGH),
        (40_000.0, RiskBand.HIGH),
        (40_001.0, RiskBand.SEVERE),
        (50_000.0, RiskBand.SEVERE),
    ],
)
def test_heavy_load_rule_35_to_44_mph(load, expected):
    band, metadata = classify_checkpoint(
        wind_mph=40.0,
        rain_in_hr=0.0,
        snow_in_hr=0.0,
        load_lb=load,
    )

    assert band == expected
    assert metadata["final_band"] == expected.name



@pytest.mark.parametrize(
    ("wind", "rain", "snow", "load"),
    [
        (40.0, 0.75, 0.1, 45_000.0),
        (50.0, 1.25, 0.1, 35_000.0),
        (55.0, 0.0, 0.0, 10_000.0),
    ],
)
def test_final_risk_never_below_base_risk(wind, rain, snow, load):
    band, metadata = classify_checkpoint(
        wind_mph=wind,
        rain_in_hr=rain,
        snow_in_hr=snow,
        load_lb=load,
    )

    base = RiskBand[metadata["base_band"]]

    assert band >= base
    assert RiskBand[metadata["final_band"]] == band




def test_rule_triggered_is_separate_from_risk_change():
    band, metadata = classify_checkpoint(
        wind_mph=55.0,
        rain_in_hr=0.0,
        snow_in_hr=0.0,
        load_lb=10_000.0,
    )

    assert metadata["base_band"] == "NO_TRAVEL"
    assert band == RiskBand.NO_TRAVEL

    assert metadata["load_rule_triggered"] is True
    assert metadata["load_override_changed_risk"] is False

   