import smtplib
import ssl
from email.message import EmailMessage

from app.core.config import get_settings


settings = get_settings()


def send_verification_email(
    *,
    recipient: str,
    code: str,
) -> None:

    subject = (
        "MNPC SABOUWA - Verification de votre adresse e-mail"
    )

    body = (
        "Bonjour,\n\n"
        "Vous venez de creer un compte MNPC SABOUWA.\n\n"
        f"Votre code de verification est : {code}\n\n"
        f"Ce code est valable pendant "
        f"{settings.verification_code_minutes} minutes.\n\n"
        "Cette verification est effectuee une seule fois "
        "pour activer votre adresse e-mail.\n\n"
        "Si vous n'etes pas a l'origine de cette demande, "
        "ignorez ce message.\n\n"
        "MNPC SABOUWA"
    )


    # MODE DEVELOPPEMENT
    # Affichage du code dans le terminal serveur
    if settings.email_mode.lower() == "console":

        print("\n========== EMAIL VERIFICATION ==========")
        print(f"DESTINATAIRE : {recipient}")
        print(f"SUJET        : {subject}")
        print("----------------------------------------")
        print(body)
        print("========================================\n")

        return


    # MODE PRODUCTION SMTP
    if settings.email_mode.lower() != "smtp":

        raise RuntimeError(
            "EMAIL_MODE doit etre 'console' ou 'smtp'."
        )


    required_settings = (
        settings.smtp_host,
        settings.smtp_username,
        settings.smtp_password,
        settings.smtp_from_email,
    )


    if not all(required_settings):

        raise RuntimeError(
            "La configuration SMTP est incomplete."
        )


    message = EmailMessage()

    message["Subject"] = subject

    message["From"] = (
        f"{settings.smtp_from_name} "
        f"<{settings.smtp_from_email}>"
    )

    message["To"] = recipient

    message.set_content(body)


    if settings.smtp_use_ssl:

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(
            settings.smtp_host,
            settings.smtp_port,
            timeout=30,
            context=context,
        ) as smtp:

            smtp.login(
                settings.smtp_username,
                settings.smtp_password,
            )

            smtp.send_message(message)

        return


    with smtplib.SMTP(
        settings.smtp_host,
        settings.smtp_port,
        timeout=30,
    ) as smtp:

        smtp.ehlo()

        smtp.starttls(
            context=ssl.create_default_context()
        )

        smtp.ehlo()

        smtp.login(
            settings.smtp_username,
            settings.smtp_password,
        )

        smtp.send_message(message)