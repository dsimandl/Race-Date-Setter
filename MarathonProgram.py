from BeautifulSoup import BeautifulSoup

class MarathonProgram():

    def __init__(self, page):
        self.page = page
        self.days_list = ['Sunday', 'Saturday', 'Friday' ,'Thursday',
                'Wednesday', 'Tuesday', 'Monday']
        self.fonttaglist = []
        self.week_dic_list = []

    def get_marathon_program(self):
        soup = BeautifulSoup(self.page)
        tables = soup.findAll('table')
        allptags = tables[2].findAll('p')
        allfonttags = tables[2].findAll('font')
        del allptags[0]
        del allptags[95:]

        del allfonttags[0:103]
        del allfonttags[98:120]
        del allfonttags[100]
        del allfonttags[101:103]
        del allfonttags[102]

        del allptags[193:]

        allptags.extend(allfonttags)

        instructions = allptags[193:]
        del allptags[193:]

        for place, ptag in enumerate(reversed(allptags)):
            if len(ptag.contents) == 3:
                runtext = 'run ' + ptag.contents[0][3] + " in the morning " + ptag.contents[2][3] + " in the evening "
                self.fonttaglist.append(runtext)
            elif len(ptag.contents) == 0:
                pass
            elif (ptag.font != None) or (ptag.contents[0].string.find('Week') != -1):
                pass
            elif ptag.contents[0].string == "Phase II":
                pass
            elif ptag.a != None:
                if (ptag.a.string == 'AT1') or (ptag.a.string == 'AT5'):
                    runtext = 'run ' + instructions[0].contents[0].string + instructions[0].contents[1]                     
                    self.fonttaglist.append(runtext)
                elif (ptag.a.string == 'AT2') or (ptag.a.string == 'AT3') or (ptag.a.string == 'AT4'):
                    runtext = 'run ' + instructions[1].contents[0].string + instructions[1].contents[1]
                    self.fonttaglist.append(runtext)
                elif ptag.a.string == 'Race1':
                    runtext = 'run ' + instructions[2].contents[0]
                    self.fonttaglist.append(runtext)
                elif ptag.a.string == 'Race2':
                    runtext = 'run ' + instructions[2].contents[2]
                    self.fonttaglist.append(runtext)
                elif ptag.a.string == 'Race3':
                    runtext = 'run ' + instructions[2].contents[4]
                    self.fonttaglist.append(runtext)
                elif ptag.a.string.find('hills') != -1:
                    runtext = 'run ' + instructions[3].contents[0].string + instructions[3].contents[1]
                    self.fonttaglist.append(runtext)
                elif ptag.a.string == 'WO1':
                    runtext = 'run ' + instructions[4].contents[0].string + instructions[4].contents[1]
                    self.fonttaglist.append(runtext)
                elif (ptag.a.string == 'WO2') or (ptag.a.string == 'WO4') or (ptag.a.string == 'WO6'):
                    runtext = 'run ' + ptag.a.string + " " + instructions[4].contents[4]
                    self.fonttaglist.append(runtext)
                elif (ptag.a.string == 'WO3') or (ptag.a.string == 'WO8'):
                    runtext = 'run ' + ptag.a.string + " " + instructions[4].contents[7]
                    self.fonttaglist.append(runtext)
                elif (ptag.a.string == 'WO5'):
                    runtext = 'run ' + ptag.a.string + " " + instructions[4].contents[10]
                    self.fonttaglist.append(runtext)
                elif (ptag.a.string == 'WO7'):
                    runtext = 'run ' + ptag.a.string + " " + instructions[4].contents[13]
                    self.fonttaglist.append(runtext)
                elif (ptag.a.string == 'WO9'):
                    runtext = 'run ' + ptag.a.string + " " + instructions[4].contents[16]
                    self.fonttaglist.append(runtext)
            elif ptag.contents[0].string == 'off':
                runtext = ptag.contents[0].string
                self.fonttaglist.append(runtext)
            else:
                runtext = 'run ' + ptag.contents[0].string
                self.fonttaglist.append(runtext)
            if len(self.fonttaglist) == 7:
                week_dic = dict(zip(self.days_list, self.fonttaglist))
                self.week_dic_list.append(week_dic)
                self.fonttaglist = []
        return self.week_dic_list

