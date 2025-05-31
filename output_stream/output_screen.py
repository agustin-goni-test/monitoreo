from .output_writer import OutputWriter

class ScreenWriter(OutputWriter):
    def write_default(self, service_name: str, data_matrix: list[list]):
        print("Writing to the screen...")
        print(f"Service Name: {service_name}")
        
        header = data_matrix[0]
        for row in data_matrix[1:]:  # Skip header row since we’re labeling columns
            output_row = []
            for col_name, value in zip(header, row):
                # if col_name.lower() != "timestamp" and isinstance(value, (int, float)):
                #     # Add 'seconds' for time values — you could refine this further based on your metric name/type logic
                #     value_str = f"{value} seconds" if "time" in col_name.lower() else str(value)
                # else:
                #     value_str = str(value)
                value_str = str(value)
                output_row.append(f"{col_name}: {value_str}")
            print(", ".join(output_row))
        
        print(f"\nWrote a total of {len(data_matrix) - 1}  data points, with {len(data_matrix[0]) - 1} columns, to the screen")
        