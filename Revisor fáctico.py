import tkinter as tk
import openai

openai.api_key = ''
reglas = open('revisor_factico.txt', 'r', encoding="utf8")

# Creamos funciones para preparar el texto
def eliminar_salto_inicial(texto):
        while texto[0] == "\n":
            texto = texto[1:]
        return texto


def borrar_saltos_linea_vacios(texto):
    return texto.replace("\n\n", "\n")


def tabular_parrafos(texto):
    parrafos = texto.split("\n")
    parrafos_tabular = []
    for parrafo in parrafos:
        parrafos_tabular.append("\t" + parrafo)
    return "\n".join(parrafos_tabular)


def texto_preparado_para_procesador(texto):
    preparado1 = eliminar_salto_inicial(texto)
    preparado2 = borrar_saltos_linea_vacios(preparado1)
    preparado3 = tabular_parrafos(preparado2)
    return preparado3

def get_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": reglas.read() + "####\nEstas son todas las reglas que tienes que seguir. Piensa paso a paso, analiza el texto del recurso, las palabras usadas en el texto alternativo propuesto, y en los documentos que se proponen.\nNunca menciones que estás siguiendo 'reglas', sino en todo caso señalar la jurisprudencia de la Sala Cuarta del Tribunal Supremo o 'de conformidad con el art. 193.b) LRJS'.\nEste es el recurso que tienes que resolver:"},
            {"role": "user", "content": prompt},
        ]
    )
    return response['choices'][0]['message']['content']


def valorar_texto():
    input_text = left_text.get(1.0, tk.END).strip()
    response = get_response(input_text)

    # Mostrar la respuesta en el cuadro de texto derecho
    right_text.delete(1.0, tk.END)
    right_text.insert(tk.END, response)
    root.clipboard_clear()
    root.clipboard_append(texto_preparado_para_procesador(response))

def toggle_instructions_left():
    if instructions_label_left.winfo_viewable():
        instructions_label_left.grid_remove()
    else:
        instructions_label_left.grid(row=1, column=1, sticky=tk.N)

def toggle_instructions_right():
    if instructions_label_right.winfo_viewable():
        instructions_label_right.grid_remove()
    else:
        instructions_label_right.grid(row=1, column=2, sticky=tk.N)

def toggle_both_instructions():
    toggle_instructions_left()
    toggle_instructions_right()


def abrir_ventana_feedback():
    def enviar_feedback():
        feedback = cuadro_feedback.get("1.0", "end-1c")
        texto_original = left_text.get("1.0", "end-1c")
        regla = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres una IA que asume el rol de juez que resuelve recursos de suplicación. El siguiente texto es una corrección ante un recurso que se te ha planteado y lo has resuelto mal. La corrección corresponde al usuario, que ha considerado que el resultado que tú has dado es incorrecto. Estudia cuál es el recurso y la corrección del usuario, extrae de este texto una regla clara, completa y precisa que puedas utilizar a partir de ahora para resolver los recursos. Escríbela de forma que tú la comprendas y puedas evitar cometer el mismo error la próxima vez. Esta regla se incluirá dentro de un archivo donde están el resto de reglas que utilizarás para resolver los recursos. La estructura es 'Regla:' y la explicación. Escribe la regla a partir del siguiente texto:"},
                {"role": "user", "content": f"Petición de revisión: {texto_original}\n Solución resumida: {feedback}"},
            ]
        )
        with open("revisor_factico.txt", "a", encoding='utf-8') as f:
            f.write(borrar_saltos_linea_vacios(eliminar_salto_inicial(regla['choices'][0]['message']['content'])) + "\n##\n")
        ventana_feedback.destroy()

    ventana_feedback = tk.Toplevel(root)
    ventana_feedback.title("Retroalimentación")
    ventana_feedback['bg'] = "#ffffff"
    cuadro_feedback = tk.Text(ventana_feedback, wrap=tk.WORD, width=45, height=10, font=("SegoeUI", 9), relief='groove', bd=2)
    cuadro_feedback.pack(expand=True, fill=tk.BOTH, padx=10)
    boton_cerrar = tk.Button(ventana_feedback, text="Cerrar", command=enviar_feedback, bg="white", activebackground="light grey", relief="groove")
    boton_cerrar.pack(pady=10, padx=10)

root = tk.Tk()
root.title("Revisor fáctico suplicacional")
root['bg'] = "#ffffff"
root.resizable(width=False, height=False)

frame = tk.Frame(root, padx="10", pady="10")
frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
frame.config(bg="white")

label_titulo = tk.Label(root, text="Revisor fáctico suplicacional", background="#ffffff", font=45)
label_titulo.grid(row=0, column=0, pady=10, columnspan=3)

instructions_label_left = tk.Label(frame, text="Este es el cuadro en el que tendrá que introducir la revisión fáctica interesada en el recurso, introduciendo el texto de la propuesta del recurrente tal y como se plantea.", bg="white", wraplength=310)
instructions_label_left.grid(row=1, column=1, sticky=tk.N)
instructions_label_left.grid_remove()

instructions_label_right = tk.Label(frame, text="Este es el cuadro en el que se mostrará el Dictamen de la IA, sobre la revisión fáctica. El texto se copiará automáticamente en el portapapeles.", bg="white", wraplength=330)
instructions_label_right.grid(row=1, column=2, sticky=tk.N)
instructions_label_right.grid_remove()

left_text = tk.Text(frame, wrap=tk.WORD, width=45, height=26, font=("SegoeUI", 9), relief='groove', bd=2)
left_text.grid(row=0, column=1, padx=(0, 10), pady=(0, 10))

right_text = tk.Text(frame, wrap=tk.WORD, width=45, height=26, font=("SegoeUI", 9), relief='groove', bd=2)
right_text.grid(row=0, column=2, padx=(10, 0), pady=(0, 10))

valorar_button = tk.Button(frame, text="Valorar", command=valorar_texto,
                           bg="white", activebackground="light grey", relief="groove")
valorar_button.grid(row=2, column=1, columnspan=2, pady=10)

toggle_instructions_button_left = tk.Button(frame, bitmap="info", command=toggle_both_instructions, bg="white", activebackground="white", width="20", relief="groove", bd=0)
toggle_instructions_button_left.grid(row=2, column=1, sticky=(tk.W))

toggle_instructions_button_right = tk.Button(frame, bitmap="warning", command=abrir_ventana_feedback, bg="white", activebackground="white", width="20", relief="groove", bd=0)
toggle_instructions_button_right.grid(row=2, column=2, sticky=(tk.E))

root.bind('<Control-Return>', lambda event: valorar_button.invoke())
root.bind('<Control-BackSpace>', lambda event: right_text.delete('1.0', tk.END))

root.mainloop()
