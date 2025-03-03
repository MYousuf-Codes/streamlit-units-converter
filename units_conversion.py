conversion_factors = {
    "Length": {
        "Kilometers to Miles": 0.621371,
        "Miles to Kilometers": 1.60934,
        "Meters to Feet": 3.28084,
        "Feet to Meters": 0.3048,
        "Centimeters to Inches": 0.393701,
        "Inches to Centimeters": 2.54,
        "Millimeters to Inches": 0.0393701,
        "Inches to Millimeters": 25.4,
        "Yards to Meters": 0.9144,
        "Meters to Yards": 1.09361
    },
    "Mass": {
        "Kilograms to Pounds": 2.20462,
        "Pounds to Kilograms": 0.453592,
        "Grams to Ounces": 0.035274,
        "Ounces to Grams": 28.3495,
        "Tons to Kilograms": 907.184,
        "Kilograms to Tons": 0.00110231
    },
    "Time": {
        "Seconds to Minutes": 1 / 60,
        "Minutes to Seconds": 60,
        "Minutes to Hours": 1 / 60,
        "Hours to Minutes": 60,
        "Hours to Days": 1 / 24,
        "Days to Hours": 24
    },
    "Temperature": {
        "Celsius to Fahrenheit": lambda c: (c * 9 / 5) + 32,
        "Fahrenheit to Celsius": lambda f: (f - 32) * 5 / 9,
        "Celsius to Kelvin": lambda c: c + 273.15,
        "Kelvin to Celsius": lambda k: k - 273.15,
        "Fahrenheit to Kelvin": lambda f: (f - 32) * 5 / 9 + 273.15,
        "Kelvin to Fahrenheit": lambda k: (k - 273.15) * 9 / 5 + 32
    },
    "Digital Storage": {
        "Bytes to Kilobytes": 1 / 1024,
        "Kilobytes to Bytes": 1024,
        "Kilobytes to Megabytes": 1 / 1024,
        "Megabytes to Kilobytes": 1024,
        "Megabytes to Gigabytes": 1 / 1024,
        "Gigabytes to Megabytes": 1024,
        "Gigabytes to Terabytes": 1 / 1024,
        "Terabytes to Gigabytes": 1024
    },
    "Speed": {
        "Kilometers per Hour to Miles per Hour": 0.621371,
        "Miles per Hour to Kilometers per Hour": 1.60934,
        "Meters per Second to Kilometers per Hour": 3.6,
        "Kilometers per Hour to Meters per Second": 1 / 3.6
    },
    "Volume": {
        "Liters to Milliliters": 1000,
        "Milliliters to Liters": 1 / 1000,
        "Gallons to Liters": 3.78541,
        "Liters to Gallons": 1 / 3.78541,
        "Cups to Milliliters": 236.588,
        "Milliliters to Cups": 1 / 236.588
    }
}

def convert_units(value, category, unit):
    factor = conversion_factors[category][unit]
    return factor(value) if callable(factor) else value * factor
