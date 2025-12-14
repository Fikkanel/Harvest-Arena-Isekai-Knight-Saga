# Harvest Arena: Isekai Knight Saga

Game RPG **Farming + Battle** berbasis **Python (Pygame)** dengan penerapan **Pemrograman Berorientasi Objek (PBO)** dan integrasi **Generative AI (Google Gemini)** untuk sistem quest dinamis.

---

## 🎮 Deskripsi Singkat

**Harvest Arena: Isekai Knight Saga** adalah game desktop 2D yang menggabungkan mekanik **farming simulator** ala Harvest Moon dengan **turn-based battle RPG**. Keunikan utama game ini adalah sistem **Dynamic Quest** yang dapat dihasilkan secara otomatis oleh AI (Google Gemini) menggunakan **multithreading**, sehingga permainan terasa variatif dan tidak statis.

Game ini dikembangkan sebagai **Proyek UAS Mata Kuliah Pemrograman Berorientasi Objek (PBO)**.

---

## ✨ Fitur Utama

* 🌱 **Farming System**: cangkul, tanam bibit, siram, dan panen tanaman
* ⚔️ **Battle System (Turn-Based)**: lawan musuh seperti Slime dan Golem
* 🤖 **AI Dynamic Quest (Google Gemini)**
* 🔄 **Fallback Offline Quest** jika AI tidak tersedia
* 💾 **Save & Load Game** berbasis JSON
* 🧱 **World Tile System** dengan ribuan FarmTile
* 🎵 **Procedural Sound Effect** (tanpa file audio eksternal)
* 🧠 Implementasi penuh **OOP (Encapsulation, Inheritance, Polymorphism)**

---

## 🧩 Penerapan Konsep PBO

### 1. Encapsulation

Digunakan pada kelas `PlayerStats` untuk melindungi data penting seperti HP, Mana, Gold, dan XP menggunakan `@property`.

### 2. Inheritance

```text
Entity (Parent)
 ├── Hero (Child)
 └── Enemy (Child)
```

### 3. Polymorphism

Metode `update()` dan `redraw()` diimplementasikan berbeda pada `Hero` dan `Enemy`.

---

## 🗺️ Arsitektur Sistem

* **MasterGame**: Controller utama (Game Loop & State Manager)
* **WorldSystem**: Manajemen map dan FarmTile
* **FarmTile**: Representasi setiap petak tanah
* **PlayerStats**: Data pemain & sistem quest
* **Quest**: Objekt misi (AI & Offline)
* **BattleScene**: Pertarungan turn-based
* **Hotbar & Inventory**: Manajemen item

---

## 🤖 AI Quest System

* Menggunakan **Google Gemini API**
* Diproses menggunakan **Thread terpisah** (non-blocking)
* Output AI wajib berupa **JSON valid**
* Jika AI gagal → otomatis fallback ke **Offline Quest**

Contoh output AI:

```json
{
  "desc": "Kumpulkan 5 Jamur untuk bertahan hidup",
  "target_val": 5,
  "type": "harvest",
  "target_name": "Mushroom"
}
```

---

## 💾 Save & Load System

* Menggunakan **Serialisasi JSON**
* Mendukung:

  * PlayerStats
  * Inventory
  * Quest progress
  * Ribuan FarmTile
* Key tuple `(x, y)` dikonversi menjadi string `"x,y"`

---

## 🛠️ Teknologi yang Digunakan

* **Python 3.12+**
* **Pygame**
* **Google Generative AI (Gemini)**
* **JSON** (Save Data)
* **Multithreading (threading)**

---

## 📦 Instalasi & Menjalankan Game

### 1. Clone Repository

```bash
git clone https://github.com/username/harvest-arena.git
cd harvest-arena
```

### 2. Install Dependency

```bash
pip install pygame google-generativeai
```

### 3. (Opsional) Set API Key Gemini

Edit di `main.py`:

```python
GEMINI_API_KEY = "ISI_API_KEY_GEMINI_DISINI"
```

Jika tidak diisi, game otomatis berjalan dalam **Offline Mode**.

### 4. Jalankan Game

```bash
python main.py
```

---

## 🎮 Kontrol Dasar

| Aksi      | Tombol         |
| --------- | -------------- |
| Bergerak  | W A S D        |
| Interaksi | Klik Mouse     |
| Farming   | Tool di Hotbar |
| Battle    | Klik Menu Aksi |

---

## 📁 Struktur File (Sederhana)

```text
├── main.py
├── ASSETS/
│   ├── tile_*.png
│   ├── crops/
│   ├── enemy/
│   └── hero_*.png
├── savegame.json
└── README.md
```

---

## 📌 Catatan Penting

* Game dirancang **offline-first**
* AI hanya fitur tambahan, bukan ketergantungan utama
* Semua sound dihasilkan secara **procedural**

---

## 📚 Referensi

* Python Documentation
* Pygame Documentation
* Google Gemini API
* Design Patterns – GoF

---

## 👤 Author

**M. Fikkan El Haq**
D4 Manajemen Informatika
Universitas Negeri Surabaya
2025

---

⭐ *Proyek ini dibuat untuk keperluan akademik dan pembelajaran.*
