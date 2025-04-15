"""
Tests for Terraform infrastructure deployment.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add the src directory to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture
def terraform_dir():
    """Return the path to the Terraform directory."""
    return Path(__file__).parent.parent / "terraform"


@pytest.mark.infrastructure
class TestTerraformValidation:
    """Tests for Terraform configuration validation."""

    @patch("subprocess.run")
    def test_terraform_validate(self, mock_run, terraform_dir):
        """Test that Terraform configuration is valid."""
        # Configure mock
        mock_run.return_value = MagicMock(
            returncode=0, stdout=b'{"valid":true,"error_count":0}', stderr=b""
        )

        # Change to Terraform directory
        original_dir = os.getcwd()
        os.chdir(terraform_dir)

        try:
            # Run terraform validate
            result = subprocess.run(
                ["terraform", "validate", "-json"], capture_output=True, check=True
            )

            # Parse output
            output = json.loads(result.stdout)

            # Check validation result
            assert output["valid"], f"Terraform configuration is not valid: {output}"
            assert output["error_count"] == 0, (
                f"Terraform has {output['error_count']} errors"
            )

        finally:
            # Return to original directory
            os.chdir(original_dir)

    @patch("subprocess.run")
    def test_terraform_plan(self, mock_run, terraform_dir):
        """Test that Terraform plan runs without errors."""
        # Configure mock
        mock_run.return_value = MagicMock(
            returncode=0, stdout=b"Terraform plan executed successfully", stderr=b""
        )

        # Change to Terraform directory
        original_dir = os.getcwd()
        os.chdir(terraform_dir)

        try:
            # Run terraform plan
            result = subprocess.run(
                ["terraform", "plan", "-no-color", "-out=tfplan", "-input=false"],
                capture_output=True,
                check=True,
            )

            # Check return code
            assert result.returncode == 0, f"Terraform plan failed: {result.stderr}"

        finally:
            # Return to original directory
            os.chdir(original_dir)


@pytest.mark.infrastructure
class TestTerraformModules:
    """Tests for individual Terraform modules."""

    def test_s3_module_outputs(self, terraform_dir):
        """Test that the S3 module defines the expected outputs."""
        # Path to S3 module
        s3_module_dir = terraform_dir / "modules" / "s3"

        # Check that module directory exists
        assert s3_module_dir.exists(), f"S3 module directory not found: {s3_module_dir}"

        # Check outputs.tf file
        outputs_file = s3_module_dir / "outputs.tf"
        assert outputs_file.exists(), f"outputs.tf not found in {s3_module_dir}"

        # Read outputs.tf content
        outputs_content = outputs_file.read_text()

        # Check for expected outputs
        expected_outputs = ["bucket_name", "bucket_arn", "bucket_id"]
        for output in expected_outputs:
            assert f'output "{output}"' in outputs_content, (
                f'Output "{output}" not found in outputs.tf'
            )

    def test_athena_module_variables(self, terraform_dir):
        """Test that the Athena module defines the expected variables."""
        # Path to Athena module
        athena_module_dir = terraform_dir / "modules" / "athena"

        # Check that module directory exists
        assert athena_module_dir.exists(), (
            f"Athena module directory not found: {athena_module_dir}"
        )

        # Check variables.tf file
        variables_file = athena_module_dir / "variables.tf"
        assert variables_file.exists(), f"variables.tf not found in {athena_module_dir}"

        # Read variables.tf content
        variables_content = variables_file.read_text()

        # Check for expected variables
        expected_variables = ["database_name", "output_location", "workgroup_name"]
        for variable in expected_variables:
            assert f'variable "{variable}"' in variables_content, (
                f'Variable "{variable}" not found in variables.tf'
            )


# If we want to run this test file directly
if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
