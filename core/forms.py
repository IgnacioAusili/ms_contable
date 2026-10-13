from django import forms
from decimal import Decimal


class DecimalInputField(forms.DecimalField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", forms.TextInput())
        super().__init__(*args, **kwargs)

        self.widget.attrs.setdefault("class", "decimal-input")
        self.widget.attrs.setdefault("inputmode", "decimal")
        self.widget.attrs.setdefault(
            "data-decimal-places", str(self.decimal_places or 2),
        )

    def prepare_value(self, value):
        if value is None:
            return value

        precision = max(self.decimal_places or 0, 2)
        formatted = f"{Decimal(value):.{precision}f}"

        integer, decimals = formatted.split(".")

        while len(decimals) > 2 and decimals.endswith("0"):
            decimals = decimals[:-1]

        return f"{integer}.{decimals}"
