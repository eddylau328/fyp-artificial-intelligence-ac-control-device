#include <LiquidCrystal.h>
int Con=100;
LiquidCrystal lcd(12,11,37,35,33,31);

void setup() {
  analogWrite(8,Con);
  // put your setup code here, to run once:
  lcd.begin(16, 2);
  lcd.print("hello world");
}

void loop() {
  // put your main code here, to run repeatedly:

}
