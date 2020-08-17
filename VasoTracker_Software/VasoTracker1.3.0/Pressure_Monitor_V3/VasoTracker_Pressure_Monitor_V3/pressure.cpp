// Include support function header
#include "pressure.h"
//#include "WheatstoneBridge.h"

// Return the first pressed button found
byte read_LCD_buttons()

// read the value from the analog pin connected to the LCD and determine which button is being pressed.
{
  int adc_key_in = analogRead(A5);
  if (adc_key_in > 1000) return btnNONE;
  if (adc_key_in < 50)   return btnRIGHT;
  if (adc_key_in < 250)  return btnUP;
  if (adc_key_in < 450)  return btnDOWN;
  if (adc_key_in < 650)  return btnLEFT;
  if (adc_key_in < 850)  return btnSELECT;
                         return btnNONE;
}

// Display full screen of text (2 rows x 16 characters)
void displayScreen(char row1[], char row2[])
{
  lcd.clear();
  lcd.setCursor(0, 0); lcd.print(row1);
  lcd.setCursor(0, 1); lcd.print(row2);
}

// Displays text on screen and an ADC value at chosen position from selected pin. Waits for user input (select button by default)
int getValueADC(char row1[], char row2[], byte pos, byte pin, byte endButton)
{
  int value = 0;
  int lastValue = -1;
  byte buttons = btnNONE;

  displayScreen(row1, row2);
  delay(1000);
  while (buttons != endButton)
  {
    // Check inputs
    buttons = read_LCD_buttons();

    // Update readout from analog port
    value = analogRead(pin);

    // Update display
    if (value != lastValue)
    {
      lcd.setCursor(pos, 1); lcd.print("                ");
      lcd.setCursor(pos, 1); lcd.print(value);
      lastValue = value;
      delay(400);
    }
  }

  // Return the last measured ADC value
  return (value);
}

// Displays text on screen and a changeable value at chosen position. User input can change the value (left/right/up/down) and press select to accept it.
int getValueInRange(char row1[], char row2[], byte pos, int valueDefault, int valueMin, int valueMax, int valueStep, int valueStepLarge)
{
  int value = valueDefault;
  int lastValue = -1;
  int buttons = btnNONE;

  displayScreen(row1, row2);
  delay(500);
  while (buttons != btnSELECT)
  {
    // Check inputs
    buttons = read_LCD_buttons();
    switch (buttons)
    {
      case btnUP:
        value += valueStep;
        if (value > valueMax)
          value = valueMax;
        break;

      case btnRIGHT:
        value += valueStepLarge;
        if (value > valueMax)
          value = valueMax;
        break;

      case btnDOWN:
        value -= valueStep;
        if (value < valueMin)
          value = valueMin;
        break;

      case btnLEFT:
        value -= valueStepLarge;
        if (value < valueMin)
          value = valueMin;
        break;
    }

    // Update display
    if (value != lastValue)
    {
      lcd.setCursor(pos, 1); lcd.print("                ");
      lcd.setCursor(pos, 1); lcd.print(value);
      lastValue = value;
      delay(200);
    }
  }
  // Return the last selected value
  return (value);
}

// Displays text on screen and a changeable value at chosen position. User input can change the value (left/right/up/down) and press select to accept it.
int getValueAndCalib(char row1[], char row2[], byte pos, int valueDefault, int valueMin, int valueMax, int valueStep, int valueStepLarge)
{
  int value = valueDefault;
  int lastValue = -1;
  int buttons = btnNONE;

  displayScreen(row1, row2);
  delay(500);
  while (buttons != btnSELECT)
  {
    // Check inputs
    buttons = read_LCD_buttons();
    switch (buttons)
    {
      case btnUP:
        value += valueStep;
        if (value > valueMax)
          value = valueMax;
        break;

      case btnRIGHT:
        value += valueStepLarge;
        if (value > valueMax)
          value = valueMax;
        break;

      case btnDOWN:
        value -= valueStep;
        if (value < valueMin)
          value = valueMin;
        break;

      case btnLEFT:
        value -= valueStepLarge;
        if (value < valueMin)
          value = valueMin;
        break;
    }

    // Update display
    if (value != lastValue)
    {
      lcd.setCursor(pos, 1); lcd.print("                ");
      lcd.setCursor(pos, 1); lcd.print(value);
      lastValue = value;
      delay(200);
    }
  }

  // Return the last selected value
  return (value);
}

// Displays text on screen and allows the carriages to move. Pressing select accepts it.
int getInit(char row1[], char row2[], byte direct, byte enab, byte pulse, int valueStart)
{
  int value = valueStart;
  int buttons = btnNONE;

  displayScreen(row1, row2);
  delay(1000);
  while (buttons != btnSELECT)
  {
    // Check inputs
    buttons = read_LCD_buttons();
    switch (buttons)
    {
      case btnRIGHT:
        digitalWrite(direct, HIGH);
        digitalWrite(enab, HIGH);
        digitalWrite(pulse, HIGH);
        delayMicroseconds(value);
        digitalWrite(pulse, LOW);
        delayMicroseconds(value);
        break;

      case btnLEFT:
        digitalWrite(direct, LOW);
        digitalWrite(enab, HIGH);
        digitalWrite(pulse, HIGH);
        delayMicroseconds(value);
        digitalWrite(pulse, LOW);
        delayMicroseconds(value);
        break;

      case btnNONE:
        digitalWrite(direct, HIGH);
        digitalWrite(enab, LOW);
        digitalWrite(pulse, LOW);
        break;
    }
  }
}

// Displays text on screen and allows the carriages to move. Pressing select accepts it.
int getInit2(char row1[], char row2[], byte direct, byte enab, byte pul, int valueStart, int PulseNum)
{
  int value = valueStart;
  int buttons = btnNONE;
  int pulses = PulseNum;

  
  displayScreen(row1, row2);
  delay(1000);
  while (buttons != btnSELECT)
  {
    // Check inputs
    buttons = read_LCD_buttons();
    switch (buttons)
    {
      case btnRIGHT:
        digitalWrite(direct, HIGH);
        digitalWrite(enab, HIGH);
        digitalWrite(pul, HIGH);
        delayMicroseconds(value);
        digitalWrite(pul, LOW);
        delayMicroseconds(value);
        --pulses;
        break;

      case btnLEFT:
        digitalWrite(direct, LOW);
        digitalWrite(enab, HIGH);
        digitalWrite(pul, HIGH);
        delayMicroseconds(value);
        digitalWrite(pul, LOW);
        delayMicroseconds(value);
        pulses++;
        break;

      case btnNONE:
        digitalWrite(direct, HIGH);
        digitalWrite(enab, LOW);
        digitalWrite(pul, LOW);
        break;
    }
  }
  // Return the last selected value
  return (pulses);
}
// < Constructor >
/* Sets the proper analog pin to input. Also does calibration if given by user.
*/
WheatstoneBridge::WheatstoneBridge(byte AnalogPin, int inputMin, int inputMax, int outputMin, int outputMax)
{
  iPin = AnalogPin;
  pinMode(iPin, INPUT);
  iMin = inputMin;
  iMax = inputMax;
  oMin = outputMin;
  oMax = outputMax;
}

// < Destructor >
WheatstoneBridge::~WheatstoneBridge()
{
  // Nothing to destruct
}

// measureForce
/* Obtain the analog measurement from ADC and convert it by interpolation to a force using the latest calibration values.
*/
int WheatstoneBridge::measureForce()
{
  // Obtain ADC raw measurement
  lastForceADCRaw = analogRead(iPin);
  
  // 
  lastForce = map(lastForceADCRaw, iMin, iMax, oMin, oMax) + oMin;
  
  // Return value
  return (lastForce);
}

// getLastForce
/* Return the last force calculation (does not perform a new reading).
*/
int WheatstoneBridge::getLastForce()
{
  return (lastForce);
}

// getLastForceRawADC
/* Return the last force raw ADC value (does not perform a new reading).
*/
int WheatstoneBridge::getLastForceRawADC()
{
  return (lastForceADCRaw);
}

// linearCalibration
/* Calibrates the Wheatstone bridge linear interpolation.
  inputMin: Minimum expected value of raw ADC input
  inputMax: Maximum expected value of raw ADC output
  outputMin:  First (lower) calibration point with a known force, usually 0.
  outputMax:  Second (higher) calibration point with a known force, usually near the maximum force measurable by the load cell used.
*/
void WheatstoneBridge::linearCalibration(int inputMin, int inputMax, int outputMin, int outputMax)
{
  iMin = inputMin;
  iMax = inputMax;
  oMin = outputMin;
  oMax = outputMax;
}
