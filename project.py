# 오늘날 전염성 변수는 실제로 임의적이나, 개인 건강 상태에 따라 달라 질 수 있지만, 기본적인 시뮬레이션을 위해 랜덤으로 설정x
# TODO : 무증상자 비율

# 자연 면역 비율, 나이, 마스크,
# 10세 이하는 제외
from scipy.stats import norm
import random
import time
import sys

peopleDictionary = []


# simulation of a single person
class Person():
    def __init__(self, startingImmunity):
        if random.randint(0, 100) < startingImmunity:   # TODO : sir_info로 바꾸고 intensity 도 넣는다.
            self.immunity = True
        else:
            self.immunity = False
        self.contagiousness = 0  # 전염성
        # self.mask = False
        self.contagiousDay = 0  # 감염된 후 지난 시간

        self.sir_info = 0  # 취약자 : 0, 감염자 : 1, 회복자 : 2

        # self.asymptomatic = False  # 무증상자
        # self.super = False  # 슈퍼 감염 환자
        self.intensity = 0  # 0: 무증상자, 1: 일반 증상자, 2: 슈퍼 감염 환자

        # teen bool
        if random.random() <= 0.098784778:  # if teen -> go classroom at weekday. 5/7
            self.teen = True
        else:                               # else -> go office at weekday 5/7
            self.teen = False

        self.placeToday = 3     # 0: office, 1: classroom, 2: reception, 3: home
        #self.mask = 0   # 0, 1, 2이면
    #def wearMask(self):  # 전염력을 반으로 줄임
        #self.contagiousness /= 2

    def infection(self):  # 감염 걸렸을 때 무증상 여부 판단
        temp = random.randint(0, 100)
        if temp <= 21:  # 21%가 무증상자
            self.asymptomatic = True
        elif temp <= 31:  # 10%가 슈퍼 감염 환자
            self.super = True

def type(type_scenario):
    # 위험도 리스트를 [무증상자, 증상자, 슈퍼 감염자] 로 나타냄.
    if type_scenario == 65:     # A
        risk = [[0, 47, 100], [0, 92, 100], [0, 100, 100], [0, 0, 0]]

    elif type_scenario == 66:   # B
        risk = [[0, 20, 90], [0, 60, 100], [0, 80, 100], [0, 0, 0]]

    elif type_scenario == 67:   # C
        risk = [[0, 6.6, 50], [0, 24, 94], [0, 38, 99], [0, 0, 0]]

    elif type_scenario == 68:   # D
        risk = [[0, 1.1, 11], [0, 4.5, 37], [0, 7.6, 55], [0, 0, 0]]

    elif type_scenario == 69:   # E
        risk = [[0, 6.0, 46], [0, 22, 91], [0, 35, 99], [0, 0, 0]]

    else:
        sys.exit("Error : input between A~E")

    # 무증상자 1/3 확률 추가
    for i in range(len(risk)):
        risk[i][0] = risk[i][1] / 3

    return risk



def initiateSim():  # 시뮬레이션을 시작하는  함수
    numPeople = int(input("Population: "))  # 인구
    startingImmunity = int(input("자연 면역을 가진 사람의 비율: "))
    startingInfecters = int(input("t=0 일때 전염된 사람: "))
    for x in range(0, numPeople):  # 인구수만큼의 사람 생성
        peopleDictionary.append(Person(startingImmunity))
    for x in range(0, startingInfecters):  # 생성된 인구수에서 0일째 감염된 사람을 랜덤으로 지정함.
        peopleDictionary[random.randint(0, len(peopleDictionary) - 1)].contagiousness = int(
            (norm.rvs(size=1, loc=0.5, scale=0.15)[0] * 10).round(0) * 10)
    daysContagious = int(input("How many days contagious: "))  # 전염성이 있는 날짜(?) -> 전염 가능한 일수(?)
    lockdownDay = int(input("Lockdown(봉쇄) 시행일: "))
    maskDay = int(input("Day for masks to be used: "))  # 마스크 사용 시작일
    type_scenario = ord(input("A~E 시나리오 선택: ").split()[0])  # 시나리오 A~E 설정
    risk = type(type_scenario)
    return daysContagious, lockdownDay, maskDay, risk


def runDay(daysContagious): # TODO: infection 함수 사용!!!!!!!!!!!!!
    # TODO : 개인마다 이벤트를 줌. 어디로 갈 것 인지
    cnt = [0,0,0]
    # 모든 사람이 어디로 가는지 설정(이때, 가정, office, classroom, reception 는 모두 하나의 장소만 존재)

    place_patient = [0,0,0,0]   # 확진자가 있는 곳 체크

    # TODO : 날짜 카운트 해서 평일은 이렇게(평일에는 제택 근무 여부도 추가) 하고 주말에는 이렇게 하고
    # peopleDictionary 에 존재하는 사람들에 대해서 돌림
    for x in peopleDictionary:
        place = 0   # 0: office, 1: classroom, 2: reception, 3: home
        if random.random() <= 5/7:  # go office or school
            if x.teen:
                place = 1
            else:
                place = 0
        elif random.random() <= 0.7:    # 사람들이 office 나 school 을 안가고 0.6 확률로 집에 있음.
            place = 3
        else:
            place = 2

        x.placeToday = place
        if x.sir_info == 1: # 확진자인 경우 place_patient 에 어디로 갔는지 카운트
            place_patient[place] += 1
            x.contagiousDay += 1
            if x.contagiousness > daysContagious:
                x.immunity = True
                x.contagiousness = 0
                print("|||", peopleDictionary.index(x),"|||")
        cnt[x.sir_info] += 1

    # TODO 논리 오류 해결 필요; 같은 장소에 확진자가 얼마나 많든 상관 없는 상태, 즉 가중치를 만들어주어야함.

    # person : 개인 한명을 의미함
    # 취약자들 중에서만 경우를 생각해보자!
    for person in [person for person in peopleDictionary if place_patient[person.placeToday] >= 1 and person.sir_info == 0]:
        if random.random() <= (risk[person.placeToday][person.sir_info] / 100):
            person.sir_info = 1

    return cnt
    # this section simulates the spread, so it only operates on contagious people, thus:

    '''
    for person in [person for person in peopleDictionary if person.contagiousness > 0 and person.friends > 0]:
        peopleCouldMeetToday = int(person.friends / 2)  # 하루에 만날 수 있는 친구 수는 최대값이 절반
        if peopleCouldMeetToday > 0:
            peopleMetToday = random.randint(0, peopleCouldMeetToday)
        else:
            peopleMetToday = 0

        if lockdown == True:
            peopleMetToday = 0

        for x in range(0, peopleMetToday):  # peopleDictionary 에서 만날 사람을 선택함.
            friendInQuestion = peopleDictionary[random.randint(0, len(peopleDictionary)-1)]
            if random.randint(0, 100) < person.contagiousness and friendInQuestion.contagiousness == 0 and friendInQuestion.immunity == False :
                friendInQuestion.contagiousness = int((norm.rvs(size = 1, loc=0.5, scale=0.15)[0] * 10).round(0) * 10)
                print(peopleDictionary.index(person), ">>>", peopleDictionary.index(friendInQuestion))
    for person in [person for person in peopleDictionary if person.contagiousness > 0]:
        person.contagiousness += 1
        if person.contagiousness > daysContagious:
            person.immunity = True
            person.contagiousness = 0
            print("|||", peopleDictionary.index(person), "|||")
    '''

# TODO: txt 파일 생성 법
# main 함수
lockdown = False
daysContagious, lockdownDay, maskDay, risk = initiateSim()  # initializing
#saveFile = open("pandemicsave.txt", "a")  # file open

for x in range(0, 100):  # 100일까지 순환하는 것을 의미
    if x == lockdownDay:
        lockdown = True

    if x == maskDay:
        for person in peopleDictionary:
            person.wearMask()

    cnt_sir = runDay(daysContagious)
    print("DAY ", x, "    ", cnt_sir)
    # write = str(len([person for person in peopleDictionary if person.contagiousness > 0])) + "\n"
    # saveFile.write(write)
    # print(len([person for person in peopleDictionary if person.contagiousness > 0]),
    #      " people are contagious on this day.")

#saveFile.close()
