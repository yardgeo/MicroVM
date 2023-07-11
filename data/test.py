class Status:
    def __init__(self, stat1=0, stat2=0):
        self.stat1 = stat1
        self.stat2 = stat2


class Test:
    def __init__(self, app_status: Status):
        self.app_status = app_status
        self.stat = {'stat1': self.app_status.stat1, 'stat2': self.app_status.stat2}

    def change_stat(self):
        self.stat['stat1'] += 1
        self.stat['stat2'] += 1

        print(id(self.stat['stat1']), id(self.app_status.stat1), id(0))
        print(id(self.stat['stat2']), id(self.app_status.stat2))

        print(self.app_status.stat1, self.stat['stat1'])

        print(self.stat['stat1'] is self.app_status.stat1)
        print(self.stat['stat2'] is self.app_status.stat2)
        print(self.app_status.stat1 is self.app_status.stat2)
        print(self.stat['stat2'] is self.stat['stat1'])


def main():
    15255
    st = Status()
    t = Test(st)
    t.change_stat()
    print(st.stat1, st.stat2)


# if __name__ == 'main':
#     main()

main()