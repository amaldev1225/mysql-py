
import mysql.connector
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap import Style
from tkinter import messagebox
from tkinter import ttk


con = mysql.connector.connect(
    user='root',
    password='7356181225',
    host='localhost',
    database="food_system"
)
cur = con.cursor()

def create_tables():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS food_items (
            item_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            category VARCHAR(50),
            price INT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INT AUTO_INCREMENT PRIMARY KEY,
            customer_name VARCHAR(100)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            order_id INT,
            item_id INT,
            quantity INT,
            total_price INT,
            FOREIGN KEY (order_id) REFERENCES orders(order_id),
            FOREIGN KEY (item_id) REFERENCES food_items(item_id)
        )
    """)
    con.commit()

def seed_foods():
    cur.execute("SELECT COUNT(*) FROM food_items")
    (count,) = cur.fetchone()
    if count > 0:
        return

    foods = [
        ('Chicken Biriyani', 'biryani', 150),
        ('Al Faham Mandhi', 'mandhi', 300),
        ('Shawarma Roll', 'snacks', 80),
        ('Alfaham (Full)', 'grill', 380),
        ('Club Sandwich', 'snacks', 90),
        ('Pepsi', 'drink', 40),
        ('Lime Juice', 'drink', 30),
        ('Water Bottle', 'drink', 20)
    ]

    sql = "INSERT INTO food_items(name, category, price) VALUES (%s, %s, %s)"
    cur.executemany(sql, foods)
    con.commit()


create_tables()
seed_foods()


ROYAL_BLUE = "#0052cc"   
GOLD_YELLOW = "#f1c40f"  
WHITE = "#ffffff"
TEXT_COLOR = "#000000"


style = Style(theme="flatly")  
root = style.master
root.title("Food Ordering — Yellow & Blue")
root.geometry("900x600")
root.configure(bg=WHITE)


style.configure("Gold.TButton",
                foreground=TEXT_COLOR,
                background=GOLD_YELLOW,
                font=("Segoe UI", 10, "bold"),
                focusthickness=3, focuscolor="none")

style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))


header = tb.Frame(root, bootstyle=PRIMARY)
header.pack(fill="x")
header.configure(padding=10)
header_label = tb.Label(header, text="Food Ordering System", font=("Segoe UI", 20, "bold"),
                        foreground=WHITE, background=ROYAL_BLUE)
header_label.pack(anchor="center")


main = tb.Frame(root, padding=12)
main.pack(fill="both", expand=True)


left = tb.Frame(main)
left.pack(side="left", fill="y", padx=(0,12))

btn_view_menu = tb.Button(left, text="View Menu", bootstyle="warning", width=24)
btn_place_order = tb.Button(left, text="Place Order", bootstyle="warning", width=24)
btn_view_orders = tb.Button(left, text="View Orders", bootstyle="warning", width=24)
btn_exit = tb.Button(left, text="Exit", bootstyle="secondary", width=24, command=root.destroy)


for b in (btn_view_menu, btn_place_order, btn_view_orders):
    b.configure(style="Gold.TButton")

btn_view_menu.pack(pady=8)
btn_place_order.pack(pady=8)
btn_view_orders.pack(pady=8)
btn_exit.pack(pady=8)


workspace = tb.Frame(main)
workspace.pack(side="left", fill="both", expand=True)


def clear_workspace():
    for widget in workspace.winfo_children():
        widget.destroy()

def view_menu():
    clear_workspace()
    header_lbl = tb.Label(workspace, text="Menu", font=("Segoe UI", 16, "bold"))
    header_lbl.pack(pady=(6,12))

    cols = ("ID", "Name", "Category", "Price")
    tree = ttk.Treeview(workspace, columns=cols, show="headings", height=18)
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, anchor="center")
    tree.pack(fill="both", expand=True, padx=10, pady=6)

    cur.execute("SELECT item_id, name, category, price FROM food_items")
    rows = cur.fetchall()
    for r in rows:
        tree.insert("", "end", values=r)


def place_order():
    clear_workspace()
    header_lbl = tb.Label(workspace, text="Place Order", font=("Segoe UI", 16, "bold"))
    header_lbl.pack(pady=(6,12))

    frm = tb.Frame(workspace)
    frm.pack(pady=8)

    tb.Label(frm, text="Customer Name:", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="e", padx=6, pady=6)
    name_entry = tb.Entry(frm, width=30)
    name_entry.grid(row=0, column=1, pady=6)

    def create_order():
        name = name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Customer name required.")
            return
        cur.execute("INSERT INTO orders (customer_name) VALUES (%s)", (name,))
        con.commit()
        order_id = cur.lastrowid
        messagebox.showinfo("Order Created", f"Order created. Order ID: {order_id}")
        add_items_window(order_id)

    btn = tb.Button(frm, text="Create Order", bootstyle="warning", command=create_order)
    btn.grid(row=1, column=0, columnspan=2, pady=(8,0))
    btn.configure(style="Gold.TButton")


def add_items_window(order_id):
    win = tb.Toplevel(root)
    win.title(f"Add Items to Order #{order_id}")
    win.geometry("700x520")
    win.configure(bg=WHITE)

    tb.Label(win, text=f"Order ID: {order_id}", font=("Segoe UI", 12, "bold")).pack(pady=8)

    frame_tree = tb.Frame(win)
    frame_tree.pack(fill="both", expand=False, padx=10, pady=6)

    cols = ("ID", "Name", "Category", "Price")
    tree = ttk.Treeview(frame_tree, columns=cols, show="headings", height=12)
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, anchor="center")
    tree.pack(side="left", fill="both", expand=True)

    vsb = tb.Scrollbar(frame_tree, orient="vertical", command=tree.yview)
    tree.configure(yscroll=vsb.set)
    vsb.pack(side="right", fill="y")

    cur.execute("SELECT item_id, name, category, price FROM food_items")
    rows = cur.fetchall()
    for r in rows:
        tree.insert("", "end", values=r)


    frm = tb.Frame(win)
    frm.pack(pady=8)

    tb.Label(frm, text="Item ID:").grid(row=0, column=0, padx=6, pady=6, sticky="e")
    item_id_entry = tb.Entry(frm, width=12)
    item_id_entry.grid(row=0, column=1, padx=6, pady=6)

    tb.Label(frm, text="Quantity:").grid(row=0, column=2, padx=6, pady=6, sticky="e")
    qty_entry = tb.Entry(frm, width=12)
    qty_entry.grid(row=0, column=3, padx=6, pady=6)

    def add_item():
        try:
            item_id = int(item_id_entry.get())
            qty = int(qty_entry.get())
            if qty <= 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Error", "Enter valid numeric Item ID and Quantity.")
            return

        cur.execute("SELECT price, name FROM food_items WHERE item_id = %s", (item_id,))
        row = cur.fetchone()
        if not row:
            messagebox.showerror("Error", "Invalid Item ID.")
            return
        price, name = row
        total = price * qty
        cur.execute(
            "INSERT INTO order_items(order_id, item_id, quantity, total_price) VALUES (%s, %s, %s, %s)",
            (order_id, item_id, qty, total)
        )
        con.commit()
        messagebox.showinfo("Added", f"{name} x{qty} added. Item total = ₹{total}")
        item_id_entry.delete(0, 'end')
        qty_entry.delete(0, 'end')

    def use_selected():
        sel = tree.selection()
        if not sel:
            messagebox.showerror("Error", "Select an item from the list.")
            return
        vals = tree.item(sel[0], "values")
        item_id_entry.delete(0, 'end')
        item_id_entry.insert(0, vals[0])

    btn_frame = tb.Frame(win)
    btn_frame.pack(pady=10)
    b1 = tb.Button(btn_frame, text="Use Selected Item", bootstyle="secondary", command=use_selected)
    b2 = tb.Button(btn_frame, text="Add Item", bootstyle="warning", command=add_item)
    b1.grid(row=0, column=0, padx=8)
    b2.grid(row=0, column=1, padx=8)
    b2.configure(style="Gold.TButton")

 
    tb.Button(win, text="View Order Details", bootstyle="outline-info", command=lambda: show_order_details(order_id)).pack(pady=6)

def view_orders():
    clear_workspace()
    header_lbl = tb.Label(workspace, text="All Orders", font=("Segoe UI", 16, "bold"))
    header_lbl.pack(pady=(6,12))

    cols = ("Order ID", "Customer", "Total (₹)")
    tree = ttk.Treeview(workspace, columns=cols, show="headings", height=16)
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, anchor="center")
    tree.pack(fill="both", expand=True, padx=10, pady=6)

    cur.execute("""
        SELECT 
            o.order_id,
            o.customer_name,
            IFNULL(SUM(oi.total_price), 0) AS total_bill
        FROM orders o
        LEFT JOIN order_items oi ON o.order_id = oi.order_id
        GROUP BY o.order_id
        ORDER BY o.order_id DESC
    """)
    rows = cur.fetchall()
    for r in rows:
        tree.insert("", "end", values=r)

 
    btns = tb.Frame(workspace)
    btns.pack(pady=8)
    def on_view_details():
        sel = tree.selection()
        if not sel:
            messagebox.showerror("Error", "Select an order.")
            return
        order_id = tree.item(sel[0], "values")[0]
        show_order_details(order_id)

    tb.Button(btns, text="View Selected Order Details", bootstyle="secondary", command=on_view_details).grid(row=0, column=0, padx=6)
    tb.Button(btns, text="Refresh", bootstyle="outline-info", command=view_orders).grid(row=0, column=1, padx=6)


def show_order_details(order_id):
    try:
        order_id = int(order_id)
    except Exception:
        messagebox.showerror("Error", "Invalid order id.")
        return
    win = tb.Toplevel(root)
    win.title(f"Order #{order_id} Details")
    win.geometry("700x500")

    cur.execute("SELECT customer_name FROM orders WHERE order_id = %s", (order_id,))
    row = cur.fetchone()
    if not row:
        messagebox.showerror("Error", "Order not found.")
        win.destroy()
        return
    customer_name = row[0]
    tb.Label(win, text=f"Order ID: {order_id}  •  Customer: {customer_name}", font=("Segoe UI", 12, "bold")).pack(pady=8)

    cols = ("Item Name", "Qty", "Price", "Item Total")
    tree = ttk.Treeview(win, columns=cols, show="headings", height=16)
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, anchor="center")
    tree.pack(fill="both", expand=True, padx=10, pady=6)

    cur.execute("""
        SELECT fi.name, oi.quantity, fi.price, oi.total_price
        FROM order_items oi
        JOIN food_items fi ON oi.item_id = fi.item_id
        WHERE oi.order_id = %s
    """, (order_id,))
    rows = cur.fetchall()
    grand_total = 0
    if not rows:
        tb.Label(win, text="No items added to this order yet.", foreground="red").pack()
    else:
        for r in rows:
            tree.insert("", "end", values=r)
            grand_total += r[3]

    tb.Label(win, text=f"Grand Total: ₹{grand_total}", font=("Segoe UI", 12, "bold")).pack(pady=8)

    def delete_order():
        if messagebox.askyesno("Confirm", "Delete this order and its items?"):
            cur.execute("DELETE FROM order_items WHERE order_id = %s", (order_id,))
            cur.execute("DELETE FROM orders WHERE order_id = %s", (order_id,))
            con.commit()
            messagebox.showinfo("Deleted", f"Order #{order_id} deleted.")
            win.destroy()

    tb.Button(win, text="Delete Order", bootstyle="danger", command=delete_order).pack(pady=6)


btn_view_menu.configure(command=view_menu)
btn_place_order.configure(command=place_order)
btn_view_orders.configure(command=view_orders)


def welcome_panel():
    clear_workspace()
    tb.Label(workspace, text="Welcome to the Food Ordering App", font=("Segoe UI", 16, "bold")).pack(pady=20)
    tb.Label(workspace,  font=("Segoe UI", 10)).pack(pady=6)
welcome_panel()


root.mainloop()


try:
    cur.close()
    con.close()
except Exception:
    pass
