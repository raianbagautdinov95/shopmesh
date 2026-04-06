from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.catalog import Category, Product


class CatalogRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_categories(self) -> list[Category]:
        stmt = select(Category).order_by(Category.name.asc())
        return list(self.db.scalars(stmt).all())

    def get_category_by_slug(self, slug: str) -> Category | None:
        stmt = select(Category).where(Category.slug == slug)
        return self.db.scalar(stmt)

    def create_category(self, *, slug: str, name: str, description: str | None) -> Category:
        category = Category(slug=slug, name=name, description=description)
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def list_products(
        self,
        *,
        limit: int,
        offset: int,
        search: str | None,
        category_slug: str | None,
        active_only: bool,
    ) -> tuple[list[Product], int]:
        filters = []
        if active_only:
            filters.append(Product.is_active.is_(True))
        if search:
            pattern = f"%{search.strip()}%"
            filters.append((Product.name.ilike(pattern)) | (Product.sku.ilike(pattern)))
        if category_slug:
            filters.append(Category.slug == category_slug)

        base_stmt = select(Product).join(Category).options(joinedload(Product.category))
        if filters:
            for condition in filters:
                base_stmt = base_stmt.where(condition)

        count_stmt = select(func.count(Product.id)).join(Category)
        if filters:
            for condition in filters:
                count_stmt = count_stmt.where(condition)

        items = list(
            self.db.scalars(
                base_stmt.order_by(Product.created_at.desc()).offset(offset).limit(limit)
            ).unique().all()
        )
        total = int(self.db.scalar(count_stmt) or 0)
        return items, total

    def get_product_by_id(self, product_id: int) -> Product | None:
        stmt = (
            select(Product)
            .where(Product.id == product_id)
            .options(joinedload(Product.category))
        )
        return self.db.scalar(stmt)

    def get_product_by_slug(self, slug: str) -> Product | None:
        stmt = (
            select(Product)
            .where(Product.slug == slug)
            .options(joinedload(Product.category))
        )
        return self.db.scalar(stmt)

    def get_product_by_sku(self, sku: str) -> Product | None:
        stmt = select(Product).where(Product.sku == sku)
        return self.db.scalar(stmt)

    def create_product(self, product: Product) -> Product:
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def save(self, product: Product) -> Product:
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product
