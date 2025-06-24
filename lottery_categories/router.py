from fastapi import APIRouter, HTTPException, Body, Depends, Query
from typing import List, Optional

from . import db as categories_db
from .models import LotteryCategory, LotteryCategoryCreate, LotteryCategoryUpdate
from pymongo.errors import PyMongoError

router = APIRouter()

@router.post("/", response_model=LotteryCategory, status_code=201)
def create_new_category(category_in: LotteryCategoryCreate):
    try:
        category_id = categories_db.create_category(category_in)
        if not category_id:
            raise HTTPException(status_code=500, detail="Failed to create lottery category in database.")

        # Fetch the created category to return it in full
        created_category = categories_db.get_category_by_id(category_id)
        if not created_category: # Should not happen if create_category was successful and returned an ID
            raise HTTPException(status_code=500, detail="Failed to retrieve created lottery category.")
        return created_category
    except PyMongoError as e:
        print(f"PyMongoError creating category: {e}")
        raise HTTPException(status_code=500, detail=f"Database error while creating category: {str(e)}")
    except Exception as e:
        print(f"Unexpected error creating category: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@router.get("/", response_model=List[LotteryCategory])
def list_all_categories(active_only: bool = Query(False, description="Filter for active categories only")):
    try:
        categories = categories_db.get_all_categories(active_only=active_only)
        return categories
    except PyMongoError as e:
        print(f"PyMongoError listing categories: {e}")
        raise HTTPException(status_code=500, detail=f"Database error while listing categories: {str(e)}")
    except Exception as e:
        print(f"Unexpected error listing categories: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.get("/{category_id}", response_model=LotteryCategory)
def get_single_category(category_id: str):
    try:
        category = categories_db.get_category_by_id(category_id)
        if category is None:
            raise HTTPException(status_code=404, detail="Lottery category not found.")
        return category
    except PyMongoError as e:
        print(f"PyMongoError getting category {category_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Database error while retrieving category: {str(e)}")
    except HTTPException: # Re-raise HTTPExceptions (like 404)
        raise
    except Exception as e:
        print(f"Unexpected error getting category {category_id}: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@router.put("/{category_id}", response_model=LotteryCategory)
def update_existing_category(category_id: str, category_update: LotteryCategoryUpdate):
    try:
        # Check if category exists first
        existing_category = categories_db.get_category_by_id(category_id)
        if not existing_category:
            raise HTTPException(status_code=404, detail="Lottery category not found to update.")

        success = categories_db.update_category(category_id, category_update)
        if not success:
            # This might be because nothing changed, or DB error not caught by PyMongoError
            # Re-fetch to see if it's a "no change" or actual error
            updated_category_check = categories_db.get_category_by_id(category_id)
            if updated_category_check and \
               all(getattr(updated_category_check, k, None) == v for k, v in category_update.model_dump(exclude_unset=True).items() if v is not None):
                return updated_category_check # No actual change, but data is consistent
            raise HTTPException(status_code=500, detail="Failed to update lottery category or no changes made.")

        updated_category = categories_db.get_category_by_id(category_id)
        if not updated_category: # Should not happen if update was successful
             raise HTTPException(status_code=500, detail="Failed to retrieve category after update.")
        return updated_category
    except PyMongoError as e:
        print(f"PyMongoError updating category {category_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Database error while updating category: {str(e)}")
    except HTTPException: # Re-raise HTTPExceptions
        raise
    except Exception as e:
        print(f"Unexpected error updating category {category_id}: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@router.delete("/{category_id}", status_code=204) # No content response
def delete_existing_category(category_id: str):
    try:
        # Check if category exists first
        existing_category = categories_db.get_category_by_id(category_id)
        if not existing_category:
            raise HTTPException(status_code=404, detail="Lottery category not found to delete.")

        success = categories_db.delete_category(category_id)
        if not success:
            # Could be already deleted by another request, or DB error
            still_exists = categories_db.get_category_by_id(category_id)
            if still_exists:
                raise HTTPException(status_code=500, detail="Failed to delete lottery category.")
            # If it doesn't exist anymore, it's effectively deleted.
        return None # Return No Content
    except PyMongoError as e:
        print(f"PyMongoError deleting category {category_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Database error while deleting category: {str(e)}")
    except HTTPException: # Re-raise HTTPExceptions
        raise
    except Exception as e:
        print(f"Unexpected error deleting category {category_id}: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
