import phonenumbers
from phonenumbers import timezone, geocoder, carrier, number_type, PhoneNumberType, NumberParseException
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import json
import os
from datetime import datetime
import csv

class PhoneNumberTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Phone Number Location Tracker")
        self.root.geometry("1000x900")
        self.root.resizable(True, True)
        
        # Color themes
        self.themes = {
            "light": {
                "bg": "#f0f0f0",
                "fg": "#333333",
                "accent": "#007bff",
                "secondary": "#6c757d",
                "success": "#28a745",
                "warning": "#ffc107",
                "error": "#dc3545",
                "frame_bg": "#ffffff",
                "button_bg": "#007bff",
                "button_fg": "#ffffff",
                "hover_bg": "#0056b3",
                "active_bg": "#004085"
            },
            "dark": {
                "bg": "#2b2b2b",
                "fg": "#ffffff",
                "accent": "#0d6efd",
                "secondary": "#6c757d",
                "success": "#28a745",
                "warning": "#ffc107",
                "error": "#dc3545",
                "frame_bg": "#3c3c3c",
                "button_bg": "#0d6efd",
                "button_fg": "#ffffff",
                "hover_bg": "#0b5ed7",
                "active_bg": "#0a58ca"
            }
        }
        
        # Initialize template categories first
        self.template_categories = {
            "Business": {
                "Corporate Office": "+1-212-555-1234",
                "Customer Support": "+44-20-7123-4567",
                "Sales Department": "+91-80-1234-5678"
            },
            "Emergency": {
                "Police": "+1-911",
                "Ambulance": "+44-999",
                "Fire Department": "+91-101"
            },
            "International": {
                "US Embassy": "+1-202-501-4444",
                "UK Embassy": "+44-20-7008-1500",
                "Indian Embassy": "+91-11-2419-8000"
            }
        }
        
        # Initialize data
        self.templates = self.load_templates()
        self.search_history = self.load_search_history()
        self.current_theme = "light"
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create all UI elements
        self.create_ui_elements()
        
        # Apply initial theme
        self.apply_theme()
        
    def create_ui_elements(self):
        # Template management frame
        template_frame = ttk.LabelFrame(self.main_frame, text="Templates", padding="5")
        template_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Template category combobox
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(template_frame, textvariable=self.category_var, width=20)
        self.category_combo.grid(row=0, column=0, padx=5, pady=5)
        self.category_combo['values'] = list(self.template_categories.keys())
        self.category_combo.bind('<<ComboboxSelected>>', self.update_template_list)
        
        # Template combobox
        self.template_var = tk.StringVar()
        self.template_combo = ttk.Combobox(template_frame, textvariable=self.template_var, width=25)
        self.template_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Template buttons with icons
        self.save_template_btn = ttk.Button(template_frame, text="Save Template", command=self.save_template)
        self.save_template_btn.grid(row=0, column=2, padx=5)
        
        self.delete_template_btn = ttk.Button(template_frame, text="Delete Template", command=self.delete_template)
        self.delete_template_btn.grid(row=0, column=3, padx=5)
        
        self.add_category_btn = ttk.Button(template_frame, text="Add Category", command=self.add_category)
        self.add_category_btn.grid(row=0, column=4, padx=5)
        
        # Quick Country Code Lookup
        country_frame = ttk.LabelFrame(self.main_frame, text="Quick Country Code Lookup", padding="5")
        country_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.country_var = tk.StringVar()
        self.country_combo = ttk.Combobox(country_frame, textvariable=self.country_var, width=30)
        self.country_combo.grid(row=0, column=0, padx=5, pady=5)
        self.country_codes = self.get_country_codes()
        self.country_combo['values'] = [f"{country} (+{code})" for country, code in self.country_codes.items()]
        self.country_combo.bind('<<ComboboxSelected>>', self.insert_country_code)
        
        # Phone number input frame
        input_frame = ttk.LabelFrame(self.main_frame, text="Phone Number Input", padding="5")
        input_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(input_frame, text="Enter phone number with country code:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.phone_entry = ttk.Entry(input_frame, width=30)
        self.phone_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)
        self.phone_entry.bind('<KeyRelease>', self.validate_number_live)
        
        # Live validation label
        self.validation_label = ttk.Label(input_frame, text="")
        self.validation_label.grid(row=0, column=2, sticky=tk.W, pady=5, padx=5)
        
        # Track button
        self.track_btn = ttk.Button(input_frame, text="Track", command=self.track_number)
        self.track_btn.grid(row=0, column=3, pady=5, padx=5)
        
        # History frame
        history_frame = ttk.LabelFrame(self.main_frame, text="Search History", padding="5")
        history_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.history_listbox = tk.Listbox(history_frame, height=5)
        self.history_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        self.history_listbox.bind('<Double-Button-1>', self.load_from_history)
        
        history_scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_listbox.yview)
        history_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.history_listbox.configure(yscrollcommand=history_scrollbar.set)
        
        # Update history display
        self.update_history_display()
        
        # Results frame
        self.results_frame = ttk.LabelFrame(self.main_frame, text="Results", padding="10")
        self.results_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Create labels for results
        self.result_labels = {}
        self.fields = [
            "Time Zone(s)", "General Location", "Service Provider", "Number Type",
            "Network Code", "International Format", "National Format", "E.164 Format",
            "Country Code", "Country Name", "Possible Lengths", "Is Possible Number",
            "Is Valid Number"
        ]
        
        for i, field in enumerate(self.fields):
            ttk.Label(self.results_frame, text=f"{field}:").grid(row=i, column=0, sticky=tk.W, pady=2)
            self.result_labels[field] = ttk.Label(self.results_frame, text="")
            self.result_labels[field].grid(row=i, column=1, sticky=tk.W, pady=2)
            
        # Apply modern styling
        self.apply_modern_style()
        
    def apply_theme(self):
        theme = self.themes[self.current_theme]
        
        # Configure root window
        self.root.configure(bg=theme['bg'])
        
        # Configure styles
        style = ttk.Style()
        
        # Frame styles
        style.configure("TFrame", background=theme['bg'])
        style.configure("TLabelframe", background=theme['bg'], foreground=theme['fg'])
        style.configure("TLabelframe.Label", background=theme['bg'], foreground=theme['fg'])
        
        # Label styles
        style.configure("TLabel", background=theme['bg'], foreground=theme['fg'])
        
        # Button styles
        style.configure("TButton", 
                      background=theme['button_bg'],
                      foreground=theme['button_fg'],
                      font=('Helvetica', 10, 'bold'))
        style.map("TButton",
                 background=[('active', theme['active_bg']),
                           ('pressed', theme['active_bg']),
                           ('hover', theme['hover_bg'])])
        
        # Combobox styles
        style.configure("TCombobox",
                       fieldbackground=theme['frame_bg'],
                       background=theme['frame_bg'],
                       foreground=theme['fg'])
        
        # Listbox styles
        self.history_listbox.configure(
            bg=theme['frame_bg'],
            fg=theme['fg'],
            selectbackground=theme['accent'],
            selectforeground=theme['button_fg']
        )
        
        # Entry styles
        style.configure("TEntry",
                       fieldbackground=theme['frame_bg'],
                       foreground=theme['fg'])
        
    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme()
        
    def apply_modern_style(self):
        style = ttk.Style()
        
        # Configure modern fonts
        style.configure("TFrame", font=('Helvetica', 10))
        style.configure("TLabel", font=('Helvetica', 10))
        style.configure("TLabelframe", font=('Helvetica', 10, 'bold'))
        style.configure("TLabelframe.Label", font=('Helvetica', 10, 'bold'))
        style.configure("TButton", font=('Helvetica', 10, 'bold'))
        style.configure("TCombobox", font=('Helvetica', 10))
        
        # Configure modern colors
        self.apply_theme()
        
    def update_template_list(self, event=None):
        category = self.category_var.get()
        if category in self.template_categories:
            self.template_combo['values'] = list(self.template_categories[category].keys())
            self.template_combo.set('')
            
    def add_category(self):
        category_name = simpledialog.askstring("Add Category", "Enter category name:")
        if category_name:
            self.template_categories[category_name] = {}
            self.category_combo['values'] = list(self.template_categories.keys())
            self.save_templates()
            
    def load_templates(self):
        try:
            if os.path.exists('templates.json'):
                with open('templates.json', 'r') as f:
                    return json.load(f)
            return self.template_categories
        except Exception:
            return self.template_categories
            
    def save_templates(self):
        try:
            with open('templates.json', 'w') as f:
                json.dump(self.template_categories, f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save templates: {str(e)}")
            
    def save_template(self):
        number = self.phone_entry.get().strip()
        if not number:
            messagebox.showerror("Error", "Please enter a phone number to save as template")
            return
            
        try:
            # Validate the number
            phone_number = phonenumbers.parse(number)
            if not phonenumbers.is_valid_number(phone_number):
                messagebox.showerror("Error", "Invalid phone number! Please enter a valid number.")
                return
                
            # Get template name and category
            category = self.category_var.get()
            if not category:
                messagebox.showerror("Error", "Please select a category first")
                return
                
            template_name = simpledialog.askstring("Save Template", "Enter template name:")
            if not template_name:
                return
                
            # Save the template
            self.template_categories[category][template_name] = number
            self.save_templates()
            
            # Update combobox
            self.template_combo['values'] = list(self.template_categories[category].keys())
            self.template_combo.set(template_name)
            
            messagebox.showinfo("Success", "Template saved successfully!")
            
        except NumberParseException:
            messagebox.showerror("Error", "Invalid phone number format. Please try again.")
            
    def load_template(self, event=None):
        category = self.category_var.get()
        template_name = self.template_var.get()
        if category in self.template_categories and template_name in self.template_categories[category]:
            self.phone_entry.delete(0, tk.END)
            self.phone_entry.insert(0, self.template_categories[category][template_name])
            
    def delete_template(self):
        category = self.category_var.get()
        template_name = self.template_var.get()
        if not category or not template_name:
            messagebox.showerror("Error", "Please select a category and template to delete")
            return
            
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete template '{template_name}' from category '{category}'?"):
            del self.template_categories[category][template_name]
            self.save_templates()
            self.template_combo['values'] = list(self.template_categories[category].keys())
            self.template_var.set('')
            messagebox.showinfo("Success", "Template deleted successfully!")
    
    def create_menu_bar(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Results", command=self.export_results)
        file_menu.add_command(label="Clear History", command=self.clear_history)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Toggle Theme", command=self.toggle_theme)
    
    def get_country_codes(self):
        # Dictionary of common country codes
        return {
            "United States": "1",
            "United Kingdom": "44",
            "India": "91",
            "China": "86",
            "Japan": "81",
            "Germany": "49",
            "France": "33",
            "Australia": "61",
            "Canada": "1",
            "Brazil": "55"
        }
    
    def insert_country_code(self, event=None):
        selected = self.country_var.get()
        if selected:
            code = selected.split("(+")[1].rstrip(")")
            self.phone_entry.delete(0, tk.END)
            self.phone_entry.insert(0, f"+{code}")
    
    def validate_number_live(self, event=None):
        number = self.phone_entry.get().strip()
        if number:
            try:
                phone_number = phonenumbers.parse(number)
                is_valid = phonenumbers.is_valid_number(phone_number)
                is_possible = phonenumbers.is_possible_number(phone_number)
                
                if is_valid:
                    self.validation_label.config(text="✓ Valid", foreground="green")
                elif is_possible:
                    self.validation_label.config(text="⚠ Possible", foreground="orange")
                else:
                    self.validation_label.config(text="✗ Invalid", foreground="red")
            except NumberParseException:
                self.validation_label.config(text="✗ Invalid Format", foreground="red")
        else:
            self.validation_label.config(text="")
    
    def load_search_history(self):
        try:
            if os.path.exists('search_history.json'):
                with open('search_history.json', 'r') as f:
                    return json.load(f)
            return []
        except Exception:
            return []
    
    def save_search_history(self):
        try:
            with open('search_history.json', 'w') as f:
                json.dump(self.search_history, f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save search history: {str(e)}")
    
    def update_history_display(self):
        self.history_listbox.delete(0, tk.END)
        for item in reversed(self.search_history[-10:]):  # Show last 10 searches
            self.history_listbox.insert(0, f"{item['number']} - {item['timestamp']}")
    
    def load_from_history(self, event=None):
        selection = self.history_listbox.curselection()
        if selection:
            selected_item = self.history_listbox.get(selection[0])
            number = selected_item.split(" - ")[0]
            self.phone_entry.delete(0, tk.END)
            self.phone_entry.insert(0, number)
            self.track_number()
    
    def clear_history(self):
        if messagebox.askyesno("Clear History", "Are you sure you want to clear the search history?"):
            self.search_history = []
            self.save_search_history()
            self.update_history_display()
    
    def export_results(self):
        if not any(label.cget("text") for label in self.result_labels.values()):
            messagebox.showwarning("Export", "No results to export!")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Field", "Value"])
                    for field in self.fields:
                        writer.writerow([field, self.result_labels[field].cget("text")])
                messagebox.showinfo("Export", "Results exported successfully!")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export results: {str(e)}")
    
    def track_number(self):
        number = self.phone_entry.get().strip()
        if not number:
            messagebox.showerror("Error", "Please enter a phone number")
            return
            
        try:
            # Clear previous results
            for label in self.result_labels.values():
                label.config(text="")
            
            # Parse the phone number
            phone_number = phonenumbers.parse(number)
            
            if not phonenumbers.is_valid_number(phone_number):
                messagebox.showerror("Error", "Invalid phone number! Please enter a valid number.")
                return
            
            # Add to search history
            self.search_history.append({
                "number": number,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            self.save_search_history()
            self.update_history_display()
            
            # Update results
            self.result_labels["Time Zone(s)"].config(text=str(timezone.time_zones_for_number(phone_number)))
            self.result_labels["General Location"].config(text=geocoder.description_for_number(phone_number, "en"))
            self.result_labels["Service Provider"].config(text=carrier.name_for_number(phone_number, "en"))
            
            # Phone number type
            phone_type = number_type(phone_number)
            type_mapping = {
                PhoneNumberType.MOBILE: "Mobile",
                PhoneNumberType.FIXED_LINE: "Fixed-line",
                PhoneNumberType.FIXED_LINE_OR_MOBILE: "Fixed-line or Mobile",
                PhoneNumberType.TOLL_FREE: "Toll-Free",
                PhoneNumberType.PREMIUM_RATE: "Premium Rate",
                PhoneNumberType.VOIP: "VoIP",
                PhoneNumberType.PAGER: "Pager",
                PhoneNumberType.UAN: "UAN (Universal Access Number)",
                PhoneNumberType.UNKNOWN: "Unknown",
            }
            self.result_labels["Number Type"].config(text=type_mapping.get(phone_type, "Unknown"))
            
            # Network code
            self.result_labels["Network Code"].config(text=str(carrier._is_mobile(phone_number)))
            
            # Format numbers
            self.result_labels["International Format"].config(
                text=phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            )
            self.result_labels["National Format"].config(
                text=phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.NATIONAL)
            )
            self.result_labels["E.164 Format"].config(
                text=phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164)
            )
            
            # Country information
            self.result_labels["Country Code"].config(text=f"+{phone_number.country_code}")
            self.result_labels["Country Name"].config(text=geocoder.country_name_for_number(phone_number, "en"))
            
            # Other information and all
            self.result_labels["Possible Lengths"].config(
                text=str(phonenumbers.length_of_geographical_area_code(phone_number))
            )
            self.result_labels["Is Possible Number"].config(
                text="Yes" if phonenumbers.is_possible_number(phone_number) else "No"
            )
            self.result_labels["Is Valid Number"].config(
                text="Yes" if phonenumbers.is_valid_number(phone_number) else "No"
            )
            
        except NumberParseException:
            messagebox.showerror("Error", "Invalid phone number format. Please try again.")

if __name__ == "__main__":
    root = tk.Tk()
    app = PhoneNumberTracker(root)
    root.mainloop()
