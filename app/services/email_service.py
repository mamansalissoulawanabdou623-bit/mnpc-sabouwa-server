import httpx

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


    # ==========================================
    # MODE DEVELOPPEMENT : CONSOLE
    # ==========================================

    if settings.email_mode.lower() == "console":

        print("\n========== EMAIL VERIFICATION ==========")
        print(f"DESTINATAIRE : {recipient}")
        print(f"SUJET        : {subject}")
        print("----------------------------------------")
        print(body)
        print("========================================\n")

        return


    # ==========================================
    # MODE PRODUCTION : RESEND
    # ==========================================

    if settings.email_mode.lower() == "resend":

        if not settings.resend_api_key:

            raise RuntimeError(
                "RESEND_API_KEY est manquante."
            )


        payload = {
            "from": (
                f"{settings.resend_from_name} "
                f"<{settings.resend_from_email}>"
            ),
            "to": [recipient],
            "subject": subject,
            "text": body,
        }


        headers = {
            "Authorization": (
                f"Bearer {settings.resend_api_key}"
            ),
            "Content-Type": "application/json",
        }


        try:

            response = httpx.post(
                "https://api.resend.com/emails",
                json=payload,
                headers=headers,
                timeout=30.0,
            )


        except httpx.RequestError as exc:

            raise RuntimeError(
                "Impossible de contacter le service "
                "d'envoi d'e-mails."
            ) from exc


        if response.status_code >= 400:

            raise RuntimeError(
                "Erreur Resend : "
                f"{response.status_code} - "
                f"{response.text}"
            )


        print(
            f"E-mail de verification envoye a : "
            f"{recipient}"
        )

        return


    # ==========================================
    # MODE INVALIDE
    # ==========================================

    raise RuntimeError(
        "EMAIL_MODE doit etre 'console' ou 'resend'."
    )