import os
import time
import requests
from dotenv import load_dotenv
load_dotenv()


HUBSPOT_KEY = os.getenv("HUBSPOT_KEY")

if not HUBSPOT_KEY:
    raise RuntimeError("No HUBSPOT_KEY in your .env file.")

API_CALL_DELAY = 0.2
API_REQUEST_TIMEOUT = 10

CONTACT_URL = "https://api.hubapi.com/crm/v3/objects/contacts"
COMPANY_URL = "https://api.hubapi.com/crm/v3/objects/companies"
LABEL_URL = "https://api.hubapi.com/crm/v4/associations/contacts/companies/labels"

API_HEADERS = {
    "Authorization": f"Bearer {HUBSPOT_KEY}",
    "Content-Type": "application/json"
}

EMPLOYEE_LABEL_NAME = "Employee"


def get_employee_label() -> int:
    """
    Ensure an 'Employee' association label exists between contacts and
    companies and return the Contact → Company associationTypeId.
    """
    payload = {
        "name": "employee",
        "label": EMPLOYEE_LABEL_NAME
    }

    response = requests.post(
        url=LABEL_URL,
        headers=API_HEADERS,
        json=payload,
        timeout=API_REQUEST_TIMEOUT
    )

    if response.status_code in (200, 201):
        results = response.json()["results"]
        return results[0]["typeId"]

    if response.status_code == 400 and "already exists" in response.text.lower():
        response = requests.get(
            url=LABEL_URL,
            headers=API_HEADERS,
            timeout=API_REQUEST_TIMEOUT
        )
        response.raise_for_status()

        for item in response.json()["results"]:
            if item["label"] == EMPLOYEE_LABEL_NAME:
                return item["typeId"]

        raise RuntimeError("Employee label exists but ID not found")

    raise RuntimeError(
        f"Failed to create or retrieve Employee label "
        f"(status={response.status_code}, response={response.text})"
    )


def create_contact(email: str, firstname: str, lastname: str) -> str:
    """
    Create a contact via HubSpot API and return the contact ID. If the
    contact already exists, return the existing contact ID.
    """
    if not email:
        raise ValueError("'email' must be provided.")
    
    if not firstname:
        raise ValueError("'firstname' must be provided.")
    
    if not lastname:
        raise ValueError("'lastname' must be provided.")
    
    payload = {
        "properties": {
            "email": email,
            "firstname": firstname,
            "lastname": lastname
        }
    }

    response = requests.post(
        url=CONTACT_URL,
        headers=API_HEADERS,
        json=payload,
        timeout=API_REQUEST_TIMEOUT
    )

    time.sleep(API_CALL_DELAY)

    if response.status_code == 201:
        return response.json()["id"]
    
    if response.status_code == 409:
        message = response.json().get("message", "")
        candidate_id = message[-12:]

        if candidate_id.isdigit():
            return candidate_id
        
        raise RuntimeError(f"409 received but could not extract contact ID: {message}")

    raise RuntimeError(
        f"Failed to create contact " 
        f"(status={response.status_code}, response={response.text})"
    )


def create_company(name: str, domain: str) -> str:
    """
    Create a company via HubSpot API and return the company ID.
    """
    if not name:
        raise ValueError("'name' must be provided.")
    
    if not domain:
        raise ValueError("'domain' must be provided.")
    
    payload = {
        "properties": {
            "name": name,
            "domain": domain
        }
    }

    response = requests.post(
        url=COMPANY_URL,
        headers=API_HEADERS,
        json=payload,
        timeout=API_REQUEST_TIMEOUT
    )

    time.sleep(API_CALL_DELAY)

    if response.status_code == 201:
        return response.json()["id"]
    
    raise RuntimeError(
        f"Failed to create company (status={response.status_code},"
        f" response={response.text})"
    )


def add_contact_to_company(
    contact_id: str,
    company_id: str,
    label_id: int
) -> None:
    """
    Create a labeled association between a contact and a company. The
    label_id must be the Contact → Company associationTypeId 
    (e.g. Employee).
    """

    url = (
        f"https://api.hubapi.com/crm/v4/objects/"
        f"contact/{contact_id}/associations/company/{company_id}"
    )

    payload = [
        {
            "associationCategory": "USER_DEFINED",
            "associationTypeId": label_id
        }
    ]

    response = requests.put(
        url=url,
        headers=API_HEADERS,
        json=payload,
        timeout=API_REQUEST_TIMEOUT
    )

    if response.status_code not in (200, 201, 204):
        raise RuntimeError(
            f"Failed to associate contact with company "
            f"(status={response.status_code}, response={response.text})"
        )
    
    print(f"Successfully linked contact {contact_id} to company {company_id} as Employee.")


if __name__ == "__main__":
    contact_id = create_contact(
        email="candidate.test@example.com", 
        firstname="Candidate", 
        lastname="Test"
    )
    company_id = create_company(
        name="Test Challenge Company",
        domain="test-challenge-company.com"
    )

    label_id = get_employee_label()
    add_contact_to_company(
        contact_id=contact_id, 
        company_id=company_id, 
        label_id=label_id
    )