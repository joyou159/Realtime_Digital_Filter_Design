# Digital Filter Designer

This desktop application enables users to design custom digital filters by placing zeros and poles on the z-plane. The application provides a user-friendly interface with the following features:

## Interactive Z-Plane Plot:

### Insertion:

- **Mode Selection:** Use the toggle buttons above to determine whether you want to insert a zero or a pole.
- **Procedure:** Left-click on the z-plane to insert the selected zero or pole.
  
### Deletion

- **Selection:** Right-click on any item in the z-plane.
- **Options:** A list of options will appear, including the deletion option.
- **Procedure:** Choose the deletion option to remove the selected item.

### Dragging

- **Action:** Left-click and hold on an item in the z-plane.
- **Procedure:** Move the mouse to drag the corresponding item to a new position on the z-plane.

### Swapping

- **Selection:** Right-click on any item in the z-plane.
- **Options:** A list of options will appear, including the swapping option.
- **Procedure:** Choose the swapping option to interchange the position of the selected item with another item.

### Clear Operations

- **Mode Selection:** Use the combo box below the z-plane to select the mode of clearing: zeros, poles, or both.
- **Procedure:** After selecting the desired mode, press the clear button to remove the corresponding elements from the z-plane.

### Conjugates

- **Control:** Use the checkbox above to enable or disable the addition of conjugate pairs.
- **Procedure:** When enabled, inserting a zero or pole will automatically add its conjugate pair if applicable.

### Conjugates Control

- **Functionality:** When pairs are inserted as conjugates, all operations (insertion, deletion, dragging, and swapping) will be performed on the pair as long as the checkbox is checked.

## Frequency Response Visualization

- **Magnitude and Phase Response Plot:** Visualize the frequency response of the designed filter with separate graphs for magnitude and phase responses.

## Real-Time Filtering

- **Real-Time Signal Processing:** Apply the designed filter on a lengthy signal in real-time, with customizable temporal resolution.
- **Signal Input:** Users can input an arbitrary real-time signal by moving the mouse on a small padding area. The input signal is determined by the x- or y-dimension of the mouse coordinate, and the motion speed influences the signal frequency.

## All-Pass Filters for Phase Correction

- **All-Pass Filter Library:** Explore and visualize a library of all-pass filters, including their zero-pole combinations and phase responses.
- **Library Selection:** Pick one or more all-pass filters from the library to add to the original design.
- **Custom All-Pass Filters:** Users can build their own all-pass filters by providing arbitrary parameters, and the application calculates the phase response and integrates it into the library.
- **Enable/Disable Functionality:** Users can enable/disable added all-pass elements via checkboxes group.

## Preveiw 

**Low Pass Filter**


**Low Pass Filter**


## Getting Started

1. Clone this repository.

```bash
git clone git@github.com:joyou159/Realtime_Digital_Filter_Design.git
```

2. Install the required dependencies.

```bash
pip install -r requirements.txt
```

3. Run the application.
``` bash 
python main.py
```

## Usage

1. Run the application.
2. Interactively design the filter by placing zeros and poles on the z-plane.
3. Visualize the frequency response.
4. Apply real-time filtering to a signal.
5. Explore and add all-pass filters for phase correction.

Feel free to explore and customize your digital filter design with ease!
