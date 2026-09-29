## Part 1. Main Document.

### 1. Title and Basic Information.

• **Name:** Lazy Clock

• **Purpose:** Project No. 11. Product.

• **Project Phase:** Phase II.

• **Technology Stack:** Python (PySide6 library).

• **Project Status:** Fully completed.

### 2. Project Overview.

**Lazy Clock** is a desktop clock application developed in Python using the PySide6 library (Qt for Python).

The application displays an analog clock with smoothly moving hour, minute, and second hands on a transparent, frameless window.

Its key feature is system tray integration, which allows users to control the clock's visibility, keep it always on top of other windows, and exit the application through the context menu.

The project is a fully functional application with a clean, minimalist interface and convenient controls.

### 3. Project Goals.

• Create a functional desktop clock application with an analog clock face.

• Implement smooth hand movement with a high refresh rate of 60 FPS.

• Provide a transparent clock window without a standard window frame.

• Implement the ability to drag the clock around the desktop using the mouse.

• Integrate the application with the system tray for state management.

• Add the ability to keep the clock always on top of other windows.

• Implement proper application shutdown both through the system tray and system signals (`SIGINT`, `SIGTERM`).

• Demonstrate a desktop application development approach using PySide6 and `QSystemTrayIcon`.

### 4. Project Components.

• The project consists of a single executable file containing all components:

• `lazy_clock.py` – the main script containing all application code, including rendering logic, mouse event handling, window management, and system tray integration.

### 5. Usage Instructions.

**5.1. Launch:**

• Make sure the PySide6 library is installed (`pip install PySide6`).

• Run the script using Python (for example, through PyCharm).

**5.2. Application Purpose:**

• Display the current time as an analog clock on the desktop.

• The application can run in the background while remaining accessible through the system tray icon.

**5.3. Controls:**

• Left mouse button (hold and drag): move the clock around the desktop.

• Double-click the tray icon: show/hide the clock.

• Tray context menu (right-click):

* Show/Hide Clock: toggle the visibility of the clock window.

* Always on Top: enable/disable keeping the clock above other windows.

* Exit: completely close the application.

**5.4. Interface:**

• Clock window size: 700x700 pixels.

• Transparent background without a window frame (`FramelessWindowHint`, `WA_TranslucentBackground`).

• Three hands:

* Hour hand – black (`#111111`), length 140, width 12.

* Minute hand – dark gray (`#222222`), length 200, width 8.

* Second hand – red (`#d22`), length 235, width 2.

• Black central circle with a radius of 8 pixels.

• System tray icon – blue circle (`#3498db`) on a transparent background.

## Part 2. Technical Document.

### 1. Development Goals.

• The primary goal of the development was to create a desktop clock application using the modern PySide6 library while strengthening Qt development skills.

• The project also focused on learning how to create transparent frameless windows, integrate an application with the system tray, handle mouse events, and process system signals.

• The tasks included working with `QPainter` for custom rendering, `QTimer` for animation, `QSystemTrayIcon` for application management, and `QMenu` for the context menu.

### 2. Technologies Used.

• **Programming Language:** Python

• **GUI Library:** PySide6 (Qt for Python)

• **Standard Libraries:** `sys` (for handling arguments and application termination), `signal` (for system signal handling), `math` (for calculating hand coordinates), `datetime` (for retrieving the current time).

• **PySide6 Modules:**

* QtCore: `Qt`, `QPoint`, `QTimer`.

* QtGui: `QColor`, `QPainter`, `QPen`, `QAction`, `QIcon`, `QPixmap`.

* QtWidgets: `QApplication`, `QWidget`, `QSystemTrayIcon`, `QMenu`, `QMainWindow`.

### 3. Project Architecture.

• The project is implemented as an application divided into two main classes: `ClockWidget` (clock rendering) and `MainWindow` (application and system tray management).

• Main loop: event-driven, controlled by `QApplication.exec()`.

• The logic is divided between the classes:

* `ClockWidget` – responsible for rendering, animation, and window dragging.

* `MainWindow` – responsible for system tray creation, menu handling, and system signal processing.

• At each frame (60 FPS), the following operations are performed: retrieving the current time, calculating the hand angles, and rendering the clock face.

### 4. Project Structure.

• Initialization: PySide6 setup, creation of `QApplication`, and setting `setQuitOnLastWindowClosed(False)`.

• **`ClockWidget` class:**

* `__init__(always_on_top=False)` – configures the window, flags, and timer.

* `paintEvent(event)` – renders the clock hands and center.

* `draw_hand(...)` – helper method for drawing a clock hand.

* `mousePressEvent(event)` – starts dragging.

* `mouseMoveEvent(event)` – moves the window.

• **`MainWindow` class:**

* `__init__()` – creates `ClockWidget`, the system tray, and connects signals.

* `signal_handler(signum, frame)` – handles `SIGINT`/`SIGTERM`.

* `create_tray_icon()` – creates the tray icon and context menu.

* `tray_clicked(reason)` – handles tray icon clicks.

* `toggle_clock()` – shows/hides the clock.

* `toggle_top(checked)` – enables/disables always-on-top mode.

* `quit_app()` – performs a proper application shutdown.

• Entry point: `if __name__ == "__main__":` – creates the application and window and starts the event loop.

• Global variables: none (all state is encapsulated within the classes).

### 5. Key System Components.

• **Clock Rendering (`paintEvent`):** Uses `QPainter` with Antialiasing for smooth rendering. Hand angles are calculated based on the current time, including microseconds for smooth movement.

• **Clock Hands:** Represented as lines drawn using `drawLine` with `RoundCap`. Angles: hour hand – `hour * 30`, minute hand – `minute * 6`, second hand – `sec * 6`.

• **Animation System:** `QTimer` with an interval of `1000 // 60` (≈16.67 ms) calls `update()` 60 times per second.

• **Window Dragging:** Implemented by storing the global mouse position when pressed and calculating the offset while the mouse is moved.

• **System Tray:** `QSystemTrayIcon` with a `QMenu` context menu containing `QAction` items for application management.

• **Signal Handling:** `signal.signal(signal.SIGINT, ...)` and `signal.SIGTERM` are used for proper shutdown when the application is interrupted from the terminal.

### 6. User Interface Implementation.

• The interface is fully implemented using PySide6.

• Main elements: the clock window (transparent, frameless), system tray icon, and context menu.

• Rendering is performed through `QPainter` in `paintEvent` using `QPen` and `drawEllipse`.

• The system tray icon is generated programmatically using `QPixmap` and `QPainter`.

### 7. Development Process.

• Development was carried out in several stages:

* creation of a basic window with a transparent background.

* implementation of the clock face and hand rendering.

* addition of a timer for animation.

* implementation of mouse-based window dragging.

* integration with the system tray.

* addition of the tray menu (show/hide, always on top, exit).

* implementation of the always-on-top functionality.

* handling of system signals for proper application shutdown.

### 8. Main Challenges and Solutions.

• **(1) Challenge:** Properly dragging a frameless window.

**Solution:** Using `event.globalPosition().toPoint()` to obtain global coordinates and calculate the offset relative to `self.pos()`.

• **(2) Challenge:** Smooth movement of the second hand.

**Solution:** Taking microseconds into account when calculating the angle (`sec = now.second + now.microsecond / 1000000`).

• **(3) Challenge:** Proper application shutdown when exiting through the system tray.

**Solution:** Setting `app.setQuitOnLastWindowClosed(False)` and explicitly calling `QApplication.quit()` in `quit_app()`.

• **(4) Challenge:** Handling system signals in a Qt application.

**Solution:** Connecting `signal.signal` to a custom `signal_handler` that calls `quit_app()`.

### 9. Current Project Limitations.

• No digital time display.

• No ability to customize the clock size, color, or style.

• No window position persistence between launches.

• No sound notifications (alarm).

• The code remains monolithic and is not divided into separate modules.

### 10. Potential Improvements and Future Development.

• Refactoring the code (splitting it into modules).

• Adding a digital time display.

• Customizing the appearance (color, size, hand style, and clock face style).

• Saving the window position and settings to a configuration file.

• Adding an alarm and sound notifications.

• Supporting both dark and light themes.
