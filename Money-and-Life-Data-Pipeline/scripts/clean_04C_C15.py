"""04C featured case. Run only the financial well-being (C15) parser."""
from clean_04C_bankofcanada import parse_chart


if __name__ == "__main__":
    qa = parse_chart("C15")
    print("\nC15 cleaning completed successfully.")
    print("Series:", qa["series"])
    print("Study quarters:", qa["study_quarters_present"])
    print("Study records:", qa["study_records"])
    print("Missing study values:", qa["study_values_missing_in_source"])
