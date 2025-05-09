# README.md

# PyQt6 Desktop Application

This project is a desktop application built using PyQt6. It features a main interface with two buttons that navigate to different panels for testing.

## Project Structure

```
qt-desktop-app
├── src
│   ├── main.py                # Entry point of the application
│   ├── views
│   │   ├── main_window.py      # Main interface with buttons
│   │   ├── control_panel.py     # Control panel interface
│   │   └── motor_panel.py       # Motor panel interface
│   ├── controllers
│   │   ├── control_test.py      # Logic for control panel test
│   │   └── motor_test.py        # Logic for motor panel test
│   └── resources
│       └── styles.qss          # Stylesheet for the application
├── requirements.txt            # Project dependencies
└── README.md                   # Project documentation
```

## Requirements

To run this application, you need to have the following dependencies installed:

- PyQt6

You can install the required packages using pip:

```
pip install -r requirements.txt
```

## Running the Application

To start the application, run the following command:

```
python src/main.py
```

## Features

- Main interface with two buttons:
  - **控制板测试**: Navigates to the control panel test.
  - **电机板测试**: Navigates to the motor panel test.

## License

This project is licensed under the MIT License.