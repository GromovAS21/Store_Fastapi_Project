from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select, insert, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db_depends import get_db
from models import Product
from models.reviews import Review
from routers.auth import get_current_user
from schemas import CreateReview

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("/")
async def all_reviews(db: Annotated[AsyncSession, Depends(get_db)]):
    """
    Роут для получения всех отзывов по продуктам, у которых поле is_activate = True.

    Args:
        db: Объект асинхронной сессии с базой данных
    Returns:
        dict: Словарь с отзывами
    """
    reviews = await db.scalars(
        select(Review).join(Product).where(Product.is_activate == True)
    )
    return reviews.all()


@router.get("/{product_slug}")
async def get_reviews_about_product(
    db: Annotated[AsyncSession, Depends(get_db)], product_slug: str
):
    """
    Получить все отзывы по продукту.

    Args:
        db: Объект асинхронной сессии с базой данных
        product_slug: slug продукта для получения отзывов
    Returns:
        dict: Словарь с отзывами
    """
    reviews = await db.scalars(
        select(Review).join(Product).where(Product.slug == product_slug)
    )
    return reviews.all()


@router.post("/{product_slug}/create")
async def create_review(
    db: Annotated[AsyncSession, Depends(get_db)],
    get_user: Annotated[dict, Depends(get_current_user)],
    review: CreateReview,
    product_slug: str,
):
    """
    Создание отзыва.

    Args:
        db: Объект асинхронной сессии с базой данных
        get_user: Объект пользователя
        review: Объект отзыва
        product_slug: slug продукта на что пишется отзыв
    Returns:
        dict: Статус запроса
    """
    if get_user.get("is_customer"):
        product = await db.scalar(select(Product).where(Product.slug == product_slug))
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )

        await db.execute(
            insert(Review).values(
                user_id=get_user.get("id"),
                product_id=product.id,
                comment=review.comment,
                grade=review.grade,
            )
        )
        await db.commit()

        grade = await db.scalar(
            select(func.avg(Review.grade))
            .join(Product)
            .where(Product.slug == product_slug)
        )
        await db.execute(
            update(Product).where(Product.slug == product_slug).values(rating=grade)
        )
        await db.commit()
        return {"status_code": status.HTTP_201_CREATED, "transaction": "Successful"}

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to use this method",
        )


@router.delete("/{review_id}")
async def delete_review(
    db: Annotated[AsyncSession, Depends(get_db)],
    get_user: Annotated[dict, Depends(get_current_user)],
    review_id: int,
):
    """
    Удалить отзыв.

    Args:
        db: Объект асинхронной сессии с базой данных
        get_user: Объект пользователя
        review_id: id отзыва для удаления
    Returns:
        dict: Статус запроса
    """
    if get_user.get("is_admin"):
        review = await db.scalar(
            select(Review).where(Review.id == review_id, Review.is_active == True)
        )

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
            )

        await db.execute(
            update(Review).where(Review.id == review_id).values(is_active=False)
        )
        await db.commit()
        return {"status_code": status.HTTP_200_OK, "transaction": "Successful"}

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to use this method",
        )
