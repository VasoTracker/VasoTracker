

/* VasoTracker Pressure Monitor Code */

/*
  This code was written by Calum Wilson with help from Penny Lawton.

*/

// First thing's first, link to the required libraries:

#include <WheatstoneBridge.h> // Include the Wheatstone library
#include <LiquidCrystal.h> // Include the LCD library
#include "strain_gauge_shield_and_lcd_support_functions.h" // Include support function header ---> This file should be in the working folder!

// Initialize the library with the numbers of the interface pins
LiquidCrystal lcd(8, 9, 4, 5, 6, 7);

// Initial calibration values
const int CST_PRESSURE_IN_MIN = 350;       // Raw value calibration lower point
const int CST_PRESSURE_IN_MAX = 650;       // Raw value calibration upper point
const int CST_PRESSURE_OUT_MIN = 0;        // Pressure calibration lower point
const int CST_PRESSURE_OUT_MAX = 200;     // Pressure calibration upper point ---> 140 is about the maximum that can be read out with the default gain on the RB-Onl-38 and 26PCDFG5G pressure transducers. Can change the gain with surface mount resistors.

const int CST_CAL_PRESSURE_MIN = 0;
const int CST_CAL_PRESSURE_MAX = 200;
const int CST_CAL_PRESSURE_STEP = 5;
const int CST_CAL_PRESSURE_STEP_LARGE = 10;

// Initialize the first Wheatstone bridge object
WheatstoneBridge wsb_pressure1(A1, CST_PRESSURE_IN_MIN, CST_PRESSURE_IN_MAX, CST_PRESSURE_OUT_MIN, CST_PRESSURE_OUT_MAX);

// Initialize the second Wheatstone bridge object
WheatstoneBridge wsb_pressure2(A0, CST_PRESSURE_IN_MIN, CST_PRESSURE_IN_MAX, CST_PRESSURE_OUT_MIN, CST_PRESSURE_OUT_MAX);



// < Setup function >
void setup()
{
  // Initialize LCD screen
  lcd.begin(16, 2);
  
  // Intro screen
  displayScreen("Myograph", "Pressure Monitor");
  delay(1000);

  //Calibrate the first pressure transducer!
  // Calibration
  displayScreen("* Calibration *", "Transducer 1");
  delay(1000);
  
  // Calibration - Low value
  displayScreen("* Calibration *", "Low value");
  delay(1000);
  
  // Calibration - linear interpolation
  int cal_adc_low = CST_PRESSURE_IN_MIN;
  int cal_adc_high = CST_PRESSURE_IN_MAX;
  int cal_pressure_low = CST_PRESSURE_OUT_MIN;
  int cal_pressure_high = CST_PRESSURE_OUT_MAX;
  
  // Calibration - Low value
  displayScreen("* Calibration *", "Low value");
  //Serial.println("* Calibration * - Low value");
  delay(1000);
  // Get force value
  cal_pressure_low = getValueInRange("Set low pressure", "Pres (mmHg):", 13, cal_pressure_low, CST_CAL_PRESSURE_MIN, CST_CAL_PRESSURE_MAX, CST_CAL_PRESSURE_STEP, CST_CAL_PRESSURE_STEP_LARGE);
  // Get ADC raw value
  cal_adc_low = getValueADC("Set low raw ADC", "Raw ADC:", 13, A1, btnSELECT);
  
  // Calibration - High value
  displayScreen("* Calibration *", "High value");
  //Serial.println("* Calibration * - High value");
  delay(1000);
  // Get force value
  cal_pressure_high = getValueInRange("Set high pressure", "Pres (mmHg):", 13, cal_pressure_high, CST_CAL_PRESSURE_MIN, CST_CAL_PRESSURE_MAX, CST_CAL_PRESSURE_STEP, CST_CAL_PRESSURE_STEP_LARGE);
  // Get ADC raw value
  cal_adc_high = getValueADC("Set high raw ADC", "Raw ADC:", 13, A1, btnSELECT);
  
  //Perform calibration
  wsb_pressure1.linearCalibration(cal_adc_low, cal_adc_high, cal_pressure_low, cal_pressure_high);



  
  //Calibrate the second pressure transducer!
  // Calibration
  displayScreen("* Calibration *", "Transducer 2");
  delay(1000);
  
  // Calibration - Low value
  displayScreen("* Calibration *", "Low value");
  delay(1000);
  
  // Calibration - linear interpolation
  int cal_adc_low2 = CST_PRESSURE_IN_MIN;
  int cal_adc_high2 = CST_PRESSURE_IN_MAX;
  int cal_pressure_low2 = CST_PRESSURE_OUT_MIN;
  int cal_pressure_high2 = CST_PRESSURE_OUT_MAX;
  
  // Calibration - Low value
  displayScreen("* Calibration *", "Low value");
  delay(1000);
  // Get pressure value
  cal_pressure_low2 = getValueInRange("Set low pressure", "Pres (mmHg):", 13, cal_pressure_low2, CST_CAL_PRESSURE_MIN, CST_CAL_PRESSURE_MAX, CST_CAL_PRESSURE_STEP, CST_CAL_PRESSURE_STEP_LARGE);
  // Get ADC raw value
  cal_adc_low2 = getValueADC("Set low raw ADC", "Raw ADC:", 13, A0, btnSELECT);
  
  // Calibration - High value
  displayScreen("* Calibration *", "High value");
  delay(1000);
  // Get pressure value
  cal_pressure_high2 = getValueInRange("Set high pressure", "Pres (mmHg):", 13, cal_pressure_high2, CST_CAL_PRESSURE_MIN, CST_CAL_PRESSURE_MAX, CST_CAL_PRESSURE_STEP, CST_CAL_PRESSURE_STEP_LARGE);
  // Get ADC raw value
  cal_adc_high2 = getValueADC("Set high raw ADC", "Raw ADC:", 13, A0, btnSELECT);
  
  // Perform calibration
  wsb_pressure2.linearCalibration(cal_adc_low2, cal_adc_high2, cal_pressure_low2, cal_pressure_high2);

  // Setup display labels
  displayScreen("P1 (mmHg):", "P2 (mmHg):");
  Serial.begin(9600);
}

// Timing management
long display_time_step = 1000;
long display_time = 0;

// Force measurement & display
int pressure_adc;
int pressure;
int pressure_adc2;
int pressure2;
int force_pos_offset;

#define NUMSAMPLES 5
uint16_t samples[NUMSAMPLES];
uint16_t samples2[NUMSAMPLES];
// < Main code >
void loop(){



    //Measure from the first pressure transducer
    
    // Make a force measurement and obtain the calibrated force value


    uint8_t i;
    float average;
    float average2;
   
    // take N samples in a row, with a slight delay
    for (i=0; i< NUMSAMPLES; i++) {
     samples[i] = wsb_pressure1.measureForce();
     delay(5);
    }

    // average all the samples out
    average = 0;
    for (i=0; i< NUMSAMPLES; i++) {
       average += samples[i];
    }
    average /= NUMSAMPLES;

    // Display raw ADC value
    lcd.setCursor(11, 0); lcd.print("       ");
    lcd.setCursor(11, 0); lcd.print(average);
    
    //pressure = wsb_pressure1.measureForce();
    
    // Obtain the raw ADC value from the last measurement
    //pressure_adc = wsb_pressure1.getLastForceRawADC();


    //Measure from the second pressure transducer
    
    // Make a force measurement and obtain the calibrated force value

   
    // take N samples in a row, with a slight delay
    for (i=0; i< NUMSAMPLES; i++) {
     samples2[i] = wsb_pressure2.measureForce();
     delay(5);
    }

    // average all the samples out
    average2 = 0;
    for (i=0; i< NUMSAMPLES; i++) {
       average2 += samples2[i];
    }
    average2 /= NUMSAMPLES;

    
    //pressure2 = wsb_pressure2.measureForce();
    
    // Obtain the raw ADC value from the last measurement
    //pressure_adc2 = wsb_pressure2.getLastForceRawADC();

    
    

    
      // Display raw ADC value
    lcd.setCursor(11, 1); lcd.print("       ");
    lcd.setCursor(11, 1); lcd.print(average2);


    Serial.print("<Pressure1");
    Serial.print(":");
    Serial.print(average);
    Serial.print(";");
    
    Serial.print("Pressure2");
    Serial.print(":");
    Serial.print(average2);
    Serial.print(";");
    
    Serial.println(">");

    

    //if(Serial.read()>=0){

      //char sf2[15];
      //sprintf(sf2, "%i\n", pressure2);
      //char sf[15];
      //sprintf(sf, "%i\n", pressure);
      //Serial.write(sf);
      //Serial.write(sf2);
      
    //}  

    
    // Reset time counter
    display_time = millis();
  
}
