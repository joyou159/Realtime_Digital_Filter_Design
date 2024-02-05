# Digital Filter Designer

This desktop application enables users to design custom digital filters by placing zeros and poles on the z-plane. The application provides a user-friendly interface with the following features:

## Z-Plane Plotting

- **Interactive Z-Plane Plot:** Users can place zeros and poles on the z-plane, and make modifications such as dragging elements.
- **Element Modification:** Modify the position of placed zeros/poles by dragging them interactively.
- **Deletion:** Click on a zero or pole to delete it from the design.
- **Clear Operations:** Options to clear all zeros, clear all poles, or clear both.
- **Conjugates:** Users can choose to add conjugates for complex elements.

## Frequency Response Visualization

- **Magnitude and Phase Response Plot:** Visualize the frequency response of the designed filter with separate graphs for magnitude and phase responses.

## Real-Time Filtering

- **Real-Time Signal Processing:** Apply the designed filter on a lengthy signal in real-time, with customizable temporal resolution.
- **Signal Input:** Users can input an arbitrary real-time signal by moving the mouse on a small padding area. The input signal is determined by the x- or y-dimension of the mouse coordinate, and the motion speed influences the signal frequency.

## All-Pass Filters for Phase Correction

- **All-Pass Filter Library:** Explore and visualize a library of all-pass filters, including their zero-pole combinations and phase responses.
- **Library Selection:** Pick one or more all-pass filters from the library to add to the original design.
- **Custom All-Pass Filters:** Users can build their own all-pass filters by providing arbitrary parameters, and the application calculates the phase response and integrates it into the library.
- **Enable/Disable Functionality:** Users can enable/disable added all-pass elements via a drop-menu or checkboxes group.

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
