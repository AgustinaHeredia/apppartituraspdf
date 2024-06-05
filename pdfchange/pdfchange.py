import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import shutil
import os

class PDFEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Editor")

        self.canvas = tk.Canvas(self.root, bg="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.entry_frame = tk.Frame(self.root)
        self.entry_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.open_button = tk.Button(self.entry_frame, text="Open PDF", command=self.open_pdf)
        self.open_button.pack()

        self.old_text_label = tk.Label(self.entry_frame, text="Text to replace:")
        self.old_text_label.pack()
        self.old_text_entry = tk.Entry(self.entry_frame)
        self.old_text_entry.pack(fill=tk.X)
        
        self.new_text_label = tk.Label(self.entry_frame, text="New text:")
        self.new_text_label.pack()
        self.new_text_entry = tk.Entry(self.entry_frame)
        self.new_text_entry.pack(fill=tk.X)
        
        self.replace_button = tk.Button(self.entry_frame, text="Replace Text", command=self.replace_text)
        self.replace_button.pack()
        
        self.undo_button = tk.Button(self.entry_frame, text="Undo", command=self.undo_replace)
        self.undo_button.pack()

        self.prev_page_button = tk.Button(self.entry_frame, text="Previous Page", command=self.prev_page)
        self.prev_page_button.pack()
        
        self.next_page_button = tk.Button(self.entry_frame, text="Next Page", command=self.next_page)
        self.next_page_button.pack()

        self.save_button = tk.Button(self.entry_frame, text="Save PDF", command=self.save_pdf)
        self.save_button.pack()

        self.doc = None
        self.current_page = 0
        self.image = None
        self.original_pdf_path = None
        self.backup_pdf_path = None

    def open_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if not file_path:
            return
        
        self.doc = fitz.open(file_path)
        self.current_page = 0
        self.original_pdf_path = file_path
        self.backup_pdf_path = file_path + ".backup"
        shutil.copyfile(file_path, self.backup_pdf_path)
        self.render_page()

    def render_page(self):
        if not self.doc:
            return
        
        page = self.doc.load_page(self.current_page)
        pix = page.get_pixmap()
        mode = "RGB" if pix.alpha == 0 else "RGBA"
        img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
        self.image = ImageTk.PhotoImage(img)

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def replace_text(self):
        if not self.doc:
            messagebox.showerror("Error", "No PDF opened")
            return
        
        old_text = self.old_text_entry.get()
        new_text = self.new_text_entry.get()
        
        if not (old_text and new_text):
            messagebox.showerror("Error", "Both old and new text must be provided")
            return

        self.backup_pdf_path = self.original_pdf_path + ".backup"
        shutil.copyfile(self.original_pdf_path, self.backup_pdf_path)
        
        for page_num in range(len(self.doc)):
            page = self.doc.load_page(page_num)
            areas = page.search_for(old_text)
            if areas:
                for inst in areas:
                    rect = inst
                    # Draw a white rectangle over the old text
                    page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))
                    text_x = rect.tl[0] + 2
                    rect_height = rect.br[1] - rect.tl[1]
                    text_y = rect.tl[1] + rect_height // 4 
                    # Insert the new text inside the rectangle
                    page.insert_text((text_x, text_y), new_text, fontsize=12, color=(0, 0, 0))

        self.render_page()
    
    def undo_replace(self):
        if not self.doc or not self.backup_pdf_path:
            messagebox.showerror("Error", "No PDF backup found")
            return
        
        os.remove(self.original_pdf_path)
        shutil.copyfile(self.backup_pdf_path, self.original_pdf_path)
        self.doc = fitz.open(self.original_pdf_path)
        self.render_page()

    def prev_page(self):
        if self.doc and self.current_page > 0:
            self.current_page -= 1
            self.render_page()

    def next_page(self):
        if self.doc and self.current_page < len(self.doc) - 1:
            self.current_page += 1
            self.render_page()

    def save_pdf(self):
        if not self.doc:
            messagebox.showerror("Error", "No PDF opened")
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if save_path:
            self.doc.save(save_path)
            messagebox.showinfo("Success", "PDF saved successfully")

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFEditorApp(root)
    root.mainloop()
