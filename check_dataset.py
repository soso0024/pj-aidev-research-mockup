from datasets import load_dataset


def check_dataset_structure():
    print("Loading dataset...")
    dataset = load_dataset("evalplus/mbppplus")

    print("\nDataset structure:")
    print(dataset)

    print("\nFirst example details:")
    first_example = dataset["test"][0]
    for key, value in first_example.items():
        print(f"\n{key}:")
        if isinstance(value, list):
            print(f"Type: {type(value)}")
            print(f"Length: {len(value)}")
            print("First few items:")
            for item in value[:3]:
                print(f"  {item}")
        else:
            print(f"Type: {type(value)}")
            print(f"Value: {value}")


if __name__ == "__main__":
    check_dataset_structure()
