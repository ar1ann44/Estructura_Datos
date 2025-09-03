import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# Nodo para la lista enlazada
class Node:
    def __init__(self, client_name, party_size, reservation_time):
        self.client_name = client_name
        self.party_size = party_size
        self.reservation_time = reservation_time
        self.next = None

# Clase para la lista de espera del restaurante
class RestaurantWaitlist:
    def __init__(self):
        self.head = None
        # Mesas disponibles por tamaño (2, 4, 6 personas)
        self.tables = {2: 5, 4: 3, 6: 2}  # inicial: 5 mesas de 2, 3 de 4, 2 de 6
        self.wait_time_per_table = 30  # tiempo promedio por mesa en minutos

    def add_client(self, client_name, party_size, reservation_time):
        """Añadir cliente a la lista de espera"""
        new_node = Node(client_name, party_size, reservation_time)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node

    def call_next_table(self):
        """Llamar a la siguiente mesa disponible"""
        if not self.head:
            return False, "No hay clientes en la lista de espera."

        current = self.head
        table_size = self._find_suitable_table(current.party_size)
        
        if table_size and self.tables[table_size] > 0:
            self.tables[table_size] -= 1  # Ocupar mesa
            client_name = current.client_name
            self.head = current.next  # Remover de la lista
            return True, f"Llamando a {client_name} para una mesa de {table_size} personas."
        else:
            return False, f"No hay mesas disponibles para {current.client_name} (grupo de {current.party_size})."

    def _find_suitable_table(self, party_size):
        """Encontrar mesa adecuada según el tamaño del grupo"""
        for size in sorted(self.tables.keys()):
            if party_size <= size:
                return size
        return None

    def get_waitlist(self):
        """Obtener la lista completa de espera"""
        clients = []
        current = self.head
        while current:
            clients.append({
                'name': current.client_name,
                'party_size': current.party_size,
                'time': current.reservation_time
            })
            current = current.next
        return clients

    def cancel_reservation(self, client_name):
        """Cancelar una reservación"""
        if not self.head:
            return False, "La lista de espera está vacía."
        
        if self.head.client_name == client_name:
            self.head = self.head.next
            return True, f"Reservación de {client_name} cancelada."

        current = self.head
        while current.next and current.next.client_name != client_name:
            current = current.next
        
        if current.next:
            current.next = current.next.next
            return True, f"Reservación de {client_name} cancelada."
        else:
            return False, f"No se encontró a {client_name} en la lista de espera."

    def estimate_wait_time(self, party_size):
        """Estimar tiempo de espera para un grupo"""
        count = 0
        current = self.head
        while current:
            if current.party_size <= party_size:
                count += 1
            current = current.next
        
        table_size = self._find_suitable_table(party_size)
        if not table_size or self.tables[table_size] == 0:
            wait_time = count * self.wait_time_per_table
        else:
            wait_time = (count - self.tables[table_size]) * self.wait_time_per_table
        
        return max(0, wait_time)

    def free_table(self, table_size):
        """Liberar una mesa"""
        if table_size in self.tables:
            self.tables[table_size] += 1
            return True
        return False

# Interfaz gráfica
class RestaurantApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Lista de Espera - Restaurante")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        self.waitlist = RestaurantWaitlist()
        
        self.setup_ui()
        self.update_displays()

    def setup_ui(self):
        # Título principal
        title_label = tk.Label(self.root, text="Sistema de Lista de Espera", 
                            font=('Arial', 18, 'bold'), bg='#f0f0f0', fg='#333')
        title_label.pack(pady=10)

        # Frame principal
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Panel izquierdo - Controles
        left_frame = tk.Frame(main_frame, bg='white', relief='ridge', bd=2)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))

        # Sección de agregar cliente
        add_frame = tk.LabelFrame(left_frame, text="Agregar Cliente", font=('Arial', 12, 'bold'), 
                                bg='white', fg='#333', pady=10)
        add_frame.pack(fill='x', padx=10, pady=10)

        tk.Label(add_frame, text="Nombre del Cliente:", bg='white').pack(anchor='w', padx=10)
        self.name_entry = tk.Entry(add_frame, width=30)
        self.name_entry.pack(padx=10, pady=(0, 5))

        tk.Label(add_frame, text="Tamaño del Grupo:", bg='white').pack(anchor='w', padx=10)
        self.size_var = tk.StringVar(value="2")
        size_frame = tk.Frame(add_frame, bg='white')
        size_frame.pack(padx=10, pady=(0, 5))
        for size in [2, 4, 6]:
            tk.Radiobutton(size_frame, text=f"{size} personas", variable=self.size_var, 
                        value=str(size), bg='white').pack(side='left', padx=5)

        tk.Label(add_frame, text="Hora de Reserva:", bg='white').pack(anchor='w', padx=10)
        self.time_entry = tk.Entry(add_frame, width=20)
        self.time_entry.pack(padx=10, pady=(0, 5))
        self.time_entry.insert(0, datetime.now().strftime("%H:%M"))

        tk.Button(add_frame, text="Agregar a Lista de Espera", command=self.add_client,
                bg='#4CAF50', fg='white', font=('Arial', 10, 'bold')).pack(pady=10)

        # Sección de acciones
        actions_frame = tk.LabelFrame(left_frame, text="Acciones", font=('Arial', 12, 'bold'),
                                    bg='white', fg='#333', pady=10)
        actions_frame.pack(fill='x', padx=10, pady=10)

        tk.Button(actions_frame, text="Llamar Siguiente Mesa", command=self.call_next,
                bg='#2196F3', fg='white', font=('Arial', 10, 'bold')).pack(pady=5)

        cancel_frame = tk.Frame(actions_frame, bg='white')
        cancel_frame.pack(fill='x', pady=5)
        tk.Label(cancel_frame, text="Cancelar:", bg='white').pack(side='left')
        self.cancel_entry = tk.Entry(cancel_frame, width=20)
        self.cancel_entry.pack(side='left', padx=5)
        tk.Button(cancel_frame, text="Cancelar", command=self.cancel_reservation,
                bg='#f44336', fg='white').pack(side='left')

        # Sección de mesas
        tables_frame = tk.LabelFrame(left_frame, text="Gestión de Mesas", font=('Arial', 12, 'bold'),
                                    bg='white', fg='#333', pady=10)
        tables_frame.pack(fill='x', padx=10, pady=10)

        self.tables_label = tk.Label(tables_frame, text="", bg='white', justify='left')
        self.tables_label.pack(padx=10, pady=5)

        free_frame = tk.Frame(tables_frame, bg='white')
        free_frame.pack(pady=5)
        tk.Label(free_frame, text="Liberar mesa de:", bg='white').pack(side='left')
        self.free_var = tk.StringVar(value="2")
        for size in [2, 4, 6]:
            tk.Radiobutton(free_frame, text=f"{size}", variable=self.free_var, 
                        value=str(size), bg='white').pack(side='left', padx=2)
        tk.Button(free_frame, text="Liberar", command=self.free_table,
                bg='#FF9800', fg='white').pack(side='left', padx=5)

        # Panel derecho - Lista de espera
        right_frame = tk.Frame(main_frame, bg='white', relief='ridge', bd=2)
        right_frame.pack(side='right', fill='both', expand=True)

        tk.Label(right_frame, text="Lista de Espera Actual", font=('Arial', 14, 'bold'),
                bg='white', fg='#333').pack(pady=10)

        # Crear Treeview para la lista
        columns = ('Posición', 'Cliente', 'Grupo', 'Hora', 'Espera Estimada')
        self.tree = ttk.Treeview(right_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor='center')

        scrollbar = ttk.Scrollbar(right_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side='right', fill='y', padx=(0, 10), pady=10)

    def add_client(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Por favor ingrese el nombre del cliente")
            return
        
        party_size = int(self.size_var.get())
        time = self.time_entry.get().strip()
        
        self.waitlist.add_client(name, party_size, time)
        
        # Limpiar campos
        self.name_entry.delete(0, tk.END)
        self.time_entry.delete(0, tk.END)
        self.time_entry.insert(0, datetime.now().strftime("%H:%M"))
        
        self.update_displays()
        messagebox.showinfo("Éxito", f"Cliente {name} agregado a la lista de espera")

    def call_next(self):
        success, message = self.waitlist.call_next_table()
        if success:
            messagebox.showinfo("Mesa Asignada", message)
        else:
            messagebox.showwarning("Sin Mesas", message)
        self.update_displays()

    def cancel_reservation(self):
        name = self.cancel_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Por favor ingrese el nombre del cliente")
            return
        
        success, message = self.waitlist.cancel_reservation(name)
        if success:
            messagebox.showinfo("Cancelación", message)
        else:
            messagebox.showwarning("Error", message)
        
        self.cancel_entry.delete(0, tk.END)
        self.update_displays()

    def free_table(self):
        table_size = int(self.free_var.get())
        if self.waitlist.free_table(table_size):
            messagebox.showinfo("Mesa Liberada", f"Mesa para {table_size} personas liberada")
            self.update_displays()

    def update_displays(self):
        # Actualizar lista de espera
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        clients = self.waitlist.get_waitlist()
        for i, client in enumerate(clients, 1):
            wait_time = self.waitlist.estimate_wait_time(client['party_size'])
            self.tree.insert('', 'end', values=(
                i, client['name'], f"{client['party_size']} personas", 
                client['time'], f"{wait_time} min"
            ))
        
        # Actualizar información de mesas
        tables_info = "Mesas Disponibles:\n"
        for size, count in self.waitlist.tables.items():
            tables_info += f"• {size} personas: {count} mesas\n"
        self.tables_label.config(text=tables_info)

if __name__ == "__main__":
    root = tk.Tk()
    app = RestaurantApp(root)
    root.mainloop()