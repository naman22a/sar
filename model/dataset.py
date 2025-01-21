import kagglehub

# Download latest version
path = kagglehub.dataset_download("aaryamenon/sar-image-colorization")

print("Path to dataset files:", path)