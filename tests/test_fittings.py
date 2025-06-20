import asyncio

from app.schemas.fittings import Fitting
from app.services.fittings_store import get_fitting, add_fitting
from app.routers.fittings import read_fitting, create_fitting


def test_get_fitting_default():
    fitting = get_fitting("4A-C4L-25-SS")
    assert fitting
    assert fitting.description == "Check valve"


def test_add_and_get_fitting_service():
    fit = Fitting(
        code="2B-XYZ-10-CS",
        description="Sample valve",
        series="2B",
        configuration="XYZ",
        cracking_pressure="10 psi",
        material="carbon steel",
    )
    add_fitting(fit)
    retrieved = get_fitting("2B-XYZ-10-CS")
    assert retrieved and retrieved.material == "carbon steel"


def test_fitting_endpoints():
    new_fit = Fitting(
        code="1A-TEST-5-SS",
        description="Dummy",
        series="1A",
        configuration="TEST",
        cracking_pressure="5 psi",
        material="stainless steel",
    )
    created = asyncio.run(create_fitting(new_fit))
    assert created.code == new_fit.code
    fetched = asyncio.run(read_fitting("1A-TEST-5-SS"))
    assert fetched.configuration == "TEST"
