import google.generativeai as genai
import json
import os
import json
from datetime import datetime, date
from pydantic import BaseModel, Field, ValidationError, field_validator
from typing import List, Dict, Optional
# from services.extract_service import extract_data


def extract_text(loc):
    # importing required modules
    from pypdf import PdfReader

    # creating a pdf reader object
    reader = PdfReader(loc)

    # printing number of pages in pdf file
    print(len(reader.pages))

    # getting a specific page from the pdf file
    page = reader.pages[0]

    # extracting text from page
    text = page.extract_text()
    print(text)
    return text



# --- Define the schema using Pydantic V2 style ---
class LicenseAgreement(BaseModel):
    parties: Dict[str, str]
    licensing_terms: Dict[str, object]
    financial_terms: Dict[str, object]
    usage_restrictions: Dict[str, List[str]]
    intellectual_property: Dict[str, str]
    legal_compliance: Dict[str, str]
    contract_termination: Dict[str, object]

    @field_validator("parties")
    @classmethod
    def check_parties(cls, v):
        if "licensor" not in v or "licensee" not in v:
            raise ValueError("Both 'licensor' and 'licensee' must be specified.")
        return v

# --- Define the LicenseAgreementExtractor class ---
class LicenseAgreementExtractor:
    def __init__(self, api_key: str):
        # Configure the API key for your generative model service
        genai.configure(api_key=api_key)
        # Use an appropriate model (using gemini-1.5-flash here)
        self.model = genai.GenerativeModel("gemini-1.5-flash")
    
    def clean_response(self, text: str) -> str:
        """
        Clean the raw response text by removing markdown formatting
        like triple backticks.
        """
        cleaned = text.strip()
        # Remove leading and trailing triple backticks, if present
        if cleaned.startswith("```json") and cleaned.endswith("```"):
            cleaned = cleaned[7:-3].strip()
        return cleaned

    def extract_license_details(self, contract_text: str) -> Optional[Dict]:
        """
        Extract structured details from a content licensing agreement
        using advanced NLP techniques.
        """
        prompt = f"""You are an expert legal NLP assistant specializing in parsing content licensing agreements.

EXTRACTION INSTRUCTIONS:
- Extract precise, concise information for each specified category.
- If information is not found, use "N/A", refrain from returning Null.
- Ensure JSON output is clean and standardized.
- Try to fill in the gaps if any from inference
- Reread your output to make sense or find gaps
- Strictly adhere to this format no matter what.

EXTRACTION CATEGORIES:
1. PARTIES INVOLVED
2. LICENSING TERMS
3. PAYMENT & FEES
4. USAGE RESTRICTIONS
5. INTELLECTUAL PROPERTY
6. LEGAL COMPLIANCE
7. TERMINATION & DISPUTE RESOLUTION

DETAILED EXTRACTION SCHEMA:
{{
    "parties": {{
        "licensor": "Full legal name of content owner",
        "licensee": "Full legal name of rights recipient"
    }},
    "licensing_terms": {{
        "effective_date": "Exact date license begins",
        "term_duration": "License period (e.g., '12 months')",
        "scope_of_use": ["List of allowed usage contexts"],
        "license_characteristics": {{
            "exclusivity": "Exclusive/Non-Exclusive",
            "transferability": "Transferable/Non-Transferable",
            "geographical_scope": "Regions covered",
            "user_access": "Single/Multi-User"
        }}
    }},
    "financial_terms": {{
        "license_fee": "Total amount payable",
        "royalty_terms": "Details of ongoing payments"
    }},
    "usage_restrictions": {{
        "prohibited_uses": ["List of explicitly forbidden uses"]
    }},
    "intellectual_property": {{
        "copyright_ownership": "Description of IP rights",
        "attribution_requirements": "Credit/acknowledgment details"
    }},
    "legal_compliance": {{
        "third_party_rights": "Required releases or permissions",
        "indemnification": "Liability assignment details",
        "liability_limitations": "Scope of licensor's responsibilities"
    }},
    "contract_termination": {{
        "termination_grounds": ["List of license revocation conditions"],
        "dispute_resolution": {{
            "governing_law": "Jurisdiction for legal matters",
            "resolution_mechanism": "Method of resolving disputes"
        }}
    }}
}}

CONTRACT TEXT TO ANALYZE:
{contract_text}
"""
        try:
            response = self.model.generate_content(prompt)
            raw_output = response.text.strip()
            cleaned_output = self.clean_response(raw_output)
            print(cleaned_output)
            # Attempt to parse the cleaned output as JSON
            extracted_json = json.loads(cleaned_output)
            # Validate the extracted JSON using the Pydantic schema
            validated_data = LicenseAgreement.model_validate(extracted_json)
            return validated_data.model_dump()
        except json.JSONDecodeError as e:
            print(f"JSON Parsing Error: {e}")
            print("Raw Model Response:", raw_output)
            return None
        except ValidationError as ve:
            print("Validation Error:", ve.json(indent=2))
            return None


    def save_to_json(self, data: Dict, filename: str = 'license_agreement_details.json'):
        """
        Save extracted data to a JSON file with pretty formatting.
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"Data successfully saved to {filename}")
        except IOError as e:
            print(f"Error saving file: {e}")



def gemini_call(contract_text):
    # access environment variable
    API_KEY = os.environ['GEMINI_API']

    extractor = LicenseAgreementExtractor(API_KEY)

    # Extract license details
    extracted_details = extractor.extract_license_details(contract_text)

    if extracted_details:
        return  extracted_details


if __name__ == '__main__':
    file = open('/nikhil/contractiq-backend/uploads/XACCT Technologies, Inc.SUPPORT AND MAINTENANCE AGREEMENT.txt', "r")
    data = file.read()
    res = gemini_call(data)