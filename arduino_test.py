import serial
import time

# Change COM15 if your Arduino uses another port
arduino = serial.Serial('COM15', 9600, timeout=1)

time.sleep(2)

print("Arduino connected!")

try:
    while True:
        print("\nChoose signal:")
        print("1. RED")
        print("2. YELLOW")
        print("3. GREEN")
        print("4. Buzzer")
        print("5. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            arduino.write(b"SIGNAL_RED\n")
            print("Red signal activated")

        elif choice == "2":
            arduino.write(b"SIGNAL_YELLOW\n")
            print("Yellow signal activated")

        elif choice == "3":
            arduino.write(b"SIGNAL_GREEN\n")
            print("Green signal activated")

        elif choice == "4":
            arduino.write(b"EVENT\n")
            print("Buzzer event sent")

        elif choice == "5":
            break

        else:
            print("Invalid choice")

except KeyboardInterrupt:
    print("Stopped")

finally:
    arduino.close()