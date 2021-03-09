def read_database(FileName, id_point):
    import sqlite3
    conn = sqlite3.connect(FileName)
    cur = conn.cursor()

    max_point = cur.execute("SELECT point FROM Points WHERE id_point = '%d'" % id_point).fetchall()[0][0]
    students = cur.execute("SELECT id_student, fio, expel FROM Students").fetchall()
    ratings = cur.execute("SELECT id_student, curr_point, absence_count FROM Rating WHERE id_point = '%d'" % id_point).fetchall()
    conn.close()

    import numpy as np
    id = np.array([student[0] for student in students])
    fio = np.array([student[1] for student in students])
    expel = np.array([bool(student[2]) for student in students])
    curr_point = np.array([rating[1] for rating in ratings])
    absence_count = np.array([rating[2] for rating in ratings])

    id = id[expel]
    fio = fio[expel]
    curr_point = curr_point[expel]
    absence_count = absence_count[expel]

    import pandas as pd
    Data = pd.DataFrame({"id": id, "fio": fio, "curr_point": curr_point, "absence_count": absence_count})
    return Data, max_point


def parseHTML(data, web, FileName, id_point):
    DBData, max_point = read_database(FileName, id_point)
    from bs4 import BeautifulSoup, SoupStrainer
    soup = BeautifulSoup(data, "html.parser")
    import re

    #Количество фамилий в браузере
    count = 0
    ok = True
    while ok:
        el = soup.find(id="ctl00_ContentPlaceHolder1_ASPxGridView1_cell%d_3_LinkButton1" % (count+1))
        if el is None:
            ok = False
        else:
            count += 1

    for index, row in DBData.iterrows():
        row["fio"] = row["fio"].upper()
        print(row["id"], row["fio"], row["curr_point"])

        row_number = row["id"]
        el = soup.find(id="ctl00_ContentPlaceHolder1_ASPxGridView1_cell%d_3_LinkButton1" % row_number)
        if el is None:
            ok = False
        else:
            text = el.findAll(text=True)[0]
            surname = re.search(r'[А-Яа-яЁёA-Za-z]+\s[А-Яа-яЁёA-Za-z]+\s[А-Яа-яЁёA-Za-z]+', text)
            if surname is not None:
                surname = surname.group(0)
                surname = surname.upper()
                ok = row["fio"].find(surname) != -1
                print(surname, ok)

        if not ok:
            for i in range(1,count+1):
                el = soup.find(id="ctl00_ContentPlaceHolder1_ASPxGridView1_cell%d_3_LinkButton1" % i)
                text = el.findAll(text=True)[0]
                surname = re.search(r'[А-Яа-яЁёA-Za-z]+\s[А-Яа-яЁёA-Za-z]+\s[А-Яа-яЁёA-Za-z]+', text)
                if surname is not None:
                    surname = surname.group(0)
                    surname = surname.upper()
                    if row["fio"].find(surname) != -1:
                        row_number = i
                        ok = True
                        break
            print(row_number)


        shift = 2
        if ok:
            ok = True
            if id_point > 1:
                id_element = "ctl00_ContentPlaceHolder1_ASPxGridView1_cell%d_%d_TextBox1" % (row_number, 2 + (id_point - 1) * 3 + shift)
                el = soup.find(id=id_element)
                try:
                    old_value = int(el['value'])
                    if row["curr_point"] < old_value:
                        ok = False
                except:
                    ok = True

            if ok:
                id_element = "ctl00_ContentPlaceHolder1_ASPxGridView1_cell%d_%d_TextBox1" % (row_number, 2+id_point*3 + shift)
                web.page().runJavaScript('document.getElementById("%s").value="%d";' % (id_element, row["curr_point"]))
            else:
                print("Ошибка! Рейтинг меньше предыдушего")
            id_element = "ctl00_ContentPlaceHolder1_ASPxGridView1_cell%d_%d_TextBox1" % (row_number, 3+id_point*3 + shift)
            web.page().runJavaScript('document.getElementById("%s").value="%d";' % (id_element, row["absence_count"]))
        else:
            print("Ошибка! Фамилии не совпадают: %d %s" % (row["id"], row["fio"]))

    id_element = "ctl00_ContentPlaceHolder1_ASPxGridView1_cell%d_%d_TextBox1" % (0, 2 + id_point * 3 + shift)
    web.page().runJavaScript('document.getElementById("%s").value="%d";' % (id_element, max_point))


