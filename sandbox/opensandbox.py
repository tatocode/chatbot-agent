from __future__ import annotations

import asyncio
from pathlib import Path
from typing import TYPE_CHECKING

from opensandbox.exceptions import SandboxException

if TYPE_CHECKING:
    from opensandbox import SandboxSync
from deepagents.backends.protocol import ExecuteResponse, FileUploadResponse, FileDownloadResponse
from deepagents.backends.sandbox import BaseSandbox
from opensandbox.models import Execution, WriteEntry


class OpenSandbox(BaseSandbox):
    enable_capture_offload = True

    def __init__(self, sandbox: SandboxSync):
        self._sandbox = sandbox
        self._default_timeout: int = 30 * 60

    @property
    def id(self) -> str:
        """Return the LangSmith sandbox name."""
        return self._sandbox.id

    def execute(self, command: str, timeout: int | None = None) -> ExecuteResponse:
        execution: Execution = self._sandbox.commands.run(command)

        return ExecuteResponse(
            output=str(execution),
            exit_code=-1 if execution.exit_code is None else execution.exit_code,
            truncated=False,
        )

    def upload_files(self, files: list[tuple[str, bytes]]) -> list[FileUploadResponse]:
        """Upload multiple files to the sandbox.

        Implementations must support partial success - catch exceptions per-file
        and return errors in `FileUploadResponse` objects rather than raising.

        Upload files is responsible for ensuring that the parent path exists
        (if user permissions allow the user to write to the given directory)
        """

        responses: list[FileUploadResponse] = []
        for path, content in files:
            if not path.startswith("/"):
                responses.append(FileUploadResponse(path=path, error="invalid_path"))
                continue
            try:
                self._sandbox.files.write_file(path, content)
                responses.append(FileUploadResponse(path=path, error=None))
            except SandboxException as e:
                # logger.debug("Failed to upload %s: %s", path, e)
                responses.append(FileUploadResponse(path=path, error=f"An error occurred while uploading file in sandbox: {e}"))
        return responses

    def download_files(self, paths: list[str]) -> list[FileDownloadResponse]:
        """Download multiple files from the sandbox.

        Implementations must support partial success - catch exceptions per-file
        and return errors in `FileDownloadResponse` objects rather than raising.
        """

        responses: list[FileDownloadResponse] = []
        for path in paths:
            if not path.startswith("/"):
                responses.append(FileDownloadResponse(path=path, content=None, error="invalid_path"))
                continue
            try:
                content: bytes = self._sandbox.files.read_bytes(path)
                responses.append(FileDownloadResponse(path=path, content=content, error=None))
            except SandboxException as e:
                responses.append(FileDownloadResponse(path=path, content=None, error=f"An error occurred while uploading file in sandbox: {e}"))
        return responses


