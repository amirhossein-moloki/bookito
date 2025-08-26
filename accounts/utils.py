import os
import logging
from melipayamak import Api

# It's better to initialize the logger at the module level
logger = logging.getLogger(__name__)

def send_sms(phone_number, otp_code):
    """
    Sends an SMS with the OTP code to the given phone number using MelliPayamak.

    Reads credentials from environment variables. In a real application, these
    would be set in the production environment.
    """
    # In a real-world scenario, you would get the DEBUG value from Django settings
    IS_DEBUG = os.environ.get('DJANGO_DEBUG', 'False').lower() in ('true', '1', 't')

    if IS_DEBUG:
        # In debug mode, just print the OTP to the console.
        print("----------------------------------------------------")
        print(f"DEBUG SMS: Sending OTP to {phone_number}")
        print(f"OTP Code: {otp_code}")
        print("----------------------------------------------------")
        return True

    # --- Production SMS Sending Logic ---
    try:
        username = os.environ.get('MELLIPAYAMAK_USERNAME')
        password = os.environ.get('MELLIPAYAMAK_PASSWORD')
        sender = os.environ.get('MELLIPAYAMAK_SENDER')

        if not all([username, password, sender]):
            logger.error("MelliPayamak credentials are not configured in environment variables.")
            return False

        api = Api(username, password)
        sms = api.sms()

        # The MelliPayamak `send` method is a good choice for simple messages.
        # It expects `to`, `_from`, `text`.
        response = sms.send(
            to=phone_number,
            _from=sender,
            text=f"Your verification code is: {otp_code}"
        )

        # A successful response from the library might not be a simple boolean.
        # You might need to inspect the `response` object to confirm success.
        # For now, we'll assume no exception means it worked.
        logger.info(f"SMS sent to {phone_number} via MelliPayamak. Response: {response}")
        return True

    except Exception as e:
        # Catch any exception from the API call, log it, and return False.
        logger.error(f"Failed to send SMS via MelliPayamak to {phone_number}: {e}", exc_info=True)
        return False
