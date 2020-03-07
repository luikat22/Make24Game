from . import models
from player.models import Player
from scoreboard.models import Scoreboard
from django.contrib.auth.models import User
from random import randint
import datetime

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from mysql.connector import Error
import pymysql

difficulty = 0

@login_required(login_url='/player/login/')
def index(request):
    return render(request, 'make24.html')

def instr(request):
    return render(request, 'how_to_play.html')

def select_difficulty(request):
    if request.method == 'GET':
        # const falling time
        time = [2000, 1500, 1000]
        
        # return time interval
        level = int(request.GET.get('difficulty'))
        global difficulty
        difficulty = level
        data = {
            'time': time[level]
        }
        return JsonResponse(data)


def create_question(request):
    if request.method == 'GET':
        # base time/score based on difficulty
        base_time = int(request.GET.get('time'))
        base_score = [50, 100, 150]
        
        # get question from database
        question_set, accuracy = models.select_question(difficulty)
        
        offset = 0
        if accuracy >= 80:
            offset = 0
        elif accuracy >= 50:
            offset = accuracy
        else:
            offset = (100 - accuracy) * 3
        
        timeout = base_time * 10 + offset * 100
        score = base_score[difficulty % 3] + offset

        # return question set and falling time
        data = {
            'set': question_set,
            'time': timeout,
            'score': score
        }
        return JsonResponse(data)


def update_score_to_db(request):
    score = 0
    correct = 0
    question = 0
    if request.method == 'GET':
        score = int(request.GET.get('score'))
        correct = int(request.GET.get('correct'))
        question = int(request.GET.get('question'))
        
    date_time = datetime.datetime.now().strftime("%d%m%y%H%M")
    Scoreboard.objects.create(playername=request.user.username, difficulty=difficulty+1, score=score, date=date_time)

    data = {
        'status': 'success'
    }

    try:
        player = Player.objects.get(user_id=request.user.id)
        # update score
        if score > player.highestscore:
            Player.objects.filter(user_id=request.user.id).update(highestscore=score)
        Player.objects.filter(user_id=request.user.id).update(recentscore=score)
        # update accuracy
        clearedQuestion = player.clearedQuestion + correct
        totalQuestion = player.totalQuestion + question
        accuracy = float(clearedQuestion / totalQuestion) * 100
        Player.objects.filter(user_id=request.user.id).update(accuracy=accuracy)
        Player.objects.filter(user_id=request.user.id).update(clearedQuestion=clearedQuestion)
        Player.objects.filter(user_id=request.user.id).update(totalQuestion=totalQuestion)

    except Player.DoesNotExist:
        Player.objects.create(user_id=request.user.id, highestscore=score, recentscore=score)
            
    return JsonResponse(data)

# Get highest score of the user
def get_highest_score(request):
    bestscore = 0;
    try:
        conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='Glay@0525', db='make24_db')
        # conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='kat199722', db='make24_db')
        cur = conn.cursor()

        # get score record
        cur.execute("Select score From ScoreBoard WHERE score=(select max(score) from ScoreBoard where playerName = %s)"
                    , request.user.username,)
        highest_score = cur.fetchone()
        bestscore = highest_score[0]

    except Error as error:
        print("Failed to connect to database: {}".format(error))
        conn.rollback()

    finally:
        # closing database connection.
        cur.close()
        conn.close()

        data = {
            'score': bestscore
        }
        return JsonResponse(data)
