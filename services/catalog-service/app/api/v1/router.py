from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_admin
from app.schemas.catalog import (
    CategoryCreateRequest,
    CategoryListResponse,
    CategoryResponse,
    ProductCreateRequest,
    ProductListResponse,
    ProductResponse,
    ProductUpdateRequest,
)
from app.schemas.common import HealthResponse
from app.services.catalog import CatalogService

api_router = APIRouter(prefix="/api/v1", tags=["catalog"])


@api_router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(service="catalog-service", status="ok")


@api_router.get("/ready", response_model=HealthResponse)
def ready() -> HealthResponse:
    return HealthResponse(service="catalog-service", status="ok")


@api_router.get("/categories", response_model=CategoryListResponse)
def list_categories(db: Session = Depends(get_db)) -> CategoryListResponse:
    service = CatalogService(db)
    service.seed_defaults()
    categories = service.list_categories()
    return CategoryListResponse(total=len(categories), items=categories)


@api_router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreateRequest,
    _: dict[str, str] = Depends(require_admin),
    db: Session = Depends(get_db),
) -> CategoryResponse:
    service = CatalogService(db)
    try:
        return service.create_category(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@api_router.get("/products", response_model=ProductListResponse)
def list_products(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    search: str | None = Query(default=None),
    category: str | None = Query(default=None),
    active_only: bool = Query(default=True),
    db: Session = Depends(get_db),
) -> ProductListResponse:
    service = CatalogService(db)
    service.seed_defaults()
    items, total = service.list_products(
        limit=limit,
        offset=offset,
        search=search,
        category_slug=category,
        active_only=active_only,
    )
    return ProductListResponse(total=total, limit=limit, offset=offset, items=items)


@api_router.get("/products/{product_id}", response_model=ProductResponse)
def get_product_by_id(product_id: int, db: Session = Depends(get_db)) -> ProductResponse:
    service = CatalogService(db)
    service.seed_defaults()
    product = service.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@api_router.get("/products/slug/{slug}", response_model=ProductResponse)
def get_product_by_slug(slug: str, db: Session = Depends(get_db)) -> ProductResponse:
    service = CatalogService(db)
    service.seed_defaults()
    product = service.get_product_by_slug(slug)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@api_router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreateRequest,
    _: dict[str, str] = Depends(require_admin),
    db: Session = Depends(get_db),
) -> ProductResponse:
    service = CatalogService(db)
    try:
        return service.create_product(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@api_router.patch("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    payload: ProductUpdateRequest,
    _: dict[str, str] = Depends(require_admin),
    db: Session = Depends(get_db),
) -> ProductResponse:
    service = CatalogService(db)
    product = service.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    try:
        return service.update_product(product, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
