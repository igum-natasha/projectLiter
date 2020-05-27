from tkinter import *
import tkinter.ttk as ttk
import numpy as np
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from time import sleep
import codecs
import re
from projectLiter.WordAnalyser.results_keys import morph_statistic_key, morph_posts_key, \
    characters_key, frequency_key, dict_of_words_key, sentimental_key, adjective_key, adverb_key, negative_key, \
    positive_key
import threading
import queue
from multiprocessing import Process
from projectLiter.WordAnalyser.word_analyser import text_analysis
from projectLiter.requests import SearchAboutAuthor, SearchBook, author, authorenglish, SearchAboutAuthorEnglish,\
    SearchBookEnglish
matplotlib.use("TkAgg")
#author = ['Антон Чехов', 'Лев Толстой', 'Иван Тургенев', 'Николай Гоголь', 'Александр Куприн',
      #    'Михаил Булгаков', 'Максим Горький', 'Виктор Астафьев', 'Александр Солженицын', 'Федор Достоевский']
datalst = [31, 41, 59, 26, 53, 58, 97, 96, 36]
help_text = "\t-=-=Welcome to the classic literature analysis application=-=-\n\n" \
            "Here you can see the writer's biography, find his poems, and also analysis:\n" \
            "find characters, top of the most popular words, and also a dictionary of vocabulary.\n" \
            "First, you must select the author’s name from the top list and select a literature \n" \
            "from the second list."
help_text1 = 'Here you can find out the main characters of the literature, as well as see the frequency\n' \
             'of their occurrence in each chapter.'
help_text2 = 'Here you can see the amount of each vocabulary in a literature, also see the top of\n' \
             'the most popular words in a work and list of the positive and \nnegative adverbs and adjectives.'
message = ''
find = ()
book = ''
result = {sentimental_key:
          {adjective_key:
           {negative_key: [],
            positive_key: []},
           adverb_key:
           {negative_key: [],
            positive_key: []}},
          frequency_key: [],
          characters_key: [],
          morph_posts_key: [],
          morph_statistic_key: [],
          dict_of_words_key: []}
end = {}
histogram = 0
label1 = 0
label11 = 0
label_biogr = 0
all_author = author+authorenglish
lang = 0
poem = 0
but = 0
combobox = 0
label = 0
flag = 0


def tabs(name):
    h = 450
    w = 490
    nb = ttk.Notebook(width=w, height=h)
    nb.grid(row=2, column=4, columnspan=4, rowspan=4, ipadx=3, ipady=2, sticky=N, padx=2, pady=2)

    f1 = Canvas(nb, background='#F5F5F5')
    name.append(f1)
    f2 = Canvas(nb, background='#F5F5F5')
    name.append(f2)
    #create_combobox(f2)
    f3 = Canvas(nb, background='#F5F5F5')
    name.append(f3)
    #create_scroll(f1, h, w)
    #create_scroll(f3, h, w)

    print_text(f1, help_text, 10, 10, 'help')
    print_text(f2, help_text1, 40, 10, 'help1')
    print_text(f3, help_text2, 40, 10,  'help2')

    nb.add(f1, text='Text')
    nb.add(f2, text='Characters')
    nb.add(f3, text='Vocabulary')


def create_scroll(f, h, w):
    label = Label(f, text=' ', fg="#000000", width=int(w / 7.3))
    label.grid(row=12, column=0, columnspan=12, sticky=W)
    label2 = Label(f, text=' ', fg="#000000", height=int(h / 14.5))
    label2.grid(row=0, column=11, rowspan=12, sticky=N)
    vsb1 = Scrollbar(f, orient="vertical", command=f.yview)
    vsb2 = Scrollbar(f, orient="horizontal", command=f.xview)
    vsb1.grid(row=0, column=12, rowspan=11, sticky='ns')
    vsb2.grid(row=11, column=0, columnspan=12, sticky='ew')
    #f.configure(yscrollcommand=vsb1.set, xscrollcommand=vsb2.set)


def get_active_text(env):
    w = env.widget
    model = w.current()
    active = w.get()
    if model < 0:
        return None
    if flag == 1:
        print_characters(active)
    elif flag == 0:
        print_vocab(active)
    elif flag == 2:
        print_top(active)
    elif flag == 3:
        print_sentim(active)


def create_combobox(f2, text, values, x, y):
    global combobox, label, flag
    if combobox:
        combobox.grid_forget()
    if label:
        label.grid_forget()
    combobox = ttk.Combobox(f2, values=values,  exportselection=0)
    label = Label(f2, text=text, fg="#000000", bg='#F5F5F5')
    label.grid(row=x, column=y, columnspan=2, ipadx=3, ipady=2, sticky=W, padx=2, pady=2)
    if flag == 1:
        combobox.grid(row=x, column=y+2, columnspan=2)
    else:
        combobox.grid(row=x, column=y+1, columnspan=2)
    combobox.bind('<<ComboboxSelected>>', get_active_text)


def graph(f3, array1, array2):
    f = Figure(figsize=(3, 3))
    a = f.add_subplot(111)
    a.plot(array1, array2, color='#228B22')
    canvas = FigureCanvasTkAgg(f, f3)
    canvas.draw()
    canvas.get_tk_widget().grid(row=3, column=0, ipadx=3, ipady=2, padx=1, pady=2)


def hist(f2,  array1, array2, x, y, flag):
    global histogram
    ff = Figure(figsize=(3, 3), dpi=100)
    xx = ff.add_subplot(111)
    ind = [i+1 for i in range(len(array2))]
    xx.bar(ind, array2, 0.8, color="#DC143C")
    canvas = FigureCanvasTkAgg(ff, master=f2)
    canvas.draw()
    if histogram:
        histogram.grid_forget()
    histogram = canvas.get_tk_widget()
    if flag:
        histogram.grid(row=x+1, column=y, columnspan=7, ipadx=3, ipady=2, padx=1, pady=2)


def print_text(f, text_message, y, x,  tag):
    global message
    print(message)
    #f.delete(message)
    message = f.create_text(x, y, anchor=NW, text=text_message, fill="#000000", tag=tag)


def cur_select_authors(evn):
    global find, label_biogr, lang, poem
    w = evn.widget
    i, value = 0, ''
    print('hello')
    if w.curselection() != ():
        i = int(w.curselection()[0])
        value = w.get(i)
    if value and value in author:
        que = queue.Queue()
        print(value)
        t = threading.Thread(target=lambda q, arg1: q.put(SearchAboutAuthor(arg1)), args=(que, value, ))
        t.start()
        print('yes')
        t.join()
        find = que.get()
        #find = SearchAboutAuthor(value)
        lang = 'ru'
    elif value and value in authorenglish:
        print('h')
        que = queue.Queue()
        print(value)
        t = threading.Thread(target=lambda q, arg1: q.put(SearchAboutAuthorEnglish(arg1)), args=(que, value),
                             daemon=True)
        t.start()
        t.join()
        find = que.get()
        #find = SearchAboutAuthorEnglish(value)
        lang = 'eng'
        print('yes')
    if poem:
        poem.grid_forget()
    label_biogr = Label(tabs_name[0], text="Biography", fg="#000000")
    label_biogr.grid(row=0, column=0, columnspan=5, ipadx=3, ipady=2, sticky=W, padx=2, pady=2)
    tabs_name[0].delete('help')
    print_text(tabs_name[0], find[0], 30, 10, 'biogr')
    print_poems(listbox_poems(), find[1])


def info(text):
    global root
    label0 = Label(text=text, fg="#eee", bg="#333")
    label0.grid(row=7, column=0, columnspan=2, ipadx=3, ipady=2, sticky=W, padx=2, pady=2)



def cur_select_poems(evn):
    global tabs_name, book, root, lang, but, poem
    #info("Analyze...")
    wid = evn.widget
    i, value = 0, ''
    if wid.curselection() != ():
        i = int(wid.curselection()[0])
        value = wid.get(i)
    if value and value not in all_author:
        if lang == 'ru':
            ''''que1 = queue.Queue()
            search = ThreadPool(1)
            search.map(lambda q, arg1, arg2, arg3: q.put(SearchBook(arg1, arg2, arg3)), args=(que1 value, find[1], find[2]))
            procs.append(search)
            search.start()
            book = que1.get()'''
            book = SearchBook(value, find[1], find[2])
        elif lang == 'eng':
            book = SearchBookEnglish(value, find[1], find[2])
            '''que1 = queue.Queue()
            search = threading.Thread(target=lambda q, arg1, arg2, arg3: q.put(SearchBookEnglish(arg1, arg2, arg3)),
                                 args=(que1, value, find[1], find[2]), daemon=True)
            procs.append(search)
            search.start()
            book = que1.get()'''
        if poem:
            poem.grid_forget()
        print_text(tabs_name[0], find[0], 30, 10, 'biogr')
        print_poems(listbox_poems(), find[1])
        but = Button(tabs_name[0], text='Book', command=print_book)
        but.grid(row=0, column=6, ipadx=3, ipady=2, padx=1, pady=2)
        analyser(book, lang)


def print_book():
    global label_biogr, poem, but
    but.grid_forget()
    label_biogr.grid_forget()
    #label_biogr = Label(tabs_name[0], text="   Text    ", fg="#000000", width=10)
    #label_biogr.grid(row=0, column=0, columnspan=5, ipadx=3, ipady=2, sticky=S, padx=2, pady=2)
    with codecs.open(book, encoding='utf-8') as file:
        text = file.read()
    tabs_name[0].delete('biogr')
    #print_text(tabs_name[0], text, 50, 'text')
    poem = Text(tabs_name[0], width=60, height=28)
    poem.insert(1.0, text)
    poem.grid(row=0, column=0, columnspan=5, ipadx=3, ipady=2, sticky=S, padx=2, pady=2)


def listbox_author():
    authors_listbox = Listbox(width=40, height=15, selectmode=SINGLE, exportselection=0, bg='#F5F5F5')
    vsb = Scrollbar(orient="vertical", bg='#F5F5F5', command=authors_listbox.yview)
    vsb.grid(row=2, column=2, sticky='ns')
    authors_listbox.configure(yscrollcommand=vsb.set)
    authors_listbox.bind('<<ListboxSelect>>', cur_select_authors)
    for writer in all_author:
        authors_listbox.insert(END, writer)
    authors_listbox.grid(row=2, column=0, columnspan=2, ipadx=3, ipady=2, sticky=N, padx=2, pady=2)


def analyser(book, language):
    global result, end
    end.clear()
    res = ''
    ind = 0
    text1 = []
    with open(book, 'r', encoding='utf-8') as file:
        for line in file:
            text1.append(str(line))
        print(text1)
        regular = r'^Глава\s[0-9]{1,4}\s{0,2}|^[IVX]{1,7}\s{0,2}|Явление\s[а-я]{3,20}\s{0,2}|' \
                  r'^ДЕЙСТВИЕ\s[а-яА-Я]{3,20}\s{0,2}'
        for i in range(ind, len(text1)):
            find_chapter = re.findall(regular, text1[i])
            if find_chapter:
                print(i, len(text1), find_chapter)
                for j in range(i+1, len(text1)):
                    print(find_chapter)
                    if re.findall(regular, text1[j]) or j == len(text1)-1:
                        print(res)
                        print(text1[j])
                        result = text_analysis(res, language)
                        res = ''
                        find_chapter = str(find_chapter[0]).replace(' \n', '')
                        print(find_chapter)
                        end[find_chapter] = result
                        print(end)
                        ind = j
                        break
                    elif not re.findall(regular, text1[j]):
                        res += text1[j]
            elif not find_chapter and i == len(text1)-1 and not end:
                print('yes')
                result = text_analysis("".join(text1), language)
                end['Полный текст'] = result
    print(end)


def listbox_poems():
    poems_listbox = Listbox(width=40, height=10, bg='#F5F5F5')
    vsb1 = Scrollbar(orient="vertical", bg='#F5F5F5', command=poems_listbox.yview)
    vsb2 = Scrollbar(orient="horizontal", bg='#F5F5F5', command=poems_listbox.xview)
    vsb1.grid(row=4, column=2, sticky='ns')
    vsb2.grid(row=5, column=0, columnspan=2, sticky='ew')
    poems_listbox.configure(yscrollcommand=vsb1.set)
    poems_listbox.configure(xscrollcommand=vsb2.set)
    poems_listbox.bind('<<ListboxSelect>>', cur_select_poems)
    poems_listbox.grid(row=4, column=0, columnspan=2, ipadx=3, ipady=2, sticky=N, padx=2, pady=2)
    return poems_listbox


def print_poems(poems_listbox, books):
    for row in books:
        poems_listbox.insert(END, row)


def characters():
    global flag
    tabs_name[1].delete('help1')
    label2 = Label(tabs_name[1], text="Найденные\nперсонажи:", fg="#000000", bg='#F5F5F5')
    label2.grid(row=1, column=0, columnspan=5, ipadx=3, ipady=2, sticky=W, padx=2, pady=2)
    print(end)
    chapters = [f'{key}' for key in end.keys()]
    flag = 1
    create_combobox(tabs_name[1], 'Выберите главы', chapters, 1, 2)


def print_characters(chapter):
    text = ['charact','not1']
    forget(tabs_name[1],text)
    answer = ''
    print(type(end[chapter]), chapter)
    if end[chapter][characters_key]:
        for character in end[chapter][characters_key]:
            answer += str(character)
            answer += '\n'
        print_text(tabs_name[1], answer, 80, 10,  'charact')
        #create_combobox(tabs_name[1], "Выберите персонажа:", end[chapter][characters_key], 0, 2)
    else:
        print_text(tabs_name[1], 'Not found!', 80, 10, 'not1')


def forget(r, list):
    for row in list:
        r.delete(row)


def vocab():
    global label1, label11, flag
    text = ['top', 'not2', 'help2', 'sentimadverb', 'sentimadject', 'vocab']
    forget(tabs_name[2], text)
    if label11:
        label11.grid_forget()
    if label1:
        label1.grid_forget()
    label1 = Label(tabs_name[2], text="Найденные части\n речи:", fg="#000000", bg='#F5F5F5')
    label1.grid(row=1, column=0, ipadx=3, ipady=2, sticky=W, padx=2, pady=2)
    chapters = [f'{key}' for key in end.keys()]
    flag = 0
    create_combobox(tabs_name[2], 'Выберите главы', chapters, 1, 1)


def sentim():
    global label1, label11, flag
    text = ['top', 'not2', 'help2', 'sentimadverb', 'sentimadject', 'vocab']
    forget(tabs_name[2], text)
    if label1:
        label1.grid_forget()
    if label11:
        label1.grid_forget()
    hist(tabs_name[2], [], [], 1, 1, 0)
    label1 = Label(tabs_name[2], text="Negative and\n positive adverbs:", fg="#000000", bg='#F5F5F5')
    label1.grid(row=2, column=0, ipadx=3, ipady=2, sticky=W, padx=2, pady=2)
    label11 = Label(tabs_name[2], text="Negative and\n positive adjectives:", fg="#000000", bg='#F5F5F5')
    label11.grid(row=2, column=1, ipadx=3, ipady=2, sticky=W, padx=2, pady=2)
    chapters = [f'{key}' for key in end.keys()]
    flag = 3
    create_combobox(tabs_name[2], 'Выберите главы', chapters, 1, 0)


def print_sentim(chapter):
    text = ['sentimadverb', 'not2', 'sentimadject']
    forget(tabs_name[2], text)
    #chapter = chapter.split()[1]
    answer, answer1 = '', ''
    if end[chapter][sentimental_key][adjective_key]:
            print('yes')
            for word in end[chapter][sentimental_key][adjective_key][negative_key]:
                answer += f'{word} -\n'
            for word in end[chapter][sentimental_key][adjective_key][positive_key]:
                answer += f'{word} +\n'
            print(answer)
            print_text(tabs_name[2], answer, 110, 110, 'sentimadject')
    if end[chapter][sentimental_key][adverb_key]:
            for word in end[chapter][sentimental_key][adverb_key][negative_key]:
                answer1 += f'{word} -\n'
            for word in end[chapter][sentimental_key][adverb_key][positive_key]:
                answer1 += f'{word} +\n'
            print(answer1)
            print_text(tabs_name[2], answer1, 110, 10, 'sentimadverb')
    if not answer and not answer1:
        print_text(tabs_name[2], 'Not found!', 110, 10, 'not2')


def top():
    global label1, label11, flag
    text = ['top', 'not2', 'help2', 'sentimadverb', 'sentimadject', 'vocab']
    forget(tabs_name[2], text)
    if label1:
        label1.grid_forget()
    if label11:
        label11.grid_forget()
    hist(tabs_name[2], [], [], 1, 1, 0)
    label1 = Label(tabs_name[2], text="TOP слов:", fg="#000000", bg='#F5F5F5')
    label1.grid(row=1, column=0, ipadx=3, ipady=2, sticky=W, padx=2, pady=2)
    chapters = [f'{key}' for key in end.keys()]
    flag = 2
    create_combobox(tabs_name[2], 'Выберите главы', chapters, 1, 1)


def print_vocab(chapter):
    text = ['vocab', 'not2']
    forget(tabs_name[2], text)
    #chapter = chapter.split()[1]
    array1, array2 = [], []
    answer = ''
    ind = 0
    if end[chapter][morph_posts_key]:
        for post in end[chapter][morph_posts_key]:
            ind += 1
            array1.append(post)
            array2.append(int(end[chapter][morph_statistic_key][post]))
            answer += f'{ind}.{post} - {end[chapter][morph_statistic_key][post]}'
            answer += '\n'
        print_text(tabs_name[2], answer, 80, 10, 'vocab')
        hist(tabs_name[2], array1, array2, 1, 1, 1)
    else:
        print_text(tabs_name[2], 'Not found!', 70, 10, 'not2')


def print_top(chapter):
    #chapter = chapter.split()[1]
    text = ['top', 'not2']
    forget(tabs_name[2], text)
    answer = ''
    ind = 0
    if end[chapter][frequency_key]:
        for word in end[chapter][frequency_key]:
            ind += 1
            if ind < 21:
                answer += f'№{ind} - {word[0]}'
                answer += '\n'
        print_text(tabs_name[2], answer, 80, 10, 'top')
    else:
        print_text(tabs_name[2], 'Not found!', 70, 10, 'not2')


def labels():
    label0 = Label(text="Authors", fg="#000000", bg='#F5F5F5', font='TimesNewRoman 12')
    label0.grid(row=1, column=0, columnspan=2, ipadx=3, ipady=2, sticky=W, padx=2, pady=2)
    label2 = Label(text="Literature", fg="#000000", bg='#F5F5F5', font='TimesNewRoman 12')
    label2.grid(row=3, column=0, columnspan=2, ipadx=3, ipady=2, sticky=W, padx=2, pady=2)
    label3 = Label(text="Research results", fg="#000000", bg='#F5F5F5', font='TimesNewRoman 12')
    label3.grid(row=1, column=4, columnspan=4, ipadx=3, ipady=2, sticky=W, padx=2, pady=2)


def bottoms(r):
    but0 = Button(r[1], text='Characters', width=15, command=characters)
    but1 = Button(r[2], text='Vocabulary', width=15, command=vocab)
    but2 = Button(r[2], text='TOP of words', width=15, command=top)
    but3 = Button(r[2], text='Sentimental analysis', width=20, command=sentim)
    but0.grid(row=0, column=0, ipadx=3, ipady=2, padx=1, pady=2)
    but1.grid(row=0, column=0, ipadx=10, ipady=2, padx=1, pady=2)
    but2.grid(row=0, column=1, ipadx=10, ipady=2,  padx=1, pady=2)
    but3.grid(row=0, column=2, ipadx=10, ipady=2, padx=1, pady=2)


def loading(r):
    p = ttk.Progressbar(r, orient=HORIZONTAL, length=200, mode="determinate", takefocus=True, maximum=100)
    label = Label(text="Loading...", fg="#000000", bg='#F5F5F5')
    label.pack(expand=1, anchor=S)
    p.pack(expand=1, anchor=N)
    for i in range(100):
        sleep(0.05)
        p.step()
        r.update()
    for ele in r.winfo_children():
        ele.destroy()


if __name__ == '__main__':
    root = Tk()
    root.title("Classic literature analysis")
    root.geometry("780x600+270+20")
    root.configure(background='#F5F5F5')
    #loading(root)
    tabs_name = []
    labels()
    listbox_author()
    listbox_poems()
    tabs(tabs_name)
    bottoms(tabs_name)
    #create_combobox(tabs_name[1])
    root.mainloop()
