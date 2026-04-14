
chunk_size = 500

with open("data/medical_text.txt",encoding="utf-8") as f:
    text = f.read()

chunks = []

for i in range(0,len(text),chunk_size):
    chunks.append(text[i:i+chunk_size])

with open("data/chunks.txt","w",encoding="utf-8") as f:
    for c in chunks:
        f.write(c+"\n\n")

print("Chunking completed.")
