"""
def detect_suspicious_tld(registrable_domain: str) -> dict | None:

    Revisa si el dominio termina en extensiones baratas/gratuitas
    muy usadas por atacantes.

    high_risk_tlds = {".zip", ".top", ".xyz", ".pw", ".tk"}

    try:
        # Extraemos la extensión (ej. de "malware.top" sacamos ".top")
        parts = registrable_domain.split('.')
        if len(parts) > 1:
            tld = f".{parts[-1].lower()}"
            if tld in high_risk_tlds:
                return {"code": "SUSPICIOUS_TLD", "evidence": f"TLD de alto riesgo usado: {tld}"}
    except Exception:
        pass # Si algo falla al procesar el string, simplemente no aplicamos esta flag

    return None
"""