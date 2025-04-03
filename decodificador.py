import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os

# Codificación de operaciones (6 bits)
OPCODES = {
    "ADD": "000000",
    "SUB": "000000",
    "SLT": "000000",
    "SW": "101011",
    "LW": "100011",
    "ADDI": "001000",
    "ANDI": "001100",
    "ORI": "001101",
    "BEQ": "000100",
    "BNE": "000101",
    "J": "000010",
    "JAL": "000011"
}

# Codificación de funciones (6 bits) para instrucciones tipo R
FUNCTIONS = {
    "ADD": "100000",
    "SUB": "100010",
    "SLT": "101010",
    "AND": "100100",
    "OR": "100101",
    "NOR": "100111",
    "SLL": "000000",
    "SRL": "000010"
}

class Decodificador32BitsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Decodificador Ensamblador → Binario (32 bits)")
        
        # Frame superior para entrada de archivo
        frame_superior = tk.Frame(root)
        frame_superior.pack(pady=10)
        
        self.label_archivo = tk.Label(frame_superior, text="Archivo seleccionado: Ninguno")
        self.label_archivo.pack(side=tk.LEFT, padx=5)
        
        self.boton_explorar = tk.Button(frame_superior, text="Explorar", command=self.seleccionar_archivo)
        self.boton_explorar.pack(side=tk.LEFT, padx=5)
        
        self.boton_convertir = tk.Button(frame_superior, text="Convertir", command=self.convertir_archivo, state=tk.DISABLED)
        self.boton_convertir.pack(side=tk.LEFT, padx=5)
        
        # Área de texto con scrollbars
        self.texto_original = tk.Text(root, height=7, width=80, wrap=tk.NONE)
        self.texto_conversion = tk.Text(root, height=7, width=80, wrap=tk.NONE)
        
        # Scrollbars
        scroll_y_orig = ttk.Scrollbar(root, orient=tk.VERTICAL, command=self.texto_original.yview)
        scroll_x_orig = ttk.Scrollbar(root, orient=tk.HORIZONTAL, command=self.texto_original.xview)
        self.texto_original.configure(yscrollcommand=scroll_y_orig.set, xscrollcommand=scroll_x_orig.set)
        
        scroll_y_conv = ttk.Scrollbar(root, orient=tk.VERTICAL, command=self.texto_conversion.yview)
        scroll_x_conv = ttk.Scrollbar(root, orient=tk.HORIZONTAL, command=self.texto_conversion.xview)
        self.texto_conversion.configure(yscrollcommand=scroll_y_conv.set, xscrollcommand=scroll_x_conv.set)
        
        # Etiquetas para las áreas de texto
        label_original = tk.Label(root, text="Instrucciones Originales")
        label_original.pack()
        self.texto_original.pack(fill=tk.BOTH, expand=True)
        scroll_x_orig.pack(side=tk.BOTTOM, fill=tk.X)
        scroll_y_orig.pack(side=tk.RIGHT, fill=tk.Y)
        
        label_conversion = tk.Label(root, text="Conversión a Binario")
        label_conversion.pack()
        self.texto_conversion.pack(fill=tk.BOTH, expand=True)
        scroll_x_conv.pack(side=tk.BOTTOM, fill=tk.X)
        scroll_y_conv.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.archivo_actual = None
        self.instrucciones_originales = []

    def registro_a_binario(self, registro):
        """Convierte $num a su representación binaria de 5 bits"""
        num = registro.replace('$', '')
        return format(int(num), '05b')

    def seleccionar_archivo(self):
        filepath = filedialog.askopenfilename(filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")])
        if filepath:
            self.archivo_actual = filepath
            self.label_archivo.config(text=f"Archivo seleccionado: {filepath}")
            self.boton_convertir.config(state=tk.NORMAL)
            
            try:
                with open(filepath, 'r') as file:
                    self.instrucciones_originales = [linea.strip() for linea in file.readlines() if linea.strip()]
                
                # Mostrar solo en el área de instrucciones originales
                self.texto_original.delete(1.0, tk.END)
                self.texto_conversion.delete(1.0, tk.END)
                for linea in self.instrucciones_originales:
                    self.texto_original.insert(tk.END, f"{linea}\n")
            
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo leer el archivo: {str(e)}")

    def convertir_archivo(self):
        if not self.instrucciones_originales:
            return
        
        self.texto_conversion.delete(1.0, tk.END)
        resultados_binarios = []
        
        for linea in self.instrucciones_originales:
            linea_limpia = linea.split('#')[0].strip()
            if not linea_limpia:
                continue
                
            partes = linea_limpia.replace(',', ' ').split()
            op = partes[0].upper()
            
            if op not in OPCODES:
                binario = f"// Instrucción no reconocida: {linea}"
            else:
                try:
                    if op in ["ADD", "SUB", "SLT"]:  # Tipo R
                        rd = self.registro_a_binario(partes[1])
                        rs = self.registro_a_binario(partes[2])
                        rt = self.registro_a_binario(partes[3])
                        shamt = "00000"
                        funct = FUNCTIONS[op]
                        binario = f"32'b{OPCODES[op]}_{rs}_{rt}_{rd}_{shamt}_{funct};"
                    
                    elif op in ["LW", "SW"]:  # Tipo I (load/store)
                        rt = self.registro_a_binario(partes[1])
                        offset_rs = partes[2].split('(')
                        offset = offset_rs[0]
                        rs = self.registro_a_binario(offset_rs[1].replace(')', ''))
                        binario = f"32'b{OPCODES[op]}_{rs}_{rt}_{self.bin(int(offset), 16)};"
                    
                    elif op in ["ADDI", "ANDI", "ORI"]:  # Tipo I (inmediato)
                        rt = self.registro_a_binario(partes[1])
                        rs = self.registro_a_binario(partes[2])
                        imm = partes[3]
                        binario = f"32'b{OPCODES[op]}_{rs}_{rt}_{self.bin(int(imm), 16)};"
                    
                    elif op in ["BEQ", "BNE"]:  # Tipo I (branch)
                        rs = self.registro_a_binario(partes[1])
                        rt = self.registro_a_binario(partes[2])
                        offset = partes[3]
                        binario = f"32'b{OPCODES[op]}_{rs}_{rt}_{self.bin(int(offset), 16)};"
                    
                    elif op in ["J", "JAL"]:  # Tipo J
                        address = partes[1]
                        binario = f"32'b{OPCODES[op]}_{self.bin(int(address), 26)};"
                    
                    else:
                        binario = f"// Instrucción no implementada: {linea}"
                
                except IndexError:
                    binario = f"// Error en formato para instrucción: {linea}"
                except ValueError:
                    binario = f"// Valor numérico inválido en: {linea}"
            
            self.texto_conversion.insert(tk.END, f"{binario}\n")
            resultados_binarios.append(binario)
        
        try:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            output_path = os.path.join(desktop, "salida_binario_32bits.txt")
            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n".join(resultados_binarios))
            
            messagebox.showinfo("Éxito", f"Archivo guardado en:\n{output_path}")
        
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{str(e)}")

    def bin(self, value, bits=16):
        """Convierte un valor entero a binario con el número de bits especificado"""
        if value >= 0:
            return format(value, f'0{bits}b')
        else:
            return format((1 << bits) + value, f'0{bits}b')

if __name__ == "__main__":
    root = tk.Tk()
    app = Decodificador32BitsApp(root)
    root.mainloop()