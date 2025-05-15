# Gunakan image Node.js sebagai base
FROM node:18

# Install Python3 dan pip
RUN apt-get update && apt-get install -y python3 python3-pip

# Alias python ke python3 (agar perintah 'python' bisa dipakai)
RUN ln -s /usr/bin/python3 /usr/bin/python

# Set working directory
WORKDIR /app

# Copy semua file ke dalam container
COPY . .

# Install dependencies Node.js
RUN npm install

# Install dependencies Python
RUN pip3 install -r requirements.txt

# Expose port (ganti sesuai port backend Anda)
EXPOSE 8080

# Jalankan aplikasi Node.js
CMD ["npm", "start"] 