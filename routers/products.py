from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from slugify import slugify
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.db_depends import get_db
from models import Category, Product
from routers.auth import get_current_user
from schemas import CreateProduct

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/")
async def all_products(db: Annotated[AsyncSession, Depends(get_db)]):
    products = await db.scalars(
        select(Product)
        .join(Category)
        .where(
            Product.is_activate == True, Category.is_active == True, Product.stock > 0
        )
    )
    list_products = products.all()
    if not list_products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="There are no products"
        )
    return list_products


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_product(
    db: Annotated[AsyncSession, Depends(get_db)],
    product: CreateProduct,
    get_user: Annotated[dict, Depends(get_current_user)],
):
    if get_user.get("is_admin") or get_user.get("is_supplier"):
        category = await db.scalar(
            select(Category).where(Category.id == product.category)
        )
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="There is no category found",
            )

        await db.execute(
            insert(Product).values(
                name=product.name,
                slug=slugify(product.name),
                description=product.description,
                price=product.price,
                image_url=product.image_url,
                category_id=product.category,
                rating=0.0,
                stock=product.stock,
                supplier_id=get_user.get("id") if get_user.get("is_supplier") else None,
            )
        )
        await db.commit()
        return {"status_code": status.HTTP_201_CREATED, "transaction": "Successful"}
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to use this method",
        )


@router.get("/{category_slug}")
async def product_by_category(
    db: Annotated[AsyncSession, Depends(get_db)], category_slug: str
):
    category = await db.scalar(select(Category).where(Category.slug == category_slug))

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    subcategories_result = await db.scalars(
        select(Category).where(Category.parent_id == category.id)
    )

    categories_id = [category.id for category in subcategories_result.all()]
    categories_id.append(category.id)
    products = await db.scalars(
        select(Product).where(
            Product.category_id.in_(categories_id),
            Product.is_activate == True,
            Product.stock > 0,
        )
    )
    return products.all()


@router.get("/detail/{product_slug}")
async def detail_product(
    db: Annotated[AsyncSession, Depends(get_db)], product_slug: str
):
    product = await db.scalar(
        select(Product).where(
            Product.slug == product_slug, Product.is_activate == True, Product.stock > 0
        )
    )
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="There is no product found"
        )
    return product


@router.put("/{product_slug}")
async def update_product(
    db: Annotated[AsyncSession, Depends(get_db)],
    product_slug: str,
    update_product: CreateProduct,
    get_user: Annotated[dict, Depends(get_current_user)],
):
    if get_user.get("is_supplier") or get_user.get("is_admin"):
        product = await db.scalar(select(Product).where(Product.slug == product_slug))

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="There is no product found",
            )

        if get_user.get("is_admin") or get_user.get("id") == product.supplier_id:
            category = await db.scalar(
                select(Category).where(Category.id == update_product.category)
            )

            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="There is no category found",
                )
            product.name = update_product.name
            product.slug = slugify(update_product.name)
            product.description = update_product.description
            product.price = update_product.price
            product.image_url = update_product.image_url
            product.category_id = update_product.category
            product.stock = update_product.stock

            await db.commit()
            return {
                "status_code": status.HTTP_200_OK,
                "transaction": "Product update is successful",
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You have not enough permission for this action",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to use this method",
        )


@router.delete("/{product_slug}")
async def delete_product(
    db: Annotated[AsyncSession, Depends(get_db)],
    product_slug: str,
    get_user: Annotated[dict, Depends(get_current_user)],
):
    if get_user.get("is_supplier") or get_user.get("is_admin"):
        product = await db.scalar(
            select(Product).where(
                Product.slug == product_slug, Product.is_activate == True
            )
        )
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="There is no product found",
            )

        if get_user.get("is_admin") or get_user.get("id") == product.supplier_id:
            product.is_activate = False
            await db.commit()
            return {
                "status_code": status.HTTP_200_OK,
                "transaction": "Product delete is successful",
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to use this method",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to use this method",
        )
