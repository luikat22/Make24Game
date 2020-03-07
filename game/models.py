from django.db import models
from mysql.connector import Error
import pymysql
from random import randint


class Questionbank(models.Model):
    questionnumber = models.IntegerField(db_column='questionNumber', primary_key=True)
    difficulty = models.IntegerField(blank=True, null=True)
    piece1 = models.IntegerField(blank=True, null=True)
    piece2 = models.IntegerField(blank=True, null=True)
    piece3 = models.IntegerField(blank=True, null=True)
    piece4 = models.IntegerField(blank=True, null=True)
    accuracy = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    frequency = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'QuestionBank'


# Select a question set from database based on the parameter(index); return a question set with 4 pieces of integer.
def select_question(difficulty):
    difficulty += 1
    try:
        conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='Glay@0525', db='make24_db')
        # conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='kat199722', db='make24_db')
        cur = conn.cursor()

        # select question set according to the input difficulty
        level = randint(1, 10)
        if difficulty == 1:
            if level >= 8:
                difficulty += 1
        elif difficulty == 2:
            if level > 8:
                difficulty += 1
            elif level <= 2:
                difficulty -= 1
        else:
            if level > 8:
                difficulty -= 2
            elif level > 6:
                difficulty -= 1


        while True:
            questionNumber = randint(1, 1362)
            cur.execute("""select difficulty from QuestionBank where questionNumber = %s;""", questionNumber,)
            difficult = cur.fetchone()

            if difficult[0] == difficulty:
                cur.execute("""select piece1,piece2,piece3,piece4 from QuestionBank where questionNumber = %s;""",
                            questionNumber,)
                question = cur.fetchone()
                cur.execute("""select accuracy from QuestionBank where questionNumber = %s;""", questionNumber, )
                accuracy = cur.fetchone()
                accuracy = int(accuracy[0])
                break

        # update the frequency of question set
        cur.execute("UPDATE QuestionBank SET frequency = frequency + 1 WHERE questionNumber = %s;", questionNumber,)
        conn.commit()

    except Error as error:
        print("Failed to connect to database: {}".format(error))
        conn.rollback()

    finally:
        # closing database connection.
        cur.close()
        conn.close()

    return question, accuracy

