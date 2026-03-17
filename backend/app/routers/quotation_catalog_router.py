from fastapi import APIRouter, HTTPException

from app.services.reference_catalog_service import (
    get_applicable_faults_for_instrument,
    get_catalog_brands,
    get_catalog_faults,
    get_catalog_instrument,
    get_catalog_models_by_brand,
)

router = APIRouter()


@router.get("/instruments/brands")
async def get_brands():
    return get_catalog_brands()


@router.get("/instruments/models/{brand_id}")
async def get_models_by_brand(brand_id: str):
    return get_catalog_models_by_brand(brand_id)


@router.get("/instruments/{instrument_id}")
async def get_instrument(instrument_id: str):
    instrument = get_catalog_instrument(instrument_id)
    if instrument:
        return instrument
    raise HTTPException(status_code=404, detail="Instrumento no encontrado")


@router.get("/faults")
async def get_faults():
    return get_catalog_faults()


@router.get("/faults/applicable/{instrument_id}")
async def get_applicable_faults(instrument_id: str):
    applicable_faults = get_applicable_faults_for_instrument(instrument_id)
    if not applicable_faults and not get_catalog_instrument(instrument_id):
        raise HTTPException(status_code=404, detail="Instrumento no encontrado")
    return applicable_faults


def build_router(*, deprecated: bool = False) -> APIRouter:
    fresh_router = APIRouter()
    fresh_router.add_api_route(
        "/instruments/brands",
        get_brands,
        methods=["GET"],
        deprecated=deprecated,
    )
    fresh_router.add_api_route(
        "/instruments/models/{brand_id}",
        get_models_by_brand,
        methods=["GET"],
        deprecated=deprecated,
    )
    fresh_router.add_api_route(
        "/instruments/{instrument_id}",
        get_instrument,
        methods=["GET"],
        deprecated=deprecated,
    )
    fresh_router.add_api_route(
        "/faults",
        get_faults,
        methods=["GET"],
        deprecated=deprecated,
    )
    fresh_router.add_api_route(
        "/faults/applicable/{instrument_id}",
        get_applicable_faults,
        methods=["GET"],
        deprecated=deprecated,
    )
    return fresh_router
