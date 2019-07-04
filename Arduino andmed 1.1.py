'''See Pythoni programm on loodud Arduino poolt kogutud andmete vastuvõtmiseks, töötlemiseks,
graafiliselt esitamiseks ja faili salvestamiseks. Võite seda muuta kuidas tahate.
Kasutamine :
1. Ühendage saatmisprogrammiga Arduino arvutiga.
2. Käivitage Pythoni programm. Programm peaks automaatselt tuvastama Arduino. Mõnikord see ei toimi.
   Sel juhul saate veateate. Tõmmake Arduino ühendus välja, pange uuesti sisse ja käivitage uuesti
   Pythoni programm.
3. Kui ühendus on loodud, käivitub andmete vastuvõtmine ja neist graafikute tegemine kohe,
   kui Arduino saadab teate "alustan".
4. Kui Arduino saadab teate "0,0,0" lõppeb andmete vastuvõtt. Programm küsib, kas andmed salvestada.
   Jaatava vastuse korral küsitakse, millise nime all info salvestada ja salvestatakse faili "andmed.txt"
5. Kui Arduino saadab uuesti teate "alustan", alustatakse uut mõõtmist.
Programmi ei saa sulgeda graafikute akent kinni pannes.

Infot matplotlib'i kohta: https://www.youtube.com/watch?v=q7Bo_J8x_dw&list=PLQVvvaa0QuDfefDfXb9Yf0la1fPDKluPF
                          https://matplotlib.org/
Matplotlib Arduinoga: https://www.youtube.com/watch?v=zH0MGNJbenc&t=354s'''



# Lisa kõik programmi toimimiseks vajalikud teegid.
import serial                        # Arduinoga ühenduse loomiseks vajalik teek.
import matplotlib.pyplot as plt      # Graafikute loomise teek.
from drawnow import *                # Graafikule pidevalt uute andmete lisamiseks vajalik teek.
import atexit
import time                          # Aja mõõtmiseks vajalik teek.
from easygui import*                 # Graafilise kasutajaliidese teek.

# Deklareeri globaalsed muutujad.
väärtusedB = []
väärtusedC = []
cnt = 0
x = []
aeg = [0]
com = 0
asukoht = []
algus = 0
# Loend xkcd värve mida saab graafikutel kasutada.
värvid = ['#e50000','#ff3800','#f97306','#f5bf03','#ffff14','#bcff00','#7eff00','#3dff00','#00ff39','#00ff7e','#00ffbf','#00ffff','#00c2ff','#007eff','#003fff','#0000ff']

plt.ion()# Lülita matplotlibi interaktiivne režiim sisse.

# Funktsioon arduino saadetud andmete vastuvõtmise ja dekodeerimise jaoks.
def arduinoLugemine():
    # Deklareeri lokaalsed muutujad loetavate andmete jaoks.
    a = 0
    b = 0
    c = 0
    # Kuni uusi andmeid pole jätka kontrollimist, kas midagi on saabunud.
    while (serialArduino.inWaiting()==0):
        pass
    
    valueRead = serialArduino.readline(500)# Loe andmed ja salvesta muutujasse valueRead.

    
    try:
        
        a,b,c = valueRead.decode().split(",")# Alusta andmete dekodeerimist ja salvesta need muutujatesse a, b ja c.
        # Lõppuni dekodeerimine.
        a = int(a)
        b = int(b)# Aeg, mis kulus mootoril poole pöörde tegemiseks.
        c = int(c)# Pinge näit ADS1115-elt töötlematta kujul.
        
        if b <= 5000024 and c <= 1000024 :# Kontrolli, et suurus ei ületaks ette antud piiri.
            if b >= 0 and c > 0 :# Kontrolli, et suurus ei oleks alla ette antud piiri.
                # Arvuta välja ning lisa uued näidud andmete järjenditesse.
                väärtusedB.append(30000000 / b)# Kiirus pööretes minutis.
                väärtusedC.append((c * 0.1875)/1000)# Pinge voltides.
                x.append(round((time.time() - algus)/60,6))# Aeg mõõtmise alustamisest minutites.
                
                drawnow(plotValues)# Uuenda andmeid graafikul
            else:
                print("Viga! Liiga madal number")# Veateade liiga madala näidu korral.
        else:
            print("Viga! Liiga suur number")# Veateade liiga suure näidu korral.
    except ValueError:
        print("Viga vastuvõtmisel")# Veateade näidu dekodeerimise ebaõnnestumise korral.
        
    if b < 3740000 :# Kui mootor on endiselt piisavalt kiire.
        arduinoLugemine()# Mine tagasi funksiooni algusesse.
    elif a == 0 :# Kontrolli, kas arduino on saatnud teate nupuvajutusest.
        msgbox("Mõõtmine katkestatud")# Teata, et mõõtmine on katkestatud.
        plt.close()# Sulge graafik.
    else :
        menüü()# Käivita funktsioon menüü.
        
    
# Funktsioon graafikute välimuse määramiseks.
def setPlotLook(ax1, ax2):
    
    # X ja y telje ulatuste määramine
    ax1.axis([0, 20, 0, 300])# Kiiruse graafik.
    ax2.axis([0, 20, 0, 3])# Pinge graafik.
    
    # Graafikutele võrgustiku lisamine.
    ax1.grid(True)
    ax2.grid(True)
    
    # Graafikute x-telgede joonte vahede määramine.
    ax1.xaxis.set_major_locator(plt.MultipleLocator(1))
    ax2.xaxis.set_major_locator(plt.MultipleLocator(1))
    # Graafikute y-telgede joonte vahede määramine.
    ax1.yaxis.set_major_locator(plt.MultipleLocator(50))
    ax2.yaxis.set_major_locator(plt.MultipleLocator(1))
    
    ax1.set_ylabel('Kiirus(rpm)')# Kiiruse graafiku y-telje nimetuse lisamine.
    ax2.set_ylabel('Pinge(V)')# Pinge graafiku y-telje nimetuse lisamine.
    ax2.set_xlabel('Aeg(min)')# X-telje nimetuse lisamine.
    

# Funktsioon arduino saadetud andmetest graafiku loomiseks.
def plotValues():
    
    # Graafikute akna kiiruse ja pinge graafikute vahel jagamine.
    ax1 = plt.subplot2grid((3,1), (0,0), rowspan=2, colspan=1)# Kiiruse graafiku asukoha ja suuruse määramine.
    ax2 = plt.subplot2grid((3,1), (2,0), rowspan=1, colspan=1)# Pinge graafiku asukoha ja suuruse määramine.
    
    ax1.set_title('Näidud Arduinolt')# Graafikute pealkirja lisamine.
    
    setPlotLook(ax1, ax2)# Käivita funktsioon setPlotLook.
    
    # Andmete põhjal graafikute loomine ja nende värvi, stiili, paksuse ja nimetuste määramine.
    ax1.plot(x,väärtusedB, color='#f5bf03', linestyle='solid', linewidth=2, label= 'Kiirus')
    ax2.plot(x,väärtusedC, color='#e50000', linestyle='solid', linewidth=2, label= 'Pinge')
    
    # Legendi asukoha määramine.
    ax1.legend(loc='upper right')
    ax2.legend(loc='upper right')
    
    

def doAtExit():
    serialArduino.close()
    print("Close serial")
    print("serialArduino.isOpen() = " + str(serialArduino.isOpen()))

atexit.register(doAtExit)

# Funktsioon menüü jaoks.
def menüü():
    
    vastus = ynbox("Valmis \n Salvestada?")# Küsi kasutajalt kas ta soovib uusi mõõtmistulemusi salvestada?
    if vastus == True :# Kui vastus on jah.
        
        f= open("andmed.txt","a+")# Ava fail nimega andmed.txt või kui seda ei ole siis loo see.
        f.write(enterbox('Mis nimega salvestada?'))# Küsi kasutajalt, mis nimega ta soovib andmeid salvestada ja lisa see faili.
        f.write("\n")# Mine järgmisele reale.
        f.write(str(väärtusedB).replace("'",''))# Kirjuta faili kiiruse andmed.
        f.write("\n")# Mine järgmisele reale.
        f.write(str(väärtusedC).replace("'",''))# Kirjuta faili pinge andmed.
        f.write("\n")# Mine järgmisele reale.
        f.write(str(x).replace("'",''))# Kirjuta faili aja andmed.
        f.write("\n")# Mine järgmisele reale.
        f.close()# Sulge fail.


        if ynbox("Valmis \n Näidata salvestusi?") :# Küsi kasutajalt kas Näidata salvestatud andmeid, kui jah siis.
            drawnow(plotSavedValues)# Käivita drawnow abil funktsioon plotSavedValues.
            
    elif vastus == False :# Kui vastus küsimusele mõõtmistulemusi salvestada on ei.
        if ccbox("Oled kindel?") :# Küsi kasutajalt kas ta on kindel, kui jah siis.
            pass# Ära tee midagi.
        else :# Kui vastus on ei.
            menüü()# Mine tagasi funksiooni algusesse.
    else :# Kui küsimusele kas mõõtmistulemusi salvestada ei vastatud või tekkis mingi viga.
        msgbox("See ei olnud vastus!")# Ütle kasutajale "See ei olnud vastus!".
        menüü()# Mine tagasi funksiooni algusesse.
    
        

def plotSavedValues():
    
    # Graafikute akna kiiruse ja pinge graafikute vahel jagamine.
    ax1 = plt.subplot2grid((3,1), (0,0), rowspan=2, colspan=1)# Kiiruse graafiku asukoha ja suuruse määramine.
    ax2 = plt.subplot2grid((3,1), (2,0), rowspan=1, colspan=1)# Pinge graafiku asukoha ja suuruse määramine.
    
    ax1.set_title('Andmed')# Graafikute pealkirja lisamine.
    
    setPlotLook(ax1, ax2)# Käivita funktsioon setPlotLook.
    
    valikud = []
    f= open("andmed.txt","r")# Andmefaili avamine lugemisrežiimis.
    f1=f.readlines()# Loe ridade kaupa kõik andmed.
    
    # Leia kõik read, mis ei hakka märgiga [ ehk on nimed ja lisa need loendisse valikud.
    for rida in f1:
        if rida[0] != '[':
            valikud.append(rida)
            
    valikud = multchoicebox('Mida näidata?', choices = valikud)# Küsi kasutajalt, milliseid andmeid ta soovib vaadata ja salvesta need loendisse valikud.
    
    # Leia failist valitud nimed.
    for k , koht in enumerate(valikud):
        for r , rida in enumerate(f1):
            if koht == rida :
                
                # Muuda andmed loenditeks.
                y1 = f1[r+1].replace('[','').replace(']','').strip().split(",")
                y2 = f1[r+2].replace('[','').replace(']','').strip().split(",")
                xS = f1[r+3].replace('[','').replace(']','').strip().split(",")
                # Muuda sõnede loendid arvude loenditeks.
                y1 = list(map(float, y1))
                y2 = list(map(float, y2))
                xS = list(map(float, xS))
                
                # Andmete põhjal graafikute loomine ja nende värvi, stiili, paksuse ja nimetuste määramine.
                ax1.plot(xS,y1, color=värvid[k], linestyle='solid',linewidth=2, label= 'Kiirus '+ koht)
                ax2.plot(xS,y2, color=värvid[k], linestyle='solid',linewidth=2, label= 'Pinge '+ koht)
        
    f.close()# Sulge fail.
    
    # Legendi asukoha määramine.
    ax1.legend(loc='upper right')
    ax2.legend(loc='upper right')
    
    plt.show()# Kuva graafikud.
    time.sleep(5)# Oota. Vajalik, et graafik õieti toimiks.
    

while com < 14 :# Kuni muutuja com on alla 14.
    try:
        serialArduino = serial.Serial('com' + str(com), 115200)# Ürita võtta ühendust sisendiga mille number on com.
        # Deklareeri lokaalsed muutujad
        oodatud = 0
        loe = True
        
        while (serialArduino.inWaiting()==0):# Kuni mingeid andmeid ei ole.
            if oodatud < 20 :# Kui on oodatud alla kahe sekundi.
                time.sleep( 0.1 )# Oota 0.1 sekundit.
                oodatud += 1# Liida muutujale oodatud 1
            else :# Kui on oodatud üle kahe sekundi.
                loe = False# Muuda muutuja loe False'iks
                break# Välju while tsüklist.
        
        if loe :# Kui loe = True
            
            valueRead = serialArduino.readline(500)# Loe saabunud andmed.
            
            if valueRead == b'Arduino\r\n':# Kui andmed on sõna arduino.
                
                msgbox("Arduino leitud com" + str(com))# Teata kasutajale, et Arduino leitud ja millisal ühendusel see on.
            
    except:# Kui ühenduse võttmine ebaõnnestus.
        print(com)# Väljasta muutuja com väärtus.
    com += 1# Suurenda muutujat com ühe võrra.



while True:
    # Kuni uusi andmeid pole jätka kontrollimist, kas midagi on saabunud.
    while (serialArduino.inWaiting()==0):
        pass
    
    valueRead = serialArduino.readline(500)# Loe saabunud andmed.
    
    try:
        if valueRead == b'Arduino\r\n':# Kui andmed on sõna arduino.
            pass# Ära tee midagi.
            
        elif valueRead == b'alustan\r\n':# Kui andmed on sõna alustan.
            # Tühjenda andmete järjendid.
            väärtusedB = []
            väärtusedC = []
            x = []
            
            algus = time.time()# Salvesta mõõtmise alustamise aeg.
            arduinoLugemine()# Käivita funktsioon arduinoLugemine.
            
        else :# Kui andmed on midagi muud.
            print("Viga vastuvõtmisel")# Veateade.
        
    except ValueError:
        print("Viga vastuvõtmisel")# Veateade andmete vastuvõtmise ebaõnnestumise korral.

