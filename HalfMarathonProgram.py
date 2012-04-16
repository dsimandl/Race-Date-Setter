from BeautifulSoup import BeautifulSoup

class HalfMarathonProgram():
    
    def __init__(self, page):
        self.page = page
        self.days_list = ['Sunday', 'Saturday', 'Friday' ,'Thursday',
                'Wednesday', 'Tuesday', 'Monday']
        self.fonttaglist = []
        self.week_dic_list = []

    def get_half_marathon_program(self):
        soup = BeautifulSoup(self.page)
        tables = soup.findAll('table')
        allfonttags = tables[2].findAll('font')
        blocktags = tables[2].findAll('blockquote')
        del allfonttags[0:7]
        for place, fonttag in enumerate(reversed(allfonttags)):
            fonttagtext = fonttag.contents[0].string
            if (place == 0 or place == 1):
                pass
            elif fonttagtext.find('Week'):
                if fonttagtext == 'off':
                    pass
                elif fonttagtext == 'WO1':
                    fonttagtext = "Run " + fonttagtext + blocktags[0].contents[1]
                elif fonttagtext == 'WO2':
                    fonttagtext = "Run " + fonttagtext + blocktags[0].contents[4]
                elif (fonttagtext == 'WO3') or (fonttagtext == 'WO5') or (fonttagtext == 'WO8'):
                    fonttagtext = "Run " + fonttagtext + blocktags[0].contents[7]
                elif fonttagtext == 'WO4':
                    fonttagtext = "Run " + fonttagtext + blocktags[0].contents[10]
                elif (fonttagtext == 'WO6') or (fonttagtext == 'WO9'):
                    fonttagtext = "Run " + fonttagtext + blocktags[0].contents[13]
                elif fonttagtext == 'WO7':
                    fonttagtext = "Run " + fonttagtext + blocktags[0].contents[16]
                elif fonttagtext == 'WO10':
                    fonttagtext = "Run " + fonttagtext + blocktags[0].contents[19]
                elif fonttagtext == 'AT1':
                    fonttagtext = "Run " + fonttagtext + blocktags[1].contents[1]
                elif fonttagtext == 'AT2':
                    fonttagtext = "Run " + fonttagtext + blocktags[1].contents[4]
                elif (fonttagtext == 'AT3') or (fonttagtext == 'AT5') or (fonttagtext == 'AT9'):
                    fonttagtext = "Run " + fonttagtext + blocktags[1].contents[7]
                elif (fonttagtext == 'AT4') or (fonttagtext == 'AT7'):
                    fonttagtext = "Run " + fonttagtext + blocktags[1].contents[10]
                elif fonttagtext == 'AT6':
                    fonttagtext = "Run " + fonttagtext + blocktags[1].contents[12]
                elif fonttagtext == 'AT8':
                    fonttagtext = "Run " + fonttagtext + blocktags[1].contents[15]
                else:
                    fonttagtext = "Run " + fonttagtext 
                self.fonttaglist.append(fonttagtext)
                if len(self.fonttaglist) == 7:
                    week_dic = dict(zip(self.days_list, self.fonttaglist))
                    self.week_dic_list.append(week_dic)
                    self.fonttaglist = []

        return self.week_dic_list



