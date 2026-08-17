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

        if not profile or not any(v is not None for v in profile.values()):
            return []

        is_farmer = bool(profile.get("is_agricultural_laborer") or profile.get("is_landholding_farmer"))
        is_student = bool(profile.get("pursuing_higher_education") or profile.get("is_govt_school_studied"))

        for scheme in self.schemes:
            rules = scheme.get("eligibility_rules", {})
            scheme_id = scheme.get("scheme_id", "")
            is_eligible = True

            # 1. Gender Validation
            if "gender" in rules:
                user_gender = profile.get("gender")
                if not user_gender or str(user_gender).lower() != str(rules["gender"]).lower():
                    is_eligible = False

            # 2. Strict Student Schemes Matching
            student_keywords = ["PUDHUMAI", "PUDHALVAN", "MUDHALVAN", "LAPTOP", "SCHOLARSHIP"]
            is_student_scheme = any(k in scheme_id for k in student_keywords)

            if is_student_scheme:
                if not is_student:
                    is_eligible = False
                if rules.get("is_govt_school_studied") and not profile.get("is_govt_school_studied"):
                    is_eligible = False
                if rules.get("pursuing_higher_education") and not profile.get("pursuing_higher_education"):
                    is_eligible = False

            # 3. Strict Farmer Schemes Matching
            farmer_keywords = ["KISAN", "UZHAVAR", "KURUVAI", "MILLET", "PULSES", "PMKSY", "SHDS", "MKMKS", "AGROFORESTRY", "SMAM", "KCC", "PMFBY"]
            is_farmer_scheme = any(k in scheme_id for k in farmer_keywords)

            if is_farmer_scheme:
                if not is_farmer:
                    is_eligible = False

            # If user is exclusively a Farmer, prevent matching student schemes
            if is_farmer and not is_student and is_student_scheme:
                is_eligible = False

            # If user is exclusively a Student, prevent matching farmer schemes
            if is_student and not is_farmer and is_farmer_scheme:
                is_eligible = False

            # 4. Age Limits
            if "min_age" in rules and (profile.get("age") is None or profile.get("age") < rules["min_age"]):
                is_eligible = False
            if "max_age" in rules and (profile.get("age") is None or profile.get("age") > rules["max_age"]):
                is_eligible = False

            # 5. Income Limits
            if "max_annual_income" in rules and (profile.get("annual_income") is None or profile.get("annual_income") > rules["max_annual_income"]):
                is_eligible = False

            # 6. Special Welfare Conditions
            if rules.get("is_widow") and not profile.get("is_widow"):
                is_eligible = False
            if rules.get("is_differently_abled") and not profile.get("is_differently_abled"):
                is_eligible = False
            if rules.get("is_pregnant") and not profile.get("is_pregnant"):
                is_eligible = False
            if rules.get("is_head_of_family") and not profile.get("is_head_of_family"):
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
