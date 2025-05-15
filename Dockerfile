# Gunakan image Node.js sebagai base
FROM node:18

# Install Python3, pip, dan venv
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv

# Alias python ke python3 (agar perintah 'python' bisa dipakai)
RUN ln -s /usr/bin/python3 /usr/bin/python

# Set working directory
WORKDIR /app

# Copy semua file ke dalam container
COPY . .

# Install dependencies Node.js
RUN npm install

# Buat virtual environment untuk Python dan install requirements di dalamnya
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port (ganti sesuai port backend Anda)
EXPOSE 8080

# Jalankan aplikasi Node.js
CMD ["npm", "start"] 