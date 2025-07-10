
class units:
    _UNIT_FACTORS = {
        "m": 1.0,
        "mm": 1000.0,
        "cm": 100.0,
        "in": 39.3701,
        "ft": 3.28084,
    }

    def __init__(self, default_unit: str = "mm"):
        if default_unit not in self._UNIT_FACTORS:
            raise ValueError(f"Unsupported unit: {default_unit}")
        self.default_unit = default_unit

    def from_user(self, value):
        """Convert a value from user units to meters (default unit)."""
        return value / self._UNIT_FACTORS[self.default_unit]

    def to_user(self, meters):
        """Convert a value from meters to user units."""
        return meters * self._UNIT_FACTORS[self.default_unit]

    def from_unit(self, value, unit):
        """Convert a value from a specific unit to meters."""
        return value / self._UNIT_FACTORS[unit]

    def from_suffixed_params(self, params: dict) -> dict:
        """Converts suffixed values like 'd_mm' to meters.

        Output keys have '_m' suffix unless they already end with '_m',
        in which case they are passed through unchanged (assumed meters).
        """
        out = {}
        for key, value in params.items():
            if not isinstance(value, (int, float)):
                continue  # skip nested dicts or other structures

            if key.endswith("_m"):
                # Already in meters, keep key and value as-is
                out[key] = value
                continue

            if "_" in key:
                name, suffix = key.rsplit("_", 1)
                if suffix in self._UNIT_FACTORS:
                    # Convert value, output key with '_m' suffix
                    out[name + "_m"] = self.from_unit(value, suffix)
                    continue

            # fallback: no recognized suffix, convert with default
            # output key gets '_m' suffix added
            out[key + "_m"] = self.from_user(value)

        return out

