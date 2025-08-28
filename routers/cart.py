from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import json
import os
from datetime import datetime
import logging
from shopping_cart import ShoppingCart

router = APIRouter(prefix="/api/cart", tags=["cart"])
logger = logging.getLogger(__name__)

# Store session carts in memory for quick access
session_carts: Dict[str, ShoppingCart] = {}

class CartItemRequest(BaseModel):
    product: Dict[str, Any]
    session_id: str = "default"

class CartItemRemoveRequest(BaseModel):
    item_title: str
    session_id: str = "default"

class CartSessionRequest(BaseModel):
    session_id: str = "default"

class CartResponse(BaseModel):
    success: bool
    message: str
    items: Optional[List[Dict[str, Any]]] = None
    total: Optional[float] = None
    item_count: Optional[int] = None

def get_cart_for_session(session_id: str) -> ShoppingCart:
    """Get or create a cart for the given session ID"""
    if session_id not in session_carts:
        # Use a different cart file for each session to avoid conflicts
        cart_file = f"cart_{session_id}.json"
        session_carts[session_id] = ShoppingCart(cart_file=cart_file)
    
    return session_carts[session_id]

@router.post("/add")
async def add_to_cart(request: CartItemRequest) -> CartResponse:
    """Add an item to the cart"""
    try:
        cart = get_cart_for_session(request.session_id)
        success, message = cart.add_item(request.product)
        
        return CartResponse(
            success=success,
            message=message,
            items=cart.cart["items"],
            total=cart.get_total_amount(),
            item_count=cart.get_item_count()
        )
    except Exception as e:
        logger.error(f"Error adding to cart: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/remove")
async def remove_from_cart(request: CartItemRemoveRequest) -> CartResponse:
    """Remove an item from the cart"""
    try:
        cart = get_cart_for_session(request.session_id)
        success, message = cart.remove_item(product_title=request.item_title)
        
        return CartResponse(
            success=success,
            message=message,
            items=cart.cart["items"],
            total=cart.get_total_amount(),
            item_count=cart.get_item_count()
        )
    except Exception as e:
        logger.error(f"Error removing from cart: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clear")
async def clear_cart(request: CartSessionRequest) -> CartResponse:
    """Clear all items from the cart"""
    try:
        cart = get_cart_for_session(request.session_id)
        message = cart.clear_cart()
        
        return CartResponse(
            success=True,
            message=message,
            items=[],
            total=0,
            item_count=0
        )
    except Exception as e:
        logger.error(f"Error clearing cart: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/items")
async def get_cart_items(session_id: str = "default") -> CartResponse:
    """Get all items in the cart"""
    try:
        cart = get_cart_for_session(session_id)
        cart_summary = cart.get_cart_summary()
        
        return CartResponse(
            success=True,
            message=cart_summary,
            items=cart.cart["items"],
            total=cart.get_total_amount(),
            item_count=cart.get_item_count()
        )
    except Exception as e:
        logger.error(f"Error getting cart items: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/checkout")
async def checkout(request: CartSessionRequest) -> CartResponse:
    """Process checkout"""
    try:
        cart = get_cart_for_session(request.session_id)
        
        if cart.get_item_count() == 0:
            return CartResponse(
                success=False,
                message="Your cart is empty. Please add some items before checkout.",
                items=[],
                total=0,
                item_count=0
            )
        
        success, message = cart.proceed_to_checkout()
        
        return CartResponse(
            success=success,
            message=message,
            items=[],  # Cart is cleared after checkout
            total=0,
            item_count=0
        )
    except Exception as e:
        logger.error(f"Error during checkout: {e}")
        raise HTTPException(status_code=500, detail=str(e))
