/* See Arduino programm on loodud elektrimootori kiiruse ja sisendpinge mõõtmiseks ning nende arvutisse Pythoni programmile edastamiseks.
 * Võite seda modifitseerida mis iganes suuruste mõõtmiseks. Selleks, et Pythoni programm saaks Arduinoga ühenduse ja selle saadetud 
 * andmeid õieti mõistaks, peab Arduino saatma serial ühenduse kaudu kuni mõõtmise alustamiseni "Arduino", mõõtmise alguses "alustan",
 * mõõtmise lõpus "0,0,0". Andmed peaks edastama järgneval kujul: 1,esimene väärtus,teine väärtus reavahe.
 * Ühenduse kiirus peaks olema 115200.
 */

#include <Wire.h>// ADS1115 toimimiseks vajalik teek.    http://henrysbench.capnfatz.com/henrys-bench/arduino-voltage-measurements/arduino-ads1115-module-getting-started-tutorial/
#include <Adafruit_ADS1015.h>// ADS1115 toimimiseks vajalik teek.

Adafruit_ADS1115 ads(0x49);// ADS'i tüübi ja aadressi määramine.

// Globaalsete muutujate deklareerimine ja enamike algväärtuste määramine.
bool nuppuOlek = HIGH;
bool eelmineNuppuOlek = HIGH;
bool tegevus = false;
bool praeguOlek;
bool enneOlek = LOW;
unsigned long eelmineMicros= 0;
unsigned long uusMicros = 0;
unsigned long aeg = 230000;
unsigned long eelmineMills= 0;

// Püsiväärtuste määramine.
const int nupp = 2;
const int optoV = 8;
const int kaivitus = 10;
const int relee = 11;

// Osa programmist, mida loetakse ainult ükskord Arduino käivitudes.
void setup() {
  // Arduino ühenduste sisenditeks või väljunditeks seadistamine.
  pinMode(nupp,INPUT_PULLUP);
  pinMode(optoV,INPUT);
  pinMode(13,OUTPUT);
  pinMode(relee,OUTPUT);
  pinMode(kaivitus,OUTPUT);

  // Väljundite olekute määramine.
  digitalWrite(relee,HIGH);// Muuda väljund 11 kõrgeks, ehk ühenda see toitepingega.
  digitalWrite(kaivitus,LOW);// Muuda väljund 10 madalaks, ehk ühenda see maandusega.
  digitalWrite(13,LOW);// Muuda väljund 13 madalaks.
  
  ads.begin();// ADS1115 ühenduse käivitamine.
  
  Serial.begin(115200);// Ühenduse arvutiga käivitamine ja selle kiiruse seadistamine 115200.
}

// Osa programmist, mida Arduino pärast käivitumist kordab.
void loop() {
  
  nuppuOlek = digitalRead(nupp);// Loe sisendi 2 väärtus ja salvesta see muutujasse nuppuOlek.
  
  if( eelmineNuppuOlek != nuppuOlek && nuppuOlek == HIGH){// Kui muutuja nuppuOlek erineb muutujast eelmineNuppuOlek ja muutuja nuppuOlek väärtus on HIGH.
    if(tegevus){// Kui muutuja tegevus väärtus on true.
      Serial.println("0,0,0");// Saada Pythoni programmile mõõtmise katkestamis käsklus.
    }
    else{// Kui muutuja tegevus väärtus ei ole true ehk on false.
      digitalWrite(kaivitus,HIGH);// Muuda väljund 10 kõrgeks, mis lülitab sisse mootori käimalükkamis ventilaatori.
      
      while(aeg > 200000){// Kuni aeg mis kulub mootoril poole pöörde tegemiseks on üle 0,2 sekundi.
        kiirus();// Käivita funktsioon kiirus.
        
      }
      digitalWrite(kaivitus,LOW);// Muuda väljund 10 madalaks, mis lülitab ventilaatori välja.
      digitalWrite(relee,LOW);// Muuda väljund 11 madalaks, mis ühendab relee abil mootori toitekondensaatorid selle külge.
      Serial.println("alustan");// Teavita Pythoni programmi, et mõõtine algab.
      
    }
    tegevus = !tegevus;// Kui muutuja tegevus väärtus on true muuda see false'iks ja vastupidi.
    digitalWrite(13,tegevus);// // Muuda väljund 13 kõrgeks või madalaks, sõltuvalt sellest kas muutuja tegevus on true või false.
  }
  if(tegevus){// Kui muutuja tegevus väärtus on true.
    
    if(millis() - eelmineMills >= 1000){// Kui eelmisest korrast on möödunud üle ühe sekundi.
      eelmineMills = millis();// Salvesta millisekundite arv Arduino käivitumisest muutujasse eelmineMills.
      
      int16_t adc0;  // Muutuja loomine ADS1115 andmete jaoks.
      adc0 = ads.readADC_SingleEnded(0);// ADS1115 sisendi 0 väärtuse lugemine.

      // Andmete saatmine Pythoni programmile.
      Serial.print(1);
      Serial.print(",");
      Serial.print(aeg);
      Serial.print(",");
      Serial.println(adc0);
      
      if(aeg >= 3740000){// Kui aeg mis kulub mootoril poole pöörde tegemiseks on ületab 3,74 sekundit.
        tegevus = !tegevus;// Kui muutuja tegevus väärtus on true muuda see false'iks ja vastupidi.
        digitalWrite(relee,HIGH);// Muuda väljund 11 madalaks, mis ühendab mootori toitekondensaatorid laadimiseks mootori küljest lahti.
      }
    }
    kiirus();// Käivita funktsioon kiirus.
    
    
  }
  else if(millis() - eelmineMills >= 10){// Kui muutuja tegevus väärtus on false ja eelmisest korrast on möödunud üle 0.01 sekundi.
    eelmineMills = millis();// Salvesta millisekundite arv Arduino käivitumisest muutujasse eelmineMills.
    Serial.println("Arduino");// Anna Pythoni programmile teada, et oled Arduino.
    
  }
  
  eelmineNuppuOlek = nuppuOlek;

}

// Funktsioon kiirus.
void kiirus(){
  
  praeguOlek = digitalRead(optoV); // Loe sisendi 8 väärtus ja salvesta see muutujasse praeguOlek.
  if( enneOlek != praeguOlek){// Kui muutuja enneOlek erineb muutujast praeguOlek.
    
    if( praeguOlek == HIGH ){ // Kui muutuja praeguOlek väärtus on HIGH.
      
      uusMicros = micros();// Salvesta mikrosekundite arv Arduino käivitumisest muutujasse uusMicros.
      aeg = ( uusMicros - eelmineMicros ); // Arvuta aeg, mis kulus mootoril poole pöörde tegemiseks ja salvesta see muutujasse aeg.
      eelmineMicros = uusMicros;
     }
   }
  enneOlek = praeguOlek;
}
