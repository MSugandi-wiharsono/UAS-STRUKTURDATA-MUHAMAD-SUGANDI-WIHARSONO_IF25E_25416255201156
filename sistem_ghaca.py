"""
=============================================================
  SISTEM MANAJEMEN DATA GAME - GHACA KHIFE
  Menggunakan Struktur Data: Linked List, Stack, Hash Map
  Database: File CSV
  Operasi: CRUD (Create, Read, Update, Delete)
=============================================================
"""

import csv
import os

CSV_FILE = "ghaca_khife_data.csv"
CSV_HEADER = ["id", "nama_pemain", "karakter", "level", "skor", "status"]

# ─────────────────────────────────────────────
# STRUKTUR DATA 1: NODE & LINKED LIST
# ─────────────────────────────────────────────
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None
        self.size = 0

    def append(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
        self.size += 1

    def delete_by_id(self, target_id):
        if not self.head:
            return False
        if self.head.data["id"] == target_id:
            self.head = self.head.next
            self.size -= 1
            return True
        current = self.head
        while current.next:
            if current.next.data["id"] == target_id:
                current.next = current.next.next
                self.size -= 1
                return True
            current = current.next
        return False

    def update_by_id(self, target_id, new_data):
        current = self.head
        while current:
            if current.data["id"] == target_id:
                current.data.update(new_data)
                return True
            current = current.next
        return False

    def to_list(self):
        result = []
        current = self.head
        while current:
            result.append(current.data)
            current = current.next
        return result

    def search_by_name(self, keyword):
        results = []
        current = self.head
        while current:
            if keyword.lower() in current.data["nama_pemain"].lower():
                results.append(current.data)
            current = current.next
        return results

    def sort_by_skor(self):
        """Bubble sort berdasarkan skor (descending)"""
        if not self.head or not self.head.next:
            return
        swapped = True
        while swapped:
            swapped = False
            current = self.head
            while current.next:
                if int(current.data["skor"]) < int(current.next.data["skor"]):
                    current.data, current.next.data = current.next.data, current.data
                    swapped = True
                current = current.next


# ─────────────────────────────────────────────
# STRUKTUR DATA 2: STACK (Riwayat Aksi / Undo)
# ─────────────────────────────────────────────
class Stack:
    def __init__(self):
        self._stack = []

    def push(self, action):
        self._stack.append(action)

    def pop(self):
        if self.is_empty():
            return None
        return self._stack.pop()

    def peek(self):
        if self.is_empty():
            return None
        return self._stack[-1]

    def is_empty(self):
        return len(self._stack) == 0

    def size(self):
        return len(self._stack)


# ─────────────────────────────────────────────
# STRUKTUR DATA 3: HASH MAP (Index Cepat by ID)
# ─────────────────────────────────────────────
class HashMap:
    def __init__(self, capacity=50):
        self.capacity = capacity
        self.buckets = [[] for _ in range(capacity)]

    def _hash(self, key):
        return hash(str(key)) % self.capacity

    def put(self, key, value):
        idx = self._hash(key)
        for i, (k, v) in enumerate(self.buckets[idx]):
            if k == key:
                self.buckets[idx][i] = (key, value)
                return
        self.buckets[idx].append((key, value))

    def get(self, key):
        idx = self._hash(key)
        for k, v in self.buckets[idx]:
            if k == key:
                return v
        return None

    def delete(self, key):
        idx = self._hash(key)
        self.buckets[idx] = [(k, v) for k, v in self.buckets[idx] if k != key]

    def exists(self, key):
        return self.get(key) is not None


# ─────────────────────────────────────────────
# CSV HELPER FUNCTIONS
# ─────────────────────────────────────────────
def load_from_csv():
    if not os.path.exists(CSV_FILE):
        return []
    with open(CSV_FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [row for row in reader]

def save_to_csv(data_list):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADER)
        writer.writeheader()
        writer.writerows(data_list)

def get_next_id(data_list):
    if not data_list:
        return "1"
    return str(max(int(d["id"]) for d in data_list) + 1)


# ─────────────────────────────────────────────
# INISIALISASI SISTEM
# ─────────────────────────────────────────────
def init_system():
    ll = LinkedList()
    hm = HashMap()
    records = load_from_csv()
    for r in records:
        ll.append(r)
        hm.put(r["id"], r)
    return ll, hm

def sync_system(ll, hm):
    """Sinkronisasi ulang HashMap dari Linked List"""
    hm.__init__()
    for item in ll.to_list():
        hm.put(item["id"], item)


# ─────────────────────────────────────────────
# OPERASI CRUD
# ─────────────────────────────────────────────
def create_pemain(ll, hm, history):
    print("\n── TAMBAH PEMAIN BARU ──")
    nama = input("Nama Pemain  : ").strip()
    if not nama:
        print("[!] Nama tidak boleh kosong.")
        return
    karakter = input("Karakter     : ").strip() or "Pejuang"
    level    = input("Level (1-50) : ").strip() or "1"
    skor     = input("Skor Awal    : ").strip() or "0"
    status   = input("Status (Aktif/Nonaktif): ").strip() or "Aktif"

    data = load_from_csv()
    new_id = get_next_id(data)
    record = {"id": new_id, "nama_pemain": nama, "karakter": karakter,
              "level": level, "skor": skor, "status": status}

    ll.append(record)
    hm.put(new_id, record)
    data.append(record)
    save_to_csv(data)

    history.push({"aksi": "CREATE", "data": record})
    print(f"[✓] Pemain '{nama}' berhasil ditambahkan dengan ID {new_id}.")

def read_all(ll):
    print("\n── DAFTAR SEMUA PEMAIN ──")
    items = ll.to_list()
    if not items:
        print("[!] Belum ada data pemain.")
        return
    print(f"{'ID':<5} {'Nama':<20} {'Karakter':<15} {'Lvl':<5} {'Skor':<8} {'Status'}")
    print("─" * 65)
    for d in items:
        print(f"{d['id']:<5} {d['nama_pemain']:<20} {d['karakter']:<15} {d['level']:<5} {d['skor']:<8} {d['status']}")

def read_by_id(hm):
    print("\n── CARI PEMAIN BY ID ──")
    pid = input("Masukkan ID : ").strip()
    result = hm.get(pid)
    if result:
        print(f"\n  ID       : {result['id']}")
        print(f"  Nama     : {result['nama_pemain']}")
        print(f"  Karakter : {result['karakter']}")
        print(f"  Level    : {result['level']}")
        print(f"  Skor     : {result['skor']}")
        print(f"  Status   : {result['status']}")
    else:
        print(f"[!] ID {pid} tidak ditemukan.")

def search_pemain(ll):
    print("\n── CARI PEMAIN BY NAMA ──")
    keyword = input("Kata kunci nama : ").strip()
    results = ll.search_by_name(keyword)
    if results:
        print(f"\nDitemukan {len(results)} pemain:")
        for d in results:
            print(f"  [{d['id']}] {d['nama_pemain']} | {d['karakter']} | Lvl {d['level']} | Skor {d['skor']}")
    else:
        print("[!] Tidak ada pemain dengan nama tersebut.")

def update_pemain(ll, hm, history):
    print("\n── UPDATE DATA PEMAIN ──")
    pid = input("ID Pemain yang diupdate : ").strip()
    if not hm.exists(pid):
        print(f"[!] ID {pid} tidak ditemukan.")
        return
    old = dict(hm.get(pid))
    print(f"Data lama: {old['nama_pemain']} | Lvl {old['level']} | Skor {old['skor']} | {old['status']}")
    print("[*] Kosongkan untuk tidak mengubah field tersebut.")
    level  = input(f"Level baru [{old['level']}]  : ").strip() or old["level"]
    skor   = input(f"Skor baru  [{old['skor']}]   : ").strip() or old["skor"]
    status = input(f"Status baru [{old['status']}]: ").strip() or old["status"]

    new_data = {"level": level, "skor": skor, "status": status}
    ll.update_by_id(pid, new_data)
    hm.put(pid, hm.get(pid))
    sync_system(ll, hm)
    save_to_csv(ll.to_list())

    history.push({"aksi": "UPDATE", "id": pid, "lama": old, "baru": new_data})
    print(f"[✓] Data pemain ID {pid} berhasil diperbarui.")

def delete_pemain(ll, hm, history):
    print("\n── HAPUS PEMAIN ──")
    pid = input("ID Pemain yang dihapus : ").strip()
    if not hm.exists(pid):
        print(f"[!] ID {pid} tidak ditemukan.")
        return
    old = hm.get(pid)
    konfirmasi = input(f"Yakin hapus '{old['nama_pemain']}'? (y/n): ").strip().lower()
    if konfirmasi != "y":
        print("[!] Pembatalan penghapusan.")
        return
    ll.delete_by_id(pid)
    hm.delete(pid)
    save_to_csv(ll.to_list())
    history.push({"aksi": "DELETE", "data": old})
    print(f"[✓] Pemain '{old['nama_pemain']}' berhasil dihapus.")

def undo_aksi(ll, hm, history):
    print("\n── UNDO AKSI TERAKHIR ──")
    if history.is_empty():
        print("[!] Tidak ada aksi yang bisa di-undo.")
        return
    last = history.pop()
    aksi = last["aksi"]
    if aksi == "CREATE":
        ll.delete_by_id(last["data"]["id"])
        hm.delete(last["data"]["id"])
        save_to_csv(ll.to_list())
        print(f"[✓] Undo CREATE: Pemain '{last['data']['nama_pemain']}' dihapus.")
    elif aksi == "DELETE":
        ll.append(last["data"])
        hm.put(last["data"]["id"], last["data"])
        save_to_csv(ll.to_list())
        print(f"[✓] Undo DELETE: Pemain '{last['data']['nama_pemain']}' dikembalikan.")
    elif aksi == "UPDATE":
        ll.update_by_id(last["id"], last["lama"])
        sync_system(ll, hm)
        save_to_csv(ll.to_list())
        print(f"[✓] Undo UPDATE: Data ID {last['id']} dikembalikan ke nilai lama.")

def leaderboard(ll):
    print("\n── LEADERBOARD TOP 5 ──")
    ll.sort_by_skor()
    items = ll.to_list()[:5]
    if not items:
        print("[!] Belum ada data.")
        return
    print(f"{'Rank':<6}{'Nama':<20}{'Karakter':<15}{'Level':<7}{'Skor'}")
    print("─" * 58)
    for i, d in enumerate(items, 1):
        print(f"  {i}   {d['nama_pemain']:<20}{d['karakter']:<15}{d['level']:<7}{d['skor']}")


# ─────────────────────────────────────────────
# MENU UTAMA
# ─────────────────────────────────────────────
def tampilkan_menu():
    print("\n" + "═" * 45)
    print("  ⚔  GHACA KHIFE — SISTEM MANAJEMEN GAME  ⚔")
    print("═" * 45)
    print("  [1] Tambah Pemain Baru      (Create)")
    print("  [2] Lihat Semua Pemain      (Read All)")
    print("  [3] Cari Pemain by ID       (Read by ID)")
    print("  [4] Cari Pemain by Nama     (Search)")
    print("  [5] Update Data Pemain      (Update)")
    print("  [6] Hapus Pemain            (Delete)")
    print("  [7] Leaderboard Skor        (Top 5)")
    print("  [8] Undo Aksi Terakhir      (Stack Undo)")
    print("  [0] Keluar")
    print("═" * 45)

def main():
    print("\n Memuat sistem Ghaca Khife...")
    ll, hm = init_system()
    history = Stack()
    print(f" {ll.size} data pemain berhasil dimuat dari CSV.\n")

    while True:
        tampilkan_menu()
        pilihan = input("  Pilih menu : ").strip()
        if pilihan == "1":
            create_pemain(ll, hm, history)
        elif pilihan == "2":
            read_all(ll)
        elif pilihan == "3":
            read_by_id(hm)
        elif pilihan == "4":
            search_pemain(ll)
        elif pilihan == "5":
            update_pemain(ll, hm, history)
        elif pilihan == "6":
            delete_pemain(ll, hm, history)
        elif pilihan == "7":
            leaderboard(ll)
        elif pilihan == "8":
            undo_aksi(ll, hm, history)
        elif pilihan == "0":
            print("\n [✓] Terima kasih telah bermain Ghaca Khife! Sampai jumpa.\n")
            break
        else:
            print("[!] Pilihan tidak valid, coba lagi.")


if __name__ == "__main__":
    main()