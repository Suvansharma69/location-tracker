import phonenumbers
from phonenumbers import timezone, geocoder, carrier, number_type, PhoneNumberType, NumberParseException
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os

class PhoneNumberTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Phone Number Location Tracker")
        self.root.geometry("600x800")
        self.root.resizable(True, True)
        
        # Load templates
        self.templates = self.load_templates()
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Template management frame
        template_frame = ttk.LabelFrame(main_frame, text="Templates", padding="5")
        template_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Template combobox
        self.template_var = tk.StringVar()
        self.template_combo = ttk.Combobox(template_frame, textvariable=self.template_var, width=25)
        self.template_combo.grid(row=0, column=0, padx=5, pady=5)
        self.template_combo['values'] = list(self.templates.keys())
        self.template_combo.bind('<<ComboboxSelected>>', self.load_template)
        
        # Template buttons
        ttk.Button(template_frame, text="Save Template", command=self.save_template).grid(row=0, column=1, padx=5)
        ttk.Button(template_frame, text="Delete Template", command=self.delete_template).grid(row=0, column=2, padx=5)
        
        # Phone number input
        ttk.Label(main_frame, text="Enter phone number with country code:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.phone_entry = ttk.Entry(main_frame, width=30)
        self.phone_entry.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        # Track button
        ttk.Button(main_frame, text="Track", command=self.track_number).grid(row=3, column=0, pady=10)
        
        # Create a frame for results
        self.results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        self.results_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Create labels for results
        self.result_labels = {}
        fields = [
            "Time Zone(s)", "General Location", "Service Provider", "Number Type",
            "Network Code", "International Format", "National Format", "E.164 Format",
            "Country Code", "Country Name", "Possible Lengths", "Is Possible Number",
            "Is Valid Number"
        ]
        
        for i, field in enumerate(fields):
            ttk.Label(self.results_frame, text=f"{field}:").grid(row=i, column=0, sticky=tk.W, pady=2)
            self.result_labels[field] = ttk.Label(self.results_frame, text="")
            self.result_labels[field].grid(row=i, column=1, sticky=tk.W, pady=2)
    
    def load_templates(self):
        try:
            if os.path.exists('templates.json'):
                with open('templates.json', 'r') as f:
                    return json.load(f)
            return {}
        except Exception:
            return {}
    
    def save_templates(self):
        try:
            with open('templates.json', 'w') as f:
                json.dump(self.templates, f)
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
                
            # Get template name
            template_name = simpledialog.askstring("Save Template", "Enter template name:")
            if not template_name:
                return
                
            # Save the template
            self.templates[template_name] = number
            self.save_templates()
            
            # Update combobox
            self.template_combo['values'] = list(self.templates.keys())
            self.template_combo.set(template_name)
            
            messagebox.showinfo("Success", "Template saved successfully!")
            
        except NumberParseException:
            messagebox.showerror("Error", "Invalid phone number format. Please try again.")
    
    def load_template(self, event=None):
        template_name = self.template_var.get()
        if template_name in self.templates:
            self.phone_entry.delete(0, tk.END)
            self.phone_entry.insert(0, self.templates[template_name])
    
    def delete_template(self):
        template_name = self.template_var.get()
        if not template_name:
            messagebox.showerror("Error", "Please select a template to delete")
            return
            
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete template '{template_name}'?"):
            del self.templates[template_name]
            self.save_templates()
            self.template_combo['values'] = list(self.templates.keys())
            self.template_var.set('')
            messagebox.showinfo("Success", "Template deleted successfully!")
    
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
            
            # Other information
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
