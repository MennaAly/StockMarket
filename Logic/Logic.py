

class logic():
    def collectColoumnData(self,data):
        coloumn = ''
        for idx,element in enumerate(data):
            if idx != len(data)-1:
                 coloumn = coloumn + element + ','
            else :
                coloumn = coloumn + element
        return coloumn


    def seperateColumnData(self,coloumn):
        return coloumn.split(',')

