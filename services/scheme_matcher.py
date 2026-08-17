import json
import os

class SchemeMatcher:
    def __init__(self, json_path: str = "data/schemes.json"):
        if not os.path.exists(json_path):
            json_path = os.path.join(os.path.dirname(__file__), "..", "data", "schemes.json")
            
        with open(json_path, "r", encoding="utf-8") as f:
            self.schemes = json.load(f)

    def evaluate_household(self, profile: dict) -> list:
        eligible_schemes = []

        # If profile is completely empty, return zero schemes
        if not profile or not any(v is not None for v in profile.values()):
            return []

        for scheme in self.schemes:
            rules = scheme.get("eligibility_rules", {})
            is_eligible = True

            # 1. Strict Gender Match
            if "gender" in rules:
                user_gender = profile.get("gender")
                if not user_gender or str(user_gender).lower() != str(rules["gender"]).lower():
                    is_eligible = False

            # 2. Strict Government School Match
            if rules.get("is_govt_school_studied"):
                if not profile.get("is_govt_school_studied", False):
                    is_eligible = False

            # 3. Strict College / Higher Education Match
            if rules.get("pursuing_higher_education"):
                if not profile.get("pursuing_higher_education", False):
                    is_eligible = False

            # 4. Strict Farmer Requirement Match
            if rules.get("is_agricultural_laborer") or rules.get("is_landholding_farmer"):
                if not profile.get("is_agricultural_laborer") and not profile.get("is_landholding_farmer"):
                    is_eligible = False

            # 5. Strict Age Limits
            if "min_age" in rules:
                user_age = profile.get("age")
                if user_age is not None and user_age < rules["min_age"]:
                    is_eligible = False

            if "max_age" in rules:
                user_age = profile.get("age")
                if user_age is not None and user_age > rules["max_age"]:
                    is_eligible = False

            # 6. Strict Income Limits
            if "max_annual_income" in rules:
                user_income = profile.get("annual_income")
                if user_income is not None and user_income > rules["max_annual_income"]:
                    is_eligible = False

            # 7. Special Category Checks
            if rules.get("is_widow") and not profile.get("is_widow"):
                is_eligible = False
            if rules.get("is_differently_abled") and not profile.get("is_differently_abled"):
                is_eligible = False
            if rules.get("is_pregnant") and not profile.get("is_pregnant"):
                is_eligible = False

            if is_eligible:
                eligible_schemes.append({
                    "scheme_id": scheme.get("scheme_id", ""),
                    "scheme_name_ta": scheme.get("scheme_name_ta", ""),
                    "scheme_name_en": scheme.get("scheme_name_en", ""),
                    "monthly_stipend": scheme.get("monthly_stipend", 0),
                    "description_ta": scheme.get("description_ta", ""),
                    "required_documents": scheme.get("required_documents", [])
                })

        return eligible_schemes
