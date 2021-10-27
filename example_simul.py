from scipy.stats import norm
import random
import time

peopleDictionary = []


# 질병에 대한 면역력 : 1%

# simulation of a single person
class Person ():
    def __init__(self, startingImmunity):  # 몇 퍼센트가 첫째 날 부터 자연 면역을 가질 것인지 의미함.
        if random.randint(0, 100) < startingImmunity:
            self.immunity = True
        else:
            self.immunity = False
        self.contagiousness = 0 # 전염력
        self.mask = False
        self.contagiousDays = 0  # 감염된 후 지난 시간
        # use gaussian distribution for number of friends; average is 5 friends
        self.friends = int((norm.rvs(size=1, loc=0.5, scale=0.15)[0] * 10).round(0))

    def wearMask(self): # 전염력을 반으로 줄임
        self.contagiousness /= 2


def initiateSim():  # 시뮬레이션을 시작하는 함수
    numPeople = int(input("Population: "))  # 인구
    startingImmunity = int(input("Percentage of people with natural immunity: "))  # 자연 면역을 가진 사람의 비율
    startingInfecters = int(input("How many people will be infectious at t=0: "))  # 0일째 전염된 사람
    for x in range(0, numPeople):  # 인구수만큼의 생성함
        peopleDictionary.append(Person(startingImmunity))
    for x in range(0, startingInfecters):  # 생성된 인구수에서 0일째 감염된 사람을 랜덤으로 지정함.
        peopleDictionary[random.randint(0, len(peopleDictionary) - 1)].contagiousness = int(
            (norm.rvs(size=1, loc=0.5, scale=0.15)[0] * 10).round(0) * 10)  # 정규 분포
    daysContagious = int(input("How many days contagious: "))  # 전염성이 있는 날짜(?) -> 전염 가능한 일수(?)
    lockdownDay = int(input("Day for lockdown to be enforced: "))  # Lockdown(봉쇄) 시행일
    maskDay = int(input("Day for masks to be used: "))  # 마스크 사용 시작일
    return daysContagious, lockdownDay, maskDay


''' 오늘날 전염성 변수는 실제로 임의적이거나, 개인 건강 상태에 따라 달라 질 수 있지만, 기본 시뮬레이션을 위해 랜덤으로 설정x'''


def runDay(daysContagious, lockdown):
    # this section simulates the spread, so it only operates on contagious people, thus:
    # 이 섹션은 확산을 시뮬레이션하여 전염성 있는 사람들에게만 작동한다.
    for person in [person for person in peopleDictionary if person.contagiousness > 0 and person.friends > 0]:
        peopleCouldMeetToday = int(person.friends / 2)  # 하루에 만날 수 있는 친구의 수는 최대값의 절반이다.
        if peopleCouldMeetToday > 0:
            peopleMetToday = random.randint(0, peopleCouldMeetToday)
        else:
            peopleMetToday = 0

        if lockdown == True:
            peopleMetToday = 0

        for x in range(0, peopleMetToday):  # peopleDictionary 에서 만날 사람을 선택함.
            friendInQuestion = peopleDictionary[random.randint(0, len(peopleDictionary) - 1)]
            if random.randint(0,
                              100) < person.contagiousness and friendInQuestion.contagiousness == 0 and friendInQuestion.immunity == False:
                friendInQuestion.contagiousness = int((norm.rvs(size=1, loc=0.5, scale=0.15)[0] * 10).round(0) * 10)
                print(peopleDictionary.index(person), " >>> ", peopleDictionary.index(friendInQuestion))
    for person in [person for person in peopleDictionary if person.contagiousness > 0]:
        person.contagiousDays += 1
        if person.contagiousDays > daysContagious:
            person.immunity = True
            person.contagiousness = 0
            print("|||", peopleDictionary.index(person), " |||")


lockdown = False
daysContagious, lockdownDay, maskDay = initiateSim()
saveFile = open("pandemicsave3.txt", "a")
for x in range(0, 100): # 100일까지 순환하는 것을 의미
    if x == lockdownDay:
        lockdown = True

    if x == maskDay:
        for person in peopleDictionary:
            person.wearMask()

    print("DAY ", x)
    runDay(daysContagious, lockdown)
    write = str(len([person for person in peopleDictionary if person.contagiousness > 0])) + "\n"
    saveFile.write(write)
    print(len([person for person in peopleDictionary if person.contagiousness > 0]),
          " people are contagious on this day.")
saveFile.close()