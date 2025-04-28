import json
import csv
from io import StringIO

class DataTransformer:
    """Data transformer tool for MCP."""

    def json_to_csv(self, json_data):
        """Convert JSON to CSV."""
        if not isinstance(json_data, list) or not json_data:
            return ""

        # Extract headers
        headers = list(json_data[0].keys())

        # Create CSV
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=headers)
        writer.writeheader()
        writer.writerows(json_data)

        return output.getvalue()

    def csv_to_json(self, csv_data):
        """Convert CSV to JSON."""
        # Parse CSV
        reader = csv.DictReader(StringIO(csv_data))

        # Convert to list of dictionaries
        result = []
        for row in reader:
            # Try to convert numeric values
            processed_row = {}
            for key, value in row.items():
                if value.strip() and value.strip().replace('.', '', 1).isdigit():
                    try:
                        processed_row[key] = float(value) if '.' in value else int(value)
                    except ValueError:
                        processed_row[key] = value
                else:
                    processed_row[key] = value

            result.append(processed_row)

        return result