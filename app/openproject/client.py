import base64
from typing import Any

import httpx

from app.config import get_settings
from app.core.exceptions import OpenProjectError
from app.openproject.schemas import (
    CreateWorkPackagePayload,
    OpenProjectProject,
    OpenProjectType,
    OpenProjectWorkPackageResult,
)


class OpenProjectClient:
    def __init__(self) -> None:
        settings = get_settings()
        self.base_url = settings.openproject_base_url.rstrip("/")
        self.token = settings.openproject_api_token

    def _headers(self) -> dict[str, str]:
        basic_token = base64.b64encode(f"apikey:{self.token}".encode("utf-8")).decode("utf-8")
        return {
            "Authorization": f"Basic {basic_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _request(self, method: str, path: str, *, json_body: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        with httpx.Client(timeout=30.0) as client:
            response = client.request(method, url, headers=self._headers(), json=json_body)

        if response.status_code >= 400:
            self._raise_normalized_error(response)
        return response.json()

    def _raise_normalized_error(self, response: httpx.Response) -> None:
        body = response.text
        if response.status_code in {401, 403}:
            raise OpenProjectError("AUTH_FAILED", body)
        if response.status_code == 404:
            raise OpenProjectError("PROJECT_NOT_FOUND", body)
        if response.status_code == 422:
            raise OpenProjectError("VALIDATION_FAILED", body)
        if response.status_code == 429:
            raise OpenProjectError("RATE_LIMITED", body)
        if response.status_code >= 500:
            raise OpenProjectError("OPENPROJECT_UNAVAILABLE", body)
        raise OpenProjectError("OPENPROJECT_ERROR", body)

    def list_projects(self) -> list[OpenProjectProject]:
        data = self._request("GET", "/api/v3/projects")
        items = data.get("_embedded", {}).get("elements", [])
        return [
            OpenProjectProject(
                id=item["id"],
                name=item.get("name", ""),
                identifier=item.get("identifier"),
            )
            for item in items
        ]

    def list_project_types(self, project_id: int) -> list[OpenProjectType]:
        data = self._request("GET", f"/api/v3/projects/{project_id}/types")
        items = data.get("_embedded", {}).get("elements", [])
        return [OpenProjectType(id=item["id"], name=item.get("name", "")) for item in items]

    def fetch_project_schema(self, project_id: int, type_id: int | None = None) -> dict[str, Any]:
        suffix = f"?type={type_id}" if type_id is not None else ""
        return self._request("GET", f"/api/v3/projects/{project_id}/work_packages/schemas/default{suffix}")

    def fetch_custom_fields(self) -> list[dict[str, Any]]:
        try:
            data = self._request("GET", "/api/v3/custom_fields")
        except OpenProjectError as exc:
            if exc.code == "PROJECT_NOT_FOUND":
                return []
            raise
        return data.get("_embedded", {}).get("elements", [])

    def create_work_package(self, payload: CreateWorkPackagePayload) -> OpenProjectWorkPackageResult:
        links: dict[str, dict[str, str]] = {
            "project": {"href": f"/api/v3/projects/{payload.project_id}"},
            "type": {"href": f"/api/v3/types/{payload.type_id}"},
        }
        if payload.priority_id:
            links["priority"] = {"href": f"/api/v3/priorities/{payload.priority_id}"}
        if payload.assignee_id:
            links["assignee"] = {"href": f"/api/v3/users/{payload.assignee_id}"}

        request_payload: dict[str, Any] = {
            "subject": payload.subject,
            "_links": links,
        }
        if payload.description:
            request_payload["description"] = {"format": "markdown", "raw": payload.description}
        if payload.due_date:
            request_payload["dueDate"] = payload.due_date

        for key, value in payload.custom_fields.items():
            request_payload[f"customField{key}"] = value

        data = self._request("POST", "/api/v3/work_packages", json_body=request_payload)
        wp_id = data["id"]
        return OpenProjectWorkPackageResult(
            id=wp_id,
            subject=data.get("subject", payload.subject),
            project_name=data.get("_links", {}).get("project", {}).get("title"),
            link=f"{self.base_url}/work_packages/{wp_id}",
        )
