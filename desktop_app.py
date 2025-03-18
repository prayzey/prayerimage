import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from prayer_image import create_prayer_image
import os
from datetime import datetime

class PrayerImageGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Prayer Image Generator")
        self.root.geometry("800x600")

        # Configure style
        style = ttk.Style()
        style.configure('TButton', padding=6, font=('Helvetica', 12))
        style.configure('TLabel', font=('Helvetica', 12))

        # Main container with padding
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Instructions
        instructions = ttk.Label(main_frame, text="Enter your prayer text below:", style='TLabel')
        instructions.pack(pady=(0, 5), anchor='w')

        # Text area with scrollbar
        self.text_area = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            width=60,
            height=15,
            font=('Helvetica', 11)
        )
        self.text_area.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Generate button
        generate_btn = ttk.Button(
            main_frame,
            text="Generate Prayer Image",
            command=self.generate_image,
            style='TButton'
        )
        generate_btn.pack(pady=10)

        # Status label
        self.status_label = ttk.Label(main_frame, text="", style='TLabel')
        self.status_label.pack(pady=5)

        # Ensure output directory exists
        if not os.path.exists("static/generated"):
            os.makedirs("static/generated", exist_ok=True)

    def generate_image(self):
        text = self.text_area.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter some prayer text first!")
            return

        try:
            self.status_label.config(text="Generating image...")
            self.root.update()

            # Generate unique filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = os.path.join("static/generated", f'prayer_{timestamp}.png')

            # Generate the image
            generated_files = create_prayer_image(text, output_filename=output_path)

            # Show success message with file location
            if generated_files:
                message = f"Images generated successfully!\nLocation: {', '.join(generated_files)}"
                messagebox.showinfo("Success", message)
            else:
                messagebox.showwarning("Warning", "No images were generated")

            self.status_label.config(text="")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_label.config(text="")

def main():
    root = tk.Tk()
    app = PrayerImageGeneratorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
