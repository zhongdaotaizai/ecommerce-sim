import os

base = r"C:\Users\20548\Documents\Codex\2026-06-20\hi\ecommerce-sim\frontend"
files = ["package.json", "app.json", "eas.json"]

for fname in files:
    path = os.path.join(base, fname)
    with open(path, "rb") as f:
        data = f.read()
    if data[:3] == b'\xef\xbb\xbf':
        data = data[3:]
        print(f"BOM removed from {fname}")
    with open(path, "wb") as f:
        f.write(data)
print("All JSON files cleaned!")

# Also fix backend files
backend_base = r"C:\Users\20548\Documents\Codex\2026-06-20\hi\ecommerce-sim\backend"
for fname in [".env"]:
    path = os.path.join(backend_base, fname)
    if os.path.exists(path):
        with open(path, "rb") as f:
            data = f.read()
        if data[:3] == b'\xef\xbb\xbf':
            data = data[3:]
            print(f"BOM removed from {fname}")
        with open(path, "wb") as f:
            f.write(data)
print("Done!")
