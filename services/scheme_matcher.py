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

        for scheme in self.schemes:
            rules = scheme.get("eligibility_rules", {})
            is_eligible = True

            # Gender Check
            if "gender" in rules:
                user_gender = profile.get("gender")
                if user_gender and str(user_gender).lower() != str(rules["gender"]).lower():
                    is_eligible = False

            # Age Check
            if "min_age" in rules:
                user_age = profile.get("age")
                if user_age is not None and user_age < rules["min_age"]:
                    is_eligible = False

            if "max_age" in rules:
                user_age = profile.get("age")
                if user_age is not None and user_age > rules["max_age"]:
                    is_eligible = False

            # Income Check
            if "max_annual_income" in rules:
                user_income = profile.get("annual_income")
                if user_income is not None and user_income > rules["max_annual_income"]:
                    is_eligible = False

            # Govt School Check
            if rules.get("is_govt_school_studied"):
                if not profile.get("is_govt_school_studied", False):
                    is_eligible = False

            # Higher Education Check
            if rules.get("pursuing_higher_education"):
                if not profile.get("pursuing_higher_education", False):
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