from os import error, stat
import sys
import time
import re
from translate.storage.tmx import tmxfile
import lxml.etree as ET
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from multiprocessing import Process
from multiprocessing import Pool
import threading
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic



pool_size = 300

tmx = ""
output = ""
filecontent = ""
status = 0

window = Tk()
window.title("Schoonmaken")

window.columnconfigure([0], minsize=200)
window.rowconfigure([0, 1, 2], minsize=30)

label_gekozenBestand = Label(window, text="Geen bestand gekozen")
label_gekozenBestand.grid(row=0, column=0, padx=5, pady=5)


app = QtWidgets.QApplication(sys.argv)

window = uic.loadUi("mainwindow.ui")
window.show()
app.exec()

class Main(object):



    def  __init__(self):
        self.test = None


    def kiezen():
        global tmx
        global output
        global filecontent
        global window
        
        label_voorbeeld = Label(window, text=f"{filecontent}")
        label_voorbeeld.grid(row=1, column=1, padx=5, pady=5)
        label_gekozenBestand = Label(window, text=f"Gekozen bestand: {tmx}")
        label_gekozenBestand.grid(row=0, column=0, padx=5, pady=5)

        filepath = askopenfilename(
            filetypes=[("TMX File", "*.tmx"), ("All Files", "*.*")]
            
        )
        if not filepath:
            return

        tmx = filepath
        output = tmx.replace('.tmx', '')
        output = f'{output}_Schoon.tmx'
        label_gekozenBestand = Label(window, text=f"Gekozen bestand: {tmx}")
        label_gekozenBestand.grid(row=0, column=0, padx=5, pady=5)
    

    def tagsVerwijderen():
        global tmx
        global output
        try:
            with open(tmx, "rb+") as input:
                tree = ET.parse(input)
                root = tree.getroot()

                rowlines = 0 
                lines = 0

                for elem in root.getiterator():
                    rowlines += 1
                   
                for elem in root.getiterator():
                    try:
                        tekst = elem.text
                        tekst = re.sub(r'<(.*?)>', '', tekst)
                        elem.text = tekst
                        lines += 1

                    except AttributeError:
                        pass

            tree.write(output, xml_declaration=True, method='xml', encoding="utf8")

            messagebox.showinfo("Gelukt", "Het opschonen is gelukt!")
        except:
            messagebox.showerror("Mislukt", "Het opschonen is niet gelukt!")


    def controleren():
        global tmx
        global output        
        with open(tmx, "rb+") as input:
            tree = ET.parse(input)
            root = tree.getroot()

            for elem in root.getiterator():
                try:
                    tekst = elem.text
                    tekst = re.search(r'<(.*?)>', tekst)
                except AttributeError:
                    pass


    def verwijderen0():
        global tmx
        global output
        global status
        global window
        global pool_size

        rowlines = 0
        lines = 0

        with open(output, 'rb+') as fin:
            tmx_file = tmxfile(fin)
            duplicates = []
                
            try:
                for node in tmx_file.unit_iter():
                    rowlines += 1
                    if node.source == node.target:
                        duplicates.append(node)
                    else:
                        pass
                lines = 0
                try:
                    for duplicate in duplicates:
                        tmx_file.removeunit(duplicate)
                        tmx_file.save()
                        lines += 1
                        status = ((lines/rowlines)*100)
                        status = str(status)
                        print(status)
                        label_status = Label(window, text=f"{status}%")
                        label_status.grid(row=0, column=1, padx=5, pady=5)
                except:
                    print("Error ".format(error))
            except:
                print("Error ".format(error))

    def verwijderen1(): 
        global tmx
        global output
        global status
        global window
        global pool_size

        source = []
        target = []
        with open(output, 'rb') as fin:
            tmx_file = tmxfile(fin)
            for node in tmx_file.unit_iter():
                source.append(node.source)
                target.append(node.target)

            n = 0
            for item in source:
                if source[n] == target[n]:
                    print("Zelfde! ", source[n], target[n])
                    del source[n]
                    del target[n]
                n += 1
        
            n = 0
            lijst = []
            for item in source:
                oorsprong = source[n]
                bestemming = target[n]
                lijst.append(oorsprong)
                lijst.append(bestemming)
                n += 1

            for item in lijst:
                tmx_file.addunit(item)
                tmx_file.save()


            #print(source, target)

    def verwijderen2():
        global tmx
        global output
        global status
        global window
        global pool_size

        with open(output, 'rb+') as fin:
            tmx_file = tmxfile(fin)
            for node in tmx_file.unit_iter():
                if node.source == node.target:
                    tmx_file.removeunit(node)
                    tmx_file.save()

    def verwijderen3():
        tree = ET.parse(output)
        root = tree.getroot()
        prev = None

        def elements_equal(e1, e2):
            if type(e1) != type(e2):
                return False
            if e1.tag != e2.tag: return False
            if e1.text != e2.text: return False
            if e1.tail != e2.tail: return False
            if e1.attrib != e2.attrib: return False
            if len(e1) != len(e2): return False
            return all([elements_equal(c1, c2) for c1, c2 in zip(e1, e2)])

        for page in root:                     # iterate over pages
            elems_to_remove = []
            for elem in page:
                if elements_equal(elem, prev):
                    print("found duplicate: %s" % elem.text)   # equal function works well
                    elems_to_remove.append(elem)
                    continue
                prev = elem
            for elem_to_remove in elems_to_remove:
                page.remove(elem_to_remove)
        tree.write(output, xml_declaration=True, method='xml', encoding="utf8")
    
    def verwijderen4():
        global tmx
        global output
        try:
            with open(output, "rb+") as input:
                tree = ET.parse(input)
                root = tree.getroot()

                rowlines = 0 
                lines = 0

                for elem in root.getiterator():
                    rowlines += 1
                   
                for elem in root.getiterator():
                    try:
                        tekst = elem.text
                        tekst = re.sub(r'<seg>^(.*)(\r?\n\1)+$</seg>', '\1', tekst)
                        elem.text = tekst
                        print(elem.text)
                        lines += 1

                    except AttributeError:
                        pass

            tree.write(output, xml_declaration=True, method='xml', encoding="utf8")

            messagebox.showinfo("Gelukt", "Het opschonen is gelukt!")
        except:
            messagebox.showerror("Mislukt", "Het opschonen is niet gelukt!")

    def verwijderen5(): 
        global tmx
        global output

        tree = ET.parse(tmx)
        root = tree.getroot()
        for seg in root.iter('seg'):
            woord = seg.text
            print(woord)

    def verwijderen6(): 
        global tmx

        tree = ET.parse(tmx)
        root = tree.getroot()
        root = ET.fromstring(tmx)
        
        for woord in root.findall('tmx/body'):
            tuid = woord.find()

            


            

    button_bestand = Button(text='Bestand kiezen', width=20, command=kiezen)
    button_dubbeleVerwijderen = Button(text='Dubbele verwijderen', width=20, command=verwijderen6)
    button_tagsVerwijderen = Button(text='Tags verwijderen', width=20, command=tagsVerwijderen)
    

    button_bestand.grid(row=1, column=0, padx=5, pady=5)
    button_dubbeleVerwijderen.grid(row=3, column=0, padx=5, pady=5)
    button_tagsVerwijderen.grid(row=2, column=0, padx=5, pady=5)
    


    #window.mainloop()