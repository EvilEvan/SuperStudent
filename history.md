# History Log

- 2024-06-09 15:25: Fixed initialization sequence error in display mode detection. Resolved NameError by properly ordering function declarations before use.
- 2024-06-09 15:10: Added automatic display scaling to welcome screen. Elements now dynamically resize based on actual screen resolution. Auto-detection feature identifies appropriate display mode (Default/QBoard) based on screen size.
- 2024-06-09 14:45: Added persistent display settings. The game now remembers the user's last selected display mode (Default or QBoard) between sessions.
- 2024-06-09 14:30: Added display size options to welcome screen. Users can now choose between "Default" mode for regular monitors and "QBoard" mode for large touch displays. All fonts, resources, and particle counts now scale according to chosen display mode.
- 2024-04-23 01:45: Identified critical visibility issue in non-colors levels. After first screen shatter, center target display and falling targets become invisible, while colors level remains functional. Issue affects alphabet, numbers, shapes, and C/L case modes.
- 2024-04-23 01:30: Updated game element visibility after screen shatter. Fixed center target, falling targets, and HUD text to maintain proper contrast with alternating background colors.
- 2023-10-XX: Updated level background colors. All levels now start with a white background and alternate with a black theme upon shattering. 
- 2023-10-XX: Fixed background shatter mechanic. Screen now requires the full amount of misclicks (MAX_CRACKS) to shatter after the first instance, ensuring consistent behavior. 
- 2023-10-XX: Corrected crack color and shape outline colors to dynamically contrast with the alternating background after shatters. 