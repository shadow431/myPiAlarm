#!/usr/bin/env python
Celsius = float(raw_input("Enter a temperature in Celsius: "))

Celsius = Celsius / 1000

Fahrenheit = 9.0/5.0 * Celsius + 32

print "Temperature:", Celsius, "Celsius = ", Fahrenheit, " F"
