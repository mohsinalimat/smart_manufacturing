"""
GCC Localization (KSA, UAE, Bahrain, Kuwait, Oman, Qatar)
- VAT 15% KSA / 5% UAE
- ZATCA e-invoicing readiness (KSA)
- Arabic language support
- Hijri date support
- Multi-currency: SAR, AED, KWD, BHD, OMR, QAR
"""

REGION_CODE = "gcc"
TAX_RATES = {
    "KSA": 15.0,
    "UAE": 5.0,
    "BHD": 10.0,
    "KWT": 0.0,
    "OMN": 5.0,
    "QAT": 0.0,
}
CURRENCIES = ["SAR", "AED", "BHD", "KWD", "OMR", "QAR"]
LANGUAGES = ["ar", "en"]
