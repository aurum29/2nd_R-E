# 오늘날 전염성 변수는 실제로 임의적이나, 개인 건강 상태에 따라 달라 질 수 있지만, 기본적인 시뮬레이션을 위해 랜덤으로 설정x
# 10세 이하는 제외

# TODO : 무증상자 비율
# TODO : 날짜 추가
# TODO : Ending day 와 MAX day 추가
# TODO : 파티랑 집에 있는 확률
from scipy.stats import norm
import random
import time
import sys
from matplotlib import pyplot as plt
import numpy as np

peopleDictionary = []
Day_of_week = 0  # 0 : 월요일, 1 : 화요일 ~~ 5 : 토요일, 6 : 일요일

a = np.exp(1.9) / 17
b = -0.9


def recovered_function(day):
    if day < 3:
        return 0
    elif 3 <= day <= 20:
        return np.exp(a * (day - 3)) + b
    else:
        return 1


# simulation of a single person
class Person:
    def __init__(self):
        self.sir_info = 0  # 취약자 : 0, 감염자 : 1, 회복자 : 2
        self.intensity = 0  # 0: 무증상자, 1: 일반 증상자, 2: 슈퍼 감염 환자
        self.contagiousDays = 0
        # teen bool
        if random.random() <= 0.098784778:  # if teen -> go classroom at weekday.
            self.teen = True
        else:  # else -> go office at weekday 5/7
            self.teen = False

        self.placeToday = 3  # 0: office, 1: classroom, 2: reception, 3: home

    def infection(self):  # 감염 걸렸을 때 무증상 여부 판단
        temp = random.randint(0, 100)
        if temp <= 21:  # 21%가 무증상자
            self.intensity = 0
        elif temp <= 31:  # 10%가 슈퍼 감염 환자
            self.intensity = 2


def type(type_scenario):
    # 위험도 리스트를 [무증상자, 증상자, 슈퍼 감염자] 로 나타냄.
    if type_scenario == 65:  # A
        risk = [[0, 47, 100], [0, 92, 100], [0, 100, 100], [0, 0, 0]]

    elif type_scenario == 66:  # B
        risk = [[0, 20, 90], [0, 60, 100], [0, 80, 100], [0, 0, 0]]

    elif type_scenario == 67:  # C
        risk = [[0, 6.6, 50], [0, 24, 94], [0, 38, 99], [0, 0, 0]]

    elif type_scenario == 68:  # D
        risk = [[0, 1.1, 11], [0, 4.5, 37], [0, 7.6, 55], [0, 0, 0]]

    elif type_scenario == 69:  # E
        risk = [[0, 6.0, 46], [0, 22, 91], [0, 35, 99], [0, 0, 0]]

    else:
        sys.exit("Error : input between A~E")

    # 무증상자 1/3 확률 추가
    for i in range(len(risk)):
        risk[i][0] = risk[i][1] / 3

    return risk


def initiateSim():  # 시뮬레이션을 시작하는  함수
    numPeople = int(input("Population: "))  # 인구
    startingInfecters = int(input("t=0 일때 전염된 사람: "))
    home = float(input("주말에 집에 있을 확률(0~1): "))
    for x in range(0, numPeople):  # 인구수만큼의 사람 생성
        peopleDictionary.append(Person())
    for x in range(0, startingInfecters):  # 생성된 인구수에서 0일째 감염된 사람을 랜덤으로 지정함.
        random_ = random.randint(0, len(peopleDictionary) - 1)
        if peopleDictionary[random_].sir_info == 0:
            peopleDictionary[random_].sir_info = 1
        else:
            x -= 1

    type_scenario = ord(input("A~E 시나리오 선택: ").split()[0])  # 시나리오 A~E 설정
    risk = type(type_scenario)
    return risk, home


def runDay(DOW, home):
    # 개인마다 이벤트를 줌. 어디로 갈 것 인지
    cnt = [0, 0, 0]  # sir 개수를 카운트
    # 모든 사람이 어디로 가는지 설정(이때, 가정, office, classroom, reception 는 모두 하나의 장소만 존재)

    place_patient = [0, 0, 0, 0]  # 확진자가 있는 곳 체크

    # peopleDictionary 에 존재하는 사람들에 대해서 돌림
    for x in peopleDictionary:
        place = 0  # 0: office, 1: classroom, 2: reception, 3: home
        if 0 <= DOW <= 4:  # go office or school in MON-FRI
            if x.teen:
                place = 1
            else:
                place = 0
        elif random.random() <= home:  # 사람들이 office 나 school 을 안가고 0.7 확률로 집에 있음.
            place = 3
        else:
            place = 2

        x.placeToday = place
        if x.sir_info == 1:  # 확진자인 경우 place_patient 에 어디로 갔는지 카운트
            place_patient[place] += 1
            x.contagiousDays += 1
            if random.random() <= recovered_function(x.contagiousDays):  # 회복
                x.sir_info = 2

        cnt[x.sir_info] += 1
    # TODO : 논리 오류 해결 필요; 같은 장소에 확진자가 얼마나 많든 상관 없는 상태, 즉 가중치를 만들어주어야함.

    # 취약자들 중에서만 경우를 생각해보자!
    for person in [person for person in peopleDictionary if
                   place_patient[person.placeToday] >= 1 and person.sir_info == 0]:
        if random.random() <= (risk[person.placeToday][person.intensity] / 100):
            person.sir_info = 1
            person.infection()
            cnt[x.sir_info] += 1
            cnt[0] -= 1

    # 요일 카운트
    DOW += 1
    if DOW == 7: DOW = 0
    return cnt, DOW


# main 함수
risk, home = initiateSim()  # initializing
S = []
I = []
R = []
x = 0
max_day = 0
while True:
    cnt_sir, Day_of_week = runDay(Day_of_week, home)
    print("DAY ", x, "    ", cnt_sir)
    S.append(cnt_sir[0])
    I.append(cnt_sir[1])
    R.append(cnt_sir[2])

    if cnt_sir[1] == 0: break  # 확진자가 0일 때 시뮬레이션 break
    if I[max_day] < I[x]: max_day = x

    x += 1

print('\n', max_day, I[max_day])
print('End day:', len(S))
plt.plot(range(0, len(S)), S, 'r', label='S')
plt.plot(range(0, len(I)), I, 'b', label='I')
plt.plot(range(0, len(R)), R, 'g', label='R')
plt.scatter(max_day, I[max_day], c='b', label='max of infection', marker='D')
plt.legend()
plt.xticks(range(0, len(S), 7))
plt.xlabel('Time')
plt.ylabel('Number of Person')
plt.grid()
plt.show()
