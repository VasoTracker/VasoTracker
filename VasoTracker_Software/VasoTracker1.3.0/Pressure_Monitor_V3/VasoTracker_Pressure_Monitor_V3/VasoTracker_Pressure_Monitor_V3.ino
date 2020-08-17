/* VasoTracker Pressure Monitor Code: Dr. N8-Style*/
/* This code was written by Calum Wilson with help from Penny Lawton.*/
/* It was made significantly better by Nathan Tykocki.*/

//  Include the LCD, wheatstone bridge, and stepper motor support libraries and headers
#include <LiquidCrystal.h>
#include "pressure.h" //This file should be in the working folder. It now contains all the wheatstone bride headers and associated info (from here: https://github.com/RobotShop/Wheatstone-Bridge-Amplifier-Shield/archive/master.zip).

//  Initialize the library with the numbers of the interface pins
LiquidCrystal lcd(8, 9, 4, 5, 6, 7);

//  Initial calibration values for force transducer
const int CST_PRESSURE_IN_MIN = 350;     // Raw value calibration lower point
const int CST_PRESSURE_IN_MAX = 650;     // Raw value calibration upper point
const int CST_PRESSURE_OUT_MIN = 0;      // Pressure calibration lower point
const int CST_PRESSURE_OUT_MAX = 200;    // Pressure calibration upper point. This is in mmHg. This is about the max it can do.
const int CST_CAL_PRESSURE_MIN = 0;      // As with before, in mmHg.
const int CST_CAL_PRESSURE_MAX = 200;    // As with before, in mmHg.
const int CST_CAL_STEP_SM = 1;           // Change this to change what the L/R buttons do during calibration.
const int CST_CAL_STEP_LG = 10;          // Change this to change what the U/D buttons do during calibration.

//  Setup the data recording (data to be sent out, sampling rate)
//******************************************************************************************************************
  #define       NUMSAMPLES 5               //  Change this to alter the number of samples averaged.                *
  unsigned long TIME_DELAY = 5;           //  Change this to alter the time delay for wheatstone bridge output.   *
  unsigned long LCD_TIME_DELAY = 500;           // Setting a delay to update the LCD screen
//******************************************************************************************************************

uint16_t      samples1[NUMSAMPLES];      // Needed to determine how the samples will be summed and averaged.
uint16_t      samples2[NUMSAMPLES];      // Needed to determine how the samples will be summed and averaged.
unsigned long previousMillis = 0;        // Resetting the clock to determine how much time has elapsed.
unsigned long initMillis = 0;            // Resetting the clock to determine how much time has elapsed.
unsigned long elapsedMillis = 0;
bool update_flag = 0;                    // Flag to update the LCD display

//  Initialize the Wheatstone bridge object, plugged into Strain2 on the shield
WheatstoneBridge wsb1(A1, CST_PRESSURE_IN_MIN, CST_PRESSURE_IN_MAX, CST_PRESSURE_OUT_MIN, CST_PRESSURE_OUT_MAX);

//  Initialize the Wheatstone bridge object, plugged into Strain2 on the shield
WheatstoneBridge wsb2(A0, CST_PRESSURE_IN_MIN, CST_PRESSURE_IN_MAX, CST_PRESSURE_OUT_MIN, CST_PRESSURE_OUT_MAX);

//  All Setup functions go in here: calibrate transducer, regulate everything, etc.
void setup()
{
  //  Transducer 1: Calibration and variables needed for linear interpolation
  int cal_adc_low = CST_PRESSURE_IN_MIN;
  int cal_adc_high = CST_PRESSURE_IN_MAX;
  int cal_pressure_low = CST_PRESSURE_OUT_MIN;
  int cal_pressure_high = CST_PRESSURE_OUT_MAX;
  
  //  Initialize LCD screen and intro
  lcd.begin(16, 2); displayScreen("VasoTracker", "Pressure Monitor"); delay(1000);

  //Calibrate the first pressure transducer!
  displayScreen("* Calibration *", "Transducer 1"); delay(1000);
  
  // Calibration 1: low value. Get low pressure value and associated ADC value.
  displayScreen("* Calibration *", "Low value"); delay(1000);
  cal_pressure_low   = getValueInRange("Set low pressure", "Pres (mmHg):", 13, cal_pressure_low, CST_CAL_PRESSURE_MIN, CST_CAL_PRESSURE_MAX, CST_CAL_STEP_SM, CST_CAL_STEP_LG);
  cal_adc_low     = getValueADC("Set low raw ADC", "Raw ADC:", 13, A1, btnSELECT);

  // Calibration 1: high value. Get high pressure value and associated ADC value.
  displayScreen("* Calibration *", "High value"); delay(1000);
  cal_pressure_high  = getValueInRange("Set high pressure", "Pres (mmHg):", 13, cal_pressure_high, CST_CAL_PRESSURE_MIN, CST_CAL_PRESSURE_MAX, CST_CAL_STEP_SM, CST_CAL_STEP_LG);
  cal_adc_high    = getValueADC("Set high raw ADC", "Raw ADC:", 13, A1, btnSELECT);

  //  Peform linear calibration based on values chosen and selected above for transducer 1.
  wsb1.linearCalibration(cal_adc_low, cal_adc_high, cal_pressure_low, cal_pressure_high);
  
  //  Transducer 2: Calibration and variables needed for linear interpolation
  int cal_adc_low2 = CST_PRESSURE_IN_MIN;
  int cal_adc_high2 = CST_PRESSURE_IN_MAX;
  int cal_pressure_low2 = CST_PRESSURE_OUT_MIN;
  int cal_pressure_high2 = CST_PRESSURE_OUT_MAX;
  
  //Calibrate the secondpressure transducer!  
  displayScreen("* Calibration *", "Transducer 2"); delay(1000);
  
  // Calibration 2: Low value. Get low pressure value and associated ADC value.
  displayScreen("* Calibration *", "Low value"); delay(1000);
  cal_pressure_low2   = getValueInRange("Set low pressure", "Pres (mmHg):", 13, cal_pressure_low2, CST_CAL_PRESSURE_MIN, CST_CAL_PRESSURE_MAX, CST_CAL_STEP_SM, CST_CAL_STEP_LG);
  cal_adc_low2     = getValueADC("Set low raw ADC", "Raw ADC:", 13, A0, btnSELECT);

  // Calibration 2: high value. Get high pressure value and associated ADC value.
  displayScreen("* Calibration *", "High value"); delay(1000);
  cal_pressure_high2 = getValueInRange("Set high pressure", "Pres (mmHg):", 13, cal_pressure_high2, CST_CAL_PRESSURE_MIN, CST_CAL_PRESSURE_MAX, CST_CAL_STEP_SM, CST_CAL_STEP_LG);
  cal_adc_high2 = getValueADC("Set high raw ADC", "Raw ADC:", 13, A0, btnSELECT);

  //  Peform linear calibration based on values chosen and selected above for transducer 2.
  wsb2.linearCalibration(cal_adc_low2, cal_adc_high2, cal_pressure_low2, cal_pressure_high2);
  
  //  Initialize serial communication and set display labels.
  // Setup display labels
  Serial.begin(9600);
  lcd.begin(16,2);
  displayScreen("P1 (mmHg):", "P2 (mmHg):");
}

//  Defining void loops to do the dirty work. The first one pulls the number of samples needed from both transducers and averages them separately. Time is set above.
void pressure(bool update_flag){
  uint8_t i;
  float avg1;
  float avg2;
  unsigned long currentMillis = millis();
  
  if ((currentMillis - previousMillis) >= TIME_DELAY){
    
    for (i = 0; i < NUMSAMPLES; i++){
      samples1[i] = wsb1.measureForce();
      samples2[i] = wsb2.measureForce();
    }
    
    avg1 = 0;
    avg2 = 0;
    
    for (i = 0; i < NUMSAMPLES; i++){
      avg1 += samples1[i];
      avg2 += samples2[i];
    }
    
    avg1 /= NUMSAMPLES;
    avg2 /= NUMSAMPLES;    

    if (update_flag == 1){
      lcd.setCursor(11, 0); lcd.print(avg1);
      lcd.setCursor(11, 1); lcd.print(avg2);
    }
    previousMillis = currentMillis;
  }

  Serial.print("<P1"); Serial.print(":"); Serial.print(avg1);  Serial.print(";");
  Serial.print("P2");  Serial.print(":"); Serial.print(avg2); Serial.print(";"); Serial.println(">");
  
}

//If you want to do more things it's easy to add the loops here. Like if you wanted to do only 1 transducer and add temperature controls to a single unit...
unsigned long currentMillis_LCD = millis();
void loop(){
  currentMillis_LCD = millis(); //Get the current time
  elapsedMillis = currentMillis_LCD - initMillis;
  
  if (elapsedMillis > LCD_TIME_DELAY){
    initMillis = currentMillis_LCD;
    update_flag = 1;
  }
  
  pressure(update_flag);  // Get the current pressure values
  update_flag = 0;
}
