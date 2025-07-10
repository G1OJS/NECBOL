import warnings
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class units:
    
    _UNIT_FACTORS = {
        "m": 1.0,
        "mm": 1000.0,
        "cm": 100.0,
        "in": 39.3701,
        "ft": 3.28084,
    }

    def __init__(self, default_unit: str = "m"):
        if default_unit not in self._UNIT_FACTORS:
            raise ValueError(f"Unsupported unit: {default_unit}")
        self.default_unit = default_unit

    def from_suffixed_params(self, params: dict, whitelist=[]) -> dict:
        """Converts suffixed values like 'd_mm' to meters.

        Output keys have '_m' suffix unless they already end with '_m',
        in which case they are passed through unchanged (assumed meters).
        """
        
        out = {}
        names_seen = []
        for key, value in params.items():
    
            if not isinstance(value, (int, float)):
                continue  # skip nested dicts or other structures

            name = key
            suffix = ""
            if "_" in name:
                name, suffix = name.rsplit("_", 1)
                
            if(name in names_seen):
                warnstr = f"Duplicate value of '{name}' seen: ignoring latest ({key} = {value})"
                warnings.warn(warnstr)
                continue

            names_seen.append(name)

            if suffix in self._UNIT_FACTORS:
                # Convert value, output key with '_m' suffix
                out[name + "_m"] = value / self._UNIT_FACTORS[suffix]
                continue

            if key in whitelist:
                continue
            
            # fallback: no recognised suffix, assume metres
            warnings.warn(f"No recognised units specified for {name}: '{suffix}' specified, metres assumed")
            # output key gets '_m' suffix added
            out[name + "_m"] = value

        return out



