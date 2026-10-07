import asyncio

from aiosmtplib import SMTP
from app.core.config import settings


async def test_smtp():
    smtp = SMTP(
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        start_tls=True,
        timeout=30
    )

    try:
        print("Connecting to Gmail SMTP...")

        await smtp.connect()

        print("SMTP CONNECTED")

        await smtp.login(
            settings.SMTP_USERNAME,
            settings.SMTP_PASSWORD
        )

        print("SMTP LOGIN SUCCESS")

    finally:
        if smtp.is_connected:
            await smtp.quit()


asyncio.run(test_smtp())