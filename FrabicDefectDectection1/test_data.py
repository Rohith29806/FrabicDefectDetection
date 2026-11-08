
from training.data import load_dataset

for name in ["FDD", "TILDA", "ZD001"]:

    print("\nTesting:", name)

    train_ds, val_ds, classes = load_dataset(name)

    print("Classes:", classes)
    print("Training batches:", len(train_ds))
    print("Validation batches:", len(val_ds))

print("\nAll datasets loaded successfully!")
