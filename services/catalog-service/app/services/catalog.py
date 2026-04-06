from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.catalog import Category, Product
from app.repositories.catalog import CatalogRepository
from app.schemas.catalog import CategoryCreateRequest, ProductCreateRequest, ProductUpdateRequest


DEFAULT_CATEGORIES = [
    {
        "slug": "electronics",
        "name": "Electronics",
        "description": "Devices, accessories, and smart gadgets.",
    },
    {
        "slug": "apparel",
        "name": "Apparel",
        "description": "Everyday clothing and premium essentials.",
    },
    {
        "slug": "home",
        "name": "Home",
        "description": "Useful home goods and modern living items.",
    },
]

DEFAULT_PRODUCTS = [
    {
        "sku": "SM-HEADPHONES-01",
        "name": "ShopMesh Wireless Headphones",
        "slug": "shopmesh-wireless-headphones",
        "description": "Noise-cancelling over-ear headphones with 30-hour battery life.",
        "price": Decimal("129.99"),
        "currency": "USD",
        "category_slug": "electronics",
        "stock_status": "in_stock",
        "image_url": "https://example.com/images/headphones.jpg",
        "is_active": True,
    },
    {
        "sku": "SM-HOODIE-01",
        "name": "ShopMesh Essential Hoodie",
        "slug": "shopmesh-essential-hoodie",
        "description": "Heavyweight cotton hoodie with relaxed fit.",
        "price": Decimal("59.00"),
        "currency": "USD",
        "category_slug": "apparel",
        "stock_status": "low_stock",
        "image_url": "https://example.com/images/hoodie.jpg",
        "is_active": True,
    },
    {
        "sku": "SM-LAMP-01",
        "name": "ShopMesh Desk Lamp",
        "slug": "shopmesh-desk-lamp",
        "description": "Minimal desk lamp with adjustable brightness settings.",
        "price": Decimal("42.50"),
        "currency": "USD",
        "category_slug": "home",
        "stock_status": "in_stock",
        "image_url": "https://example.com/images/lamp.jpg",
        "is_active": True,
    },
]


class CatalogService:
    def __init__(self, db: Session) -> None:
        self.repo = CatalogRepository(db)

    def seed_defaults(self) -> None:
        categories = self.repo.list_categories()
        if categories:
            return

        for category_data in DEFAULT_CATEGORIES:
            self.repo.create_category(**category_data)

        for product_data in DEFAULT_PRODUCTS:
            category = self.repo.get_category_by_slug(product_data["category_slug"])
            if not category:
                continue
            product = Product(
                sku=product_data["sku"],
                name=product_data["name"],
                slug=product_data["slug"],
                description=product_data["description"],
                price=product_data["price"],
                currency=product_data["currency"],
                category_id=category.id,
                stock_status=product_data["stock_status"],
                image_url=product_data["image_url"],
                is_active=product_data["is_active"],
            )
            self.repo.create_product(product)

    def list_categories(self) -> list[Category]:
        return self.repo.list_categories()

    def create_category(self, payload: CategoryCreateRequest) -> Category:
        existing = self.repo.get_category_by_slug(payload.slug)
        if existing:
            raise ValueError("Category slug already exists")
        return self.repo.create_category(
            slug=payload.slug,
            name=payload.name,
            description=payload.description,
        )

    def list_products(
        self,
        *,
        limit: int,
        offset: int,
        search: str | None,
        category_slug: str | None,
        active_only: bool,
    ) -> tuple[list[Product], int]:
        return self.repo.list_products(
            limit=limit,
            offset=offset,
            search=search,
            category_slug=category_slug,
            active_only=active_only,
        )

    def get_product_by_id(self, product_id: int) -> Product | None:
        return self.repo.get_product_by_id(product_id)

    def get_product_by_slug(self, slug: str) -> Product | None:
        return self.repo.get_product_by_slug(slug)

    def create_product(self, payload: ProductCreateRequest) -> Product:
        if self.repo.get_product_by_sku(payload.sku):
            raise ValueError("Product SKU already exists")
        if self.repo.get_product_by_slug(payload.slug):
            raise ValueError("Product slug already exists")

        category = self.repo.get_category_by_slug(payload.category_slug)
        if not category:
            raise ValueError("Category not found")

        product = Product(
            sku=payload.sku,
            name=payload.name,
            slug=payload.slug,
            description=payload.description,
            price=payload.price,
            currency=payload.currency.upper(),
            category_id=category.id,
            stock_status=payload.stock_status,
            image_url=payload.image_url,
            is_active=payload.is_active,
        )
        return self.repo.create_product(product)

    def update_product(self, product: Product, payload: ProductUpdateRequest) -> Product:
        if payload.name is not None:
            product.name = payload.name
        if payload.slug is not None and payload.slug != product.slug:
            existing = self.repo.get_product_by_slug(payload.slug)
            if existing and existing.id != product.id:
                raise ValueError("Product slug already exists")
            product.slug = payload.slug
        if payload.description is not None:
            product.description = payload.description
        if payload.price is not None:
            product.price = payload.price
        if payload.currency is not None:
            product.currency = payload.currency.upper()
        if payload.category_slug is not None:
            category = self.repo.get_category_by_slug(payload.category_slug)
            if not category:
                raise ValueError("Category not found")
            product.category_id = category.id
        if payload.stock_status is not None:
            product.stock_status = payload.stock_status
        if payload.image_url is not None:
            product.image_url = payload.image_url
        if payload.is_active is not None:
            product.is_active = payload.is_active
        return self.repo.save(product)
