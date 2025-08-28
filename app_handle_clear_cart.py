"""
Function to handle clearing the cart
"""
def handle_clear_cart(self):
    try:
        message = self.cart.clear_cart()
        speak(message)
    except Exception as e:
        logger.error(f"Clear cart error: {e}")
        speak("Sorry, I encountered an error clearing your cart.")
