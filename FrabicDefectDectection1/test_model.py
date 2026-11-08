from training.model import build_model

datasets = {
    "FDD": 3,
    "TILDA": 4,
    "ZD001": 3
}

for name, classes in datasets.items():

    print("\nTesting model:", name)

    model = build_model(classes)

    print("Model created successfully!")
    print("Number of classes:", classes)
    print("Input shape:", model.input_shape)
    print("Output shape:", model.output_shape)

print("\nAll models tested successfully!")